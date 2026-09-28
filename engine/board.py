import random


class Board:
    def __init__(self, width=9, height=9, num_mines=10):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.mines = set()
        self.revealed = set()
        self.flagged = set()
        self.game_over = False
        self.won = False
        self._mines_placed = False

    def _place_mines(self, exclude):
        """Place mines randomly, avoiding the first-clicked cell."""
        all_cells = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) != exclude
        ]
        self.mines = set(random.sample(all_cells, self.num_mines))
        self._mines_placed = True

    def _neighbors(self, x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    yield (nx, ny)

    def _adjacent_mine_count(self, x, y):
        return sum(1 for n in self._neighbors(x, y) if n in self.mines)

    def reveal(self, x, y):
        if self.game_over or (x, y) in self.flagged:
            return

        if not self._mines_placed:
            self._place_mines(exclude=(x, y))

        if (x, y) in self.mines:
            self.revealed.add((x, y))
            self.game_over = True
            self.won = False
            return

        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in self.revealed:
                continue
            self.revealed.add((cx, cy))
            if self._adjacent_mine_count(cx, cy) == 0:
                for n in self._neighbors(cx, cy):
                    if n not in self.revealed and n not in self.flagged:
                        stack.append(n)

        self._check_win()

    def toggle_flag(self, x, y):
        if self.game_over or (x, y) in self.revealed:
            return
        if (x, y) in self.flagged:
            self.flagged.remove((x, y))
        else:
            self.flagged.add((x, y))

    def _check_win(self):
        total_cells = self.width * self.height
        if len(self.revealed) == total_cells - self.num_mines:
            self.game_over = True
            self.won = True
    def safe_moves(self):
        safe = set()
        for (x, y) in self.revealed:
            count = self._adjacent_mine_count(x, y)
            neighbors = list(self._neighbors(x, y))
            flagged_neighbors = [n for n in neighbors if n in self.flagged]
            hidden_neighbors = [
                n for n in neighbors
                if n not in self.revealed and n not in self.flagged
            ]
            if count == len(flagged_neighbors):
                safe.update(hidden_neighbors)
        return safe

    def encode(self):
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x, y) in self.flagged:
                    row.append("F")
                elif (x, y) in self.revealed:
                    if (x, y) in self.mines:
                        row.append("X")
                    else:
                        row.append(str(self._adjacent_mine_count(x, y)))
                else:
                    row.append(".")
            rows.append("".join(row))
        return "\n".join(rows)

    def state_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "board": self.encode(),
            "game_over": self.game_over,
            "won": self.won,
        }


if __name__ == "__main__":
    b = Board(width=5, height=5, num_mines=3)
    b.reveal(2, 2)
    print(b.encode())
    print("Safe moves:", b.safe_moves())