import sys
from os import path, sep

modpath = path.abspath(__file__)
dir_path = path.dirname(modpath)
sys.path.append(dir_path)
initpathlist = path.realpath(__file__).split(sep)

PROJ_PATH = sep.join(initpathlist[:-1])
EXP = initpathlist[-2]

DATA_PATH = sep.join(initpathlist[:-1] + ['data'])
SOLVERS_PATH = sep.join(initpathlist[:-1] + ['solvers'])
print(SOLVERS_PATH)
print(DATA_PATH)
exepath = path.join(SOLVERS_PATH, 'scipampl601')
print(exepath)
