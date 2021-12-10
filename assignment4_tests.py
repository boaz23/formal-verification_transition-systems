from assignment4 import *
from tests_core import *


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


def test_ts_1_independent():
    l1 = {
        's1': {'b'},
        's2': {'a', 'b'},
        's3': set(),
    }
    ts1 = {'S': {'s1', 's3', 's2'},
           'Act': {'b', 'd', 'a'},
           'to': {('s2', 'd', 's3'), ('s1', 'a', 's2'), ('s2', 'b', 's1')},
           'I': {'s1'},
           'AP': {'b', 'a'},
           'L': lambda s: l1[s],
    }

    l2 = {
        's4': {'a'},
        's5': set(),
    }
    ts2 = {'S': {'s4', 's5'},
           'Act': {'b', 'a', 'c'},
           'to': {('s4', 'a', 's5'), ('s5', 'b', 's5'), ('s5', 'c', 's4')},
           'I': {'s4'},
           'AP': {'b', 'a'},
           'L': lambda s: l2[s],
    }

    expected = {
        'S': {('s1', 's4'), ('s1', 's5'), ('s3', 's4'), ('s2', 's4'), ('s3', 's5'), ('s2', 's5')},
        'Act': {'a', 'b', 'c', 'd'},
        'to': {
            (('s1', 's4'), 'a', ('s1', 's5')),
            (('s1', 's4'), 'a', ('s2', 's4')),
            (('s1', 's5'), 'a', ('s2', 's5')),
            (('s1', 's5'), 'b', ('s1', 's5')),
            (('s1', 's5'), 'c', ('s1', 's4')),
            (('s2', 's4'), 'a', ('s2', 's5')),
            (('s2', 's4'), 'b', ('s1', 's4')),
            (('s2', 's4'), 'd', ('s3', 's4')),
            (('s2', 's5'), 'b', ('s1', 's5')),
            (('s2', 's5'), 'b', ('s2', 's5')),
            (('s2', 's5'), 'c', ('s2', 's4')),
            (('s2', 's5'), 'd', ('s3', 's5')),
            (('s3', 's4'), 'a', ('s3', 's5')),
            (('s3', 's5'), 'b', ('s3', 's5')),
            (('s3', 's5'), 'c', ('s3', 's4')),
        },
        'I': {('s1', 's4')}, 'AP': {'b', 'a'},
        'L': {
            ('s1', 's4'): l1['s1'] | l2['s4'],
            ('s1', 's5'): l1['s1'] | l2['s5'],
            ('s3', 's4'): l1['s3'] | l2['s4'],
            ('s2', 's4'): l1['s2'] | l2['s4'],
            ('s3', 's5'): l1['s3'] | l2['s5'],
            ('s2', 's5'): l1['s2'] | l2['s5'],
        },
    }
    # expected = debuggableTs(expected, convertLabelsFuncToMap=False)

    interleaved_ts = interleave_transition_systems(ts1, ts2, set())
    convertTsLabelsFuncToMap(interleaved_ts)
    # interleaved_ts = debuggableTs(interleaved_ts)

    assert interleaved_ts == expected


def test_ts_1_handshake_1():
    l1 = {
        's1': {'b'},
        's2': {'a', 'b'},
        's3': set(),
    }
    ts1 = {'S': {'s1', 's3', 's2'},
           'Act': {'b', 'd', 'a'},
           'to': {('s2', 'd', 's3'), ('s1', 'a', 's2'), ('s2', 'b', 's1')},
           'I': {'s1'},
           'AP': {'b', 'a'},
           'L': lambda s: l1[s],
    }

    l2 = {
        's4': {'a'},
        's5': set(),
    }
    ts2 = {'S': {'s4', 's5'},
           'Act': {'b', 'a', 'c'},
           'to': {('s4', 'a', 's5'), ('s5', 'b', 's5'), ('s5', 'c', 's4')},
           'I': {'s4'},
           'AP': {'b', 'a'},
           'L': lambda s: l2[s],
    }

    expected = {
        'S': {('s1', 's4'), ('s1', 's5'), ('s3', 's4'), ('s2', 's4'), ('s3', 's5'), ('s2', 's5')},
        'Act': {'a', 'b', 'c', 'd'},
        'to': {(('s2', 's5'), 'c', ('s2', 's4')), (('s1', 's5'), 'c', ('s1', 's4')), (('s1', 's4'), 'a', ('s2', 's5')), (('s2', 's4'), 'd', ('s3', 's4')), (('s2', 's5'), 'd', ('s3', 's5')), (('s3', 's5'), 'c', ('s3', 's4')), (('s2', 's5'), 'b', ('s1', 's5'))},
        'I': {('s1', 's4')}, 'AP': {'b', 'a'},
        'L': {
            ('s1', 's4'): l1['s1'] | l2['s4'],
            ('s1', 's5'): l1['s1'] | l2['s5'],
            ('s3', 's4'): l1['s3'] | l2['s4'],
            ('s2', 's4'): l1['s2'] | l2['s4'],
            ('s3', 's5'): l1['s3'] | l2['s5'],
            ('s2', 's5'): l1['s2'] | l2['s5'],
        },
    }
    # expected = debuggableTs(expected, convertLabelsFuncToMap=False)

    interleaved_ts = interleave_transition_systems(ts1, ts2, {'a', 'b',})
    convertTsLabelsFuncToMap(interleaved_ts)
    # interleaved_ts = debuggableTs(interleaved_ts)

    assert interleaved_ts == expected


def runTests():
    test_peterson()
    test_ts_1_independent()
    test_ts_1_handshake_1()


if __name__ == '__main__':
    runTests()