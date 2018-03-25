from itertools import chain


class Cell:
    def __init__(self, x=0, y=0, ori=True, pos=None):
        self.x, self.y, self.o = pos or (x, y, ori)

    def __repr__(self):
        return f'Cell(x={self.x}, y={self.y}, o={self.o})'

    def __add__(self, rhs):
        return Cell(self.x + rhs[0], self.y + rhs[1], self.o)

    def n(self, rhs):
        return Cell(self.x + rhs[0], self.y + rhs[1], not self.o)

    def tuple(self):
        return (self.x, self.x, self.o)

    def __eq__(self, rhs):
        return self.x == rhs.x and self.y == rhs.y and self.o == rhs.o

    def __hash__(self):
        return hash(self.tuple())

    def __lt__(self, rhs):
        return self.x < rhs.x if self.x != rhs.x else self.y < rhs.y if self.y != rhs.y else self.o > rhs.o

    def __getitem__(self, index):
        if index == 0: return self.x
        elif index == 1: return self.y
        elif index == 2: return self.o
        else: raise ValueError


class Polyhex:

    UP_DIRECTIONS =   [(0, 0), (0, -1), (-1, 0)]
    DOWN_DIRECTIONS = [(0, 0), (0,  1), ( 1, 0)]

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
        if cell.o:
            return [cell.n(direction) for direction in self.UP_DIRECTIONS if cell.n(direction) in self]
        else:
            return [cell.n(direction) for direction in self.DOWN_DIRECTIONS if cell.n(direction) in self]

    def degree(self, cell):
        return sum(int(neighbor in self) for neighbor in self.neighbors(cell))

    def is_leaf(self, cell):
        return self.degree(cell) == 1

    def get_all_rooted_polyhexes(self):
        for leaf in self.leaves:
            if leaf.o:
                for direction in self.UP_DIRECTIONS:
                    if leaf.n(direction) in self:
                        yield RootedPolyhex(self, leaf, direction)
            else:
                for direction in self.DOWN_DIRECTIONS:
                    if leaf.n(direction) in self:
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
    
    def to_tex(self):
        rtn = r'''\documentclass[tikz, crop]{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usepackage{xcolor}
\definecolor{coldeg1}{HTML}{a3be8c}
\definecolor{coldeg2}{HTML}{ebcb8b}
\definecolor{coldeg3}{HTML}{88c0d0}
\definecolor{coldeg4}{HTML}{d08770}
\definecolor{coldeg5}{HTML}{b48ead}
\definecolor{coldeg6}{HTML}{BF616A}

  \newcommand\tricell[4]{
    \begin{scope}[
      scale = 0.3, 
      xshift = #1 cm * 0.866,
      yshift = 1.5 * #2 cm - (#3 - 1) * 0.25 cm,
    ] 
      \draw[fill=#4] (-30*#3:1cm) -- (90*#3:1cm) -- (210*#3:1cm) -- cycle; 
    \end{scope}
  }
  \newcommand\triupleaf[2]{
    \tricell{#1}{#2}1{coldeg1}
  }
  \newcommand\tridownleaf[2]{
    \tricell{#1}{#2}{-1}{coldeg1}
  }
  \newcommand\triupint[2]{
    \tricell{#1}{#2}1{coldeg3}
  }
  \newcommand\tridownint[2]{
    \tricell{#1}{#2}{-1}{coldeg3}
  }
  \newcommand\triuptwo[2]{
    \tricell{#1}{#2}{1}{coldeg2}
  }
  \newcommand\tridowntwo[2]{
    \tricell{#1}{#2}{-1}{coldeg2}
  }
\begin{document}
\begin{tikzpicture}
'''
        for cell in self:
            if self.degree(cell) == 1:
                if cell.o:
                    rtn += '\\triupleaf{' + str(cell.x*2 + cell.y) + '}{' + str(cell.y) + '}\n'
                else:
                    rtn += '\\tridownleaf{' + str(cell.x*2 + cell.y + 1 - int(cell.o)) + '}{' + str(cell.y) + '}\n'
            if self.degree(cell) == 2:
                if cell.o:
                    rtn += '\\triuptwo{' + str(cell.x*2 + cell.y) + '}{' + str(cell.y) + '}\n'
                else:
                    rtn += '\\tridowntwo{' + str(cell.x*2 + cell.y + 1 - int(cell.o)) + '}{' + str(cell.y) + '}\n'
            if self.degree(cell) == 3:
                if cell.o:
                    rtn += '\\triupint{' + str(cell.x*2 + cell.y) + '}{' + str(cell.y) + '}\n'
                else:
                    rtn += '\\tridownint{' + str(cell.x*2 + cell.y + 1 - int(cell.o)) + '}{' + str(cell.y) + '}\n'
        rtn += r'''
    \end{tikzpicture}
    \end{document}
    '''
        return rtn

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
        directions = self.UP_DIRECTIONS if deg2.o else self.DOWN_DIRECTIONS
        for dir in directions:
            if deg2.n(dir) in self:
                dir1 = dir
        for dir in directions:
            if deg2.n(dir) in self and dir != dir1:
                dir2 = dir
        rtn = []
        for dir in (dir1, dir2):
            visited = []
            to_visit = [deg2.n(dir)]
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
        if self.direction[0] != -rhs.direction[0] or self.direction[1] != -rhs.direction[1] or self.cell.o == rhs.cell.o:
            return None
        translation_vector = (self.cell.x - rhs.cell.x + self.direction[0],
                              self.cell.y - rhs.cell.y + self.direction[1])
        union = Polyhex(self.polyhex)
        for cell in rhs.polyhex.translate(translation_vector):
            union.append(cell)
        return union.min_trans().sort() if union.is_tree and len(union) == len(self.polyhex) + len(rhs.polyhex) - 2 else None
    
