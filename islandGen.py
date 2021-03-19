#Import libraries

import random
import os
import noise
import numpy
import math
import sys
from chunks import Chunks as chk
from PIL import Image
import subprocess
from scipy.misc import toimage

random.seed(os.urandom(6))

#Functions

def percentChance(chance):
    n = random.randrange(101)
    if (100 - n) < chance:
        return(True)
    else:
        return(False)

def mapVal(inp, inpMin, inpMax, outMin, outMax):
    return (inp - inpMin) * (outMax - outMin) / (inpMax - inpMin) + outMin

def createCircleGrad(gridSize): #Obsolete
    #Create circular gradient (Obsolete)

    center_x, center_y = gridSize // 2, gridSize // 2 #Define centre
    circle_grad = numpy.zeros((gridSize,gridSize)) #Create array

    for y in range(gridSize): #Loop array
        for x in range(gridSize):
            distx = abs(x - center_x) #Get distance from centre on x and y
            disty = abs(y - center_y)
            dist = math.sqrt(distx*distx + disty*disty) #Get the actual distance from centre (pythag)
            circle_grad[y][x] = dist

    max_grad = numpy.max(circle_grad)
    circle_grad = circle_grad / max_grad #This is some weird math that I don't quite understand but it works
    circle_grad -= 0.5
    circle_grad *= 2.0
    circle_grad = -circle_grad

    for y in range(gridSize): #More weird math, I think its just amplifying anything that is above 0
        for x in range(gridSize):
            if circle_grad[y][x] > 0:
                circle_grad[y][x] *= 20

    max_grad = numpy.max(circle_grad)
    circle_grad = circle_grad / max_grad #For some reason it's lowered again

    return(circle_grad)

#Colours

dwaterCol = [54, 137, 245]
waterCol = [67, 146, 245]
dsandCol = [224, 214, 164]
sandCol = [247, 232, 176]
rockCol = [209, 209, 209]
grassCol = [37, 170, 77]
dgrassCol = [34, 161, 63]
treeCol = [10, 122, 42]
mountCol = [74, 62, 36]
mountRockCol = [56, 48, 30]
snowCol = [245, 254, 255]

#Control Variables

a = sys.argv

if len(a) > 1:
    gridSize = int(a[1])
    scale = float(a[2])
    octaves = int(a[3])
    persistance = float(a[4])
    lacunarity = float(a[5])
    thres = float(a[6])
else:
    gridSize = 1024 #Side length
    scale = 250.0
    octaves = 6
    persistance = 0.5
    lacunarity = 2.0
    thres = 0.08

#Generate base noise, Apply gradient

im = Image.open("gradient/circle_grad.png")
circle_grad = im.convert("L")

main = numpy.zeros((gridSize,gridSize)) #Init arrays
mainNoise = numpy.zeros_like(main)

seed = random.randint(0,200) #Gen seed

for y in range(gridSize):
    for x in range(gridSize):
        main[y][x] = noise.pnoise2(y/scale,x/scale,octaves=octaves,persistence=persistance,lacunarity=lacunarity,repeatx=gridSize,repeaty=gridSize,base=seed) #Set noise
        mainNoise[y][x] = (main[y][x] * mapVal(circle_grad.getpixel((round((1024/gridSize)*x),round((1024/gridSize)*y))), 0, 255, -0.05, 1)) #Apply gradient to noise
        if mainNoise[y][x] > 0:
            mainNoise[y][x] *= 20 #Amplify

max_grad = numpy.max(mainNoise)
mainNoise = mainNoise / max_grad #Weird even out math thing

#Lay base

