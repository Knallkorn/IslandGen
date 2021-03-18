import os, sys
from pathlib import Path
from numpy import zeros

p = str(Path(__file__).parent.absolute())
os.chdir(p)

if os.path.exists("world/0_0.chunk"):
    os.remove("world/0_0.chunk")

c = open("world/0_0.chunk", "w")
for y in range(16):
    for x in range(16):
        c.write("0,0,0|")
    c.write("\n")
c.close()

class chunks:

    def __init__

    #Read chunk
    @staticmethod
    def readChunk(cx,cy):
        p = "world/" + str(cx) + "_" + str(cy) + ".chunk"
        if os.path.exists(p):
            c = open(p, "r")
            chunk = zeros((16,16)+(3,))
            for y in range(16):
                l = c.readline()
                ls = l.split("|")
                for x in range(16):
                    chunk[y][x] = ls[x].split(',')
            c.close()
            return chunk
        else:
            raise Exception("No chunk at provided co-ords")

    #Write chunk
    @staticmethod
    def writeChunk(cx,cy,inp):
        p = "world/" + str(cx) + "_" + str(cy) + ".chunk"
        if os.path.exists(p):
            chunk = ""
            for y in range(16):
                for x in range(16):
                    chunk = chunk + str(inp[y][x][0]) + "," + str(inp[y][x][1]) + "," + str(inp[y][x][2]) + "|"
                chunk += "\n"
            c = open(p, "w")
            c.write(chunk)
            c.close()