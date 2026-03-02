WITH
  "start.1"("@ctrl") AS (
    SELECT x AS "@ctrl"
    from range(10_000_000) as _(x)
  ),
  "assignment.1"("@ctrl", "c") AS (
    SELECT "start.1"."@ctrl" AS "@ctrl",
           (random() >= 0.5) AS "c"
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
  "assignment.4"("@ctrl", "c") AS (
    SELECT "assignment.2"."@ctrl" AS "@ctrl",
           (random() >= 0.5) AS "c"
    FROM   "assignment.2"
  ),
  "assignment.5"("@ctrl", "c") AS (
    SELECT "assignment.3"."@ctrl" AS "@ctrl",
           (random() >= 0.5) AS "c"
    FROM   "assignment.3"
  ),
  "emit.1"("@res") AS (
    SELECT "assignment.2"."r" AS "@res"
    FROM   "assignment.2"
  ),
  "emit.2"("@res") AS (
    SELECT "assignment.3"."r" AS "@res"
    FROM   "assignment.3"
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
  "where.5"("@ctrl") AS (
    SELECT "assignment.5"."@ctrl" AS "@ctrl"
    FROM   "assignment.5"
    WHERE  "assignment.5"."c" IS NOT DISTINCT FROM TRUE
  ),
  "where.6"("@ctrl") AS (
    SELECT "assignment.5"."@ctrl" AS "@ctrl"
    FROM   "assignment.5"
    WHERE  "assignment.5"."c" IS DISTINCT FROM TRUE
  ),
  "assignment.6"("r", "@ctrl") AS (
    SELECT ('tails') AS "r",
           "where.3"."@ctrl" AS "@ctrl"
    FROM   "where.3"
  ),
  "assignment.7"("r", "@ctrl") AS (
    SELECT ('heads') AS "r",
           "where.4"."@ctrl" AS "@ctrl"
    FROM   "where.4"
  ),
  "assignment.8"("r", "@ctrl") AS (
    SELECT ('tails') AS "r",
           "where.5"."@ctrl" AS "@ctrl"
    FROM   "where.5"
  ),
  "assignment.9"("r", "@ctrl") AS (
    SELECT ('heads') AS "r",
           "where.6"."@ctrl" AS "@ctrl"
    FROM   "where.6"
  ),
  "assignment.10"("@ctrl", "c") AS (
    SELECT "assignment.6"."@ctrl" AS "@ctrl",
           (random() >= 0.5) AS "c"
    FROM   "assignment.6"
  ),
  "assignment.11"("@ctrl", "c") AS (
    SELECT "assignment.8"."@ctrl" AS "@ctrl",
           (random() >= 0.5) AS "c"
    FROM   "assignment.8"
  ),
  "assignment.12"("@ctrl", "c") AS (
    SELECT "assignment.9"."@ctrl" AS "@ctrl",
           (random() >= 0.5) AS "c"
    FROM   "assignment.9"
  ),
  "assignment.13"("@ctrl", "c") AS (
    SELECT "assignment.7"."@ctrl" AS "@ctrl",
           (random() >= 0.5) AS "c"
    FROM   "assignment.7"
  ),
  "emit.3"("@res") AS (
    SELECT "assignment.6"."r" AS "@res"
    FROM   "assignment.6"
  ),
  "emit.4"("@res") AS (
    SELECT "assignment.8"."r" AS "@res"
    FROM   "assignment.8"
  ),
  "emit.5"("@res") AS (
    SELECT "assignment.9"."r" AS "@res"
    FROM   "assignment.9"
  ),
  "emit.6"("@res") AS (
    SELECT "assignment.7"."r" AS "@res"
    FROM   "assignment.7"
  ),
  "where.10"("@ctrl") AS (
    SELECT "assignment.11"."@ctrl" AS "@ctrl"
    FROM   "assignment.11"
    WHERE  "assignment.11"."c" IS DISTINCT FROM TRUE
  ),
  "where.11"("@ctrl") AS (
    SELECT "assignment.13"."@ctrl" AS "@ctrl"
    FROM   "assignment.13"
    WHERE  "assignment.13"."c" IS NOT DISTINCT FROM TRUE
  ),
  "where.12"("@ctrl") AS (
    SELECT "assignment.13"."@ctrl" AS "@ctrl"
    FROM   "assignment.13"
    WHERE  "assignment.13"."c" IS DISTINCT FROM TRUE
  ),
  "where.13"("@ctrl") AS (
    SELECT "assignment.12"."@ctrl" AS "@ctrl"
    FROM   "assignment.12"
    WHERE  "assignment.12"."c" IS NOT DISTINCT FROM TRUE
  ),
  "where.14"("@ctrl") AS (
    SELECT "assignment.12"."@ctrl" AS "@ctrl"
    FROM   "assignment.12"
    WHERE  "assignment.12"."c" IS DISTINCT FROM TRUE
  ),
  "where.7"("@ctrl") AS (
    SELECT "assignment.10"."@ctrl" AS "@ctrl"
    FROM   "assignment.10"
    WHERE  "assignment.10"."c" IS NOT DISTINCT FROM TRUE
  ),
  "where.8"("@ctrl") AS (
    SELECT "assignment.10"."@ctrl" AS "@ctrl"
    FROM   "assignment.10"
    WHERE  "assignment.10"."c" IS DISTINCT FROM TRUE
  ),
  "where.9"("@ctrl") AS (
    SELECT "assignment.11"."@ctrl" AS "@ctrl"
    FROM   "assignment.11"
    WHERE  "assignment.11"."c" IS NOT DISTINCT FROM TRUE
  ),
  "assignment.14"("r") AS (
    SELECT ('tails') AS "r"
    FROM   "where.7"
  ),
  "assignment.15"("r") AS (
    SELECT ('heads') AS "r"
    FROM   "where.8"
  ),
  "assignment.16"("r") AS (
    SELECT ('tails') AS "r"
    FROM   "where.9"
  ),
  "assignment.17"("r") AS (
    SELECT ('heads') AS "r"
    FROM   "where.10"
  ),
  "assignment.18"("r") AS (
    SELECT ('tails') AS "r"
    FROM   "where.11"
  ),
  "assignment.19"("r") AS (
    SELECT ('heads') AS "r"
    FROM   "where.12"
  ),
  "assignment.20"("r") AS (
    SELECT ('tails') AS "r"
    FROM   "where.13"
  ),
  "assignment.21"("r") AS (
    SELECT ('heads') AS "r"
    FROM   "where.14"
  ),
  "emit.10"("@res") AS (
    SELECT "assignment.16"."r" AS "@res"
    FROM   "assignment.16"
  ),
  "emit.11"("@res") AS (
    SELECT "assignment.15"."r" AS "@res"
    FROM   "assignment.15"
  ),
  "emit.12"("@res") AS (
    SELECT "assignment.18"."r" AS "@res"
    FROM   "assignment.18"
  ),
  "emit.13"("@res") AS (
    SELECT "assignment.17"."r" AS "@res"
    FROM   "assignment.17"
  ),
  "emit.14"("@res") AS (
    SELECT "assignment.19"."r" AS "@res"
    FROM   "assignment.19"
  ),
  "emit.7"("@res") AS (
    SELECT "assignment.20"."r" AS "@res"
    FROM   "assignment.20"
  ),
  "emit.8"("@res") AS (
    SELECT "assignment.14"."r" AS "@res"
    FROM   "assignment.14"
  ),
  "emit.9"("@res") AS (
    SELECT "assignment.21"."r" AS "@res"
    FROM   "assignment.21"
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
  UNION ALL
(SELECT "emit.7"."@res"
 FROM   "emit.7")
  UNION ALL
(SELECT "emit.8"."@res"
 FROM   "emit.8")
  UNION ALL
(SELECT "emit.9"."@res"
 FROM   "emit.9")
  UNION ALL
(SELECT "emit.10"."@res"
 FROM   "emit.10")
  UNION ALL
(SELECT "emit.11"."@res"
 FROM   "emit.11")
  UNION ALL
(SELECT "emit.12"."@res"
 FROM   "emit.12")
  UNION ALL
(SELECT "emit.13"."@res"
 FROM   "emit.13")
  UNION ALL
(SELECT "emit.14"."@res"
 FROM   "emit.14")