WITH RECURSIVE
  "%trampoline%"("%kind%", "%result%", "%label%", "poh0", "poh") AS (
    (
      SELECT 'control', NULL :: text, 'entry',
             (NULL) :: struct(label text, loc point) AS "poh0",
             (NULL) :: struct(label text, loc point) AS "poh"
    )
      UNION ALL -- recursive union!
    (
      WITH
        "entry"("%kind%", "%result%", "%label%", "poh0") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "poh0", "poh") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "poh0",
                     "poh"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'entry'
            )

          SELECT 'control', NULL, NULL,
                 (SELECT p FROM points AS p ORDER BY p.loc.x LIMIT 1) AS "new%poh0"
          FROM   "%sources%"
        ),
        "inter0"("%kind%", "%result%", "%label%", "poh0", "poh") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "poh0") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "poh0"
              FROM   "entry"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "poh0" AS "new%poh0",
                 ("poh0") AS "new%poh"
          FROM   "%sources%"
        ),
        "loop0_head"("%kind%", "%result%", "%label%", "poh0", "poh") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "poh0", "poh") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "poh0",
                     "poh"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop0_head'
            )

          SELECT 'control', NULL, NULL,
                 "poh0" AS "new%poh0",
                 (SELECT p1 FROM points AS p1 WHERE p1 <> "poh" AND NOT EXISTS (SELECT 1 FROM points AS p2 WHERE left_of(p2.loc, "poh".loc, p1.loc))) AS "new%poh"
          FROM   "%sources%"

            UNION ALL
          SELECT 'data', ("poh".label), NULL, NULL, NULL
          FROM   "%sources%"
        ),
        "inter2"("%kind%", "%result%", "%label%", "poh0", "poh", "condition%0") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "poh0", "poh") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "poh0",
                     "poh"
              FROM   "loop0_head"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "poh0" AS "new%poh0",
                 "poh" AS "new%poh",
                 ("poh" = "poh0") AS "new%condition%0"
          FROM   "%sources%"
        )

      -- jumps
      SELECT 'control', NULL, 'loop0_head', "poh0", "poh" 
      FROM   "inter0"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop0_head', "poh0", "poh" 
      FROM   "inter2"
      WHERE  "%kind%" = 'control'
      AND    TRUE AND NOT (NOT "condition%0" IS DISTINCT FROM TRUE)
        UNION ALL
      -- emits
      SELECT "%kind%", "%result%", "%label%", NULL, NULL
      FROM   "loop0_head"
      WHERE  "%kind%" = 'data'
    )
  )

SELECT "%result%" FROM "%trampoline%" WHERE "%kind%" = 'data';
