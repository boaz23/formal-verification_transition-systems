import copy
import pprint


def printableTs(ts):
    ts = copy.deepcopy(ts)
    ts['AP'] = sorted(list(ts['AP']))
    for s in ts['S']:
        ts['L'][s] = sorted(list(ts['L'][s]))
    return ts


def printTs(ts):
    pprint.pprint(printableTs(ts))


def convertLabelsFuncToMap(L, states):
    lmap = {}
    for s in states:
        lmap[s] = L(s)
    return lmap