display = numpy.zeros((gridSize//16,gridSize//16)+(16,16)+(3,))
passOver = [[False] * (gridSize)] * (gridSize//16)

for cy in range(gridSize//16):
    for cx in range(gridSize//16):
        for y in range(16):
            for x in range(16):
                m = mainNoise[y + (16*cy)][x + (16*cx)] #Set iterator to value of main array and check if meets certain thresholds to set colours
                if m < thres + 0.015:
                    m = dwaterCol
                elif m < thres + 0.11:
                    m = waterCol
                elif m < thres + 0.12:
                    m = dsandCol
                    passOver[cy][cx] = True
                elif m < thres + 0.15:
                    m = sandCol
                    passOver[cy][cx] = True
                elif m < thres + 0.28:
                    m = grassCol
                    passOver[cy][cx] = True
                elif m < thres + 0.46:
                    m = dgrassCol
                    passOver[cy][cx] = True
                elif m < thres + 0.78:
                    m = mountCol
                    passOver[cy][cx] = True
                elif m < thres + 1.0:
                    m = snowCol
                    passOver[cy][cx] = True
                display[cy][cx][y][x] = m

#Second pass (Natural features)

featSeed = random.randint(0,100) #Generate seed
for cy in range(gridSize//16):
    for cx in range(gridSize//16):
        if passOver[cy][cx] == True:
            for y in range(16):
                for x in range(16):
                    m = display[cy][cx][y][x]
                    p = noise.pnoise2((y + (cy * 16))/(scale/2.5),(x + (cx * 16))/(scale/2.5),octaves=10,persistence=0.55,lacunarity=1.55,repeatx=gridSize,repeaty=gridSize,base=featSeed) #Get pond noise
                    if all(m == grassCol) or all(m == dsandCol) or all(m == sandCol): #If light grass or beach generate pond
                        if p > 0.17:
                            if p < 0.25:
                                m = sandCol
                            elif p < 1.0:
                                m = waterCol
                    display[cy][cx][y][x] = m

#Third pass (Structures)

def addTree(arr,cx,cy,x,y,inpScale):
    arr[cy][cx][y][x] = treeCol
    n = y
    while n < y+inpScale: #Loop through tree size (Only creates plus sign)
        arr[cy][cx][min(n+1,15)][x] = treeCol
        n += 1
    n = y
    while n > y-inpScale:
        arr[cy][cx][max(n-1,0)][x] = treeCol
        n -= 1
    n = x
    while n < x+inpScale:
        arr[cy][cx][y][min(n+1,15)] = treeCol
        n += 1
    n = x
    while n > x-inpScale:
        arr[cy][cx][y][max(n-1,0)] = treeCol
        n -= 1

def addRock(arr,cx,cy,x,y,inpScale,c):
    arr[cy][cx][y][x] = c
    arr[cy][cx][min(y+random.randint(0,1),15)][x] = c #Random whether one is placed, if 0 is gen the origin is painted over
    arr[cy][cx][max(y-random.randint(0,1),0)][x] = c
    arr[cy][cx][y][min(x+random.randint(0,1),15)] = c
    arr[cy][cx][y][max(x-random.randint(0,1),0)] = c

structScale = int(scale // 200)
for cy in range(gridSize//16):
    for cx in range(gridSize//16):
        if passOver[cy][cx] == True:
            for y in range(16):
                for x in range(16): #Place rocks on beach and mountnain
                    m = display[cy][cx][y][x]
                    if all(m == sandCol):
                        if percentChance(2) == True:
                            addRock(display,cx,cy,x,y,structScale,rockCol)
                    elif all(m == grassCol):
                        if percentChance(5) == True:
                            addTree(display,cx,cy,x,y,structScale)
                    elif all(m == dgrassCol):
                        if percentChance(20) == True:
                            addTree(display,cx,cy,x,y,structScale)
                    elif all(m == mountCol):
                        if percentChance(0.01) == True:
                            addRock(display,cx,cy,x,y,structScale,mountRockCol)

#Write to chunks

for cy in range(gridSize//16):
    for cx in range(gridSize//16):
        chk.writeChunk(cx,cy,display[cy][cx])

#Start main

toimage(chk.readChunkArray(gridSize,display)).show()