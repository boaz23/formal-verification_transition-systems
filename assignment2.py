class LogicCircuit:
    def __init__(self, numberOfInputs, numberOfRegisters, numberOfOutputs, updateRegisters, computeOutputs):
        self.inputsAmount = numberOfInputs
        self.registersAmount = numberOfRegisters
        self.outputsAmount = numberOfOutputs
        self.computeNewRegisterValues = updateRegisters
        self.computeOutputValues = computeOutputs


class AllInputValuesEnumerator:
    def __init__(self, inputsAmount, onInputValue):
        self.inputsAmount = inputsAmount
        self.onInputValue = onInputValue

    def enumerate(self):
        self._enumerateInputValues(self.inputsAmount, [])

    def _enumerateInputValues(self, remainingInputs, valueAcc):
        if remainingInputs == 0:
            self.onInputValue(valueAcc)
            return

        for boolValue in [True, False]:
            self._enumerateInputValues(remainingInputs - 1, valueAcc + [boolValue])


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
        AllInputValuesEnumerator(self.logicCircuit.inputsAmount, self._onInputValue).enumerate()

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


def transitionSystemFromCircuit(*args):
    return TransitionSystemFromLogicCircuitConvertor(LogicCircuit(*args)).convert()


def main():
    pass


if __name__ == '__main__':
    main()
