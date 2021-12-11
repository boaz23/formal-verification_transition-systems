from typing import Set, List


def map_unpack(f, iter):
    result = []
    for value in iter:
        result.append(f(*value))
    return result


def tuple_set(t, i, v):
    l = list(t)
    l[i] = v
    t = tuple(l)
    return t


class Stack:
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = []

        self.list = list(iterable)

    def push(self, value):
        self.list.append(value)

    def pop(self):
        return self.list.pop()

    def updateTop(self, value):
        self.list[self.lastIndex()] = value

    def clear(self):
        self.list = []

    def peek(self):
        return self.list[self.lastIndex()]

    def isEmpty(self):
        return not self.list

    def lastIndex(self):
        return len(self.list) - 1

    def clone_shallow(self):
        return Stack(self.list)

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        return iter(self.list)

    def __str__(self):
        return str(self.list)


class ProductIterator:
    def __init__(self, iterables):
        self.descriptorsList = iterables
        self.stateStack: Stack = Stack()

        self.index = 0
        self.acc = [None] * len(iterables)
        self._push_allFromCurrent()

    class IterState:
        def __init__(self, index, iterator):
            self.index = index
            self.iterator = iterator

        def __repr__(self):
            return f'IterState({self.index}, iter(...))'

        def __str__(self):
            return f'{{'\
                   f'  index=\'{self.index}\''\
                   f'}}'

    def __next__(self):
        if self.stateStack.isEmpty():
            raise StopIteration

        retNext = self._buildNext()
        while not self.stateStack.isEmpty():
            iterState = self.stateStack.peek()
            try:
                self._update_next(iterState)
                break
            except StopIteration:
                # Iteration on the values of the current var is done.
                # Move on the to the next value of the previous var.
                self._pop()

        return retNext

    def _push_allFromCurrent(self):
        while self.index < len(self.descriptorsList):
            self._push_single_start()
            self.index = self.index + 1

            # We "pushed" but the stack is empty?
            # That must be because the var has no values.
            if self.stateStack.isEmpty():
                break

    def _push_single_start(self):
        iterable = self.descriptorsList[self.index]
        iterator = iter(iterable)
        try:
            value = next(iterator)
            self.acc[self.index] = value
            self.stateStack.push(self.IterState(self.index, iterator))
        except StopIteration:
            self.stateStack.clear()

    def _buildNext(self):
        # make a copy of the current accumulator
        # (because it is going to get mutated).
        return list(self.acc)

    def _pop(self):
        self.index = self.index - 1
        self.stateStack.pop()

    def _update_next(self, iterState):
        self._update_valueOfCurrent(iterState)
        self._push_allFromCurrent()

    def _update_valueOfCurrent(self, iterState):
        value = next(iterState.iterator)
        self.acc[self.index - 1] = value


class Product:
    def __init__(self, iterables):
        self.iterables = list(iterables)

    def __iter__(self):
        return ProductIterator(self.iterables)


class ProgramGraph:
    def __init__(self, pgDict):
        self.loc = pgDict['Loc']
        self.loc0 = pgDict['Loc0']
        self.act = pgDict['Act']
        self.eval = pgDict['Eval']
        self.effect = pgDict['Effect']
        self.to = pgDict['to']
        self.g0 = pgDict['g0']

    def postTransitions(self, loc):
        result = set()
        for transition in self.to:
            loc_from, cond, act, loc_to = transition
            if loc_from == loc:
                result.add(transition)
        return result


class InterleaveProgramGraphsConvertor:
    def __init__(self, pg1: ProgramGraph, pg2: ProgramGraph):
        self.pg1: ProgramGraph = pg1
        self.pg2: ProgramGraph = pg2
        self.pgs = [pg1, pg2]

        self.loc = set()
        self.act = set()
        self.conditionEvalMap = {}
        self.actEffectMap = {}
        self.to = set()
        self.loc0 = set()
        self.g0 = "True"

        self.leftStack = Stack()
        self.debug = False

    def convert(self, debug):
        self.debug = debug
        self._initConvert()
        self._convert_fromStartAll()
        return self._build()

    def _build(self):
        return {
            'Loc': set(self.loc),
            'Act': set(self.act),
            'Eval': self._buildTagMapFunc(self.conditionEvalMap),
            'Effect': self._buildTagMapFunc(self.actEffectMap),
            'to': set(self.to),
            'Loc0': set(self.loc0),
            'g0': self.g0,
        }

    def _buildTagMapFunc(self, map):
        def func(a, eta):
            return map[a](a, eta)

        return func if not self.debug else map

    def _convert_fromStartAll(self):
        for start in self.loc0:
            if start in self.loc:
                continue

            self.loc.add(start)
            self._convert_fromStartSpecific(start)

    def _convert_fromStartSpecific(self, start):
        self.leftStack = Stack([start])
        while not self.leftStack.isEmpty():
            loc = self.leftStack.pop()
            self._traverse(loc)

    def _traverse(self, loc):
        for locIndex in range(0, len(self.pgs)):
            self._traverse_allTransitionOf(loc, locIndex)

    def _traverse_allTransitionOf(self, loc, locIndex):
        pg = self.pgs[locIndex]
        subLoc = loc[locIndex]
        for transition in pg.postTransitions(subLoc):
            self._traverse_transition(locIndex, loc, transition)

    def _traverse_transition(self, locIndex, loc, transition):
        loc_from, cond, act, loc_to = transition

        # Tag them with the corresponding functions of the current PG.
        # Override the last tag of the cond and act.
        # Since mutual items for both PGs is guaranteed to be the same,
        # we don't care overriding.
        self.conditionEvalMap[cond] = self.pgs[locIndex].eval if not self.debug else locIndex
        self.actEffectMap[act] = self.pgs[locIndex].effect if not self.debug else locIndex

        # post location stuff
        followingLoc = self._followingOf(loc, locIndex, loc_to)
        self.to.add((loc, cond, act, followingLoc,))
        if followingLoc not in self.loc:
            self.loc.add(followingLoc)
            self.leftStack.push(followingLoc)

    def _followingOf(self, loc, locIndex, loc_to):
        return tuple_set(loc, locIndex, loc_to)

    def _initConvert(self):
        self._initStarts()
        self.act = self.pg1.act | self.pg2.act
        self.g0 = f'{self.pg1.g0} and {self.pg2.g0}'

    def _initStarts(self):
        for loc0_1 in self.pg1.loc0:
            for loc0_2 in self.pg2.loc0:
                self.loc0.add((loc0_1, loc0_2,))


