class Traveler:
    def __init__(self, V1: int, V2: int, P: int):
        self.V1 = V1
        self.V2 = V2
        self.P = P

    def reward(self) -> tuple[int, int]:
        minV = min(self.V1, self.V2)
        if self.V1 == self.V2:
            return minV, minV
        elif self.V1 < self.V2:
            return minV + self.P, minV - self.P
        else:
            return minV - self.P, minV + self.P
