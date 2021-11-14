import pprint

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


class HashableDictBuilder(dict):
    def build(self):
        return frozenset(self.items())

    def cloneAndAdd(self, key, value):
        clone = self.clone_shallow()
        clone[key] = value
        return clone

    def clone_shallow(self):
        return HashableDictBuilder(self)


class AllStartValuesIterator:
    def __init__(self, varDescriptors):
        self.varDescriptorsList = list(varDescriptors.items())
        self.stateStack: Stack = Stack()

        self.pushVars(0, HashableDictBuilder())

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

    def pushVars(self, index_start, acc_start):
        acc = acc_start
        for i in range(index_start, len(self.varDescriptorsList)):
            self.pushVar(i, acc)

            # We "pushed" but the stack is empty?
            # That must be because the var has no values.
            if self.stateStack.isEmpty():
                break

    def pushVar(self, i, acc):
        var, possibleValues = self.varDescriptorsList[i]
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

        retNext = self.buildNext()
        while self.stateStack.hasItems():
            varState = self.stateStack.pop()
            try:
                self.nextVarState(varState)
                break
            except StopIteration:
                pass

        return retNext

    def buildNext(self):
        varState = self.stateStack.peek()
        return varState.acc\
            .cloneAndAdd(varState.var, varState.value)\
            .build()

    def nextVarState(self, varState):
        value = next(varState.valuesIterator)
        self.stateStack.push(self.VarState(
            index=varState.index,
            var=varState.var,
            valuesIterator=varState.valuesIterator,
            value=value,
            acc=varState.acc,
        ))

        if varState.index + 1 < len(self.varDescriptorsList):
            self.pushVars(
                varState.index + 1,
                varState.acc.cloneAndAdd(varState.var, value)
            )



class AllStartValues:
    def __init__(self, vars):
        self.vars = vars

    def __iter__(self):
        return AllStartValuesIterator(self.vars)


class TransitionSystemFromLogicCircuitConvertor:
    def __init__(self, logicCircuit):
        self.logicCircuit = logicCircuit

        self.stateLabelsMap = {}
        self.states_start = set()
        self.act = set()
        self.to = set()
        self.ap = set()

        self._initFromAllInputValues()
        self._initAp()

    def convert(self):
        self._convert_allStartStates()
        return self._buildTransitionSystem()

    def _convert_allStartStates(self):
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

    def _initFromAllInputValues(self):
        self._registerAllZeros = (False,) * self.logicCircuit.registersAmount
        AllStartValuesIterator(self.logicCircuit.inputsAmount, self._onInputValue).enumerate()

    def _onInputValue(self, inputValue):
        inputValue = tuple(inputValue)
        self.states_start.add(self._registerAllZeros + inputValue)
        self.act.add(inputValue)

    def _initAp(self):
        self._appendApSymbols(self.logicCircuit.registersAmount, 'r')
        self._appendApSymbols(self.logicCircuit.inputsAmount, 'x')
        self._appendApSymbols(self.logicCircuit.outputsAmount, 'y')

    def _appendApSymbols(self, count, symbol):
        for i in range(1, count + 1):
            self.ap.add(f'{symbol}{i}')


def main():
    pass


if __name__ == '__main__':
    main()
