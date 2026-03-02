WITH
  "start.1"("@ctrl") AS (
    SELECT x AS "@ctrl"
    from range(10_000_000) as _(x)
  ),
  "assignment.1"("c", "@ctrl") AS (
    SELECT CAST((random() >= 0.5) AS boolean) AS "c",
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
  "assignment.2"("@ctrl", "r") AS (
    SELECT "where.1"."@ctrl" AS "@ctrl",
           CAST(('tails') AS text) AS "r"
    FROM   "where.1"
  ),
  "assignment.3"("@ctrl", "r") AS (
    SELECT "where.2"."@ctrl" AS "@ctrl",
           CAST(('heads') AS text) AS "r"
    FROM   "where.2"
  ),
  "merge.1"("@ctrl", "r") AS (
    (SELECT "assignment.2"."@ctrl" AS "@ctrl",
            "assignment.2"."r" AS "r"
     FROM   "assignment.2")
      UNION ALL
    (SELECT "assignment.3"."@ctrl" AS "@ctrl",
            "assignment.3"."r" AS "r"
     FROM   "assignment.3")
  ),
  "assignment.4"("c", "@ctrl") AS (
    SELECT CAST((random() >= 0.5) AS boolean) AS "c",
           "merge.1"."@ctrl" AS "@ctrl"
    FROM   "merge.1"
  ),
  "emit.1"("@res") AS (
    SELECT "merge.1"."r" AS "@res"
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
  "assignment.5"("@ctrl", "r") AS (
    SELECT "where.3"."@ctrl" AS "@ctrl",
           CAST(('tails') AS text) AS "r"
    FROM   "where.3"
  ),
  "assignment.6"("@ctrl", "r") AS (
    SELECT "where.4"."@ctrl" AS "@ctrl",
           CAST(('heads') AS text) AS "r"
    FROM   "where.4"
  ),
  "merge.2"("@ctrl", "r") AS (
    (SELECT "assignment.5"."@ctrl" AS "@ctrl",
            "assignment.5"."r" AS "r"
     FROM   "assignment.5")
      UNION ALL
    (SELECT "assignment.6"."@ctrl" AS "@ctrl",
            "assignment.6"."r" AS "r"
     FROM   "assignment.6")
  ),
  "assignment.7"("c", "@ctrl") AS (
    SELECT CAST((random() >= 0.5) AS boolean) AS "c",
           "merge.2"."@ctrl" AS "@ctrl"
    FROM   "merge.2"
  ),
  "emit.2"("@res") AS (
    SELECT "merge.2"."r" AS "@res"
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
  "assignment.8"("@ctrl", "r") AS (
    SELECT "where.5"."@ctrl" AS "@ctrl",
           CAST(('tails') AS text) AS "r"
    FROM   "where.5"
  ),
  "assignment.9"("@ctrl", "r") AS (
    SELECT "where.6"."@ctrl" AS "@ctrl",
           CAST(('heads') AS text) AS "r"
    FROM   "where.6"
  ),
  "merge.3"("r") AS (
    (SELECT "assignment.8"."r" AS "r"
     FROM   "assignment.8")
      UNION ALL
    (SELECT "assignment.9"."r" AS "r"
     FROM   "assignment.9")
  ),
  "emit.3"("@res") AS (
    SELECT "merge.3"."r" AS "@res"
    FROM   "merge.3"
  )
(SELECT "emit.1"."@res"
 FROM   "emit.1")
  UNION ALL
(SELECT "emit.2"."@res"
 FROM   "emit.2")
  UNION ALL
(SELECT "emit.3"."@res"
 FROM   "emit.3")