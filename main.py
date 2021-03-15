#Import libraries

import tkinter as tk
import os
import subprocess

#Init control variables

global size
global octaves
global persistance
global lacunarity
global thres

#Define events

def enterEvent():
    size = sizeScale.get()
    octaves = octavesScale.get()
    persistance = persistanceScale.get()
    lacunarity = lacunarityScale.get()
    thres = thresScale.get()
    root.destroy()

#Init window

root = tk.Tk()
root.title("Island Generator")

#Add sliders and button

sizeScale = tk.Scale(root, from_=100.0, to=2000.0, orient=tk.HORIZONTAL, length=150)
sizeScale.set(250.0)
sizeScale.grid(row=1, column=0)

octavesScale = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, length=150)
octavesScale.set(6)
octavesScale.grid(row=3, column=0)

persistanceScale = tk.Scale(root, from_=0.1, to=2.0, orient=tk.HORIZONTAL, length=150, digits=3, resolution=0.05)
persistanceScale.set(0.5)
persistanceScale.grid(row=5, column=0)

lacunarityScale = tk.Scale(root, from_=1.0, to=5.0, orient=tk.HORIZONTAL, length=150, digits=3, resolution=0.05)
lacunarityScale.set(2.0)
lacunarityScale.grid(row=7, column=0)

thresScale = tk.Scale(root, from_=0.0, to=1.0, orient=tk.HORIZONTAL, length=150, digits=3, resolution=0.01)
thresScale.set(0.08)
thresScale.grid(row=9, column=0)

enterBut = tk.Button(root, text="Generate", command=enterEvent)
enterBut.grid(row=10, column=0)

#Start mainloop

root.mainloop()