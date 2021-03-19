#Import libraries

from scipy.misc import toimage
from chunks import Chunks as chk

cx, cy = 0, 0
while os.path.exists("world/chunk" + str(cx) + "_" + str(cy) + ".chunk"):
    cx += 1
worldSize = cx

for cy in range(worldSize):
    for cx in range(worldSize):
        chk.readChunk()