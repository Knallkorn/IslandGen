#INFO
#This is really janky and stuc together, all the elements in the generation menu have to be global
#because the event that passes them into the islandgen script cant get their values otherwise

#Import libraries

import tkinter as tk
import os
import subprocess
import math
from chunks import Chunks as chk
from numpy import zeros
from scipy.misc import toimage

#Init control variables

global size
global octaves
global persistance
global lacunarity
global thres

#Define events

def generateEvent(): #Event for button in generation window
    size = str(sizeScale.get())
    scale = str(scaleScale.get())
    octaves = str(octavesScale.get())
    persistance = str(persistanceScale.get())
    lacunarity = str(lacunarityScale.get())
    thres = str(thresScale.get())
    subprocess.run(["python", "islandGen.py", size, scale, octaves, persistance, lacunarity, thres])
    root.destroy()

def generateWindow():

    #Kill old window

    start.destroy()

    #Init window

    global root
    root = tk.Tk()
    root.title("Generate Island")

    #Add sliders and button

    global sizeScale
    sizeScale = tk.Scale(root, from_=100, to=2000, orient=tk.HORIZONTAL, length=150, resolution=16)
    sizeScale.set(1024)
    sizeScale.grid(row=1, column=0)

    global scaleScale
    scaleScale = tk.Scale(root, from_=50.0, to=500.0, orient=tk.HORIZONTAL, length=150)
    scaleScale.set(250.0)
    scaleScale.grid(row=3, column=0)

    global octavesScale
    octavesScale = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, length=150)
    octavesScale.set(6)
    octavesScale.grid(row=5, column=0)

    global persistanceScale
    persistanceScale = tk.Scale(root, from_=0.1, to=2.0, orient=tk.HORIZONTAL, length=150, digits=3, resolution=0.05)
    persistanceScale.set(0.5)
    persistanceScale.grid(row=7, column=0)

    global lacunarityScale
    lacunarityScale = tk.Scale(root, from_=1.0, to=5.0, orient=tk.HORIZONTAL, length=150, digits=3, resolution=0.05)
    lacunarityScale.set(2.0)
    lacunarityScale.grid(row=9, column=0)

    global thresScale
    thresScale = tk.Scale(root, from_=0.0, to=1.0, orient=tk.HORIZONTAL, length=150, digits=3, resolution=0.01)
    thresScale.set(0.08)
    thresScale.grid(row=11, column=0)

    generateBut = tk.Button(root, text="Generate", command=generateEvent)
    generateBut.grid(row=12, column=0)

    #Labels

    tk.Label(root, text="Island Size").grid(row=0, column=0)
    tk.Label(root, text="Noise Scale").grid(row=2, column=0)
    tk.Label(root, text="Noise Octaves").grid(row=4, column=0)
    tk.Label(root, text="Noise Persistance").grid(row=6, column=0)
    tk.Label(root, text="Noise Lacunarity").grid(row=8, column=0)
    tk.Label(root, text="Island Generation Threshold").grid(row=10, column=0)

    #Start mainloop

    root.mainloop()

def loadWindow():

    filelist = [ f for f in os.listdir("world/") if f.endswith(".chunk") ] #Get list of all chunks
    byChunkSize = int(math.sqrt(len(filelist))) #L or W of chunk array
    print(byChunkSize)
    display = zeros((byChunkSize*16,byChunkSize*16)+(16,16)+(3,))
    for cy in range(byChunkSize):
        for cx in range(byChunkSize):
            cur = chk.readChunk(cx,cy)
            for y in range(16):
                for x in range(16):
                    display[cy][cx][y][x] = cur[y][x]
    toimage(chk.readChunkArray(byChunkSize*16,display)).show()

#Start Window

start = tk.Tk()
start.title("Island Generator")

#Frame

frameLeft = tk.Frame(start, width=200, height=100).grid(row=0,column=0)
frameRight = tk.Frame(start, width=200, height=100).grid(row=0,column=1)

#Buttons

generateWinBut = tk.Button(frameLeft, text="New Island", command=generateWindow).grid(row=0, column=0)
loadWinBut = tk.Button(frameRight, text="Load Island", command=loadWindow).grid(row=0, column=1)

#Enter mainloop for start window

start.mainloop()