.read sudokus/setup.sql

INSERT INTO sudoku(cells)
  SELECT apply(split(replace(txt.content[:-2], E'\n', ''), ''), lambda c: if(c = '.', 0, c :: int))
  FROM   read_text('sudokus/crafted/*.txt') AS txt;
