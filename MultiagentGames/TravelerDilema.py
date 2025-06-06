from typing import Callable, Tuple
import random
import statistics

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
    

def estrategia1(valor_real, penalidad):
    return random.randint(60,90)

def estrategia2(valor_real, penalidad):
    return random.randint(70, 80)

jugador1 = Player(estrategia1, False)
jugador2 = Player(estrategia2, False)

juego = SimpleGame(70, 5)

simulacion = Simulacion(juego, jugador1, jugador2, 100)

print(simulacion.simular())