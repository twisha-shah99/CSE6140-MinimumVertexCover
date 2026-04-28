import time
import sys
sys.setrecursionlimit(100000)



class Timer:
    def __init__(self, cutoff: float) -> None:
        self.start = time.perf_counter()
        self.cutoff = cutoff

    def elapsed(self) -> float:
        return time.perf_counter() - self.start

    def expired(self) -> bool:
        return self.elapsed() >= self.cutoff


class Trace:
    def __init__(self) -> None:
        self.rows: list[tuple[float, int]] = []

    def add(self, timestamp: float, size: int) -> None:
        if self.rows and size >= self.rows[-1][1]:
            return
        self.rows.append((timestamp, size))


class Graph:
    def __init__(self, n: int, edges: list[tuple[int, int]]) -> None:
        self.n = n
        self.edges = [(u - 1, v - 1) for u, v in edges]
        self.adj_vertices: list[list[int]] = [[] for _ in range(n)]
        for u, v in self.edges:
            if not (0 <= u < n and 0 <= v < n):
                raise ValueError("vertex index out of range")
            if u == v:
                raise ValueError("self-loops are not supported")
            self.adj_vertices[u].append(v)
            self.adj_vertices[v].append(u)

    @property
    def m(self) -> int:
        return len(self.edges)


class BranchAndBoundSolver:
    def __init__(self, graph: Graph, timer: Timer, trace: Trace, incumbent: list[bool]) -> None:
        self.graph = graph
        self.timer = timer
        self.trace = trace
        self.active = [True] * graph.n
        self.in_cover = [False] * graph.n
        self.degrees = [len(neighbors) for neighbors in graph.adj_vertices]
        self.cover_size = 0
        self.edge_count = graph.m
        self.best_cover = incumbent[:]
        self.best_size = sum(incumbent)

    def solve(self) -> list[bool]:
        self._search(list(range(self.graph.n)))
        return self.best_cover

    def _search(self, seeds: list[int]) -> None:
        if self.timer.expired():
            return

        changes: list[tuple[int, bool, list[int]]] = []
        self._reduce_state(changes, seeds)
        if self.timer.expired():
            self._undo(changes)
            return

        if self.edge_count == 0:
            self._update_best()
            self._undo(changes)
            return

        if self.cover_size >= self.best_size:
            self._undo(changes)
            return

        if self.cover_size + self._matching_lower_bound() >= self.best_size:
            self._undo(changes)
            return

        u, v = self._choose_branch_edge()
        if self.degrees[v] > self.degrees[u]:
            u, v = v, u

        for branch_vertex in (u, v):
            if self.timer.expired():
                break
            branch_changes: list[tuple[int, bool, list[int]]] = []
            touched = self._include_vertex(branch_vertex, branch_changes)
            self._search(touched)
            self._undo(branch_changes)

        self._undo(changes)

    def _update_best(self) -> None:
        if self.cover_size >= self.best_size:
            return
        self.best_size = self.cover_size
        self.best_cover = self.in_cover[:]
        self.trace.add(self.timer.elapsed(), self.best_size)

    def _reduce_state(self, changes: list[tuple[int, bool, list[int]]], seeds: list[int]) -> None:
        pending = list(seeds)
        scheduled = set(pending)
        while pending and not self.timer.expired():
            vertex = pending.pop()
            scheduled.discard(vertex)
            if not self.active[vertex]:
                continue

            degree = self.degrees[vertex]
            if degree == 0:
                self._remove_vertex(vertex, False, changes)
                continue

            if degree == 1:
                neighbor = self._first_active_neighbor(vertex)
                touched = self._include_vertex(neighbor, changes)
                for other in touched:
                    if self.active[other] and other not in scheduled:
                        pending.append(other)
                        scheduled.add(other)

    def _matching_lower_bound(self) -> int:
        matched = [False] * self.graph.n
        size = 0
        for vertex in range(self.graph.n):
            if not self.active[vertex] or matched[vertex] or self.degrees[vertex] == 0:
                continue
            for neighbor in self.graph.adj_vertices[vertex]:
                if self.active[neighbor] and not matched[neighbor]:
                    matched[vertex] = True
                    matched[neighbor] = True
                    size += 1
                    break
        return size

    def _choose_branch_edge(self) -> tuple[int, int]:
        pivot = -1
        pivot_degree = -1
        for vertex in range(self.graph.n):
            if self.active[vertex] and self.degrees[vertex] > pivot_degree:
                pivot = vertex
                pivot_degree = self.degrees[vertex]
        if pivot_degree <= 0:
            raise RuntimeError("invalid branch state")

        neighbor = -1
        neighbor_degree = -1
        for other in self.graph.adj_vertices[pivot]:
            if self.active[other] and self.degrees[other] > neighbor_degree:
                neighbor = other
                neighbor_degree = self.degrees[other]
        if neighbor == -1:
            raise RuntimeError("failed to find uncovered edge")
        return pivot, neighbor

    def _first_active_neighbor(self, vertex: int) -> int:
        for neighbor in self.graph.adj_vertices[vertex]:
            if self.active[neighbor]:
                return neighbor
        raise RuntimeError("expected an active neighbor")

    def _include_vertex(self, vertex: int, changes: list[tuple[int, bool, list[int]]]) -> list[int]:
        return self._remove_vertex(vertex, True, changes)

    def _remove_vertex(self, vertex: int, add_to_cover: bool, changes: list[tuple[int, bool, list[int]]]) -> list[int]:
        if not self.active[vertex]:
            return []

        touched = [neighbor for neighbor in self.graph.adj_vertices[vertex] if self.active[neighbor]]
        self.active[vertex] = False
        if add_to_cover:
            self.in_cover[vertex] = True
            self.cover_size += 1

        self.edge_count -= len(touched)
        self.degrees[vertex] = 0
        for neighbor in touched:
            self.degrees[neighbor] -= 1

        changes.append((vertex, add_to_cover, touched))
        return touched

    def _undo(self, changes: list[tuple[int, bool, list[int]]]) -> None:
        while changes:
            vertex, add_to_cover, touched = changes.pop()
            self.active[vertex] = True
            self.degrees[vertex] = len(touched)
            self.edge_count += len(touched)
            for neighbor in touched:
                self.degrees[neighbor] += 1
            if add_to_cover:
                self.in_cover[vertex] = False
                self.cover_size -= 1


