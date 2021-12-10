from assignment4 import *
from tests_core import sortedListFromIter


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


def sortedInterleavedPg(pg):
    pg = dict(pg)
    pg['to'] = sortedListFromIter(pg['to'])
    pg['Loc'] = sortedListFromIter(pg['Loc'])
    pg['Act'] = sortedListFromIter(pg['Act'])
    pg['Loc0'] = sortedListFromIter(pg['Loc0'])
    return pg


def test_peterson():
    def effect(act, eta):
        eta = HashableDict(eta)
        exec(act, None, eta)
        return eta

    def evaluate(cond, eta):
        return eval(cond, None, eta)

    peterson0 = {'Loc': {'crit', 'noncrit', 'wait'},
                 'Act': {'', 'b0=True;x=1', 'b0=False'},
                 'Eval': evaluate,
                 'Effect': effect,
                 'to': {('noncrit', 'True', 'b0=True;x=1', 'wait'), ('wait', 'x==0 or not b1', '', 'crit'),
                        ('crit', 'True', 'b0=False', 'noncrit')},
                 'Loc0': {'noncrit'},
                 'g0': 'not b0'}
    peterson1 = {'Loc': {'crit', 'noncrit', 'wait'},
                 'Act': {'', 'b1=True;x=0', 'b1=False'},
                 'Eval': evaluate,
                 'Effect': effect,
                 'to': {('noncrit', 'True', 'b1=True;x=0', 'wait'), ('crit', 'True', 'b1=False', 'noncrit'),
                        ('wait', 'x==1 or not b0', '', 'crit')},
                 'Loc0': {'noncrit'},
                 'g0': 'not b1'}

    expected = {
        'Loc': {('crit', 'noncrit'), ('wait', 'noncrit'), ('noncrit', 'crit'), ('noncrit', 'wait'), ('crit', 'crit'), ('crit', 'wait'), ('wait', 'crit'), ('wait', 'wait'), ('noncrit', 'noncrit')},
        'Act': {'', 'b0=False', 'b1=True;x=0', 'b0=True;x=1', 'b1=False'},
        # How to test these??
        # 'Eval': {},
        # 'Effect': {},
        'to': {(('crit', 'crit'), 'True', 'b1=False', ('crit', 'noncrit')), (('crit', 'noncrit'), 'True', 'b0=False', ('noncrit', 'noncrit')), (('wait', 'noncrit'), 'x==0 or not b1', '', ('crit', 'noncrit')), (('wait', 'crit'), 'x==0 or not b1', '', ('crit', 'crit')), (('crit', 'wait'), 'x==1 or not b0', '', ('crit', 'crit')), (('crit', 'wait'), 'True', 'b0=False', ('noncrit', 'wait')), (('wait', 'noncrit'), 'True', 'b1=True;x=0', ('wait', 'wait')), (('wait', 'wait'), 'x==1 or not b0', '', ('wait', 'crit')), (('noncrit', 'crit'), 'True', 'b0=True;x=1', ('wait', 'crit')), (('wait', 'crit'), 'True', 'b1=False', ('wait', 'noncrit')), (('wait', 'wait'), 'x==0 or not b1', '', ('crit', 'wait')), (('noncrit', 'noncrit'), 'True', 'b0=True;x=1', ('wait', 'noncrit')), (('crit', 'noncrit'), 'True', 'b1=True;x=0', ('crit', 'wait')), (('crit', 'crit'), 'True', 'b0=False', ('noncrit', 'crit')), (('noncrit', 'wait'), 'True', 'b0=True;x=1', ('wait', 'wait')), (('noncrit', 'wait'), 'x==1 or not b0', '', ('noncrit', 'crit')), (('noncrit', 'noncrit'), 'True', 'b1=True;x=0', ('noncrit', 'wait')), (('noncrit', 'crit'), 'True', 'b1=False', ('noncrit', 'noncrit'))},
        'Loc0': {('noncrit', 'noncrit')},
        'g0': 'not b0 and not b1'
    }
    # expected = sortedInterleavedPg(expected)

    interleaved_peterson = interleave_program_graphs(peterson0, peterson1)
    # interleaved_peterson = sortedInterleavedPg(interleaved_peterson)
    del interleaved_peterson['Eval']
    del interleaved_peterson['Effect']

    assert interleaved_peterson == expected


def runTests():
    test_peterson()


if __name__ == '__main__':
    runTests()