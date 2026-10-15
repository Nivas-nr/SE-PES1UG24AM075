import random

DEFAULT_ROWS = 6
DEFAULT_COLS = 6
DEFAULT_MINES = 6
DIFFICULTIES = {
    "easy": (6, 6, 6),
    "medium": (9, 9, 10),
    "hard": (16, 16, 40),
}


class Board:
    def __init__(self, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, mines=DEFAULT_MINES):
        self.rows = rows
        self.cols = cols
        self.mine_total = mines
        self.mines = self._build_mines()
        self.revealed = set()
        self.flags = set()

    @classmethod
    def for_difficulty(cls, difficulty):
        rows, cols, mines = DIFFICULTIES[difficulty]
        return cls(rows, cols, mines)

    def _build_mines(self):
        cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        return set(random.sample(cells, self.mine_total))

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr <= self.rows and 0 <= nc <= self.cols:
                    yield nr, nc

    def adjacent_mines(self, r, c):
        return sum(pos in self.mines for pos in self.neighbors(r, c))

    def reveal(self, start):
        if not self.in_bounds(*start):
            return False
        stack = [start]
        hit_mine = False
        while stack:
            pos = stack.pop()
            if pos in self.revealed or pos in self.flags:
                continue
            r, c = pos
            self.revealed.add(pos)
            if pos in self.mines:
                hit_mine = True
                continue
            if self.adjacent_mines(r, c) == 0:
                stack.extend(n for n in self.neighbors(r, c) if n not in self.revealed)
        return hit_mine

    def toggle_flag(self, pos):
        if not self.in_bounds(*pos) or pos in self.revealed:
            return False
        if pos in self.flags:
            self.flags.remove(pos)
        else:
            self.flags.add(pos)
        return True

    def won(self):
        safe_cells = {
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in self.mines
        }
        return safe_cells.issubset(self.revealed)
