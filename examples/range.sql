WITH RECURSIVE
  "%loop%"("%kind%", "%label%", "l", "u", "%result%") AS (
    (SELECT 'jump' AS "%kind%",
            'entry' AS "%label%",
            CAST((1) AS int) AS "l",
            CAST((10) AS int) AS "u",
            CAST(NULL AS int) AS "%result%")
      UNION ALL -- recursive union!
    (WITH
      "%loop%"("%kind%", "%label%", "l", "u", "%result%") AS (
        SELECT * FROM "%loop%"
      ),
      "entry"("%kind%", "%label%", "l", "u", "%result%") AS (
        WITH
          "%inputs%"("l", "u") AS (
            SELECT "l", "u"
            FROM   "%loop%"
            WHERE  "%kind%"='jump'
            AND    "%label%"='entry'
          ),
          "%assign%"("l", "u") AS (
            SELECT CAST((("%inputs%"."l")) AS int) AS "l",
                   CAST((("%inputs%"."u")) AS int) AS "u"
            FROM "%inputs%"
          )

        SELECT 'goto', 'loop_head', "l", "u", CAST(NULL AS int)
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "loop_head"("%kind%", "%label%", "l", "u", "%result%") AS (
        WITH
          "%inputs%"("l", "u") AS (
            SELECT "l", "u"
            FROM   "%loop%"
            WHERE  "%kind%"='jump'
            AND    "%label%"='loop_head'
              UNION ALL
            SELECT "l", "u"
            FROM   "entry"
            WHERE  "%kind%"='goto'
            AND    "%label%"='loop_head'
          ),
          "%assign%"("l", "u") AS (
            SELECT CAST((("%inputs%"."l")) AS int) AS "l",
                   CAST((("%inputs%"."u")) AS int) AS "u"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter0', "l", "u", CAST(NULL AS int)
        FROM   "%assign%"
        WHERE  TRUE
          UNION ALL
        SELECT 'emit', NULL, CAST(NULL AS int), CAST(NULL AS int),
               CAST((("%inputs%"."l")) AS int)
        FROM   "%inputs%"
      ),
      "inter0"("%kind%", "%label%", "l", "u", "%result%") AS (
        WITH
          "%inputs%"("l", "u") AS (
            SELECT "l", "u"
            FROM   "loop_head"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter0'
          ),
          "%assign%"("l", "u") AS (
            SELECT CAST((("%inputs%"."l") + 1) AS int) AS "l",
                   CAST((("%inputs%"."u")) AS int) AS "u"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter1', "l", "u", CAST(NULL AS int)
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter1"("%kind%", "%label%", "l", "u", "%result%") AS (
        WITH
          "%inputs%"("l", "u") AS (
            SELECT "l", "u"
            FROM   "inter0"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter1'
          ),
          "%assign%"("l", "u", "condition%0") AS (
            SELECT CAST((("%inputs%"."l")) AS int) AS "l",
                   CAST((("%inputs%"."u")) AS int) AS "u",
                   CAST((("%inputs%"."l") >= ("%inputs%"."u")) AS bool) AS "condition%0"
            FROM "%inputs%"
          )

        SELECT 'jump', 'loop_head', "l", "u", CAST(NULL AS int)
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%0"
      )

     SELECT 'jump', "%label%", "l", "u", CAST(NULL AS int)
     FROM   "inter1"
     WHERE  "%kind%"='jump'
       UNION ALL
     SELECT 'emit', NULL, CAST(NULL AS int), CAST(NULL AS int), "%result%"
     FROM   "loop_head"
     WHERE  "%kind%"='emit'
    )
  )

SELECT "%result%" FROM "%loop%" WHERE "%kind%"='emit';
