from typing import Callable, Tuple
import random
import statistics
import math
from time import time

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
                victorias2 += 1
            else:
                victorias1 += 1

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

# def hierarchical_softmax_strategy(game, level_k: int, temperatura: float = 1.0, samples: int = 50):
#     posibles_valores = list(range(2, 100))  # Dominio de decisiones

#     def build_policy(level):
#         if level == 0:
#             # Nivel 0: elige al azar
#             def policy_0(real_value, penalty):
#                 return random.choice(posibles_valores)
#             return policy_0

#         # Nivel > 0: responde con softmax a la política del nivel inferior
#         lower_policy = build_policy(level - 1)
#         def policy(real_value, penalty):
#             recompensas_esperadas = []

#             for mi_valor in posibles_valores:
#                 recompensas = []
#                 for _ in range(samples):
#                     valor_otro = lower_policy(real_value, penalty)
#                     r1, _ = game.reward(mi_valor, valor_otro)
#                     recompensas.append(r1)

#                 recompensa_prom = sum(recompensas) / samples
#                 recompensas_esperadas.append(recompensa_prom)

#             probs = softmax(recompensas_esperadas, temperatura)
#             elegido = random.choices(list(posibles_valores), weights=probs, k=1)[0]
#             return elegido

#         return policy

#     return build_policy(level_k)

def hierarchical_softmax(game, lambda_: float, k: int, jugador: int = 0):
    acciones = list(range(2, 100))  # Dominio de acciones
    n = 2  # Suponiendo un juego de 2 jugadores

    # Inicializamos políticas uniformes
    pi = []
    for _ in range(n):
        probs = [1 / len(acciones)] * len(acciones)
        pi.append(dict(zip(acciones, probs)))

    # Iteramos k niveles de razonamiento
    for _ in range(k):
        new_pi = []
        for i in range(n):
            otro = 1 - i
            recompensas_esperadas = []
            for ai in acciones:
                esperada = 0.0
                for aj, prob_aj in pi[otro].items():
                    r1, r2 = game.reward(ai, aj)
                    ri = r1 if i == 0 else r2
                    esperada += prob_aj * ri
                recompensas_esperadas.append(esperada)

            probs = softmax(recompensas_esperadas, lambda_)
            new_pi.append(dict(zip(acciones, probs)))
        pi = new_pi

    # Devolvemos una estrategia que elige según la política resultante del jugador pedido
    final_policy = pi[jugador]

    def strategy(real_value=None, penalty=None):
        valores = list(final_policy.keys())
        pesos = list(final_policy.values())
        return random.choices(valores, weights=pesos, k=1)[0]

    return strategy

def estrategia1(valor_real, penalidad):
    return random.randint(30,90)

# Juego
juego = SimpleGame(real_value=90, penalidad=60)

# Políticas
rand_policy = Policy(estrategia1)  # Oponente
h_softmax_policy = hierarchical_softmax(juego, 2, 50)
br_stoch_policy = Policy(best_response_stochastic_strategy(juego, rand_policy, real_value_known=True))

# Jugadores
jugador1 = Player(h_softmax_policy, knows_value=True)
# jugador2 = Player(rand_policy, knows_value=False)
jugador2 = Player(h_softmax_policy, knows_value=False)
a = time()
# Simulación
sim = Simulacion(juego, jugador1, jugador2, n_simulaciones=1000)
print(sim.simular())
print((time() - a) / 60)
