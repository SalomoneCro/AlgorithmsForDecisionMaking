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

        for _ in range(self.n):
            v1 = self.jugador1.decide(self.juego.real_value, self.juego.penalidad)
            v2 = self.jugador2.decide(self.juego.real_value, self.juego.penalidad)
            decisiones.append(v1)
            decisiones.append(v2)

        resumen = {
            "media": statistics.mean(decisiones),
            "mediana": statistics.median(decisiones),
            "desviacion": statistics.stdev(decisiones) if len(decisiones) > 1 else 0.0
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

def estrategia1(valor_real, penalidad):
    return random.randint(85,100)

# Juego
juego = SimpleGame(real_value=80, penalidad=10)

# Políticas
rand_policy = Policy(estrategia1)  # Oponente
br_stoch_policy = Policy(best_response_stochastic_strategy(juego, rand_policy, knows_opponent=False))

# Jugadores
jugador1 = Player(br_stoch_policy, knows_value=True)
jugador2 = Player(rand_policy, knows_value=False)

# Simulación
sim = Simulacion(juego, jugador1, jugador2, n_simulaciones=1000)
print(sim.simular())
