

class Swarm:

    def __init__(self, n, w, c1, c2):





class Particle:
    def __init__(self, x0):
        self.x = x0
        self.v = 0
        self.best = x0

    def update_coords(self, w, c1, c2, swarm_best):
        self.v = self.v*w + c1*(self.best-self.x) + c2*(swarm_best-self.x)
        self.x = self.x + self.v
