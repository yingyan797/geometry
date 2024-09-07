from painter import Animation, copy
from util import sveqsolve
import numpy as np
import matplotlib.pyplot as plt
import os

class RodSlide:
    def __init__(self, ani:Animation, traj=True, sweep=True, r=100, l=200, dx=1) -> None:
        self.traj, self.sweep = traj, sweep
        self.ani = ani
        self.r = r
        self.l = l
        self.dx = dx
        self.template = None
    def reset(self):
        self.traj, self.l1, self.l2 = [], [], []
    def block(self, s, i):
        if s == 1:
            if not isinstance(self.l1[i], np.ndarray):
                return [self.l1[i], 0]
            return self.l1[i]
        else:
            if not isinstance(self.l2[i], np.ndarray):
                return [0, self.l2[i]]
            return self.l2[i]
    def corners(self, dtype):
        pass
    def position(self, lx, ly):
        dx = (ly[0]-lx[0])/self.r*self.l
        dy = (ly[1]-lx[1])/self.r*self.l
        px = lx[0]+dx
        py = lx[1]+dy
        return [px, py]
    def full_cycle(self):
        self.traj = np.array(self.traj, dtype=np.int16)
        self.l1 = np.array(self.l1, dtype=np.int16)
        self.l2 = np.array(self.l2, dtype=np.int16)
        self.corners(bool if not self.sweep else np.uint8)
    
    def animate(self, name, trajw=1):
        trans = np.array([self.hc, self.hr], dtype=np.int16)
        if trajw >= 0:
            for t in self.traj:
                pen = t+trans
                self.ani.base[pen[1]-trajw:pen[1]+trajw+1,pen[0]-trajw:pen[0]+trajw+1] = 0
        self.ani.template = copy.deepcopy(self.ani.base)
        for imi in range(len(self.traj)):
            self.ani.base_edit()
            pen = self.traj[imi]+trans
            x = self.block(1, imi)+trans
            y = self.block(2, imi)+trans
            if self.sweep:
                self.ani.line_connect(pen, x, 150, 3)
            self.ani.base_save()
            self.ani.draw_rect(pen[1], pen[0], 3)
            self.ani.draw_rect(x[1], x[0], 5)
            self.ani.draw_rect(y[1], y[0], 5)
            self.ani.line_connect(pen, x, w=1)
            self.ani.add_frame()
        print("graphics")
        self.ani.animate(f"{type(self).__name__}-{name}")

class Biaxial(RodSlide):
    def _qcycle(self):
        x, l1, l2, p = 0, [], [], []
        while x <= self.r:
            y = np.sqrt(np.power(self.r, 2) - np.power(x, 2))
            l1.append(x)
            l2.append(y)
            p.append(self.position([x,0], [0,y]))
            x += self.dx
        return l1, l2, p
    def corners(self, dtype):
        self.ani.create(2*int(np.max(self.traj[:,1]))+20, 2*int(np.max(self.traj[:,0]))+20, dtype)
        self.hr, self.hc = int(self.ani.base.shape[0]/2), int(self.ani.base.shape[1]/2)
    def full_cycle(self):
        self.reset()
        l1, l2, qtraj = self._qcycle()
        self.traj += qtraj
        self.l1 += l1
        self.l2 += l2
        funcs = [(lambda c: [c[0], -c[1]], True), (lambda c: [-c[0], -c[1]], False), (lambda c: [-c[0], c[1]], True)]
        for func, rv in funcs:
            t = [c for c in map(func, qtraj)]
            if rv:
                t.reverse()
            self.traj += t
            t = [c for c in map(func, zip(l1, l2))]
            if rv:
                t.reverse()
            self.l1 += [p[0] for p in t]
            self.l2 += [p[1] for p in t]
        super().full_cycle() 
        self.ani.base[self.hr, :] = 0
        self.ani.base[:, self.hc] = 0       

