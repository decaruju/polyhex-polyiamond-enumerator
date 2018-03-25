from polyhex import Polyhex, Cell, RootedPolyhex
from pprint import pprint
from itertools import chain
from collections import Counter

deg3s = (Polyhex([Cell(0, 0), Cell(1, 0),   Cell(0, 1),  Cell(-1, -1)]), 
         Polyhex([Cell(0, 0), Cell(-1, 0),  Cell(0, -1), Cell(1, 1)]))
deg2s = (Polyhex([Cell(0, 0), Cell(1, 0),   Cell(-1, 0)]), 
         Polyhex([Cell(0, 0), Cell(0, 1),   Cell(0, -1)]),
         Polyhex([Cell(0, 0), Cell(-1, -1), Cell(1, 1)]),
         Polyhex([Cell(0, 0), Cell(1, 0),   Cell(0, 1)]),
         Polyhex([Cell(0, 0), Cell(1, 0),   Cell(-1, -1)]),
         Polyhex([Cell(0, 0), Cell(0, 1),   Cell(-1, -1)]),
         Polyhex([Cell(0, 0), Cell(-1, 0),  Cell(0, -1)]),
         Polyhex([Cell(0, 0), Cell(-1, 0),  Cell(1, 1)]),
         Polyhex([Cell(0, 0), Cell(0, -1),  Cell(1, 1)]))

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
    print(i, ':', len(sets[i]))
    print(i, Counter(Polyhex(px).degs for px in sets[i]))


