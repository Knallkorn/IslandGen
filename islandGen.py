#Import libraries

import random
import os
import noise
import numpy
import math
import sys
import chunks as chk
from scipy.misc import toimage
from PIL import Image

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
"""
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
"""
#Generate base noise, Apply gradient

im = Image.open("gradient/circle_grad.png")
circle_grad = im.convert("L")

main = numpy.zeros((gridSize,gridSize)) #Init arrays
mainNoise = numpy.zeros_like(main)

seed = random.randint(0,200) #Gen seed

for y in range(gridSize):
    for x in range(gridSize):
        main[y][x] = noise.pnoise2(y/scale,x/scale,octaves=octaves,persistence=persistance,lacunarity=lacunarity,repeatx=gridSize,repeaty=gridSize,base=seed) #Set noise
        mainNoise[y][x] = (main[y][x] * mapVal(circle_grad.getpixel((x,y)), 0, 255, -0.05, 1)) #Apply gradient to noise
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

toimage(chk.Chunks.readChunkArray(gridSize,display)).show()

"""
for y in range(0,gridSize):
    for x in range(0,gridSize):
        m = mainNoise[y][x] #Set iterator to value of main array and check if meets certain thresholds to set colours
        if m < thres + 0.015:
            m = dwaterCol
        elif m < thres + 0.11:
            m = waterCol
        elif m < thres + 0.12:
            m = dsandCol
        elif m < thres + 0.15:
            m = sandCol
        elif m < thres + 0.28:
            m = grassCol
        elif m < thres + 0.46:
            m = dgrassCol
        elif m < thres + 0.78:
            m = mountCol
        elif m < thres + 1.0:
            m = snowCol

        display[y][x] = m #Set display array to the colour


#Second pass (Natural features)

featSeed = random.randint(0,100) #Generate seed
for y in range(gridSize):
    for x in range(gridSize):
        m = display[y][x]
        p = noise.pnoise2(y/(scale/2.5),x/(scale/2.5),octaves=10,persistence=0.55,lacunarity=1.55,repeatx=gridSize,repeaty=gridSize,base=featSeed) #Get pond noise
        if all(m == grassCol) or all(m == dsandCol) or all(m == sandCol): #If light grass or beach generate pond
            if p > 0.17:
                if p < 0.25:
                    m = sandCol
                elif p < 1.0:
                    m = waterCol
        display[y][x] = m

#Third pass (Structures)

def addTree(arr,x,y,inpScale):
    arr[y][x] = treeCol
    n = y
    while n < y+inpScale: #Loop through tree size (Only creates plus sign)
        arr[min(n+1,gridSize-1)][x] = treeCol
        n += 1
    n = y
    while n > y-inpScale:
        arr[max(n-1,0)][x] = treeCol
        n -= 1
    n = x
    while n < x+inpScale:
        arr[y][min(n+1,gridSize-1)] = treeCol
        n += 1
    n = x
    while n > x-inpScale:
        arr[y][max(n-1,0)] = treeCol
        n -= 1

def addRock(arr,x,y,inpScale,c):
    arr[y][x] = c
    arr[min(y+random.randint(0,1),gridSize-1)][x] = c #Random whether one is placed, if 0 is gen the origin is painted over
    arr[max(y-random.randint(0,1),0)][x] = c
    arr[y][min(x+random.randint(0,1),gridSize-1)] = c
    arr[y][max(x-random.randint(0,1),0)] = c

structScale = int(scale // 200)
for y in range(gridSize):
    for x in range(gridSize): #Place rocks on beach and mountnain
        m = display[y][x]
        if all(m == sandCol):
            if percentChance(2) == True:
                addRock(display,x,y,structScale,rockCol)
        elif all(m == grassCol):
            if percentChance(5) == True:
                addTree(display,x,y,structScale)
        elif all(m == dgrassCol):
            if percentChance(20) == True:
                addTree(display,x,y,structScale)
        elif all(m == mountCol):
            if percentChance(0.01) == True:
                addRock(display,x,y,structScale,mountRockCol)
"""