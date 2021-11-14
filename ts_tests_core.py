import copy
import pprint


def sortedListFromIter(iterable):
    return sorted(list(iterable))

def sortedListFromDict(dict):
    return sortedListFromIter(dict.items())

def sortedTupleFromIter(iterable):
    return tuple(sortedListFromIter(iterable))

def sortedTupleFromDict(dict):
    return tuple(sortedListFromDict(dict))


def printableTs(ts, convertLabelsFuncToMap=True):
    ts = copy.deepcopy(ts)
    if convertLabelsFuncToMap:
        convertTsLabelsFuncToMap(ts)
    ts['AP'] = sortedListFromIter(ts['AP'])
    for s in ts['S']:
        ts['L'][s] = sortedListFromIter(ts['L'][s])
    return ts


def printTs(ts, convertLabelsFuncToMap=True):
    pprint.pprint(printableTs(ts, convertLabelsFuncToMap))


def convertTsLabelsFuncToMap(ts):
    ts['L'] = convertLabelsFuncToMap(ts['L'], ts['S'])


def convertLabelsFuncToMap(L, states):
    lmap = {}
    for s in states:
        lmap[s] = L(s)
    return lmap
