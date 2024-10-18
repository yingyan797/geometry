import numpy as np
from painter import Animation
from matplotlib import pyplot as plt
G = 6.6743e-11

class Point:
    def __init__(self, mass, loc, vel, static=False) -> None:
        self.static = static
        self.mass = mass
        self.loc = loc
        self.vel = vel
        self.force_sum = np.zeros(2)

    def apply_force(self, fvec, dt):
        print(type(self), fvec)
        acc = fvec/self.mass
        self.vel += acc*dt

    def move(self, dt):
        self.loc += self.vel * dt

    def momentum(self):
        return self.mass * self.vel
    
    def keng(self):
        return np.dot(self.vel, self.vel)*self.mass/2

def gravity(p1:Point, p2:Point):
    vec = p2.loc - p1.loc
    r2 = np.dot(vec, vec)
    f = G * p1.mass * p2.mass / r2
    return (f*vec, -f*vec)

class Planet(Point):
    def __init__(self, radius, mass, loc, vel, static) -> None:
        self.radius = radius
        super().__init__(mass, loc, vel, static)

class Charge(Point):
    def __init__(self, charge, mass, loc, vel, static) -> None:
        self.charge = charge
        super().__init__(mass, loc, vel, static)

class Field:
    def __init__(self, particles:list[Point]) -> None:
        self.particles = particles
        self.movable = [p for p in self.particles if not p.static]
        self.static = [p for p in self.particles if p.static]

    def force(self, p):
        return np.zeros(2)
    
    def simulate(self, tlim, dt, updater=None):
        time = 0
        self.locs = tuple([] for _ in self.movable)
        while time < tlim*dt:
            if updater:
                updater()
            for i in range(len(self.movable)):
                p0 = self.movable[i]
                self.locs[i].append([x for x in p0.loc])
                p0.apply_force(self.force(p0), dt)
                p0.move(dt)
            time += dt
        self.locs = np.array(self.locs)

    def animate(self):
        ani = Animation()
        for loc in self.locs:
            xs = loc[:, 0]
            ys = loc[:, 1]
            plt.plot(xs, ys)
            plt.show()

class UniGravity(Field):
    def force(self, p:Point):
        return p.mass * np.array([0,-9.8])

class UniElectric(Field):
    def force(self, p):
        return super().force(p)

class UniMagnetic(Field):
    def force(self, p):
        return super().force(p)

class Universe(Field):
    def force(self, p:Point):
        return p.force_sum

    def calc_forces(self):
        rem_parts = [p for p in self.particles]
        for p in self.movable:
            for p0 in rem_parts:
                if p != p0:
                    gf12, gf21 = gravity(p, p0)
                    print(gf12)
                    p.force_sum += gf12
                    if not p0.static:
                        p0.force_sum += gf21
            rem_parts.remove(p)

class DampGravity(UniGravity):
    def __init__(self, particles: list[Point], resist=1/1000) -> None:
        super().__init__(particles)
        self.resist = resist
    def force(self, p:Point):
        g = super().force(p)
        v2 = np.dot(p.vel, p.vel)
        f = g - self.resist * v2 * p.vel / np.sqrt(v2)
        return f

        
if __name__ == "__main__":
    pl = Planet(6371000, 6e24, np.array([0,0], dtype=float), np.array([0,0], dtype=float), True)
    tr = Point(2, np.array([-6371000,0], dtype=float), np.array([0,7900], dtype=float))
    env = Universe([pl, tr])
    env.simulate(100, 0.1, env.calc_forces)
    env.animate()
