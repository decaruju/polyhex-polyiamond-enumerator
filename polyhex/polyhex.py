from itertools import chain

class Cell:
    def __init__(self, x=0, y=0, pos=None):
        self.x, self.y = pos or (x, y)

    def __repr__(self):
        return f'Cell(x={self.x}, y={self.y})'

    def __add__(self, rhs):
        return Cell(self.x + rhs[0], self.y + rhs[1])

    def __mul__(self, rhs):
        return Cell(rhs * self.x, rhs * self.y)

    def __rmul__(self, lhs):
        return lhs * self

    def tuple(self):
        return (self.x, self.x)

    def __eq__(self, rhs):
        return self.x == rhs.x and self.y == rhs.y

    def __hash__(self):
        return hash(self.tuple())


    def __lt__(self, rhs):
        return self.x < rhs.x if self.x != rhs.x else self.y < rhs.y

    def __getitem__(self, index):
        if index == 0: return self.x
        elif index == 1: return self.y
        else: raise ValueError

class Polyhex:

    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)]

    def __init__(self, cells):
        self._cells = list(cells)

    def __repr__(self):
        return ', '.join(repr(cell) for cell in self)

    def __contains__(self, cell):
        return cell in self._cells

    def __iter__(self):
        for cell in self._cells:
            yield cell
    
    def __len__(self):
        return len(self._cells)

    def neighbors(self, cell):
        return [cell + direction for direction in self.DIRECTIONS if cell + direction in self]

    def degree(self, cell):
        return sum(int(neighbor in self) for neighbor in self.neighbors(cell))

    def is_leaf(self, cell):
        return self.degree(cell) == 1

    def get_all_rooted_polyhexes(self):
        for leaf in self.leaves:
            for direction in self.DIRECTIONS:
                if leaf+direction in self:
                    yield RootedPolyhex(self, leaf, direction)

    @property
    def leaves(self):
        return [cell for cell in self if self.is_leaf(cell)]

    def append(self, cell):
        if cell not in self:
            self._cells.append(cell)

    def translate(self, direction):
        return Polyhex([cell + direction for cell in self])

    def min_trans(self):
        min_x = min(cell.x for cell in self)
        min_y = min(cell.y for cell in self)
        return self.translate((-min_x, -min_y))

    def __hash__(self):
        return hash(tuple(cell for cell in self))

    def sort(self):
        self._cells.sort()
        return self

    @property
    def is_tree(self):
        return self.is_connected and not self.has_cycle

    @property
    def is_connected(self):
        cells = list(self._cells)
        visited = []
        to_visit = [cells[0]]
        while len(to_visit) > 0:
            cur_cell = to_visit.pop()
            visited.append(cur_cell)
            to_visit.extend(neighbor for neighbor in self.neighbors(cur_cell) if neighbor not in visited)
        rtn = all(cell in cells for cell in visited)
        return rtn

    @property
    def degs(self):
        deg2 = [c for c in self if self.degree(c) == 2][0]
        for dir in self.DIRECTIONS:
            if deg2 + dir in self:
                dir1 = dir
        for dir in self.DIRECTIONS:
            if deg2 + dir in self and dir != dir1:
                dir2 = dir
        rtn = []
        for dir in (dir1, dir2):
            visited = []
            to_visit = [deg2 + dir]
            while len(to_visit) > 0:
                cur_cell = to_visit.pop()
                if self.degree(cur_cell) == 1:
                    continue
                visited.append(cur_cell)
                to_visit.extend(neighbor for neighbor in self.neighbors(cur_cell) if neighbor != deg2 and neighbor not in visited)
            rtn.append(len(visited))
        rtn.sort()
        return tuple(rtn)

    @property
    def has_cycle(self):
        cells = list(self._cells)
        visited = []
        to_visit = [cells[0]]
        while len(to_visit) > 0:
            cur_cell = to_visit.pop()
            visited.append(cur_cell)
            neighbors = self.neighbors(cur_cell)
            next_cells = [neighbor for neighbor in neighbors if neighbor not in visited]
            to_visit.extend(next_cells)
            if len(neighbors) - len(next_cells) > 1:
                return True
        return False

class RootedPolyhex:
    def __init__(self, polyhex, cell, direction):
        self.polyhex = polyhex
        self.cell = cell
        self.direction = direction

    def __repr__(self):
        return f'RPX(polyhex={self.polyhex}, cell={self.cell}, direction={self.direction})'

    def __add__(self, rhs):
        if self.direction[0] != -rhs.direction[0] or self.direction[1] != -rhs.direction[1]:
            return None
        translation_vector = (self.cell.x - rhs.cell.x + self.direction[0],
                              self.cell.y - rhs.cell.y + self.direction[1])
        union = Polyhex(self.polyhex)
        for cell in rhs.polyhex.translate(translation_vector):
            union.append(cell)
        return union.min_trans().sort() if union.is_tree else None
    
