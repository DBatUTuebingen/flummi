WITH RECURSIVE
sudoku(board, blank, id) AS (
  SELECT s.cells, list_position(s.cells, 0)-1 AS blank, row_number() OVER () AS id
  FROM   sudoku AS s
      UNION ALL
  SELECT s.bd[1:s.b] || [fill] || s.bd[s.b+2:81] AS board,
         list_position(board, 0)-1               AS blank,
         id                                      AS id
  FROM  sudoku AS s(bd,b,id), generate_series(1,9) AS _(fill)
  WHERE s.b IS NOT NULl
    AND NOT EXISTS (
      SELECT NULL
      FROM   generate_series(1,9) AS __(o)
      WHERE  fill IN (s.bd[(s.b//9) * 9                            + o],
                      s.bd[s.b%9                                   + (o-1)*9 + 1],
                      s.bd[((s.b//3) % 3) * 3 + (s.b//27) * 27 + o + ((o-1)//3) * 6])
   )
)
SELECT {id: id, cells: board} FROM sudoku WHERE blank IS NULL;
