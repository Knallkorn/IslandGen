#Import libraries

import random
import os
import noise
import numpy
from scipy.misc import toimage
import math
import sys

random.seed(os.urandom(6))

#OpenGL testing

from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def square():
    glBegin(GL_QUADS)
    glVertex2f(100,100)
    glVertex2f(200,100)
    glVertex2f(200,200)
    glVertex2f(100,200)
    glEnd()

def iterate():
    glViewport(0, 0, 500,500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Remove everything from screen (i.e. displays all white)
    glLoadIdentity()
    iterate()
    glColor3f(1.0,0.0,3.0)
    square()
    glutSwapBuffers()

glutInit() # Initialize a glut instance which will allow us to customize our window
glutInitDisplayMode(GLUT_RGBA) # Set the display mode to be colored
glutInitWindowSize(500, 500)   # Set the width and height of your window
glutInitWindowPosition(0, 0)   # Set the position at which this windows should appear
wind = glutCreateWindow("Test") # Give your window a title
glutDisplayFunc(showScreen)  # Tell OpenGL to call the showScreen method continuously
glutIdleFunc(showScreen)     # Draw any graphics or shapes in the showScreen function at all times
glutMainLoop()  # Keeps the window created above displaying/running in a loop

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
    gridSize = 1000 #Side length
    scale = 250.0
    octaves = 6
    persistance = 0.5
    lacunarity = 2.0
    thres = 0.08

#Create circular gradient

center_x, center_y = gridSize // 2, gridSize // 2 #Define centre
circle_grad = numpy.zeros((gridSize,gridSize)) #Create array

for x in range(gridSize): #Loop array
    for y in range(gridSize):
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

#Generate base noise, Apply gradient

main = numpy.zeros((gridSize,gridSize)) #Init arrays
mainNoise = numpy.zeros_like(main)
display = numpy.zeros((gridSize,gridSize)+(3,)) #This one is set as numpy arrrays witha length of 3

seed = random.randint(0,200) #Gen seed

for i in range(gridSize):
    for ii in range(gridSize):
        main[i][ii] = noise.pnoise2(i/scale,ii/scale,octaves=octaves,persistence=persistance,lacunarity=lacunarity,repeatx=gridSize,repeaty=gridSize,base=seed) #Set noise
        mainNoise[i][ii] = (main[i][ii] * circle_grad[i][ii]) #Apply gradient to noise
        if mainNoise[i][ii] > 0:
            mainNoise[i][ii] *= 20 #Amplify

max_grad = numpy.max(mainNoise)
mainNoise = mainNoise / max_grad #Weird even out math thing

#Lay base

for i in range(0,gridSize):
    for ii in range(0,gridSize):
        x = mainNoise[i][ii] #Set iterator to value of main array and check if meets certain thresholds to set colours
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
            x = mountCol
        elif x < thres + 1.0:
            x = snowCol

        display[i][ii] = x #Set display array to the colour

#Second pass (Natural features)

featSeed = random.randint(0,100) #Generate seed
for i in range(gridSize):
    for ii in range(gridSize):
        x = display[i][ii]
        p = noise.pnoise2(i/(scale/2.5),ii/(scale/2.5),octaves=10,persistence=0.55,lacunarity=1.55,repeatx=gridSize,repeaty=gridSize,base=featSeed) #Get pond noise
        if all(x == grassCol) or all(x == dsandCol) or all(x == sandCol): #If light grass or beach generate pond
            if p > 0.17:
                if p < 0.25:
                    x = sandCol
                elif p < 1.0:
                    x = waterCol
        display[i][ii] = x

#Third pass (Structures)

def addTree(arr,x,y,inpScale):
    arr[x][y] = treeCol
    n = x
    while n < x+inpScale: #Loop through tree size (Only creates plus sign)
        arr[min(n+1,gridSize-1)][y] = treeCol
        n += 1
    n = x
    while n > x-inpScale:
        arr[max(n-1,0)][y] = treeCol
        n -= 1
    n = y
    while n < y+inpScale:
        arr[x][min(n+1,gridSize-1)] = treeCol
        n += 1
    n = y
    while n > y-inpScale:
        arr[x][max(n-1,0)] = treeCol
        n -= 1

def addRock(arr,x,y,inpScale,c):
    arr[x][y] = c
    arr[min(x+random.randint(0,1),gridSize-1)][y] = c #Random whether one is placed, if 0 is gen the origin is painted over
    arr[max(x-random.randint(0,1),0)][y] = c
    arr[x][min(y+random.randint(0,1),gridSize-1)] = c
    arr[x][max(y-random.randint(0,1),0)] = c

structScale = int(scale // 200)
for i in range(gridSize):
    for ii in range(gridSize): #Place rocks on beach and mountnain
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
        elif all(x == mountCol):
            if percentChance(0.01) == True:
                addRock(display,i,ii,structScale,mountRockCol)

#Show image

toimage(display).show()