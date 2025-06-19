from typing import Callable, Tuple
import random
import statistics
import math

class SimpleGame:
    def __init__(self, real_value: int, penalidad: int):
        self.penalidad = penalidad
        self.real_value = real_value

    def reward(self, v1: int, v2: int) -> Tuple[int, int]:
        menor = min(v1, v2)
        if v1 == v2:
            return menor, menor
        elif v1 < v2:
            return menor + self.penalidad, menor - self.penalidad
        else:
            return menor - self.penalidad, menor + self.penalidad
        
class Policy:
    def __init__(self, strategy: Callable[[int, int], int]):
        self.strategy = strategy

    def __call__(self, real_value=None, penalty=None) -> int:
        return self.strategy(real_value, penalty)
    

class Player:
    def __init__(self, policy: Policy, knows_value: bool = True):
        self.policy = policy
        self.knows_value = knows_value

    def decide(self, real_value: int, penalty: int) -> int:
        if self.knows_value:
            return self.policy(real_value, penalty)
        else:
            return self.policy(None, penalty)
        

class Simulacion:
    def __init__(self, juego: SimpleGame, jugador1: Player, jugador2: Player, n_simulaciones: int):
        self.juego = juego
        self.jugador1 = jugador1
        self.jugador2 = jugador2
        self.n = n_simulaciones

    def simular(self):
        decisiones = []
        victorias1 = 0
        victorias2 = 0
        empates = 0

        for _ in range(self.n):
            v1 = self.jugador1.decide(self.juego.real_value, self.juego.penalidad)
            v2 = self.jugador2.decide(self.juego.real_value, self.juego.penalidad)
            decisiones.append(v1)
            decisiones.append(v2)
            if v1 == v2:
                empates += 1
            elif v1 < v2:
                victorias1 += 1
            else:
                victorias2 += 1

        resumen = {
            "media": statistics.mean(decisiones),
            "mediana": statistics.median(decisiones),
            "desviacion": statistics.stdev(decisiones) if len(decisiones) > 1 else 0.0,
            "resultados": f"V1: {victorias1}, V2: {victorias2}, empates: {empates}"
        }

        return resumen
    

def softmax(x, temperatura=1.0):
    max_x = max(x)
    exp_x = [math.exp((i - max_x) / temperatura) for i in x]
    sum_exp = sum(exp_x)
    return [v / sum_exp for v in exp_x]

def best_response_stochastic_strategy(game: SimpleGame, opponent_policy: Policy, real_value_known: bool = False, 
                                      samples: int = 50, temperatura: float = 1.0):
    def strategy(real_value, penalty):
        posibles_valores = range(2, 100)
        recompensas_esperadas = []

        for mi_valor in posibles_valores:
            recompensas = []
            for _ in range(samples):
                if real_value_known:
                    valor_otro = opponent_policy(real_value, penalty)
                else:
                    valor_otro = opponent_policy(None, penalty)

                r1, _ = game.reward(mi_valor, valor_otro)
                recompensas.append(r1)

            recompensa_prom = sum(recompensas) / samples
            recompensas_esperadas.append(recompensa_prom)

        # Elegimos con probabilidad proporcional a softmax de las recompensas
        probs = softmax(recompensas_esperadas, temperatura)
        elegido = random.choices(list(posibles_valores), weights=probs, k=1)[0]
        return elegido

    return strategy


def build_opponent_policy(game, lambda_, level, acciones):
    """
    Calcula recursivamente la política de un oponente de nivel `level`.
    """
    if level == 0:
        # Política completamente aleatoria
        prob = 1 / len(acciones)
        return {a: prob for a in acciones}

    # Política del oponente suponiendo que su oponente es de nivel (level - 1)
    lower_policy = build_opponent_policy(game, lambda_, level - 1, acciones)

    expected_rewards = []
    for ai in acciones:
        expected = 0.0
        for aj, prob_aj in lower_policy.items():
            r1, r2 = game.reward(ai, aj)
            expected += prob_aj * r2  # r2 porque es el oponente (jugador 1)
        expected_rewards.append(expected)

    probs = softmax(expected_rewards, lambda_)
    return dict(zip(acciones, probs))

