WITH RECURSIVE
  "%trampoline%"("%kind%", "%result%", "%label%", "c", "a", "b") AS (
    (
      SELECT 'control', NULL :: int, 'entry',
             (SELECT (NULL)) :: int AS "c",
             (SELECT (4)) :: int AS "a",
             (SELECT (5)) :: int AS "b"
    )
      UNION ALL -- recursive union!
    (
      WITH
        "entry"("%kind%", "%result%", "%label%", "c", "a", "b") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "c", "a", "b") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "c",
                     "a",
                     "b"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'entry'
            )

          SELECT 'control', NULL, NULL,
                 (SELECT (0)) AS "new%c",
                 "a" AS "new%a",
                 "b" AS "new%b"
          FROM   "%sources%"
        ),
        "loop0_head"("%kind%", "%result%", "%label%", "c", "b", "a") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "c", "a", "b") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "c",
                     "a",
                     "b"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop0_head'
            )

          SELECT 'control', NULL, NULL,
                 (SELECT ("a" + "c")) AS "new%c",
                 (SELECT ("b" - 1)) AS "new%b",
                 "a" AS "new%a"
          FROM   "%sources%"
        ),
        "inter1"("%kind%", "%result%", "%label%", "c", "a", "b", "condition%0") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "c", "b", "a") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "c",
                     "b",
                     "a"
              FROM   "loop0_head"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "c" AS "new%c",
                 "a" AS "new%a",
                 "b" AS "new%b",
                 (SELECT (0 = "b")) AS "new%condition%0"
          FROM   "%sources%"

            UNION ALL
          SELECT 'data', (SELECT ("c")), NULL, NULL, NULL, NULL, NULL
          FROM   "%sources%"
        )

      -- jumps
      SELECT 'control', NULL, 'loop0_head', "c", "a", "b" 
      FROM   "entry"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop0_head', "c", "a", "b" 
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
