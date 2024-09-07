import numpy as np
from PIL import Image

def a0printa3(imname:str, opf:str):
    im = Image.open(imname).transpose(Image.Transpose.ROTATE_90)

    imarr = np.array(im)[:,:,:3]
    hr, qc = int(im.height/2),int(im.width/4)
    for r in range(2):
        for c in range(4):
            Image.fromarray(imarr[hr*r:hr*(r+1), qc*c:qc*(c+1), :]).save(f"static/sep_{opf}_{r}_{c}.png")

def bw(imname, opf):
    im = Image.open(imname)
    imarr = np.mean(np.array(im), axis=2)
    for row in imarr:
        for c in range(len(row)):
            if row[c] == 0:
                row[c] = 255
    imarr = np.array(imarr, dtype=np.uint8)
    Image.fromarray(imarr).save(f"static/bw_{opf}.png")

def sveqsolve(func, eq, xf, xt, err=0.001):
    xl, xh = xf, xt
    yf, yt = func(xf), func(xt)
    fac = 1
    if yf >= eq and yt <= eq:
        fac = -1
    elif (yf-eq)*(yt-eq) > 0:
        raise TimeoutError("No solution or more than one")
    while True:
        x = (xl+xh) / 2
        y = func(x)
        if abs(y-eq) < err:
            return x
        elif fac*func(x) > fac*eq:
            xh = x
        else:
            xl = x

if __name__ == "__main__":
    print(sveqsolve(lambda x: np.power(x,4)-3*np.power(x,2)+x-5, 1, 0, 4))

    
