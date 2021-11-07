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


class DfsRun:
    def __init__(self, graph, max_depth = None):
        self.graph = graph
        self.max_depth = max_depth

        self.stack = []
        self.vertices_states = {}
        self.reached_max_depth = False
        self.found_vertex = None
        self.result = None
        self._add_start_vertices()

    def end_run(self):
        raise StopIteration

    def get_result(self):
        return self.result
    def set_result(self, result):
        self.result = result

    def on_visit_start(self, v):
        pass

    def on_back_edge(self, u, v):
        pass

    def __next__(self):
        if len(self.stack) == 0:
            self.end_run()

        path_state = self.stack.pop()
        v_current = path_state.v

        # print(f"{v_current}, {path_state.depth}")
        if v_current in self.vertices_states:
            continue
        else:
            self.vertices_states[v_current] = DfsVertexState(v_current)


    def _run_loop(self):
        while len(self.stack) > 0:
            path_state = self.stack.pop()
            v_current = path_state.v

            # print(f"{v_current}, {path_state.depth}")
            if v_current in self.vertices_states:
                continue
            else:
                self.vertices_states[v_current] = DfsVertexState(v_current)

            self.on_visit_start(v_current)
            if self.should_end_run:
                break

            if self.max_depth is not None and path_state.depth == self.max_depth:
                reached_max_depth = True
                continue

            try:
                v_next = next(path_state.neighbors_iter)
                self.stack.append(path_state)
                # print(f"{v_current} -> {v_next}")
                if v_next in self.vertices_states:
                    continue
                # stack.append(DfsPathState(v_next, iter(graph.neighbors_of(v_next)), path_state.depth + 1))
            except StopIteration:
                # we're done with this vertex
                pass

    def _add_start_vertices(self):
        for s in self.graph.start_vertices():
            self.stack.append(DfsPathState(s, iter(self.graph.neighbors_of(s)), 0))


class Dfs:
    def __init__(self, graph, max_depth = None):
        self.graph = graph
        self.max_depth = max_depth

    def run_iter(self):
        return DfsRun(self.graph, self.max_depth)

    def run(self):
        dfsRun = self.run_iter()
        while True:
            try:
                current = next(dfsRun)
            except StopIteration:
                break
        return dfsRun.get_result()

    def __iter__(self):
        return self.run_iter()


def dfs_find_one(graph, predicate, max_depth = None):
    stack = []
    vertices_states = {}
    reached_max_depth = False
    found_vertex = None

    for s in graph.start_vertices():
        stack.append(DfsPathState(s, iter(graph.neighbors_of(s)), 0))

    while len(stack) > 0:
        path_state = stack.pop()
        v_current = path_state.v

        # print(f"{v_current}, {path_state.depth}")
        if predicate(v_current):
            found_vertex = v_current
            break
        vertices_states[v_current] = DfsVertexState(v_current)

        if max_depth is not None and path_state.depth == max_depth:
            reached_max_depth = True
            continue

        try:
            v_next = next(path_state.neighbors_iter)
            stack.append(path_state)
            # print(f"{v_current} -> {v_next}")
            if v_next in vertices_states:
                continue
            stack.append(DfsPathState(v_next, iter(graph.neighbors_of(v_next)), path_state.depth + 1))
        except StopIteration:
            # we're done with this vertex
            pass

    return found_vertex, reached_max_depth


def dfid_find_one(graph, predicate):
    max_depth = 0
    result = None
    while True:
        # print(f"dfs run, max depth = {max_depth}")
        v, reached_max_depth = dfs_find_one(graph, predicate, max_depth=max_depth)
        if v is not None:
            result = v
            break
        if not reached_max_depth:
            break
        max_depth = max_depth + 1
    return result


def property0(ts):
    l_func = ts["L"]
    return dfid_find_one(TSGraph(ts), lambda s: {"crit1", "crit2"}.issubset(l_func(s))) is not None


def property1(ts):
    l_func = ts["L"]
    return dfid_find_one(TSGraph(ts), lambda s: {"even", "prime"}.issubset(l_func(s))) is None


def property2(ts):
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
    print(f"found: {dfid_find_one(tsgraph, lambda x: 'q' in TS['L'](x))}")


if __name__ == '__main__':
    # test_graph()
    pass
