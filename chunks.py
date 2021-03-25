#Import necesary libraries

import os
from pathlib import Path
from numpy import zeros

p = str(Path(__file__).parent.absolute()) #Set working dir
os.chdir(p)

class Chunks:

    #Read chunk
    @staticmethod
    def readChunk(cx,cy): #Chunk x, chunk y
        p = "world/" + str(cx) + "_" + str(cy) + ".chunk" #Check if valid coord
        if os.path.exists(p):
            c = open(p, "r") #Open file and init chunk array
            chunk = zeros((16,16)+(3,))
            for y in range(16):
                l = c.readline() #Read all x for y and split by |
                ls = l.split("|")
                for x in range(16):
                    chunk[y][x] = ls[x].split(',') #Input list values split by , into chunk array
            c.close()
            return chunk
        else:
            raise Exception("No chunk at provided co-ords")

    #Write chunk
    @staticmethod
    def writeChunk(cx,cy,inp): #Chunk x, chunk y, input chunk
        p = "world/" + str(cx) + "_" + str(cy) + ".chunk"
        chunk = "" #Init main string
        for y in range(16):
            for x in range(16):
                chunk = chunk + str(inp[cy][cx][y][x][0]) + "," + str(inp[cy][cx][y][x][1]) + "," + str(inp[cy][cx][y][x][2]) + "|" #Add values of input to string
            chunk += "\n" #Once all x for y is in, new line
        c = open(p, "w") #Write
        c.write(chunk)
        c.close()

    #Unpack and read 5D array
    @staticmethod
    def readChunkArray(size,inp):
        opt = zeros((size,size)+(3,))
        for cy in range(size//16):
            for cx in range(size//16):
                for y in range(16):
                    for x in range(16):
                        opt[y + (cy * 16)][x + (cx * 16)] = inp[cy][cx][y][x]
        return opt