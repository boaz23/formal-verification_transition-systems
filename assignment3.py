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


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

    def clone_shallow(self):
        return HashableDict(self)


class AllStartValuesIterator:
    def __init__(self, varDescriptors):
        self.descriptorsList = list(varDescriptors.items())
        self.stateStack: Stack = Stack()

        self.index = 0
        self.acc = HashableDict()
        self._push_allFromCurrent()

    class VarState:
        def __init__(self, var, valuesIterator):
            self.var = var
            self.valuesIterator = valuesIterator

        def __str__(self):
            return f'{{'\
                   f'  var=\'{self.var}\''\
                   f'}}'

    def __next__(self):
        if self.stateStack.isEmpty():
            raise StopIteration

        retNext = self._buildNext()
        while not self.stateStack.isEmpty():
            varState = self._pop()
            try:
                self._push_next(varState)
                break
            except StopIteration:
                # Iteration on the values of the current var is done.
                # Move on the to the next value of the previous var.
                pass

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
        var, possibleValues = self.descriptorsList[self.index]
        valuesIterator = iter(possibleValues)
        try:
            value = next(valuesIterator)
            self.acc[var] = value
            self.stateStack.push(self.VarState(var, valuesIterator))
        except StopIteration:
            self.stateStack.clear()

    def _buildNext(self):
        # make a copy of the current accumulator
        # (because it is going to get mutated).
        return HashableDict(self.acc)

    def _pop(self):
        self.index = self.index - 1
        varState = self.stateStack.pop()
        var, _ = self.descriptorsList[self.index]
        del self.acc[var]
        return varState

    def _push_next(self, varState):
        self._push_next_single(varState)
        self._push_allFromCurrent()

    def _push_next_single(self, varState):
        value = next(varState.valuesIterator)
        var, _ = self.descriptorsList[self.index]
        self.stateStack.push(self.VarState(var, varState.valuesIterator))
        self.acc[var] = value
        self.index = self.index + 1



class AllStartValues:
    def __init__(self, varDescriptors):
        self.varDescriptors = varDescriptors

    def __iter__(self):
        return AllStartValuesIterator(self.varDescriptors)


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

class TransitionSystemFromProgramGraphConvertor:
    def __init__(self, programGraph, varDescriptors, conditionLabels):
        self.programGraph = programGraph
        self.varDescriptors = varDescriptors
        self.conditionLabels = conditionLabels

        self.stateLabelsMap = {}
        self.states_start = set()
        self.act = set()
        self.to = set()
        self.ap = set()

    def convert(self, labelsIsMap=False):
        self._initConvert()
        self._convert_fromAllStartStates()
        return self._buildTransitionSystem(labelsIsMap)

    def _convert_fromAllStartStates(self):
        for startState in self.states_start:
            if startState in self.stateLabelsMap:
                continue

            self._convert_fromStartState(startState)

    def _buildTransitionSystem(self, labelsIsMap):
        return {
            'S': set(self.stateLabelsMap.keys()),
            'I': self.states_start,
            'Act': self.act,
            'to': self.to,
            'AP': self.ap,
            'L': self.stateLabelsMap if labelsIsMap else self.buildL(self.stateLabelsMap)
        }

    @staticmethod
    def buildL(labelsMap):
        def L(s):
            return labelsMap[s]
        return L

    def _convert_fromStartState(self, startState):
        statesLeftStack = Stack([startState])
        while not statesLeftStack.isEmpty():
            state = statesLeftStack.pop()
            loc, eta = state

            self.ap.add(loc)
            self.stateLabelsMap[state] = self._convert_computeLabels(state)
            self._convert_appendTransitions(state, statesLeftStack)

    def _convert_computeLabels(self, state):
        loc, eta = state
        labels = {loc}
        for cond in self.conditionLabels:
            if self.programGraph.eval(cond, eta):
                labels.add(cond)
        return labels

    def _convert_appendTransitions(self, state, statesLeftStack):
        loc, eta = state
        for transition in self.programGraph.postTransitions(loc):
            loc_from, cond, act, loc_to = transition
            if self.programGraph.eval(cond, eta):
                self._convert_addTransition(state, transition, statesLeftStack)

    def _convert_addTransition(self, state, transition, statesLeftStack):
        loc, eta = state
        loc_from, cond, act, loc_to = transition

        eta_new = HashableDict(self.programGraph.effect(act, eta))
        followingState = (loc_to, eta_new)
        self.to.add((state, act, followingState,))
        if followingState not in self.stateLabelsMap:
            statesLeftStack.push(followingState)
            self.stateLabelsMap[followingState] = None

    def _initConvert(self):
        self._initFromAllInputValues()
        self.act = set(self.programGraph.act)
        self.ap = set(self.conditionLabels)

    def _initFromAllInputValues(self):
        for eta in AllStartValues(self.varDescriptors):
            if not self.programGraph.eval(self.programGraph.g0, eta):
                continue

            for loc0 in self.programGraph.loc0:
                self.states_start.add((loc0, eta))


def transitionSystemFromProgramGraph(pg, vars, labels, labelsIsMap=False):
    return TransitionSystemFromProgramGraphConvertor(
        programGraph=ProgramGraph(pg),
        varDescriptors=vars,
        conditionLabels=labels
    ).convert(labelsIsMap=labelsIsMap)


def main():
    pass


if __name__ == '__main__':
    main()
