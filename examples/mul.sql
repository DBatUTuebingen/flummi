WITH RECURSIVE
  "%loop%"("%kind%", "%label%", "a", "b", "c", "%result%") AS (
    (SELECT 'jump' AS "%kind%",
            'entry' AS "%label%",
            CAST((4) AS int) AS "a",
            CAST((5) AS int) AS "b",
            CAST(NULL AS int) AS "c",
            CAST(NULL AS int) AS "%result%")
      UNION ALL -- recursive union!
    (WITH
      "%loop%"("%kind%", "%label%", "a", "b", "c", "%result%") AS (
        SELECT * FROM "%loop%"
      ),
      "entry"("%kind%", "%label%", "a", "b", "c", "%result%") AS (
        WITH
          "%inputs%"("a", "b", "c") AS (
            SELECT "a", "b", "c"
            FROM   "%loop%"
            WHERE  "%kind%"='jump'
            AND    "%label%"='entry'
          ),
          "%assign%"("a", "b", "c") AS (
            SELECT CAST((("%inputs%"."a")) AS int) AS "a",
                   CAST((("%inputs%"."b")) AS int) AS "b",
                   CAST((0) AS int) AS "c"
            FROM "%inputs%"
          )

        SELECT 'goto', 'multiplication_loop_head', "a", "b", "c", CAST(NULL AS int)
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "multiplication_loop_head"("%kind%", "%label%", "a", "b", "c", "%result%") AS (
        WITH
          "%inputs%"("a", "b", "c") AS (
            SELECT "a", "b", "c"
            FROM   "%loop%"
            WHERE  "%kind%"='jump'
            AND    "%label%"='multiplication_loop_head'
              UNION ALL
            SELECT "a", "b", "c"
            FROM   "entry"
            WHERE  "%kind%"='goto'
            AND    "%label%"='multiplication_loop_head'
          ),
          "%assign%"("a", "b", "c") AS (
            SELECT CAST((("%inputs%"."a")) AS int) AS "a",
                   CAST((("%inputs%"."b") - 1) AS int) AS "b",
                   CAST((("%inputs%"."a") + ("%inputs%"."c")) AS int) AS "c"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter1', "a", "b", "c", CAST(NULL AS int)
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter1"("%kind%", "%label%", "a", "b", "c", "%result%") AS (
        WITH
          "%inputs%"("a", "b", "c") AS (
            SELECT "a", "b", "c"
            FROM   "multiplication_loop_head"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter1'
          ),
          "%assign%"("a", "b", "c", "condition%0") AS (
            SELECT CAST((("%inputs%"."a")) AS int) AS "a",
                   CAST((("%inputs%"."b")) AS int) AS "b",
                   CAST((("%inputs%"."c")) AS int) AS "c",
                   CAST((0 = ("%inputs%"."b")) AS bool) AS "condition%0"
            FROM "%inputs%"
          )

        SELECT 'jump', 'multiplication_loop_head', "a", "b", "c", CAST(NULL AS int)
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%0"
          UNION ALL
        SELECT 'emit', NULL, CAST(NULL AS int), CAST(NULL AS int), CAST(NULL AS int),
               CAST((("%inputs%"."c")) AS int)
        FROM   "%inputs%"
      )

     SELECT 'jump', "%label%", "a", "b", "c", CAST(NULL AS int)
     FROM   "inter1"
     WHERE  "%kind%"='jump'
       UNION ALL
     SELECT 'emit', NULL, CAST(NULL AS int), CAST(NULL AS int), CAST(NULL AS int), "%result%"
     FROM   "inter1"
     WHERE  "%kind%"='emit'
    )
  )

SELECT "%result%" FROM "%loop%" WHERE "%kind%"='emit';
