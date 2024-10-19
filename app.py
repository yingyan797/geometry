from flask import Flask, render_template, request
import numpy as np
from PIL import Image
import os
from database import Database
app = Flask(__name__)

class Website:
    def __init__(self):
        self.canvas = None
        self.ready = False
        self.color = 0
        self.spanrow = []
        self.spancol = []
        self.db = Database()
        self.history = []
        self.title, self.session = "", 1

    def colorsel(self, num):
        for c in range(len(self.palette)):
            if c == num:
                self.palette[c][2] = True
                self.color = c
            else:
                self.palette[c][2] = False
    def colorset(self, palette):
        self.palette = [[i,palette[i],False] for i in range(len(palette))]

    def create(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols
        self.canvas = np.array([[[r,c,0] for c in range(ncols)] for r in range(nrows)], dtype=np.uint8)
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
    
    def get_history(self, update=False):
        if not self.history or update:
            self.history = self.db.read_all("select rowid, Title, Width, Height from History")

    def load_num(self, rid):
        title, w,h, pal, code = self.db.read_one(f"select * from History where rowid={rid}")
        canvas = canvas_decode(code, w, h)
        self.colorset([pal[i:i+6] for i in range(0,len(pal),6)])
        self.create(h,w)
        self.title = title
        self.canvas[:,:,2] = canvas
        self.get_history(True)
    
    def store(self, title, session=0):
        code = ""
        for row in self.canvas:
            for col in row:
                c = col[2]
                if c < 9:
                    code += str(c+1)
                else:
                    code += f"0{c-9}"
        pal_code = "".join([p[1] for p in self.palette])
        if not session:
            self.db.do(f"insert into History (Title, Width, Height, Palette, Canvas) values (\
                '{title}', {self.ncols}, {self.nrows}, '{pal_code}', '{code}')")
            self.session = len(self.history)+1
        else:
            self.db.do(f"update History set Title='{title}',Width={self.ncols}, Height={self.nrows}, Palette='{pal_code}', Canvas='{code}' where rowid={session}")
        self.title = title
        site.get_history(True)

    def render(self):
        colors = [[int(f"0x{p[1][i:i+2]}", 16) for i in [0,2,4]] for p in self.palette]
        imarr = np.array([[colors[self.canvas[r][c][2]] for c in range(self.ncols)] for r in range(self.nrows)], dtype=np.uint8)
        scale = int(max(1, 200 / min(self.nrows, self.ncols)))
        imarr = imarr.repeat(scale, axis=0).repeat(scale, axis=1)
        im = Image.fromarray(imarr, mode="RGB")
        im.save("static/canvas.png")
        return "static/canvas.png"

def canvas_decode(code, w, h):
    i = 0
    canvas = []
    while i < len(code):
        num = 0
        if code[i] == '0':
            num = 9+int(code[i+1])            
            i += 2
        else:
            num = int(code[i])-1
            i += 1
        canvas.append(num)
    return np.array(canvas).reshape((h,w))

site = Website()
site.colorset(["ffffff","ff00ff","00ffff","00ff00","ff0000", "0000ff", "ffff00","000000"])

@app.route("/", methods=["get", "post"])
def index():
    ani = []
    for fn in os.listdir("static"):
        if fn.endswith(".gif"):
            ani.append("static/"+fn)
    return render_template("index.html", ani=ani)

@app.route("/drawing", methods=["get", "post"])
def drawing():
    fm = request.form
    site.db.start()
    site.get_history()
    pname = ""
    if fm.get("create"):
        nrows, ncols = 20, 30
        if r:=fm.get("nrows"):
            nrows = int(r)
        if c:=fm.get("ncols"):
            ncols = int(c)
        site.create(nrows, ncols)
    elif fm.get("load"):
        site.session = int(fm.get("hid"))
        site.load_num(site.session)
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
        elif sm:=fm.get("save"):
            session = 0 if sm == "Save as copy" else site.session
            site.store(fm.get("svname"), session)
        elif fm.get("hdel"):
            if site.session > 1:
                site.db.do(f"delete from History where rowid={site.session}")
                site.db.do(f"update History set rowid=rowid-1 where rowid>{site.session}")
                if site.session == len(site.history):
                    site.session -= 1
                site.load_num(site.session)
        elif fm.get("render"):
            pname = site.render()
    site.db.save()
    return render_template("drawing.html", site=site, pname=pname)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)