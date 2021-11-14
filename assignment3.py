class Stack:
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = []

        self.stack = list(iterable)

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[len(self.stack) - 1]

    def isEmpty(self):
        return len(self.stack) == 0

    def clone_shallow(self):
        return Stack(self.stack)

    def __len__(self):
        return len(self.stack)

    def __iter__(self):
        return iter(self.stack)

    def __str__(self):
        return str(self.stack)


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

    def clone_shallow(self):
        return HashableDict(self)

    def cloneAndAdd(self, key, value):
        clone = self.clone_shallow()
        clone[key] = value
        return clone


class AllStartValuesIterator:
    def __init__(self, varDescriptors):
        self.descriptorsList = list(varDescriptors.items())
        self.stateStack: Stack = Stack()

        self._pushVars(0, HashableDict())

    class VarState:
        def __init__(self, index, var, valuesIterator, value, acc):
            self.index = index
            self.var = var
            self.valuesIterator = valuesIterator
            self.value = value
            self.acc = acc

        def __str__(self):
            return f'{{\n'\
                   f'  var=\'{self.var}\'\n'\
                   f'  value={self.value}\n'\
                   f'  index={self.index}\n'\
                   f'  acc={self.acc}\n'\
                   f'}}'

    def _pushVars(self, index_start, acc_start):
        acc = acc_start
        for i in range(index_start, len(self.descriptorsList)):
            self._pushVar(i, acc)

            # We "pushed" but the stack is empty?
            # That must be because the var has no values.
            if self.stateStack.isEmpty():
                break

    def _pushVar(self, i, acc):
        var, possibleValues = self.descriptorsList[i]
        valuesIterator = iter(possibleValues)
        try:
            value = next(valuesIterator)
            self.stateStack.push(self.VarState(i, var, valuesIterator, value, acc.clone_shallow()))
            acc[var] = value
        except StopIteration:
            self.stateStack = Stack()

    def __next__(self):
        if self.stateStack.isEmpty():
            raise StopIteration

        retNext = self._buildNext()
        while not self.stateStack.isEmpty():
            varState = self.stateStack.pop()
            try:
                self._nextVarState(varState)
                break
            except StopIteration:
                pass

        return retNext

    def _buildNext(self):
        varState = self.stateStack.peek()
        return varState.acc\
            .cloneAndAdd(varState.var, varState.value)

    def _nextVarState(self, varState):
        value = next(varState.valuesIterator)
        self.stateStack.push(self.VarState(
            index=varState.index,
            var=varState.var,
            valuesIterator=varState.valuesIterator,
            value=value,
            acc=varState.acc,
        ))

        if varState.index + 1 < len(self.descriptorsList):
            self._pushVars(
                varState.index + 1,
                varState.acc.cloneAndAdd(varState.var, value)
            )


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
        labels = set()
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


def transition_system_from_program_graph(pg, vars, labels, labelsIsMap=False):
    return TransitionSystemFromProgramGraphConvertor(
        programGraph=ProgramGraph(pg),
        varDescriptors=vars,
        conditionLabels=labels
    ).convert(labelsIsMap=labelsIsMap)


def main():
    pass


if __name__ == '__main__':
    main()
