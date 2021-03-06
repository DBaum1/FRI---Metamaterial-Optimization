from deap import base, creator, tools, algorithms
import numpy as np
from pprint import pprint 
import random
import subprocess

#200mm x 150mm
voxSize = 5  # in millimeters
padding = 4
length = 200/voxSize  #Calculates the size of the X Dimension of the array.
width =  150/voxSize   #Calculates the size of the Y dimension of the array.
lp = length + 2*padding
wp = width + 2*padding
handleSize = 5
teethSize = 3
teethGap = 1
#voxels assumed to be 5x5x5 mm
# a test comment
popSize = 150
testString = [[0,0,1,1,0,0,0,0,0,0,1,1]]

#Generating the individual seems to be working correctly for now.
def genInd():
    fullHolder = []
    for i in range(0, width): #for every row
        for k in range(0, length): # add actual randomized bits
            fullHolder.append(np.random.randint(0,2))
    return fullHolder

def printIndividual(ind): #ind is meant to be the individual, not quite sure if this is right so may need tweaking
    fullHolder = []
    for i in range(0, width): #for every row
        for j in range(0, padding):
            fullHolder.append(0) #add padding 0's at the start of the col
        for k in range(0, length): # add actual randomized bits
            fullHolder.append(ind[0][i*length + k])
        for l in range(0, padding):
            fullHolder.append(0) #add padding 0's at the end of the col
    teethY = width/2
    for i in range(0, teethSize):
        fullHolder[(teethY+teethGap)*(length+2*padding)+i] = 1 #teeth first set
        fullHolder[(teethY-teethGap)*(length+2*padding)+i] = 1
    
    for i in range(0,handleSize):
        fullHolder[length+2*padding-1-i] = 1
        fullHolder[width*(length+2*padding)-1-i] = 1
    #printing section
    F = open("transFile.txt", "w+")
    F.write('%d\n' %lp)
    F.write('%d\n' %wp)
    for i in range(0,width):
        myString = ''
        for j in range(0, (length+padding+padding)):
            myString += str(fullHolder[i*(length+padding+padding)+j])
            myString += " "
        myString += "\n"
        F.write(myString)
    F.close()

def nonFormatPrint(ind):
    F = open("unform.txt", "w+")
    F.write('%d\n' %length)
    F.write('%d\n' %width)
    for i in range(0,width):
        myString = ''
        for j in range(0, (length)):
            myString += str(ind[0][i*(length)+j])
            myString += " "
        myString += "\n"
        F.write(myString)
    F.close()

def ocxTwoPoint(ind1, ind2):
    size = min(len(ind1[0]), len(ind2[0]))
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else: # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1
    ind1[0][cxpoint1:cxpoint2], ind2[0][cxpoint1:cxpoint2] \
            = ind2[0][cxpoint1:cxpoint2], ind1[0][cxpoint1:cxpoint2]
    return ind1, ind2

def omutFlipBit(individual, indpb):
    for i in xrange(len(individual[0])):
            if random.random() < indpb:
                  individual[0][i] = type(individual[0][i])(not individual[0][i])
    return individual,

#run printIndividual, then call the other guys code, then eval fitness
def fitnessEval(ind):
    #printIndividual(ind)
    #print("fitness eval ran")
    subprocess.call("./VoxCad_Test < transFile.txt > output.txt", shell = True); 
    input = np.loadtxt("output.txt", dtype='str', delimiter=';') #might want to use actual c++ output file
    #debugging
    #    print(input) 
#    for r in range(3):
#        for c in range(3):
#            print(input[r][c]) debugging
    xDist = 0
    yDist = 0
    zDist = 0
    totalDisplace = 0
    #haven't actually tested this. Here's to hoping it doesn't crash and burn
    #get teeth positions?
    teethY = width/2
    for i in range(0, teethSize):
        #where to go from here?
        #I assume that (teethY+teethGap) indicates the top teeth?
        t1 = input[(teethY+teethGap)*(length+2*padding)+i]  #teeth first set
        #I assume that (teethY-teethGap) indicates the bottom teeth?
        t2 = input[(teethY-teethGap)*(length+2*padding)+i]
        miniList = [float(el) for el in t1.split(',')]
        miniList2 = [float(el) for el in t2.split(',')]
        xDist += miniList[0] + miniList2[0]
        yDist += miniList[1] + miniList2[1]
        zDist += miniList[2] + miniList2[2]
    #idk why I did this, but we need something
    totalDisplace = xDist + yDist + zDist
    return totalDisplace,

creator.create("FMax", base.Fitness, weights = (1.0,) )
#Technically we want the fitness to be as close to 0
creator.create("Individual", list, fitness = creator.FMax)
toolbox = base.Toolbox()
toolbox.register("genIndividual", tools.initRepeat, creator.Individual, genInd, n=1)
toolbox.register("genPop", tools.initRepeat, list, toolbox.genIndividual)
toolbox.register("evaluate", fitnessEval)
toolbox.register("mate", ocxTwoPoint)
toolbox.register("mutate", omutFlipBit, indpb = .05)
toolbox.register("select", tools.selTournament, tournsize = popSize/5)

finalPop = algorithms.eaSimple(toolbox.genPop(n=popSize), toolbox, 0.2, 0.3, 150)
#printIndividual([genInd()])
#nonFormatPrint([genInd()])
#printIndividual(testString)