def hierarchical_softmax_strategy_single(game, lambda_, k, jugador=0):
    """
    Devuelve una estrategia de un solo jugador de nivel `k`, suponiendo que
    el oponente juega una política de nivel `k-1`.
    """
    acciones = list(range(2, 100))

    # Construir política del oponente de nivel k-1
    opponent_policy = build_opponent_policy(game, lambda_, k - 1, acciones)

    # Calcular recompensa esperada contra esa política
    expected_rewards = []
    for ai in acciones:
        total = 0.0
        for aj, prob_aj in opponent_policy.items():
            r1, r2 = game.reward(ai, aj)
            total += prob_aj * (r1 if jugador == 0 else r2)
        expected_rewards.append(total)

    probs = softmax(expected_rewards, lambda_)
    final_policy = dict(zip(acciones, probs))

    def strategy(real_value=None, penalty=None):
        valores = list(final_policy.keys())
        pesos = list(final_policy.values())
        return random.choices(valores, weights=pesos, k=1)[0]

    return strategy


# br_stoch_policy = Policy(best_response_stochastic_strategy(juego1, rand_policy, real_value_known=False, temperatura=50))

def estrategia1(valor_real, penalidad):
    return random.randint(85,100)

# Juego
juego1 = SimpleGame(real_value=70, penalidad=5)

# Políticas
rand_policy = Policy(estrategia1)  # Oponente
h_softmax_policy = Policy(hierarchical_softmax_strategy_single(juego1, lambda_=35, k=3))
# Jugadores
jugador1 = Player(h_softmax_policy, knows_value=False)
jugador2 = Player(rand_policy, knows_value=False)

# Simulación
sim = Simulacion(juego1, jugador1, jugador2, n_simulaciones=100000)
print(sim.simular())

# Juego
juego2 = SimpleGame(real_value=70, penalidad=35)

def estrategia2(valor_real, penalidad):
    return random.randint(8,52)

# Políticas
rand_policy = Policy(estrategia2)  # Oponente
h_softmax_policy = Policy(hierarchical_softmax_strategy_single(juego2, lambda_=900, k=10))
# Jugadores
jugador1 = Player(h_softmax_policy, knows_value=False)
jugador2 = Player(rand_policy, knows_value=False)

# Simulación
sim = Simulacion(juego2, jugador1, jugador2, n_simulaciones=100000)
print(sim.simular())

# Juego
juego3 = SimpleGame(real_value=70, penalidad=5)

def estrategia3(valor_real, penalidad):
    return 70

# Políticas
honest_policy = Policy(estrategia3)  # Oponente
h_softmax_policy = Policy(hierarchical_softmax_strategy_single(juego3, lambda_=19, k=10))
# Jugadores
jugador1 = Player(h_softmax_policy, knows_value=True)
jugador2 = Player(honest_policy, knows_value=True)

# Simulación
sim = Simulacion(juego3, jugador1, jugador2, n_simulaciones=100000)
print(sim.simular())

# Juego
juego4 = SimpleGame(real_value=70, penalidad=35)

def estrategia4(valor_real, penalidad):
    return random.randint(20,45)

# Políticas
afraid_policy = Policy(estrategia4)  # Oponente
h_softmax_policy = Policy(hierarchical_softmax_strategy_single(juego4, lambda_=30, k=6))
# Jugadores
jugador1 = Player(h_softmax_policy, knows_value=True)
jugador2 = Player(afraid_policy, knows_value=True)

# Simulación
sim = Simulacion(juego4, jugador1, jugador2, n_simulaciones=100000)
print(sim.simular())


# Juego
juego5 = SimpleGame(real_value=70, penalidad=0)

def estrategia5(valor_real, penalidad):
    return 100

# Políticas
exploit_policy = Policy(estrategia5)  # Oponente
h_softmax_policy = Policy(hierarchical_softmax_strategy_single(juego5, lambda_=14, k=6))
# Jugadores
jugador1 = Player(h_softmax_policy, knows_value=True)
jugador2 = Player(exploit_policy, knows_value=True)

# Simulación
sim = Simulacion(juego5, jugador1, jugador2, n_simulaciones=100000)
print(sim.simular())

# Juego
juego6 = SimpleGame(real_value=20, penalidad=0)

def estrategia6(valor_real, penalidad):
    return 100

# Políticas
exploit_policy = Policy(estrategia5)  # Oponente
h_softmax_policy = Policy(hierarchical_softmax_strategy_single(juego5, lambda_=1000000, k=50))
# Jugadores
jugador1 = Player(h_softmax_policy, knows_value=True)
jugador2 = Player(exploit_policy, knows_value=True)

# Simulación
sim = Simulacion(juego6, jugador1, jugador2, n_simulaciones=100000)
print(sim.simular())
