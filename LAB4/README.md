# Scenario 13 — Minesweeper

A modular terminal Minesweeper game with hidden mines, reveal expansion, and flags.

## Objective

Inspect the supplied starter, understand how the modules interact, reproduce the
existing defect, and then extend the game through four tasks. The assignment is
designed to test debugging, reasoning about state, and careful review of LLM-generated code.

## Provided files

- `main.py` — entry point.
- `game.py` — command handling and game flow.
- `board.py` — board state, neighbours, mines, revealing, and flags.
- `requirements.txt` — dependency declaration.

## Setup

Use Python 3.9 or newer:

```bash
python main.py
```

No package installation is required.

## Before changing the code

Run the untouched starter, read all three Python files, play several turns, and trace
one reveal from the command line through the board logic. Reproduce the Task 1 defect
before attempting to fix it.

## Task 1 — Boundary-safe board traversal

Correct the neighbour traversal so every coordinate visited by reveal and mine-counting
logic is a valid board coordinate. Flood-fill must work correctly from corners, edges,
and interior cells without exceptions or phantom cells.

**Done when:** all valid reveals stay within the board and zero-adjacent regions expand
correctly from every edge and corner.

## Task 2 — Complete win and flag behaviour

Keep the existing flag command and make the game recognise a win only when every
non-mine cell has been revealed. Revealing a flagged cell must not accidentally change
its state.

**Done when:** flags can be toggled, invalid actions do not corrupt state, and a
complete safe reveal ends the game correctly.

## Task 3 — Difficulty modes

Add Easy, Medium, and Hard modes with different dimensions and mine counts. The mode
selection must happen in memory and must not require a new data file.

**Done when:** each mode produces a valid board and all existing commands continue to work.

## Task 4 — Action-level feedback

Add concise feedback for a player's reveal action. A single reveal that expands through
many zero cells should still count as one player action; internal flood-fill iterations
must not produce repeated player-facing feedback.

**Done when:** feedback is tied to actual commands, not internal loops.

## Required testing

Test corners, edges, centre cells, zero-adjacent regions, mine hits, repeated reveals,
flag toggling, invalid coordinates, invalid commands, every difficulty, and a complete win.


## LLM usage

You may use an LLM during the lab. The goal is to use it as a coding assistant while
retaining responsibility for understanding and testing the result.

- Inspect the existing code before asking for changes.
- Ask for explanations when you do not understand a proposed change.
- Test generated code against the stated behaviour and edge cases.
- Keep your complete LLM chat history for submission.
- Do not replace the whole project with an unrelated implementation.
- Keep all state in memory; do not add CSV, JSON, SQLite, or other persistence.

## Submission checklist

- [ ] Task 1 completed and the original defect was reproduced and fixed.
- [ ] Tasks 2–4 completed and tested.
- [ ] Boundary and invalid-input cases tested.
- [ ] No unnecessary external dependencies added.
- [ ] No persistent storage added.
- [ ] Code remains understandable and modular.
- [ ] Complete LLM chat-history link included.

## Folder structure

```text
scenario-01-minesweeper/
├── README.md
├── requirements.txt
├── main.py
├── game.py
└── board.py
```

## Submission Checklist

Submission is only the following three things:

- [ ] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [ ] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [ ] The Chat/LLM used page link, with the complete chat history
