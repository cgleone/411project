import numpy as np
import matplotlib.pyplot as plt
import pkbar
from food_options import f


class Swarm:

    def __init__(self, f, n, w, c1, c2, D):
        self.n = n
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.f = f

        # create particles
        dist = np.random.rand(n, D)
        low = np.zeros((n, D))
        high = np.ones((n, D))
        initial_xs = np.where(dist<.2, high, low)
        initial_xs = np.where(dist<.1, 2*high, initial_xs)
        initial_vs = np.random.rand(n, D) * 1
        self.particles = [Particle(x0, v0, f) for x0, v0 in zip(initial_xs, initial_vs)]

        self.best = self.get_best()

    def get_best(self):
        return min(self.particles, key=lambda pp: pp.get_best_f())

    def step(self, f=None, w=None):
        if f is not None:
            self.f = f

        if w is not None:
            self.w = w

        for p in self.particles:
            p.update_coords(self.w, self.c1, self.c2, self.best.get_best_x(), self.f)

        self.best = min((self.get_best(), self.best), key=lambda pp: pp.get_best_f())

    def plot_particles(self, c='b'):
        for p in self.particles:
            plt.scatter(*p.get_x(), c=c)
            plt.xlim(-5, 5)
            plt.ylim(-5, 5)


class Particle:
    def __init__(self, x0, v0, f):
        self.x = x0
        self.v = v0
        self.best_x = x0
        self.best_f = f(x0)

    def update_coords(self, w, c1, c2, swarm_best, f):
        r1, r2 = np.random.rand(2)
        self.v = self.v * w + r1 * c1 * (self.best_x - self.x) + r2 * c2 * (swarm_best - self.x)
        # self.v = (swarm_best - self.x) * 0.1
        self.x = self.x + self.v
        rounded_x = [round(a, 1) for a in self.x]

        f_val = f(rounded_x)
        if f_val < self.best_f:
            self.best_x = self.x
            self.best_f = f_val

    def get_x(self):
        return self.x

    def get_best_x(self):
        return self.best_x

    def get_best_f(self):
        return self.best_f

    def get_velocity(self):
        return self.v


def pso(n, F, w, c1, c2, menus):
    swarm = Swarm(F, n, w, c1, c2, D)
    iterations = 100
    pbar = pkbar.Pbar('running swarm', iterations)
    bests = []
    for i in range(iterations):
        #swarm.step(w=2 * np.exp(-i/1000))
        swarm.step()
        bests.append(swarm.get_best().get_best_x())
        pbar.update(i)
        print([round(a, 2) for a in bests[i]])
        # swarm.plot_particles()
        # plt.show()
    velocities = [p.get_velocity() for p in swarm.particles]
   # print("Final Particle Velocities: {}".format(velocities))
    return bests[-1]

if __name__=="__main__":

    np.random.seed(444)

    n = 350 # number of particles
    D = 70 # number of dimensions
    # def f(x):
    #     return np.sum(np.abs(x)) # f(x) = sum|x|

    x_answer = pso(n, f, 0.4, 2, 2, D)
    f_answer = f(x_answer, print_final=True)
    print([round(a, 1) for a in x_answer])
    print("Objective function value: {}".format(f_answer))

