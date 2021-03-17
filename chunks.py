import os, sys
from pathlib import Path
if os.path.exists("world/0_0.chunk"):
    os.remove("world/0_0.chunk")

p = str(Path(__file__).parent.absolute())
os.chdir(p)

c = open("world/0_0.chunk", "w")
for y in range(16):
    for x in range(16):
        c.write("[0,0,0]")
    c.write("\n")
c.close()
