from ts_tests_core import *
from assignment3 import *
from pprint import pprint

def convert(pg, vars, labels, labelsIsMap=True, shouldSortComponents=True):
    ts = transition_system_from_program_graph(pg, vars, labels, labelsIsMap)
    if shouldSortComponents:
        sortComponents(ts)
    return ts

def sortStates(states):
    newStates = []
    for state in states:
        loc, eta = state
        newStates.append((loc, sortedTupleFromDict(eta),))
    return sortedListFromIter(newStates)

def sortTo(to):
    newTo = []
    for transition in to:
        s, act, t = transition
        newTo.append(((s[0], sortedTupleFromDict(s[1])), act, (t[0], sortedTupleFromDict(t[1])),))
    return sortedListFromIter(newTo)


def sortL(L):
    newL = []
    for (s, eta), l in L.items():
        newL.append(((s, sortedTupleFromDict(eta),), sortedTupleFromIter(l)))

    return sortedListFromIter(newL)


def sortComponents(ts):
    ts['S'] = sortStates(ts['S'])
    ts['to'] = sortTo(ts['to'])
    ts['L'] = sortL(ts['L'])
    ts['I'] = sortStates(ts['I'])

def test_example():
    def evaluate(cond, eta):
        return {
            'true': lambda eta: True,
            'ncoke > 0': lambda eta: eta['ncoke'] > 0,
            'nsprite > 0': lambda eta: eta['nsprite'] > 0,
            'ncoke=0 && nsprite=0': lambda eta: eta['ncoke'] == 0 and eta['nsprite'] == 0,
            'ncoke=2 && nsprite=2': lambda eta: eta['ncoke'] == 2 and eta['nsprite'] == 2,
        }[cond](eta)

    def effect(act, eta):
        return {
            'coin': lambda eta: eta,
            'ret_coin': lambda eta: eta,
            'refill': lambda eta: {'ncoke': 2, 'nsprite': 2},
            'get_coke': lambda eta: {**eta, 'ncoke': eta['ncoke'] - 1},
            'get_sprite': lambda eta: {**eta, 'nsprite': eta['nsprite'] - 1},
        }[act](eta)

    pg = {
        'Loc': {'start', 'select'},
        'Loc0': {'start'},
        'Act': {'coin', 'refill', 'get_coke', 'get_sprite', 'ret_coin'},
        'Eval': evaluate,
        'Effect': effect,
        'to': {
            ('start', 'true', 'coin', 'select'),
            ('start', 'true', 'refill', 'start'),
            ('select', 'ncoke > 0', 'get_coke', 'start'),
            ('select', 'nsprite > 0', 'get_sprite', 'start'),
            ('select', 'ncoke=0 && nsprite=0', 'ret_coin', 'start')
        },
        'g0': "ncoke=2 && nsprite=2",
    }

    vars = {'ncoke': range(3), 'nsprite': range(3)}

    labels = {"ncoke > 0", "nsprite > 0"}

    ts = convert(pg, vars, labels)
    expected = {
        'AP': {'ncoke > 0', 'nsprite > 0', 'select', 'start'},
        'Act': {'get_sprite', 'get_coke', 'coin', 'refill', 'ret_coin'},
        'I': [('start', (('ncoke', 2), ('nsprite', 2)))],
        'L': [
            (('select', (('ncoke', 0), ('nsprite', 0))), ()),
            (('select', (('ncoke', 0), ('nsprite', 1))), ('nsprite > 0',)),
            (('select', (('ncoke', 0), ('nsprite', 2))), ('nsprite > 0',)),
            (('select', (('ncoke', 1), ('nsprite', 0))), ('ncoke > 0',)),
            (('select', (('ncoke', 1), ('nsprite', 1))),
            ('ncoke > 0', 'nsprite > 0')),
            (('select', (('ncoke', 1), ('nsprite', 2))),
            ('ncoke > 0', 'nsprite > 0')),
            (('select', (('ncoke', 2), ('nsprite', 0))), ('ncoke > 0',)),
            (('select', (('ncoke', 2), ('nsprite', 1))),
            ('ncoke > 0', 'nsprite > 0')),
            (('select', (('ncoke', 2), ('nsprite', 2))),
            ('ncoke > 0', 'nsprite > 0')),
            (('start', (('ncoke', 0), ('nsprite', 0))), ()),
            (('start', (('ncoke', 0), ('nsprite', 1))), ('nsprite > 0',)),
            (('start', (('ncoke', 0), ('nsprite', 2))), ('nsprite > 0',)),
            (('start', (('ncoke', 1), ('nsprite', 0))), ('ncoke > 0',)),
            (('start', (('ncoke', 1), ('nsprite', 1))),
            ('ncoke > 0', 'nsprite > 0')),
            (('start', (('ncoke', 1), ('nsprite', 2))),
            ('ncoke > 0', 'nsprite > 0')),
            (('start', (('ncoke', 2), ('nsprite', 0))), ('ncoke > 0',)),
            (('start', (('ncoke', 2), ('nsprite', 1))),
            ('ncoke > 0', 'nsprite > 0')),
            (('start', (('ncoke', 2), ('nsprite', 2))),
            ('ncoke > 0', 'nsprite > 0'))
        ],
        'S': [
            ('select', (('ncoke', 0), ('nsprite', 0))),
            ('select', (('ncoke', 0), ('nsprite', 1))),
            ('select', (('ncoke', 0), ('nsprite', 2))),
            ('select', (('ncoke', 1), ('nsprite', 0))),
            ('select', (('ncoke', 1), ('nsprite', 1))),
            ('select', (('ncoke', 1), ('nsprite', 2))),
            ('select', (('ncoke', 2), ('nsprite', 0))),
            ('select', (('ncoke', 2), ('nsprite', 1))),
            ('select', (('ncoke', 2), ('nsprite', 2))),
            ('start', (('ncoke', 0), ('nsprite', 0))),
            ('start', (('ncoke', 0), ('nsprite', 1))),
            ('start', (('ncoke', 0), ('nsprite', 2))),
            ('start', (('ncoke', 1), ('nsprite', 0))),
            ('start', (('ncoke', 1), ('nsprite', 1))),
            ('start', (('ncoke', 1), ('nsprite', 2))),
            ('start', (('ncoke', 2), ('nsprite', 0))),
            ('start', (('ncoke', 2), ('nsprite', 1))),
            ('start', (('ncoke', 2), ('nsprite', 2))),
        ],
        'to': [
            (('select', (('ncoke', 0), ('nsprite', 0))),
             'ret_coin',
             ('start', (('ncoke', 0), ('nsprite', 0)))),
            (('select', (('ncoke', 0), ('nsprite', 1))),
             'get_sprite',
             ('start', (('ncoke', 0), ('nsprite', 0)))),
            (('select', (('ncoke', 0), ('nsprite', 2))),
             'get_sprite',
             ('start', (('ncoke', 0), ('nsprite', 1)))),
            (('select', (('ncoke', 1), ('nsprite', 0))),
             'get_coke',
             ('start', (('ncoke', 0), ('nsprite', 0)))),
            (('select', (('ncoke', 1), ('nsprite', 1))),
             'get_coke',
             ('start', (('ncoke', 0), ('nsprite', 1)))),
            (('select', (('ncoke', 1), ('nsprite', 1))),
             'get_sprite',
             ('start', (('ncoke', 1), ('nsprite', 0)))),
            (('select', (('ncoke', 1), ('nsprite', 2))),
             'get_coke',
             ('start', (('ncoke', 0), ('nsprite', 2)))),
            (('select', (('ncoke', 1), ('nsprite', 2))),
             'get_sprite',
             ('start', (('ncoke', 1), ('nsprite', 1)))),
            (('select', (('ncoke', 2), ('nsprite', 0))),
             'get_coke',
             ('start', (('ncoke', 1), ('nsprite', 0)))),
            (('select', (('ncoke', 2), ('nsprite', 1))),
             'get_coke',
             ('start', (('ncoke', 1), ('nsprite', 1)))),
            (('select', (('ncoke', 2), ('nsprite', 1))),
             'get_sprite',
             ('start', (('ncoke', 2), ('nsprite', 0)))),
            (('select', (('ncoke', 2), ('nsprite', 2))),
             'get_coke',
             ('start', (('ncoke', 1), ('nsprite', 2)))),
            (('select', (('ncoke', 2), ('nsprite', 2))),
             'get_sprite',
             ('start', (('ncoke', 2), ('nsprite', 1)))),
            (('start', (('ncoke', 0), ('nsprite', 0))),
             'coin',
             ('select', (('ncoke', 0), ('nsprite', 0)))),
            (('start', (('ncoke', 0), ('nsprite', 0))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 0), ('nsprite', 1))),
             'coin',
             ('select', (('ncoke', 0), ('nsprite', 1)))),
            (('start', (('ncoke', 0), ('nsprite', 1))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 0), ('nsprite', 2))),
             'coin',
             ('select', (('ncoke', 0), ('nsprite', 2)))),
            (('start', (('ncoke', 0), ('nsprite', 2))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 1), ('nsprite', 0))),
             'coin',
             ('select', (('ncoke', 1), ('nsprite', 0)))),
            (('start', (('ncoke', 1), ('nsprite', 0))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 1), ('nsprite', 1))),
             'coin',
             ('select', (('ncoke', 1), ('nsprite', 1)))),
            (('start', (('ncoke', 1), ('nsprite', 1))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 1), ('nsprite', 2))),
             'coin',
             ('select', (('ncoke', 1), ('nsprite', 2)))),
            (('start', (('ncoke', 1), ('nsprite', 2))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 2), ('nsprite', 0))),
             'coin',
             ('select', (('ncoke', 2), ('nsprite', 0)))),
            (('start', (('ncoke', 2), ('nsprite', 0))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 2), ('nsprite', 1))),
             'coin',
             ('select', (('ncoke', 2), ('nsprite', 1)))),
            (('start', (('ncoke', 2), ('nsprite', 1))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 2), ('nsprite', 2))),
             'coin',
             ('select', (('ncoke', 2), ('nsprite', 2)))),
            (('start', (('ncoke', 2), ('nsprite', 2))),
             'refill',
             ('start', (('ncoke', 2), ('nsprite', 2)))),
        ]
    }
    assert ts == expected

def runTests():
    test_example()


if __name__ == '__main__':
    runTests()
