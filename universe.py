import numpy as np

G = 6.6743e-11

class Point:
    def __init__(self, mass, loc, vel) -> None:
        self.mass = mass
        self.loc = loc
        self.vel = vel

    def apply_force(self, fvec, dt):
        acc = fvec/self.mass
        self.vel += acc*dt

    def move(self, dt):
        self.loc += self.vel * dt

    def momentum(self):
        return self.mass * self.vel
    
    def keng(self):
        return np.sum(np.multiply(self.vel, self.vel))*self.mass/2

def gravity(p1:Point, p2:Point):
    vec = p2.loc - p1.loc
    r2 = np.sum(np.multiply(vec, vec))
    f = G * p1.mass * p2.mass / r2
    return (f*vec, -f*vec)

class Planet(Point):
    def __init__(self, radius, mass, loc, vel, dt=1) -> None:
        self.radius = radius
        super().__init__(mass, loc, vel, dt)

class Charge(Point):
    def __init__(self, charge, mass, loc, vel, dt=1) -> None:
        self.charge = charge
        super().__init__(mass, loc, vel, dt)

class Field:
    def __init__(self, particles:list[Point]) -> None:
        self.particles = particles

    def force(self, p):
        return np.zeros(2)
    
    def simulate(self, tlim, dt):
        time = 0
        self.locs = [[] for p in self.particles]
        while time < tlim*dt:
            for i in range(len(self.particles)):
                p0 = self.particles[i]
                self.locs[i].append(p0.loc)
                p0.apply_force(self.force(p0), dt)
                p0.move(dt)
            time += dt
    
class UniGravity(Field):
    def force(self, p):
        return np.array([0,-9.8])

class UniElectric(Field):
    def force(self, p):
        return super().force(p)

class UniMagnetic(Field):
    def force(self, p):
        return super().force(p)

class Universe(Field):
    def force(self, p0):
        for p in self.particles:
            if p != p0:
                pass
        
if __name__ == "__main__":
    ps = [Planet(100+i, 100, np.array([0,0]), np.array([1,1])) for i in range(10)]
    p0 = ps[0]
    for p in ps:
        print(p==p0)