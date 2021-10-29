class Graph:
    def vertices(self):
        raise NotImplementedError("Abstract method")

    def start_vertices(self):
        raise NotImplementedError("Abstract method")

    def neighbors_of(self, v):
        raise NotImplementedError("Abstract method")


class TSGraph(Graph):
    def __init__(self, ts):
        self.ts = ts

    def vertices(self):
        return self.ts["S"]

    def start_vertices(self):
        return self.ts["I"]

    def neighbors_of(self, v):
        return {t for (s, act, t) in self.ts["to"] if s == v}


class DfsPathState:
    def __init__(self, v, neighbors_iter, depth):
        self.v = v
        self.neighbors_iter = neighbors_iter
        self.depth = depth


class DfsVertexState:
    def __init__(self, v):
        self.v = v


def dfs_find_one(graph, predicate, max_depth = None):
    dfs_stack = []
    vertices_states = {}

    for s in graph.start_vertices():
        dfs_stack.append(DfsPathState(s, iter(graph.neighbors_of(s)), 0))

    while len(dfs_stack) > 0:
        path_state = dfs_stack.pop()
        v_current = path_state.v

        if max_depth is not None and path_state.depth > max_depth:
            continue
        print(f"{v_current}, {path_state.depth}")
        if predicate(v_current):
            return v_current
        vertices_states[v_current] = DfsVertexState(v_current)

        try:
            v_next = next(path_state.neighbors_iter)
            dfs_stack.append(path_state)
            print(f"{v_current} -> {v_next}")
            if v_next in vertices_states:
                continue
            dfs_stack.append(DfsPathState(v_next, iter(graph.neighbors_of(v_next)), path_state.depth + 1))
        except StopIteration:
            # we're done with this vertex
            pass

    return None


def property0(ts):
    pass


def test_graph():
    TS = {
        "S": {"s1", "s2", "s3"},
        "I": {"s1"},
        "Act": {"a", "b", "c"},
        "to": {("s1", "a", "s2"), ("s1", "a", "s1"), ("s1", "b", "s2"),
               ("s2", "c", "s3"), ("s3", "c", "s1")},
        "AP": {"p", "q"},
        "L": lambda s: {"p"} if s == "s1" else {"p", "q"} if s == "s2" else {}
    }
    tsgraph = TSGraph(TS)
    print(f"V: {tsgraph.vertices()}")
    print(f"S: {tsgraph.start_vertices()}")
    for v in tsgraph.vertices():
        print(f"E({v}) -> {tsgraph.neighbors_of(v)}")

    print()
    dfs_find_one(tsgraph, lambda x: False)


if __name__ == '__main__':
    test_graph()
