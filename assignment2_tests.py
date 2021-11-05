import assignment2
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


def convertCircuit(*args):
    ts = assignment2.transitionSystemFromCircuit(*args)
    ts["L"] = convertLabelsFuncToMap(ts['L'], ts['S'])
    return ts


def test1():
    ts = convertCircuit(1, 2, 1, lambda s: ((s[2] and s[1]) ^ s[0], s[2] ^ s[1]), lambda s: (s[0] and s[1] and s[2],))
    expected = {
        'S': {(False, False, False), (True, True, False), (False, True, False), (True, False, True), (False, False, True), (True, True, True), (False, True, True), (True, False, False)},
        'I': {(False, False, False), (False, False, True)},
        'Act': {(True,), (False,)},
        'to': {((False, True, False), (False,), (False, True, False)), ((True, True, True), (False,), (False, False, False)), ((True, True, True), (True,), (False, False, True)), ((False, True, True), (False,), (True, False, False)), ((True, False, False), (False,), (True, False, False)), ((True, True, False), (True,), (True, True, True)), ((True, False, True), (True,), (True, True, True)), ((True, True, False), (False,), (True, True, False)),
((False, True, True), (True,), (True, False, True)), ((True, False, True), (False,), (True, True, False)), ((False, True, False), (True,), (False, True, True)), ((False, False, False), (True,), (False, False, True)), ((False, False, True), (True,), (False, True, True)), ((False, False, True), (False,), (False, True, False)), ((True, False, False),
(True,), (True, False, True)), ((False, False, False), (False,), (False, False, False))},
        'AP': {'r2', 'y1', 'x1', 'r1'},
        'L': {
            (False, False, False): set(),
            (False, False, True): {'x1'},
            (False, True, False): {'r2'},
            (False, True, True): {'r2', 'x1'},
            (True, False, False): {'r1'},
            (True, False, True): {'x1', 'r1'},
            (True, True, False): {'r2', 'r1'},
            (True, True, True): {'r2', 'x1', 'r1', 'y1'}
        }
    }

    assert ts == expected

def runTests():
    test1()


if __name__ == '__main__':
    runTests()
