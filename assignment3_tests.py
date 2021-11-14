from ts_tests_core import *
from assignment3 import *

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

    convertor = TransitionSystemFromProgramGraphConvertor(
        programGraph=ProgramGraph(pg),
        varDescriptors=vars,
        conditionLabels=labels
    )
    convertor.initConvert()
    pass


def runTests():
    test_example()


if __name__ == '__main__':
    runTests()
