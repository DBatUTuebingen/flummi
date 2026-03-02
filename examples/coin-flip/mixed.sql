WITH
  "start.1"("@ctrl") AS (
    SELECT x AS "@ctrl"
    from range(10_000_000) as _(x)
  ),
  "assignment.1"("c", "@ctrl") AS (
    SELECT (random() >= 0.5) AS "c",
           "start.1"."@ctrl" AS "@ctrl"
    FROM   "start.1"
  ),
  "where.1"("@ctrl") AS (
    SELECT "assignment.1"."@ctrl" AS "@ctrl"
    FROM   "assignment.1"
    WHERE  "assignment.1"."c" IS NOT DISTINCT FROM TRUE
  ),
  "where.2"("@ctrl") AS (
    SELECT "assignment.1"."@ctrl" AS "@ctrl"
    FROM   "assignment.1"
    WHERE  "assignment.1"."c" IS DISTINCT FROM TRUE
  ),
  "assignment.2"("r", "@ctrl") AS (
    SELECT ('tails') AS "r",
           "where.1"."@ctrl" AS "@ctrl"
    FROM   "where.1"
  ),
  "assignment.3"("r", "@ctrl") AS (
    SELECT ('heads') AS "r",
           "where.2"."@ctrl" AS "@ctrl"
    FROM   "where.2"
  ),
  "emit.1"("@res") AS (
    SELECT "assignment.3"."r" AS "@res"
    FROM   "assignment.3"
  ),
  "emit.2"("@res") AS (
    SELECT "assignment.2"."r" AS "@res"
    FROM   "assignment.2"
  ),
  "merge.1"("@ctrl") AS (
    (SELECT "assignment.3"."@ctrl" AS "@ctrl"
     FROM   "assignment.3")
      UNION ALL
    (SELECT "assignment.2"."@ctrl" AS "@ctrl"
     FROM   "assignment.2")
  ),
  "assignment.4"("c", "@ctrl") AS (
    SELECT (random() >= 0.5) AS "c",
           "merge.1"."@ctrl" AS "@ctrl"
    FROM   "merge.1"
  ),
  "where.3"("@ctrl") AS (
    SELECT "assignment.4"."@ctrl" AS "@ctrl"
    FROM   "assignment.4"
    WHERE  "assignment.4"."c" IS NOT DISTINCT FROM TRUE
  ),
  "where.4"("@ctrl") AS (
    SELECT "assignment.4"."@ctrl" AS "@ctrl"
    FROM   "assignment.4"
    WHERE  "assignment.4"."c" IS DISTINCT FROM TRUE
  ),
  "assignment.5"("r", "@ctrl") AS (
    SELECT ('tails') AS "r",
           "where.3"."@ctrl" AS "@ctrl"
    FROM   "where.3"
  ),
  "assignment.6"("r", "@ctrl") AS (
    SELECT ('heads') AS "r",
           "where.4"."@ctrl" AS "@ctrl"
    FROM   "where.4"
  ),
  "emit.3"("@res") AS (
    SELECT "assignment.6"."r" AS "@res"
    FROM   "assignment.6"
  ),
  "emit.4"("@res") AS (
    SELECT "assignment.5"."r" AS "@res"
    FROM   "assignment.5"
  ),
  "merge.2"("@ctrl") AS (
    (SELECT "assignment.6"."@ctrl" AS "@ctrl"
     FROM   "assignment.6")
      UNION ALL
    (SELECT "assignment.5"."@ctrl" AS "@ctrl"
     FROM   "assignment.5")
  ),
  "assignment.7"("c", "@ctrl") AS (
    SELECT (random() >= 0.5) AS "c",
           "merge.2"."@ctrl" AS "@ctrl"
    FROM   "merge.2"
  ),
  "where.5"("@ctrl") AS (
    SELECT "assignment.7"."@ctrl" AS "@ctrl"
    FROM   "assignment.7"
    WHERE  "assignment.7"."c" IS NOT DISTINCT FROM TRUE
  ),
  "where.6"("@ctrl") AS (
    SELECT "assignment.7"."@ctrl" AS "@ctrl"
    FROM   "assignment.7"
    WHERE  "assignment.7"."c" IS DISTINCT FROM TRUE
  ),
  "assignment.8"("r") AS (
    SELECT ('tails') AS "r"
    FROM   "where.5"
  ),
  "assignment.9"("r") AS (
    SELECT ('heads') AS "r"
    FROM   "where.6"
  ),
  "emit.5"("@res") AS (
    SELECT "assignment.8"."r" AS "@res"
    FROM   "assignment.8"
  ),
  "emit.6"("@res") AS (
    SELECT "assignment.9"."r" AS "@res"
    FROM   "assignment.9"
  )
(SELECT "emit.1"."@res"
 FROM   "emit.1")
  UNION ALL
(SELECT "emit.2"."@res"
 FROM   "emit.2")
  UNION ALL
(SELECT "emit.3"."@res"
 FROM   "emit.3")
  UNION ALL
(SELECT "emit.4"."@res"
 FROM   "emit.4")
  UNION ALL
(SELECT "emit.5"."@res"
 FROM   "emit.5")
  UNION ALL
(SELECT "emit.6"."@res"
 FROM   "emit.6")