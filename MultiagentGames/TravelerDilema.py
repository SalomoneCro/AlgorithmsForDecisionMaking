from typing import Callable, Tuple
import random

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
        

def estrategia_deterministica(valor_real, penalidad):
    return valor_real

# Estrategia aleatoria entre 0 y 10
def estrategia_estocastica(_, penalidad):
    return random.randint(0, 10)

# Crear políticas
det_policy = Policy(estrategia_deterministica)
rand_policy = Policy(estrategia_estocastica)

# Crear jugadores
jugador1 = Player(det_policy, knows_value=True)
jugador2 = Player(rand_policy, knows_value=False)

# Crear juego
juego = SimpleGame(real_value=7, penalidad=2)

# Simular decisión y recompensa
v1 = jugador1.decide(juego.real_value, juego.penalidad)
v2 = jugador2.decide(juego.real_value, juego.penalidad)
r1, r2 = juego.reward(v1, v2)

print(f"Jugador1 eligió {v1}, recompensa: {r1}")
print(f"Jugador2 eligió {v2}, recompensa: {r2}")