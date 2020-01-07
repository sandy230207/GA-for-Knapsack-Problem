# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 21:47:52 2019

@author: user
"""

#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import random
import numpy
import matplotlib.pyplot as plt
import imageio
import os
from shutil import copyfile


from app.knapsackproblem.deapCustomize import algorithms
from app.knapsackproblem.deapCustomize import base
from app.knapsackproblem.deapCustomize import creator
from app.knapsackproblem.deapCustomize import tools

DJANGO_PATH="./app/knapsackproblem/"

IND_INIT_SIZE = 5
MAX_ITEM = 50
MAX_WEIGHT = 50
NBR_ITEMS = 20


# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().

random.seed(64)

# Create the item dictionary: item name is an integer, and value is 

# a (weight, value) 2-uple.

items = {}

# Create random items and store them in the items' dictionary.

for i in range(NBR_ITEMS):
    items[i] = (random.randint(1, 10), random.uniform(0, 100))


#fitness是背包重量的最小化和背包價值的最大化
# 適應函數
creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))  #minimizes the first objective and maximize the second one, 所以 weight 會是求最小值, value 求最大值
# indivisual 繼承 set class
# 個體
creator.create("Individual", set, fitness=creator.Fitness)


# 用Toolbox註冊generators，可以迭代的輸入來創建集合
toolbox = base.Toolbox()

# attr_item=random.randrange(NBR_ITEMS)
# Attribute generator
toolbox.register("attr_item", random.randrange, NBR_ITEMS)

# individual=tools.initRepeat(creator.Individual,toolbox.attr_item, IND_INIT_SIZE)
# 也就是說individual執行了toolbox.attr_item(就上面那個)這個函式
# 並執行了IND_INIT_SIZE(=5)次
# individual的型態為creator.Individual(前面建的)
# Structure initializers(為各個基因創建隨機的編碼)
toolbox.register("individual", tools.initRepeat, creator.Individual, 

    toolbox.attr_item, IND_INIT_SIZE)

# population=tools.initRepeat(list, toolbox.individual)
# 執行次數後續才會輸入
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


#評價函式
def evalKnapsack(individual):

    weight = 0.0
    value = 0.0

    for item in individual:
        weight += items[item][0]
        value += items[item][1]
        
    if len(individual) > MAX_ITEM or weight > MAX_WEIGHT:
        return 10000, 0             # Ensure overweighted bags are dominated
    
    return weight, value



def cxSet(ind1, ind2):

    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.

    """
    temp = set(ind1)                # Used in order to keep type
    ind1 &= ind2                    # Intersection (inplace) 二進制作AND的運算
    ind2 ^= temp                    # Symmetric Difference (inplace) 二進制作相減運算
    return ind1, ind2

    
#變異
def mutSet(individual):

    """Mutation that pops or add an element."""

    if random.random() < 0.5:

        if len(individual) > 0:     # We cannot pop from an empty set

            individual.remove(random.choice(sorted(tuple(individual))))
    else:

        individual.add(random.randrange(NBR_ITEMS))

    return individual,

toolbox.register("evaluate", evalKnapsack) #評價函式
toolbox.register("mate", cxSet) #交叉
toolbox.register("mutate", mutSet) #變異
toolbox.register("select", tools.selNSGA2) #選擇最佳個體

def ga(NGEN,MU,LAMBDA,CXPB,MUTPB):

    random.seed(64)    

    pop = toolbox.population(n=MU)
    
    hof = tools.ParetoFront()

    stats = tools.Statistics(lambda ind: ind.fitness.values)

    stats.register("avg", numpy.mean, axis=0)

    stats.register("std", numpy.std, axis=0)

    stats.register("min", numpy.min, axis=0)

    stats.register("max", numpy.max, axis=0)


    

    population, logbook, genlog = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,

                              halloffame=hof) #演化過程的最佳 individual 會被放到 hof 內

    return pop, stats, hof, logbook, genlog

