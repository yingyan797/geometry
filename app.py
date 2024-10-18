from flask import Flask, render_template, request
import numpy as np
app = Flask(__name__)

class Website:
    def __init__(self, palette):
        self.palette = [[i,palette[i],False] for i in range(len(palette))]
        self.canvas = None
        self.ready = False
        self.color = 0
        self.spanrow = []
        self.spancol = []

    def colorsel(self, num):
        for c in range(len(self.palette)):
            if c == num:
                self.palette[c][2] = True
                self.color = c
            else:
                self.palette[c][2] = False

    def create(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols
        self.canvas = np.array([[[r,c,0] for c in range(ncols)] for r in range(nrows)])
        self.ready = True

    def get_range(self):
        rf, rt, cf, ct = -1,-1,-1,-1
        if self.spanrow:
            if len(self.spanrow) == 2:
                rf, rt = min(self.spanrow), max(self.spanrow)
            else:
                rf, rt = self.spanrow[0], self.spanrow[0]
        if self.spancol:
            if len(self.spancol) == 2:
                cf, ct = min(self.spancol), max(self.spancol)
            else:
                cf, ct = self.spancol[0], self.spancol[0]
        return [rf,rt,cf,ct]


site = Website(["white","lightblue","lightgreen","lightsalmon","lightseagreen",
                "cornflowerblue","red", "blue", "yellow","black"])

@app.route("/", methods=["get", "post"])
def index():
    return render_template("index.html")

@app.route("/drawing", methods=["get", "post"])
def drawing():
    fm = request.form
    print(fm)
    if fm.get("create"):
        nrows, ncols = 20, 30
        if r:=fm.get("nrows"):
            nrows = int(r)
        if c:=fm.get("ncols"):
            ncols = int(c)
        site.create(nrows, ncols)
    else:
        for k, v in fm.items():
            if k.startswith("color_") and v:
                site.colorsel(int(k[6:]))
                break
            if k.startswith("pix_"):
                coord = [int(seg) for seg in k[4:].split("_")]
                site.canvas[coord[0]][coord[1]][2] = site.color
                break
            if k.startswith("spanrow_"):
                spr = int(k[8:])
                if len(site.spanrow) == 2:
                    site.spanrow.pop(0)
                site.spanrow.append(spr)
                break
            if k.startswith("spancol_"):
                spc = int(k[8:])
                if len(site.spancol) == 2:
                    site.spancol.pop(0)
                site.spancol.append(spc)
                break
        if fm.get("fill"):
            rg = site.get_range()
            if all(map(lambda a:a>=0, rg)):
                site.canvas[rg[0]:rg[1]+1, rg[2]:rg[3]+1, 2] = site.color

    return render_template("drawing.html", site=site)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)