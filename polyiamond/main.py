from polyhex import Polyhex, Cell, RootedPolyhex
from pprint import pprint
from itertools import chain
from collections import Counter


def expected(n):
    rtn = 0
    if n == 0: rtn += 6
    if n == 1: rtn += 12
    if n == 3: rtn += 12
    if n == 4: rtn += 12
    if n >= 2: rtn += 24
    if n >= 3: rtn += 12
    if n >= 4: rtn += 12
    if n == 2: rtn += 6
    if n == 5: rtn += 12
    if n >= 3: rtn += 12
    if n >= 4: rtn += 12
    if n == 8: rtn += 6
    if n >= 6: rtn += 12
    if n >= 7: rtn += 12
    if n >= 4: rtn += 6*(n-3)
    if n >= 5: rtn += 12*(n-4)
    if n >= 6: rtn += 6*(n-5)
    return rtn

deg3s = (
         Polyhex([Cell(0, 0, True),  Cell(0, 0, False), Cell(-1, 0, False), Cell(0, -1, False)]), 
         Polyhex([Cell(0, 0, False), Cell(0, 0, True),  Cell( 1, 0, True),  Cell(0, 1, True)]),
        )
deg2s = (
         Polyhex([Cell(0, 0, True),  Cell(0, 0, False), Cell(-1, 0, False)]), 
         Polyhex([Cell(0, 0, True),  Cell(0, 0, False), Cell(0, -1, False)]), 
         Polyhex([Cell(0, 0, True), Cell(-1, 0, False), Cell(0, -1, False)]), 
         Polyhex([Cell(0, 0, False), Cell(0, 0, True),  Cell( 1, 0, True)]),
         Polyhex([Cell(0, 0, False), Cell(0, 0, True),  Cell(0, 1, True)]),
         Polyhex([Cell(0, 0, False),  Cell( 1, 0, True),  Cell(0, 1, True)]),
        )

sets = {}
sets[1] = set(chain(deg2s))
for i in range(2, 21):
    sets[i] = set()
    for cell1 in sets[i - 1]:
        for cell2 in deg3s:
            for gpx1 in Polyhex(cell1).get_all_rooted_polyhexes():
                for gpx2 in cell2.get_all_rooted_polyhexes():
                    union = gpx1 + gpx2
                    if union is not None:
                        sets[i].add(tuple(union))
    print(i, ':', len(sets[i]), expected(i-1))
    print(i, Counter(Polyhex(px).degs for px in sets[i]))
    verbose = False
    if verbose:
        for index, plx in enumerate(sets[i]):
            with open(f'fig/plx{i}-{index}.tex', 'w') as f:
                f.write(Polyhex(plx).to_tex())




