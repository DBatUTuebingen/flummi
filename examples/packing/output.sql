WITH RECURSIVE
  "%trampoline%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
    (
      SELECT 'control', NULL :: text, 'entry',
             (281990) :: int AS "orderkey",
             (NULL) :: int AS "n",
             (NULL) :: text AS "pack",
             (NULL) :: int AS "linenumber",
             (NULL) :: int AS "max_subset",
             (NULL) :: int AS "subset",
             (60) :: int AS "capacity",
             (NULL) :: int AS "items",
             (NULL) :: int AS "max_size"
    )
      UNION ALL -- recursive union!
    (
      WITH
        "entry"("%kind%", "%result%", "%label%", "n", "orderkey", "pack", "linenumber", "max_subset", "subset", "capacity", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'entry'
            )

          SELECT 'control', NULL, NULL,
                 (SELECT COUNT(*) :: int FROM lineitem AS l WHERE l.l_orderkey = "orderkey") AS "new%n",
                 "orderkey" AS "new%orderkey",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        ),
        "inter0"("%kind%", "%result%", "%label%", "n", "orderkey", "pack", "linenumber", "max_subset", "subset", "capacity", "max_size", "condition%0") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "n", "orderkey", "pack", "linenumber", "max_subset", "subset", "capacity", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "n",
                     "orderkey",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "max_size"
              FROM   "entry"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "n" AS "new%n",
                 "orderkey" AS "new%orderkey",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "max_size" AS "new%max_size",
                 ("n" = 0 OR capacity < (SELECT MAX(p.p_size) FROM lineitem AS l, part AS p WHERE l.l_orderkey = "orderkey" AND l.l_partkey = p.p_partkey)) AS "new%condition%0"
          FROM   "%sources%"
        ),
        "falsey0"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "n", "orderkey", "pack", "linenumber", "max_subset", "subset", "capacity", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "n",
                     "orderkey",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "max_size"
              FROM   "inter0"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%0" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 ((1 << "n") - 1) AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        ),
        "loop0_head"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "capacity", "items", "condition%1") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop0_head'
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 ("items" = 0) AS "new%condition%1"
          FROM   "%sources%"
        ),
        "falsey1"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "capacity", "items") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "capacity",
                     "items"
              FROM   "loop0_head"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%1" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 (0) AS "new%max_subset",
                 ("items" & -"items") AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 (0) AS "new%max_size"
          FROM   "%sources%"
        ),
        "loop1_head"("%kind%", "%result%", "%label%", "pack", "max_subset", "items", "orderkey", "n", "linenumber", "subset", "capacity", "max_size", "size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop1_head'
            )

          SELECT 'control', NULL, NULL,
                 "pack" AS "new%pack",
                 "max_subset" AS "new%max_subset",
                 "items" AS "new%items",
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "linenumber" AS "new%linenumber",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "max_size" AS "new%max_size",
                 (SELECT SUM(p.p_size) FROM lineitem AS l, part AS p WHERE l.l_orderkey = "orderkey" AND "subset" & (1 << l.l_linenumber - 1) <> 0 AND l.l_partkey = p.p_partkey) AS "new%size"
          FROM   "%sources%"
        ),
        "loop1_exit"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "merge2"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%3" IS DISTINCT FROM TRUE
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 ('') AS "new%pack",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        ),
        "inter7"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "subset", "capacity", "items", "size", "max_subset", "max_size", "condition%2") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "pack", "max_subset", "items", "orderkey", "n", "linenumber", "subset", "capacity", "max_size", "size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "pack",
                     "max_subset",
                     "items",
                     "orderkey",
                     "n",
                     "linenumber",
                     "subset",
                     "capacity",
                     "max_size",
                     "size"
              FROM   "loop1_head"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "size" AS "new%size",
                 "max_subset" AS "new%max_subset",
                 "max_size" AS "new%max_size",
                 ("size" <= "capacity" AND "size" > "max_size") AS "new%condition%2"
          FROM   "%sources%"
        ),
        "truthy2"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "subset", "capacity", "items", "size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "subset",
                     "capacity",
                     "items",
                     "size"
              FROM   "inter7"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%2" IS DISTINCT FROM TRUE
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 ("subset") AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 ("size") AS "new%max_size"
          FROM   "%sources%"
        ),
        "merge2"("%kind%", "%result%", "%label%", "orderkey", "n", "max_subset", "subset", "capacity", "items", "max_size", "pack", "linenumber", "condition%3") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "inter7"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%2" IS DISTINCT FROM TRUE)
                UNION ALL
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "truthy2"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 ("subset" = "items") AS "new%condition%3"
          FROM   "%sources%"
        ),
        "falsey3"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "merge2"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%3" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 ("items" & ("subset" - "items")) AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        ),
        "inter13"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "loop1_exit"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 (0) AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        ),
        "loop2_head"("%kind%", "%result%", "%label%", "n", "orderkey", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop2_head'
            )

          SELECT 'control', NULL, NULL,
                 "n" AS "new%n",
                 "orderkey" AS "new%orderkey",
                 "pack" AS "new%pack",
                 ("linenumber" + 1) AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        ),
        "inter15"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size", "condition%4") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "n", "orderkey", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "n",
                     "orderkey",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "loop2_head"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size",
                 ("linenumber" > "n") AS "new%condition%4"
          FROM   "%sources%"
        ),
        "truthy4"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "inter15"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%4" IS DISTINCT FROM TRUE
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 ("items" & (-"max_subset" - 1)) AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"

            UNION ALL
          SELECT 'data', ("pack"), NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
          FROM   "%sources%"
        ),
        "falsey4"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size", "condition%5") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "inter15"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%4" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size",
                 ("max_subset" & (1 << "linenumber" - 1) <> 0) AS "new%condition%5"
          FROM   "%sources%"
        ),
        "truthy5"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "falsey4"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%5" IS DISTINCT FROM TRUE
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 ("pack" || '#') AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        ),
        "falsey5"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "falsey4"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%5" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 ("pack" || '.') AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        ),
        "merge5"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "truthy5"
              WHERE  "%kind%" = 'control'
                UNION ALL
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "n",
                     "pack",
                     "linenumber",
                     "max_subset",
                     "subset",
                     "capacity",
                     "items",
                     "max_size"
              FROM   "falsey5"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "orderkey" AS "new%orderkey",
                 "n" AS "new%n",
                 "pack" AS "new%pack",
                 "linenumber" AS "new%linenumber",
                 "max_subset" AS "new%max_subset",
                 "subset" AS "new%subset",
                 "capacity" AS "new%capacity",
                 "items" AS "new%items",
                 "max_size" AS "new%max_size"
          FROM   "%sources%"
        )

      -- jumps
      SELECT 'control', NULL, 'loop0_head', "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size" 
      FROM   "falsey0"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop1_head', "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size" 
      FROM   "falsey1"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop1_head', "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size" 
      FROM   "falsey3"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop2_head', "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size" 
      FROM   "inter13"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop0_head', "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size" 
      FROM   "truthy4"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop2_head', "orderkey", "n", "pack", "linenumber", "max_subset", "subset", "capacity", "items", "max_size" 
      FROM   "merge5"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      -- emits
      SELECT "%kind%", "%result%", "%label%", NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
      FROM   "truthy4"
      WHERE  "%kind%" = 'data'
    )
  )

SELECT "%result%" FROM "%trampoline%" WHERE "%kind%" = 'data';