def solve(
    n: int,
    edges: list[tuple[int, int]],
    cutoff: float,
    initial_cover: list[int] | None = None,
) -> tuple[list[int], list[tuple[float, int]]]:
    graph = Graph(n, edges)
    timer = Timer(cutoff)
    trace = Trace()
    if initial_cover is None:
        incumbent = _initial_cover_from_matching(graph)
    else:
        incumbent = _cover_from_vertices(graph, initial_cover)
    trace.add(timer.elapsed(), sum(incumbent))
    cover = BranchAndBoundSolver(graph, timer, trace, incumbent).solve()
    _validate_cover(graph, cover)
    vertices = [vertex + 1 for vertex, in_cover in enumerate(cover) if in_cover]
    return vertices, trace.rows


def _cover_from_vertices(graph: Graph, vertices: list[int]) -> list[bool]:
    cover = [False] * graph.n
    for vertex in vertices:
        if not 1 <= vertex <= graph.n:
            raise ValueError("initial cover contains vertex index out of range")
        cover[vertex - 1] = True
    _validate_cover(graph, cover)
    return _prune_cover(graph, cover)


def _initial_cover_from_matching(graph: Graph) -> list[bool]:
    cover = [False] * graph.n
    matched = [False] * graph.n
    for u, v in graph.edges:
        if not matched[u] and not matched[v]:
            matched[u] = True
            matched[v] = True
            cover[u] = True
            cover[v] = True
    _validate_cover(graph, cover)
    return _prune_cover(graph, cover)


def _prune_cover(graph: Graph, cover: list[bool]) -> list[bool]:
    out = cover[:]
    changed = True
    while changed:
        changed = False
        for vertex in range(graph.n):
            if not out[vertex]:
                continue
            if all(out[neighbor] for neighbor in graph.adj_vertices[vertex]):
                out[vertex] = False
                changed = True
    return out


def _validate_cover(graph: Graph, cover: list[bool]) -> None:
    for u, v in graph.edges:
        if not cover[u] and not cover[v]:
            raise RuntimeError("invalid vertex cover")