def plotChart(lgbk, NGEN):
    x = [n for n in range(0, NGEN+1)]
    y = [n[0] for n in lgbk.select("std")]

    plt.subplot(2, 1, 1)
    plt.title('Fitness')
    plt.ylabel('weight')
    plt.plot(x, y, 'o', color='blue');
    plt.savefig(DJANGO_PATH+'image.png')
    
    x1 = [n for n in range(0, NGEN+1)]
    y1 = [n[1] for n in lgbk.select("std")]

    plt.subplot(2, 1, 2)
    plt.xlabel('generation')
    plt.ylabel('value')
    plt.plot(x1, y1, 'o', color='blue');
    plt.savefig(DJANGO_PATH+'image.png')
    plt.clf()
    plt.cla()
    
#    plt.show()

def scatterChart(genlog, kind, generation):
    gen=str(generation)
    if len(gen)==1:
        gen="0"+gen
    filename = DJANGO_PATH+str(kind)+'/'+gen+'.png'
    rng = numpy.random.RandomState(0)
    fitness = [x.fitness.values for x in genlog[kind][generation]]
    weight = [x[0] for x in fitness]
    value = [x[1] for x in fitness]
    
    x = weight
    y = value
    colors = rng.rand(len(x))
    sizes = 1000 * rng.rand(len(x))
    title=str(kind)[0].upper()+str(kind)[1:]
    title=title.replace("Invalid_ind","Individual")
    plt.title(title+' Fitness in generation '+str(generation))
    plt.xlabel('weight')
    plt.ylabel('value')
    plt.scatter(x, y, c=colors, s=sizes, alpha=0.3,
                cmap='viridis')
    plt.colorbar();  # show color scale
    plt.savefig(filename)
    plt.clf()
    plt.cla()
#    plt.show()

def genGIF(folder):
    gifname = DJANGO_PATH+folder+'/'+'output.gif'
    
    images = []
    for file_name in os.listdir(DJANGO_PATH+folder):
        if file_name.endswith('.png'):
            file_path = os.path.join(DJANGO_PATH+folder, file_name)
            images.append(imageio.imread(file_path))
    imageio.mimsave(gifname, images, fps=3)
    for file_name in os.listdir(DJANGO_PATH+folder):
        if file_name.endswith('.png'):
            os.remove(os.path.join(DJANGO_PATH+folder, file_name))

def main(NGEN,MU,LAMBDA,CXPB,MUTPB):
    print("path:", os.getcwd())
    #os.chdir("./app/knapsackproblem")
    print("path:", os.getcwd())
    pop, stats, hof, logbook, genlog = ga(NGEN,MU,LAMBDA,CXPB,MUTPB)
    print('End of the generation')
    print('-'*100)
    print("Best permutation of bags :",hof[-1])
#    print(len(pop))
#    print(len(hof))
    print("Best Fitness :",evalKnapsack(hof[-1]))

    #圖表-適應函數
    plotChart(logbook,NGEN)
    
    #圖表-每個世代 Individual 的 Fitness 值
    
    for gen in range(1, NGEN+1):
        scatterChart(genlog, 'invalid_ind', gen)
    
    genGIF('invalid_ind')
    copyfile(DJANGO_PATH+'invalid_ind/output.gif', './static/individual.gif')
        
    #圖表-每個世代的 population 的 Fitness 值
    for gen in range(1, NGEN+1):
        scatterChart(genlog, 'population', gen)
    
    genGIF('population')
    copyfile(DJANGO_PATH+'population/output.gif', './static/population.gif')
    copyfile(DJANGO_PATH+'image.png', './static/image.png')
    
    result=[]
    result.append(hof[-1])
    result.append(evalKnapsack(hof[-1]))
    result.append(logbook)
    
    return result

'''    
if __name__ == "__main__":
    NGEN = 50 #generation 的數量

    MU = 50 #選擇下一次 generation 的 individual 的數量

    LAMBDA = 100 #每一個generation產生的子代數量

    CXPB = 0.7 #兩個 individual mating 的機率

    MUTPB = 0.2 #The probability that an offspring is produced by mutation. 
    main(NGEN,MU,LAMBDA,CXPB,MUTPB)
'''
    
    
