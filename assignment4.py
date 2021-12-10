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
        return len(self.list) == 0

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
            if a in map:
                return map[a](a, eta)

            raise Exception("Unknown param for map")

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
        followingLoc = self._followingLocOf(loc, locIndex, loc_to)
        self.to.add((loc, cond, act, followingLoc,))
        if followingLoc not in self.loc:
            self.loc.add(followingLoc)
            self.leftStack.push(followingLoc)

    def _followingLocOf(self, loc, locIndex, loc_to):
        locList = list(loc)
        locList[locIndex] = loc_to
        followingLoc = tuple(locList)
        return followingLoc

    def _initConvert(self):
        self._initStartLocations()
        self.act = self.pg1.act | self.pg2.act
        self.g0 = f'{self.pg1.g0} and {self.pg2.g0}'

    def _initStartLocations(self):
        for loc0_1 in self.pg1.loc0:
            for loc0_2 in self.pg2.loc0:
                self.loc0.add((loc0_1, loc0_2,))


def interleave_program_graphs(pg1, pg2, debug=False):
    return InterleaveProgramGraphsConvertor(
        pg1=ProgramGraph(pg1),
        pg2=ProgramGraph(pg2),
    ).convert(debug)


def main():
    pass


if __name__ == '__main__':
    main()
