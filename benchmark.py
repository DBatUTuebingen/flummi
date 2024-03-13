from flummi.interpreter.interpreter import Interpreter
from time import time
from statistics import mean, median
from flummi.parser import parse
import duckdb

width = 4
height = 4

def buildppm(filename, valuelist):

    valuelist = sorted(valuelist, key = lambda x: (x['x'], x['y']))

    with open('./' + filename + '.ppm', 'w', encoding="utf8") as file:
        file.write('P3\n' + str(height) + ' '+ str(width) + '\n255\n')
        for p in valuelist:
            file.write(str(int(p['r']*256)) + ' ' + str(int(p['g']*256)) + ' ' + str(int(p['b']*256)) + '\n')


# interpreter benchmark prep
interpretValuelist = []
interprTimes = []
source = ""

with open('./examples/ray_setup.sql', 'r', encoding="utf8") as file:
    filecontent = file.read()
    duckdb.execute(filecontent, {"width": width, "height": height})

with open('./examples/ray.fl', 'r', encoding="utf8") as file:
    source = file.read()

ast = parse(source)


# flummi one-by-one prep
oneFlummiValuelist = []
oneFlummiTimes = []

with open('./out.sql', 'r', encoding='utf8') as file:
    oneQuery = file.read()


# flummi batch prep
flummiBatchValuelist =[]
flummiBatchTimes = []


# benchmark interpreter, flummi one-by-one
for index in range(1, 1 + width * height):
    #interpreter
    ast.inputs[0].source = str(index)
    Interpreter.return_list = []
    Interpreter.env = {}
    Interpreter.types = {}
    interpreterStart = time()
    results = Interpreter().interpret(ast)
    interprTimes.append(round(time() - interpreterStart, 3))
    interpretValuelist.append(results[0])
    

    #one-by-one flummi
    if width < 3:
        oneFlummiStart = time()
        duckdb.execute(oneQuery, {'index': index})
        oneFlummiTimes.append(round(time() - oneFlummiStart, 3))
        oneFlummiValuelist.append(duckdb.fetchone()[0])

# benchmark flummi
with open('./out.batched.sql', 'r', encoding="utf8") as file:
    filecontent = file.read()
    flummiBatchStart = time()
    duckdb.execute(filecontent, {"width": width, "height": height})
    _results = duckdb.fetchall()
    flummiBatchTimes.append(round(time() - flummiBatchStart, 3))
    flummiBatchValuelist = [x[0] for x in _results]
    



buildppm('interpreterTest',interpretValuelist)
if width < 3:
    buildppm('oneFlummiTest',oneFlummiValuelist)
buildppm('flummiBatchTest',flummiBatchValuelist)


# build diff ppm
interpretValuelist = sorted(interpretValuelist, key = lambda x: (x['x'], x['y']))
flummiBatchValuelist = sorted(flummiBatchValuelist, key = lambda x: (x['x'], x['y']))
diffValueList = [{'x': interItem['x'], 'y': interItem['y'], 'r': interItem['r'] - flummiItem['r'], 'g': interItem['g'] - flummiItem['g'], 'b': interItem['b'] - flummiItem['b']  } for interItem, flummiItem in zip(flummiBatchValuelist, flummiBatchValuelist)]

with open('./diff.ppm', 'w', encoding="utf8") as file:
        file.write('P3\n' + str(height) + ' '+ str(width) + '\n1\n')
        for p in diffValueList:
            file.write(str(0 if int(p['r'])==0 else 1) + ' ' + str(0 if int(p['g'])==0 else 1) + ' ' + str(0 if int(p['b'])==0 else 1) + '\n')

print ('{5}: Total: {0}s Mean: {1}s Median: {2}s Min: {3}s Max: {4}s'.format(round(sum(interprTimes),3), round(mean(interprTimes),3), round(median(interprTimes),3), min(interprTimes), max(interprTimes), 'Interpreter'))
if width < 3:
    print ('{5}: Total: {0} Mean: {1}s Median: {2}s Min: {3}s Max: {4}s'.format(round(sum(oneFlummiTimes),3), round(mean(oneFlummiTimes), 3), round(median(oneFlummiTimes),3), min(oneFlummiTimes), max(oneFlummiTimes), 'Flummi one-by-one'))
print ('{2}: Total: {0}s Average/pixel: {1}s'.format(flummiBatchTimes[0], round(flummiBatchTimes[0]/(width*height), 3), 'Flummi batch'))
