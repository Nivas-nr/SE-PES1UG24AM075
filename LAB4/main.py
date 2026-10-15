from board import DIFFICULTIES
from game import Minesweeper

if __name__ == "__main__":
    while True:
        difficulty = input("Difficulty (easy/medium/hard): ").strip().lower()
        if difficulty in DIFFICULTIES:
            break
        print("Choose easy, medium, or hard.")

    Minesweeper(difficulty).run()
