from tests_core import *
import assignment2


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


def test2():
    ts = convertCircuit(1, 1, 1, lambda s: (not (s[1] or s[0]),), lambda s: (s[1] ^ s[0],))
    expected = {
        'AP': {'r1', 'x1', 'y1'},
        'Act': {(False,), (True,)},
        'I': {(False, True), (False, False)},
        'L': {
            (False, False): set(),
            (False, True): {'x1', 'y1'},
            (True, False): {'r1', 'y1'},
            (True, True): {'r1', 'x1'}
        },
        'S': {(False, True), (True, False), (True, True), (False, False)},
        'to': {
            ((False, False), (False,), (True, False)),
            ((False, False), (True,), (True, True)),
            ((False, True), (False,), (False, False)),
            ((False, True), (True,), (False, True)),
            ((True, False), (False,), (False, False)),
            ((True, False), (True,), (False, True)),
            ((True, True), (False,), (False, False)),
            ((True, True), (True,), (False, True))
        }
    }

    assert ts == expected


def test3():
    ts = convertCircuit(1, 2, 1, lambda s: ((s[2] and s[1]) ^ s[0], s[2] ^ s[1]) if s != (True, False, True) else (False, True), lambda s: (s[0] and (s[1] or s[2]),))
    expected = {
        'AP': {'r1', 'r2', 'x1', 'y1'},
        'Act': {(False,), (True,)},
        'I': {(False, False, False), (False, False, True)},
        'L': {
            (False, False, False): set(),
            (False, False, True): {'x1'},
            (False, True, False): {'r2'},
            (False, True, True): {'r2', 'x1'},
            (True, False, False): {'r1'},
            (True, False, True): {'r1', 'x1', 'y1'}
        },
        'S': {
            (False, False, False),
            (False, False, True),
            (False, True, False),
            (False, True, True),
            (True, False, False),
            (True, False, True)
        },
        'to': {
            ((False, False, False), (False,), (False, False, False)),
            ((False, False, False), (True,), (False, False, True)),
            ((False, False, True), (False,), (False, True, False)),
            ((False, False, True), (True,), (False, True, True)),
            ((False, True, False), (False,), (False, True, False)),
            ((False, True, False), (True,), (False, True, True)),
            ((False, True, True), (False,), (True, False, False)),
            ((False, True, True), (True,), (True, False, True)),
            ((True, False, False), (False,), (True, False, False)),
            ((True, False, False), (True,), (True, False, True)),
            ((True, False, True), (False,), (False, True, False)),
            ((True, False, True), (True,), (False, True, True))
        }
    }

    assert ts == expected


def test4():
    ts = convertCircuit(1, 2, 1, lambda s: (True, True), lambda s: (s[2] ^ s[1] ^ s[0],))
    expected = {
        'AP': {'r1', 'r2', 'x1', 'y1'},
        'Act': {(False,), (True,)},
        'I': {(False, False, False), (False, False, True)},
        'L': {
            (False, False, False): set(),
            (False, False, True): {'x1', 'y1'},
            (True, True, False): {'r1', 'r2'},
            (True, True, True): {'r1', 'r2', 'x1', 'y1'}
        },
        'S': {
            (False, False, False),
            (False, False, True),
            (True, True, False),
            (True, True, True)
        },
        'to': {
            ((False, False, False), (False,), (True, True, False)),
            ((False, False, False), (True,), (True, True, True)),
            ((False, False, True), (False,), (True, True, False)),
            ((False, False, True), (True,), (True, True, True)),
            ((True, True, False), (False,), (True, True, False)),
            ((True, True, False), (True,), (True, True, True)),
            ((True, True, True), (False,), (True, True, False)),
            ((True, True, True), (True,), (True, True, True))
        }
    }

    assert ts == expected


def runTests():
    test1()
    test2()
    test3()
    test4()


if __name__ == '__main__':
    runTests()