class TransitionSystem:
    def __init__(self, S, Act, to, I, AP, L):
        self.s = S
        self.act = Act
        self.to = to
        self.i = I
        self.ap = AP
        self.l = L

    def postTransitions(self, state, act=None):
        result = set()
        for transition in self.to:
            state_from, a, state_to = transition
            if state_from == state and (act is None or act == a):
                result.add(transition)
        return result


class InterleaveTransitionSystemsConvertor:
    def __init__(self, tss: List[TransitionSystem], h: Set[str]):
        self.tss = tss
        self.h = h

        self.labelsMap = {}
        self.starts = set()
        self.act = set()
        self.to = set()
        self.ap = set()

        self.leftStack = Stack()
        self.debug = False

    def convert(self, debug):
        self.debug = debug
        self._initConvert()
        self._convert_fromStartAll()
        return self._build()

    def _build(self):
        return {
            'S': set(self.labelsMap.keys()),
            'I': set(self.starts),
            'Act': set(self.act),
            'to': set(self.to),
            'AP': set(self.ap),
            'L': self.buildL(),
        }

    def buildL(self):
        labelsMap = self.labelsMap
        def L(s):
            return labelsMap[s]
        return L if not self.debug else labelsMap

    def _convert_fromStartAll(self):
        for start in self.starts:
            if start in self.labelsMap:
                continue

            self._convert_fromStartSpecific(start)

    def _convert_fromStartSpecific(self, start):
        self.leftStack = Stack([start])
        while not self.leftStack.isEmpty():
            state = self.leftStack.pop()
            self.labelsMap[state] = self._computeLabels(state)
            self._traverse(state)

    def _computeLabels(self, state):
        labelSets = self._mapStateTs(lambda s, ts: ts.l(s), state)
        return set.union(*labelSets)

    def _traverse(self, state):
        self._traverse_independent(state)
        self._traverse_handshake(state)

    def _traverse_independent(self, state):
        for index in range(0, len(self.tss)):
            self._traverse_independent_allTransitionOf(state, index)

    def _traverse_independent_allTransitionOf(self, state, index):
        ts = self.tss[index]
        subState = state[index]
        for transition in ts.postTransitions(subState):
            state_from, act, state_to = transition
            if act not in self.h:
                self._addTransition_independent(index, state, transition)

    def _addTransition_independent(self, index, state, transition):
        state_from, act, state_to = transition

        # post location stuff
        followingState = self._followingOfSingle(state, index, state_to)
        self._addTransition_core(state, act, followingState)

    def _followingOfSingle(self, state, index, state_to):
        return tuple_set(state, index, state_to)

    def _traverse_handshake(self, state):
        for act in self.h:
            transitionsList = self._mapStateTs(
                lambda s, ts: ts.postTransitions(s, act),
                state
            )
            self._traverse_handshake_transitions(state, act, transitionsList)

    def _traverse_handshake_transitions(self, state, act, transitionsList):
        for syncedTransitions in Product(transitionsList):
            self._addTransition_handshake(state, act, syncedTransitions)

    def _addTransition_handshake(self, state, act, syncedTransitions):
        state_to = tuple(map_unpack(
            lambda s_from, _, s_to: s_to,
            syncedTransitions
        ))
        self._addTransition_core(state, act, state_to)

    def _addTransition_core(self, state, act, followingState):
        self.to.add((state, act, followingState,))
        if followingState not in self.labelsMap:
            self.labelsMap[followingState] = None
            self.leftStack.push(followingState)

    def _initConvert(self):
        self._initStarts()
        self.act = set.union(*map(lambda ts: ts.act, self.tss))
        self.ap = set.union(*map(lambda ts: ts.ap, self.tss))

    def _mapStateTs(self, f, state):
        return map_unpack(f, zip(state, self.tss))

    def _initStarts(self):
        starts = Product(map(lambda ts: ts.i, self.tss))
        starts = map(lambda start: tuple(start), starts)
        starts = list(starts)
        self.starts = starts

def interleave_program_graphs(pg1, pg2, debug=False):
    return InterleaveProgramGraphsConvertor(
        pg1=ProgramGraph(pg1),
        pg2=ProgramGraph(pg2),
    ).convert(debug)


def interleave_transition_systems(ts1, ts2, h, debug=False):
    return InterleaveTransitionSystemsConvertor(
        tss=[
            TransitionSystem(**ts1),
            TransitionSystem(**ts2),
        ],
        h=h,
    ).convert(debug)


def main():
    pass


if __name__ == '__main__':
    main()
