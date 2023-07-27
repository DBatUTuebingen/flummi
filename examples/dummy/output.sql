WITH RECURSIVE
  "%trampoline%"("%kind%", "%result%", "%label%", "a", "c", "b") AS (
    (
      SELECT 'control', NULL :: int, 'entry',
             (4) :: int AS "a",
             (NULL) :: int AS "c",
             (5) :: int AS "b"
    )
      UNION ALL -- recursive union!
    (
      WITH
        "entry"("%kind%", "%result%", "%label%", "a", "c", "b") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "a", "c", "b") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "a",
                     "c",
                     "b"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'entry'
            )

          SELECT 'control', NULL, NULL,
                 "a" AS "new%a",
                 (0) AS "new%c",
                 "b" AS "new%b"
          FROM   "%sources%"
        ),
        "loop0_head"("%kind%", "%result%", "%label%", "b", "a", "c") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "a", "c", "b") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "a",
                     "c",
                     "b"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop0_head'
            )

          SELECT 'control', NULL, NULL,
                 ("b" - 1) AS "new%b",
                 "a" AS "new%a",
                 ("a" + "c") AS "new%c"
          FROM   "%sources%"
        ),
        "inter1"("%kind%", "%result%", "%label%", "a", "c", "b", "condition%0") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "b", "a", "c") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "b",
                     "a",
                     "c"
              FROM   "loop0_head"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "a" AS "new%a",
                 "c" AS "new%c",
                 "b" AS "new%b",
                 (0 = "b") AS "new%condition%0"
          FROM   "%sources%"

            UNION ALL
          SELECT 'data', ("c"), NULL, NULL, NULL, NULL, NULL
          FROM   "%sources%"
        )

      -- jumps
      SELECT 'control', NULL, 'loop0_head', "a", "c", "b" 
      FROM   "entry"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop0_head', "a", "c", "b" 
      FROM   "inter1"
      WHERE  "%kind%" = 'control'
      AND    TRUE AND NOT (NOT "condition%0" IS DISTINCT FROM TRUE)
        UNION ALL
      -- emits
      SELECT "%kind%", "%result%", "%label%", NULL, NULL, NULL
      FROM   "inter1"
      WHERE  "%kind%" = 'data'
    )
  )

SELECT "%result%" FROM "%trampoline%" WHERE "%kind%" = 'data';
