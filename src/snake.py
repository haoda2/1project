"""Simple terminal-based Snake game using curses.

Run the game with ``python -m src.snake``.

Controls:
    Arrow keys - move the snake
    q          - quit the game

The game ends if the snake collides with itself or the wall.
"""
from __future__ import annotations

import curses
import random
from dataclasses import dataclass
from typing import Deque, Tuple
from collections import deque

Position = Tuple[int, int]


@dataclass
class Snake:
    body: Deque[Position]
    direction: Position

    def move(self, grow: bool = False) -> Position:
        """Move the snake in the current direction.

        If ``grow`` is False, the tail segment is removed after moving.
        """
        head_y, head_x = self.body[0]
        delta_y, delta_x = self.direction
        new_head = (head_y + delta_y, head_x + delta_x)
        self.body.appendleft(new_head)
        if not grow:
            self.body.pop()
        return new_head

    def change_direction(self, new_direction: Position) -> None:
        """Change the snake's direction if not directly opposite."""
        curr_y, curr_x = self.direction
        new_y, new_x = new_direction
        if (curr_y + new_y, curr_x + new_x) != (0, 0):
            self.direction = new_direction

    def collides_with(self, position: Position) -> bool:
        return position in self.body


class Game:
    height: int
    width: int
    snake: Snake
    food: Position
    score: int

    def __init__(self, height: int, width: int) -> None:
        self.height = height
        self.width = width

        mid_y, mid_x = height // 2, width // 2
        body: Deque[Position] = deque(
            [(mid_y, mid_x + i) for i in range(3)]
        )  # snake starts moving left
        self.snake = Snake(body=body, direction=(0, -1))
        self.score = 0
        self.food = self._spawn_food()

    def _spawn_food(self) -> Position:
        """Generate a random food position not overlapping the snake."""
        available = {
            (y, x)
            for y in range(1, self.height - 1)
            for x in range(1, self.width - 1)
        } - set(self.snake.body)

        if not available:
            raise RuntimeError("No space left to place food.")

        return random.choice(tuple(available))

    def update(self) -> bool:
        """Advance game state. Returns False if game over."""
        next_head = (
            self.snake.body[0][0] + self.snake.direction[0],
            self.snake.body[0][1] + self.snake.direction[1],
        )

        # Check collisions with walls
        if (
            next_head[0] <= 0
            or next_head[0] >= self.height - 1
            or next_head[1] <= 0
            or next_head[1] >= self.width - 1
        ):
            return False

        growing = next_head == self.food
        # When not growing, the tail will move away, so ignore it for collision detection.
        body_to_check = list(self.snake.body)
        if not growing and body_to_check:
            body_to_check.pop()
        if next_head in body_to_check:
            return False

        self.snake.move(grow=growing)
        if growing:
            self.score += 1
            self.food = self._spawn_food()

        return True

    def render(self, window: "curses.window") -> None:
        window.clear()
        window.border()
        # Draw food
        food_y, food_x = self.food
        window.addch(food_y, food_x, "@")

        # Draw snake
        for idx, (y, x) in enumerate(self.snake.body):
            ch = "O" if idx == 0 else "o"
            window.addch(y, x, ch)

        window.addstr(0, 2, f" Score: {self.score} ")
        window.refresh()


def _game_loop(window: "curses.window", height: int, width: int) -> None:
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    window.nodelay(True)
    window.timeout(100)

    game = Game(height, width)
    direction_map = {
        curses.KEY_UP: (-1, 0),
        curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1),
        curses.KEY_RIGHT: (0, 1),
    }

    while True:
        game.render(window)
        key = window.getch()
        if key in direction_map:
            game.snake.change_direction(direction_map[key])
        elif key in (ord("q"), ord("Q")):
            break

        if not game.update():
            msg = " Game Over! Press q to exit "
            window.addstr(height // 2, (width - len(msg)) // 2, msg)
            window.refresh()
            while True:
                key = window.getch()
                if key in (ord("q"), ord("Q")):
                    return
        curses.napms(80)


def main(stdscr: "curses.window") -> None:
    min_height, min_width = 20, 40
    height, width = stdscr.getmaxyx()

    if height < min_height or width < min_width:
        stdscr.nodelay(False)
        stdscr.clear()
        warning = (
            f"终端窗口太小 (当前 {width}x{height})，\n"
            f"请调整到至少 {min_width}x{min_height} 后按任意键退出。"
        )
        for idx, line in enumerate(warning.splitlines()):
            stdscr.addstr(idx + 1, 1, line[: max(1, width - 2)])
        stdscr.refresh()
        stdscr.getch()
        return

    play_window = curses.newwin(height, width, 0, 0)
    _game_loop(play_window, height, width)


if __name__ == "__main__":
    curses.wrapper(main)
