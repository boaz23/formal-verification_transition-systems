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
