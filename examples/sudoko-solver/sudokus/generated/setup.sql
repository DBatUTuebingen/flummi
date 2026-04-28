.read sudokus/setup.sql

INSERT INTO sudoku(cells)
  SELECT apply(split(puzzle, ''), lambda c: c :: int)
  FROM   read_csv('sudokus/generated/sudokus.csv') as _(puzzle);
