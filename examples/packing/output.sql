LOAD tpch;
CALL dbgen(sf=0.05);

.timer on
WITH RECURSIVE
  "%trampoline%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
    (
      SELECT 'control', NULL :: bit, 'entry',
             NULL :: int AS "linenumber",
             281990 :: int AS "orderkey",
             NULL :: int AS "max_size",
             NULL :: int AS "max_subset",
             NULL :: bool AS "condition%1",
             NULL :: bool AS "condition%5",
             NULL :: bit AS "pack",
             NULL :: int AS "subset",
             NULL :: int AS "items",
             NULL :: bool AS "condition%2",
             NULL :: int AS "size",
             NULL :: bool AS "condition%0",
             60 :: int AS "capacity",
             NULL :: int AS "n"
    )
      UNION ALL -- recursive union!
    (
      WITH
        "entry"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'entry'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("capacity") AS "new%capacity",
                 (SELECT COUNT(*) :: int FROM lineitem AS l WHERE l.l_orderkey = "orderkey") AS "new%n"
          FROM   "%sources%"
        ),
        "inter0"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "capacity",
                     "n"
              FROM   "entry"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("n" = 0 OR capacity < (SELECT MAX(p.p_size) FROM lineitem AS l, part AS p WHERE l.l_orderkey = "orderkey" AND l.l_partkey = p.p_partkey)) AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "inter1"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'inter1'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ((1 << "n") - 1) AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "loop0_head"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop0_head'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("items" = 0) AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "falsey1"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "condition%1", "condition%5", "pack", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "inter3"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%1" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 (0) AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "inter3"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "condition%1", "condition%5", "pack", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'inter3'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 (0) AS "new%max_size",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "inter4"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "falsey1"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("items" & -"items") AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "loop1_head"("%kind%", "%result%", "%label%", "linenumber", "max_size", "orderkey", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop1_head'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("max_size") AS "new%max_size",
                 ("orderkey") AS "new%orderkey",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 (SELECT SUM(p.p_size) FROM lineitem AS l, part AS p WHERE l.l_orderkey = "orderkey" AND "subset" & (1 << l.l_linenumber - 1) <> 0 AND l.l_partkey = p.p_partkey) AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "loop1_exit"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "items",
                     "subset",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "truthy3"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 (0) AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("items") AS "new%items",
                 ("subset") AS "new%subset",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "inter7"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "max_size", "orderkey", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "max_size",
                     "orderkey",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "loop1_head"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 ("size" <= "capacity" AND "size" > "max_size") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "truthy2"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "inter8"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%2" IS DISTINCT FROM TRUE
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "merge2"("%kind%", "%result%", "%label%", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n", "linenumber", "pack", "condition%3") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "truthy2"
              WHERE  "%kind%" = 'control'
                UNION ALL
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "inter8"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%2" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("items") AS "new%items",
                 ("subset") AS "new%subset",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n",
                 ("linenumber") AS "new%linenumber",
                 ("pack") AS "new%pack",
                 ("subset" = "items") AS "new%condition%3"
          FROM   "%sources%"
        ),
        "inter8"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n", "max_subset") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'inter8'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("size") AS "new%max_size",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n",
                 ("max_subset") AS "new%max_subset"
          FROM   "%sources%"
        ),
        "truthy3"("%kind%", "%result%", "%label%", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "items",
                     "subset",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "merge2"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%3" IS DISTINCT FROM TRUE
            )

          SELECT 'control', NULL, NULL,
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 (bitstring('0', "n")) AS "new%pack",
                 ("items") AS "new%items",
                 ("subset") AS "new%subset",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "inter13"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "items",
                     "subset",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "loop1_exit"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("items" & ("subset" - "items")) AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "loop2_head"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop2_head'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber" + 1) AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("items") AS "new%items",
                 ("subset") AS "new%subset",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "loop2_exit"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "items",
                     "subset",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "truthy4"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items" & ~"max_subset") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "inter15"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n", "condition%4") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "items",
                     "subset",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "loop2_head"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("items") AS "new%items",
                 ("subset") AS "new%subset",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n",
                 ("linenumber" > "n") AS "new%condition%4"
          FROM   "%sources%"
        ),
        "truthy4"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "items", "subset", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "items",
                     "subset",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "inter15"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%4" IS DISTINCT FROM TRUE
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("items") AS "new%items",
                 ("subset") AS "new%subset",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"

            UNION ALL
          SELECT 'data', "pack", NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
          FROM   "%sources%"
        ),
        "falsey4"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "inter15"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%4" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("max_subset" & (1 << "linenumber" - 1) <> 0) AS "new%condition%5",
                 ("pack") AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        ),
        "inter17"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "linenumber",
                     "orderkey",
                     "max_size",
                     "max_subset",
                     "condition%1",
                     "condition%5",
                     "pack",
                     "subset",
                     "items",
                     "condition%2",
                     "size",
                     "condition%0",
                     "capacity",
                     "n"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'inter17'
            )

          SELECT 'control', NULL, NULL,
                 ("linenumber") AS "new%linenumber",
                 ("orderkey") AS "new%orderkey",
                 ("max_size") AS "new%max_size",
                 ("max_subset") AS "new%max_subset",
                 ("condition%1") AS "new%condition%1",
                 ("condition%5") AS "new%condition%5",
                 (set_bit("pack", "linenumber" - 1, 1)) AS "new%pack",
                 ("subset") AS "new%subset",
                 ("items") AS "new%items",
                 ("condition%2") AS "new%condition%2",
                 ("size") AS "new%size",
                 ("condition%0") AS "new%condition%0",
                 ("capacity") AS "new%capacity",
                 ("n") AS "new%n"
          FROM   "%sources%"
        )

      -- jumps
      SELECT 'control', NULL, 'inter1', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "inter0"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop0_head', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "inter1"
      WHERE  "%kind%" = 'control'
      AND    TRUE AND NOT (NOT "condition%0" IS DISTINCT FROM TRUE)
        UNION ALL
      SELECT 'control', NULL, 'inter3', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "loop0_head"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop1_head', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "inter4"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'inter8', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "inter7"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop1_head', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "merge2"
      WHERE  "%kind%" = 'control'
      AND    TRUE AND NOT (NOT "condition%3" IS DISTINCT FROM TRUE)
        UNION ALL
      SELECT 'control', NULL, 'loop2_head', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "inter13"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop0_head', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "loop2_exit"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'inter17', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "falsey4"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop2_head', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "inter17"
      WHERE  "%kind%" = 'control'
      AND    TRUE AND NOT "condition%5" IS DISTINCT FROM TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop2_head', "linenumber", "orderkey", "max_size", "max_subset", "condition%1", "condition%5", "pack", "subset", "items", "condition%2", "size", "condition%0", "capacity", "n"
      FROM   "inter17"
      WHERE  "%kind%" = 'control'
      AND    TRUE AND NOT (NOT "condition%5" IS DISTINCT FROM TRUE)
        UNION ALL
      -- emits
      SELECT "%kind%", "%result%", "%label%", NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
      FROM   "truthy4"
      WHERE  "%kind%" = 'data'
    )
  )

SELECT "%result%" FROM "%trampoline%" WHERE "%kind%" = 'data';