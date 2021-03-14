#Import libraries

import random
import keyboard
import os
import noise
import numpy
from scipy.misc import toimage
import math

random.seed(os.urandom(6))

#Functions

def percentChance(chance):
    n = random.randrange(101)
    if (100 - n) < chance:
        return(True)
    else:
        return(False)

#Colours

dwaterCol = [54, 137, 245]
waterCol = [67, 146, 245]
dsandCol = [224, 214, 164]
sandCol = [247, 232, 176]
rockCol = [209, 209, 209]
grassCol = [37, 170, 77]
dgrassCol = [34, 161, 63]
treeCol = [10, 122, 42]
dirtCol = [74, 62, 36]
mountRockCol = [56, 48, 30]
snowCol = [245, 254, 255]

#Control Variables

gridSize = 1000 #Side length

scale = 250.0
octaves = 6
persistance = 0.5
lacunarity = 2.0

thres = 0.08

#Generate base noise

main = numpy.zeros((gridSize,gridSize))

seed = random.randint(0,200)

for x in range(gridSize):
    for y in range(gridSize):
        main[x][y] = noise.pnoise2(x/scale,y/scale,octaves=octaves,persistence=persistance,lacunarity=lacunarity,repeatx=gridSize,repeaty=gridSize,base=seed)

#Create circular gradient

center_x, center_y = gridSize // 2, gridSize // 2
circle_grad = numpy.zeros_like(main)

for x in range(gridSize):
    for y in range(gridSize):
        distx = abs(x - center_x)
        disty = abs(y - center_y)
        dist = math.sqrt(distx*distx + disty*disty)
        circle_grad[y][x] = dist

max_grad = numpy.max(circle_grad)
circle_grad = circle_grad / max_grad
circle_grad -= 0.5
circle_grad *= 2.0
circle_grad = -circle_grad

for y in range(gridSize):
    for x in range(gridSize):
        if circle_grad[y][x] > 0:
            circle_grad[y][x] *= 20

max_grad = numpy.max(circle_grad)
circle_grad = circle_grad / max_grad

#Apply noise

mainNoise = numpy.zeros_like(main)

for i in range(gridSize):
    for ii in range(gridSize):
        mainNoise[i][ii] = (main[i][ii] * circle_grad[i][ii])
        if mainNoise[i][ii] > 0:
            mainNoise[i][ii] *= 20

max_grad = numpy.max(mainNoise)
mainNoise = mainNoise / max_grad

#Lay base

def convertCol(thres,inp,otp):
    for i in range(0,gridSize):
        for ii in range(0,gridSize):
            x = inp[i][ii]
            if x < thres + 0.015:
                x = dwaterCol
            elif x < thres + 0.11:
                x = waterCol
            elif x < thres + 0.12:
                x = dsandCol
            elif x < thres + 0.15:
                x = sandCol
            elif x < thres + 0.28:
                x = grassCol
            elif x < thres + 0.46:
                x = dgrassCol
            elif x < thres + 0.78:
                x = dirtCol
            elif x < thres + 1.0:
                x = snowCol

            otp[i][ii] = x

display = numpy.zeros((gridSize,gridSize)+(3,))

convertCol(0.08,mainNoise,display)

#Second pass (Natural features)

pondSeed = random.randint(0,100)
for i in range(gridSize):
    for ii in range(gridSize):
        x = display[i][ii]
        p = noise.pnoise2(i/(scale/2.5),ii/(scale/2.5),octaves=10,persistence=0.55,lacunarity=1.55,repeatx=gridSize,repeaty=gridSize,base=pondSeed)
        if all(x == grassCol) or all(x == dsandCol) or all(x == sandCol):
            if p > 0.17:
                if p < 0.25:
                    x = sandCol
                elif p < 1.0:
                    x = waterCol
        display[i][ii] = x

#Third pass (Structures)

def addTree(arr,x,y,inpScale):
    arr[x][y] = treeCol
    arr[min(x+inpScale,gridSize-1)][y] = treeCol
    arr[max(x-inpScale,0)][y] = treeCol
    arr[x][min(y+inpScale,gridSize-1)] = treeCol
    arr[x][max(y-inpScale,0)] = treeCol

def addRock(arr,x,y,inpScale,c):
    arr[x][y] = c
    arr[min(x+random.randrange(inpScale+1),gridSize-1)][y] = c
    arr[max(x-random.randrange(inpScale+1),0)][y] = c
    arr[x][min(y+random.randrange(inpScale+1),gridSize-1)] = c
    arr[x][max(y-random.randrange(inpScale+1),0)] = c

structScale = int(scale // 200)
for i in range(gridSize):
    for ii in range(gridSize):
        x = display[i][ii]
        if all(x == sandCol):
            if percentChance(2) == True:
                addRock(display,i,ii,structScale,rockCol)
        elif all(x == grassCol):
            if percentChance(5) == True:
                addTree(display,i,ii,structScale)
        elif all(x == dgrassCol):
            if percentChance(20) == True:
                addTree(display,i,ii,structScale)
        elif all(x == dirtCol):
            if percentChance(0.01) == True:
                addRock(display,i,ii,structScale,mountRockCol)

#Show image

toimage(display).show()