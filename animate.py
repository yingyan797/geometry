from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os, copy

def line_connect(imarr: np.ndarray, p1, p2, w=0):
    # print(imarr.shape, p1, p2)
    if p1[0] == p2[0]:
        imarr[min(p1[1], p2[1]):max(p1[1], p2[1]),p1[0]-w:p1[0]+w+1] = 0
    elif p1[1] == p2[1]:
        imarr[p2[1]-w:p2[1]+w+1, min(p1[0], p2[0]):min(p1[0], p2[0])] = 0
    else:
        rat = (p2[1]-p1[1])/(p2[0]-p1[0])
        d = 1
        if abs(rat) > 1:
            c = p1[0]
            if p2[1] < p1[1]:
                d = -1
            for r in range(p1[1],p2[1], d):
                imarr[r-w:r+w+1,int(c)-w:int(c)+w+1] = 0
                c += d/rat
        else:
            r = p1[1]
            if p2[0] < p1[0]:
                d = -1
            for c in range(p1[0], p2[0], d):
                imarr[int(r)-w:int(r)+w+1,c-w:c+w+1] = 0
                r += d*rat

class RodSlide:
    def __init__(self, r=100, l=200, dx=1) -> None:
        self.r = r
        self.l = l
        self.dx = dx
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
        self.base = np.ones((2*int(np.max(self.traj[:,1]))+20, 2*int(np.max(self.traj[:,0]))+20), dtype=bool)
        self.hr, self.hc = int(self.base.shape[0]/2), int(self.base.shape[1]/2)
    def animate(self, name):
        frames = []
        trans = np.array([self.hc, self.hr], dtype=np.int16)
        for t in self.traj:
            pen = t+trans
            self.base[pen[1]-1:pen[1]+2,pen[0]-1:pen[0]+2] = 0
        for imi in range(len(self.traj)):
            imarr = copy.deepcopy(self.base)
            pen = self.traj[imi]+trans
            x = self.block(1, imi)+trans
            y = self.block(2, imi)+trans
            imarr[pen[1]-5:pen[1]+6,pen[0]-5:pen[0]+6] = 0
            imarr[x[1]-7:x[1]+8,x[0]-7:x[0]+8] = 0
            imarr[y[1]-7:y[1]+8,y[0]-7:y[0]+8] = 0

            line_connect(imarr, pen, x, 1)
            im = Image.fromarray(imarr)
            frames.append(im)

        frame_one = frames[0]
        frame_one.save(f"static/{type(self).__name__}-{name}.gif", format="GIF", append_images=frames,
            save_all=True, duration=30, loop=0)

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
        self.base[self.hr, :] = 0
        self.base[:, self.hc] = 0       

class SkewBiaxial(RodSlide):
    def __init__(self, ang, r=100, l=200, dx=0.75) -> None:
        super().__init__(r, l, dx)
        while ang < -180:
            ang += 180
        while ang > 180:
            ang -= 180
        self.angle = ang*np.pi/180
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
        self.base[self.hr, :] = 0
        if self.angle == np.pi/2:
            self.base[:, self.hc] = 0  
        else:
            slop = np.tan(self.angle)
            r = int((self.hc-10)*slop)
            c = [10, self.base.shape[1]-10]
            if self.hr - r < 0:
                r = self.hr
                c[0] = self.hc - self.hr/slop
                c[1] = self.hc + self.hr/slop

            line_connect(self.base, [c[0],self.hr-r], [c[1], self.hr+r])

def clear_animate():
    for fn in os.listdir("static"):
        if fn.endswith(".gif"):
            os.remove(f"static/{fn}")

if __name__ == "__main__":
    clear_animate()
    for a in range(15, 95, 15):
        ell = SkewBiaxial(a, 75, 150)
        ell.full_cycle()
        ell.animate(a)