class SkewBiaxial(RodSlide):
    def set_angle(self, ang):
        while ang < -180:
            ang += 180
        while ang > 180:
            ang -= 180
        self.angle = ang*np.pi/180
        return self
    def corners(self, dtype):
        self.ani.create(2*int(np.max(self.traj[:,1]))+20, 2*int(np.max(self.traj[:,0]))+20, dtype)
        self.hr, self.hc = int(self.ani.base.shape[0]/2), int(self.ani.base.shape[1]/2)
    def full_cycle(self):
        self.reset()
        x, l1, l2, p = 0, [[],[]], [[],[]], [[],[]]
        up, s = True, 1
        while x >= 0:
            tsin = x * np.sin(self.angle)/self.r
            t = np.arcsin(tsin) if tsin < 1 else np.pi/2
            if s > 0:
                if tsin >= 0.999:
                    s = -1
            else:
                t = np.pi - t
            a = np.pi - t - self.angle
            yl = np.sqrt(x*x + self.r*self.r - 2*x*self.r*np.cos(a))
            if up:
                if t + self.angle >= np.pi:
                    up = False
            else:
                yl = -yl
            xy = [yl*np.cos(self.angle),yl*np.sin(self.angle)]
            l2[0].append(xy)
            # l2[1] = [[-xy[0], -xy[1]]] + l2[1]
            l2[1].append([-xy[0], -xy[1]])
            l1[0].append(x)
            # l1[1] = [-x] + l1[1]
            l1[1].append(-x)
            pos = self.position([x,0], xy)
            p[0].append(pos)
            # p[1] = [[-pos[0], -pos[1]]] + p[1]
            p[1].append([-pos[0], -pos[1]])
            x += s*self.dx
        self.l1 = l1[0] + l1[1]
        self.l2 = l2[0] + l2[1]
        self.traj = p[0] + p[1]
        super().full_cycle()
        self.ani.base[self.hr, :] = 0
        if self.angle == np.pi/2:
            self.ani.base[:, self.hc] = 0  
        else:
            slop = np.tan(self.angle)
            r = int((self.hc-10)*slop)
            c = [10, self.ani.base.shape[1]-10]
            if self.hr - r < 0:
                r = self.hr
                c[0] = self.hc - self.hr/slop
                c[1] = self.hc + self.hr/slop
            self.ani.base_edit()
            self.ani.line_connect([c[0],self.hr-r], [c[1], self.hr+r])

class FunctionCurve(RodSlide):
    def set_shape(self, func, xf, xt, width):
        self.func = func
        self.xf, self.xt = xf, xt
        self.width = width
        return self
    def corners(self, dtype):
        cs = []
        for axis in [0,1]:
            for npm in (np.min, np.max):
                cs.append(npm(np.array([npm(ps[:, axis]) for ps in [self.traj, self.l1, self.l2]])))
        self.ani.create(cs[3]-cs[2]+20, cs[1]-cs[0]+20, dtype=dtype)
        self.hr, self.hc = int(10-cs[2]), int(10-cs[0])
    def full_cycle(self):
        self.reset()
        x1 = self.xf
        def locate(x1, y1, ang):
            x2 = x1 - self.r * np.sin(ang)
            y = y1 + self.r * np.cos(ang)
            return y - self.func(x2)
        while x1 <= self.xt:
            y1 = self.func(x1)
            ang = sveqsolve(lambda ang: locate(x1, y1, ang), 0, 0, np.pi, 0.02)                
            x2 = x1 - self.r * np.sin(ang)
            y2 = y1 + self.r * np.cos(ang)
            self.l1.append([x1,y1])
            self.l2.append([x2,y2])
            self.traj.append(self.position([x1,y1], [x2,y2]))
            x1 += self.dx
        super().full_cycle()
        yp = None
        for x in range(10-self.hc, self.xt+1, 1):
            y = int(self.func(x))
            if yp is not None:
                yl, yh = min(yp,y), max(yp,y)
                self.ani.base[yl+self.hr-1:yh+self.hr+1, self.hc+x] = 0 
                if yp != y:
                    slop = 1/(yp-y)
                    dx = np.sqrt(np.power(self.width, 2) / (1+ np.power(slop, 2)))
                    dy = int(slop*dx)
                    dx = int(dx)
                    self.ani.base[yp-dy+self.hr:yp-dy+self.hr+1, x-1-dx+self.hc:x-dx+self.hc] = 0
                    self.ani.base[yp+dy+self.hr:yp+dy+self.hr+1, x-1+dx+self.hc:x+dx+self.hc] = 0
                else:
                    self.ani.base[yp+self.hr-self.width-1:yp+self.hr-self.width, self.hc+x] = 0 
                    self.ani.base[yp+self.hr+self.width-1:yp+self.hr+self.width, self.hc+x] = 0 
            yp = y

def clear_animate():
    for fn in os.listdir("static"):
        if fn.endswith(".gif"):
            os.remove(f"static/{fn}")

if __name__ == "__main__":
    # clear_animate()
    # for a in range(15, 95, 15):
    #     ani.__init__()
    #     ell = SkewBiaxial(ani).set_angle(a)
    #     ell.full_cycle()
    #     ell.animate(a)
    def straight(r, x):
        if abs(x) >= r/np.sqrt(2):
            return -abs(x)+r*np.sqrt(2)
        return np.sqrt(r*r - x*x)
    # xs = [i for i in range(-100, 100)]
    # ys = list(map(lambda x: straight(100, x), xs))
    # plt.plot(xs, ys)
    # plt.savefig("abs.png")
    for l in range(60, 105, 20):
        ani = Animation()
        parab = FunctionCurve(ani, dx=1, r=50, l=l).set_shape(lambda x: straight(50, x), -120, 120, 20)
        parab.full_cycle()
        parab.animate(f"abs_{l}", -1)

