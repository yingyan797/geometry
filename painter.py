from PIL import Image
import numpy as np
import copy
class Animation:
    def __init__(self):
        self.base:np.ndarray = None
        self.template = None
        self.canvas:np.ndarray = None
        self.frames = []

    def create(self, h, w, dtype):
        if dtype == bool:
            self.base = np.ones((h,w), bool)
        elif dtype == np.uint8:
            self.base = 255+np.zeros((h,w), np.uint8)

    def base_edit(self):
        self.canvas = self.base
    def base_save(self):
        self.base = copy.deepcopy(self.canvas)
    def add_frame(self):
        if not self.frames or not np.array_equal(self.frames[-1], self.canvas):
            self.frames.append(self.canvas)

    def draw_rect(self, r, c, w, h=None, color=0):
        if h is None:
            h = w
        self.canvas[r-h:r+h+1, c-w:c+w+1] = color

    def draw_circle(self, r, c, radius, color=0):
        for i in range(r-radius, r+radius+1):
            for j in range(c-radius, c+radius+1):
                if np.power(i-r, 2)+np.power(j-c, 2) <= radius*radius:
                    self.canvas[i][j] = color

    def line_connect(self, p1, p2, color=0, w=0):
        # print(imarr.shape, p1, p2)
        if p1[0] == p2[0]:
            self.canvas[min(p1[1], p2[1]):max(p1[1], p2[1]),p1[0]-w:p1[0]+w+1] = color
        elif p1[1] == p2[1]:
            self.canvas[p2[1]-w:p2[1]+w+1, min(p1[0], p2[0]):min(p1[0], p2[0])] = color
        else:
            rat = (p2[1]-p1[1])/(p2[0]-p1[0])
            d = 1
            if abs(rat) > 1:
                c = p1[0]
                if p2[1] < p1[1]:
                    d = -1
                for r in range(p1[1],p2[1], d):
                    self.draw_rect(r, int(c), w, color=color)
                    c += d/rat
            else:
                r = p1[1]
                if p2[0] < p1[0]:
                    d = -1
                for c in range(p1[0], p2[0], d):
                    self.draw_rect(int(r), c, w, color=color)
                    self.canvas[int(r)-w:int(r)+w+1,c-w:c+w+1] = color
                    r += d*rat

    def animate(self, name):
        print("frame length:", len(self.frames))
        if self.template:
            for i in range(len(self.frames)):
                self.frames[i] = np.minimum(self.template, self.frames[i])
        frame_one = Image.fromarray(self.frames[0]) 
        frame_one.save(f"static/{name}.gif", format="GIF", append_images=map(lambda arr: Image.fromarray(arr), self.frames),
            save_all=True, duration=30, loop=0)