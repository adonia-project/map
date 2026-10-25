from PIL import Image
import numpy as np

paths = [
    r"C:\Users\Carl\Dropbox\Adonia\Adonia Robinson Map.png",
    "B:\\02_GIT CONNECTED\\map\\Location of Aina'akea.png",
]
for p in paths:
    im = Image.open(p)
    a = np.asarray(im.convert("RGB"))
    uc = len(np.unique(a.reshape(-1, 3), axis=0))
    print(p, im.size, "| unique colors:", uc, "| mean px:", round(float(a.mean()), 1))
