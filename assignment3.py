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

    def hasItems(self):
        return len(self.stack) > 0

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
        while self.stateStack.hasItems():
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

    def convert(self):
        self._initConvert()
        self._convert_fromAllStartStates()
        return self._buildTransitionSystem()

    def _convert_fromAllStartStates(self):
        for startState in self.states_start:
            if startState in self.stateLabelsMap:
                continue

            self._convert_fromStartState(startState)

    def _buildTransitionSystem(self):
        return {
            'S': set(self.stateLabelsMap.keys()),
            'I': self.states_start,
            'Act': self.act,
            'to': self.to,
            'AP': self.ap,
            'L': self.buildL(self.stateLabelsMap)
        }

    @staticmethod
    def buildL(labelsMap):
        def L(s):
            return labelsMap[s]
        return L

    def _convert_fromStartState(self, startState):
        statesLeftStack = [startState]
        while len(statesLeftStack) > 0:
            state = statesLeftStack.pop()

            outputValues = self.logicCircuit.computeOutputValues(state)
            newRegisterValues = self.logicCircuit.computeNewRegisterValues(state)

            self.stateLabelsMap[state] = self._convert_computeLabels(state, outputValues)
            self._convert_appendTransitions(state, newRegisterValues, statesLeftStack)

    def _convert_computeLabels(self, state, outputValues):
        labels = set()
        offset = 0
        offset = self._convert_computeLabels_appendLabelsFromTuplePart(
            labels, state,
            offset=offset, symbol='r', count=self.logicCircuit.registersAmount
        )
        offset = self._convert_computeLabels_appendLabelsFromTuplePart(
            labels, state,
            offset=offset, symbol='x', count=self.logicCircuit.inputsAmount
        )
        self._convert_computeLabels_appendLabelsFromTuplePart(
            labels, outputValues,
            offset=0, symbol='y', count=len(outputValues)
        )
        return labels

    @staticmethod
    def _convert_computeLabels_appendLabelsFromTuplePart(labels, state, offset, symbol, count):
        for i in range(0, count):
            if state[i + offset]:
                labels.add(f'{symbol}{i + 1}')
        return count + offset

    def _convert_appendTransitions(self, state, newRegisterValues, statesLeftStack):
        for act in self.act:
            followingState = newRegisterValues + act
            self.to.add((state, act, followingState,))
            if followingState not in self.stateLabelsMap:
                statesLeftStack.append(followingState)
                self.stateLabelsMap[followingState] = None

    def initConvert(self):
        self._initConvert()

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


def transition_system_from_program_graph(pg, vars, labels):
    return TransitionSystemFromProgramGraphConvertor(
        programGraph=ProgramGraph(pg),
        varDescriptors=vars,
        conditionLabels=labels
    ).convert()


def main():
    pass


if __name__ == '__main__':
    main()
