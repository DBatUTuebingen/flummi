WITH
  "start.1"("#️⃣", "⚙️") AS (
    SELECT 0 AS "#️⃣",
           NULL AS "⚙️"
  ),
  "assignment.1"("#️⃣", "⚙️", "n") AS (
    SELECT "start.1"."#️⃣" AS "#️⃣",
           "start.1"."⚙️" AS "⚙️",
           CAST((10) AS int) AS "n"
    FROM   "start.1"
  ),
  "fork.1"("#️⃣", "⚙️", "i", "n") AS (
    SELECT "assignment.1"."#️⃣" AS "#️⃣",
           "assignment.1"."⚙️" AS "⚙️",
           CAST(("ℚ"."i") AS int) AS "i",
           "assignment.1"."n" AS "n"
    FROM   "assignment.1",
           LATERAL (SELECT * FROM range(("assignment.1"."n"))) AS "ℚ"("i")
  ),
  "assignment.2"("#️⃣", "⚙️", "🔍", "n") AS (
    SELECT "fork.1"."#️⃣" AS "#️⃣",
           "fork.1"."⚙️" AS "⚙️",
           CAST((random() >= 0.5) AS boolean) AS "🔍",
           "fork.1"."n" AS "n"
    FROM   "fork.1"
  ),
  "where.1"("#️⃣", "⚙️", "n") AS (
    SELECT "assignment.2"."#️⃣" AS "#️⃣",
           "assignment.2"."⚙️" AS "⚙️",
           "assignment.2"."n" AS "n"
    FROM   "assignment.2"
    WHERE  "assignment.2"."🔍" IS NOT DISTINCT FROM TRUE
  ),
  "assignment.3"("#️⃣", "⚙️", "s", "n") AS (
    SELECT "where.1"."#️⃣" AS "#️⃣",
           "where.1"."⚙️" AS "⚙️",
           CAST(('tails') AS text) AS "s",
           "where.1"."n" AS "n"
    FROM   "where.1"
  ),
  "where.2"("#️⃣", "⚙️", "n") AS (
    SELECT "assignment.2"."#️⃣" AS "#️⃣",
           "assignment.2"."⚙️" AS "⚙️",
           "assignment.2"."n" AS "n"
    FROM   "assignment.2"
    WHERE  "assignment.2"."🔍" IS DISTINCT FROM TRUE
  ),
  "assignment.4"("#️⃣", "⚙️", "s", "n") AS (
    SELECT "where.2"."#️⃣" AS "#️⃣",
           "where.2"."⚙️" AS "⚙️",
           CAST(('heads') AS text) AS "s",
           "where.2"."n" AS "n"
    FROM   "where.2"
  ),
  "merge.1"("#️⃣", "⚙️", "s", "n") AS (
    (SELECT "assignment.3"."#️⃣" AS "#️⃣",
            "assignment.3"."⚙️" AS "⚙️",
            "assignment.3"."s" AS "s",
            "assignment.3"."n" AS "n"
     FROM   "assignment.3")
      UNION ALL
    (SELECT "assignment.4"."#️⃣" AS "#️⃣",
            "assignment.4"."⚙️" AS "⚙️",
            "assignment.4"."s" AS "s",
            "assignment.4"."n" AS "n"
     FROM   "assignment.4")
  ),
  "gather.1"("#️⃣", "⚙️", "i", "n") AS (
    SELECT "merge.1"."#️⃣" AS "#️⃣",
           "merge.1"."⚙️" AS "⚙️",
           CAST((count(*)) AS int) AS "i",
           "merge.1"."n" AS "n"
    FROM   "merge.1"
    GROUP  BY "merge.1"."#️⃣",
              "merge.1"."n",
              "merge.1"."s",
              "merge.1"."⚙️"
    HAVING COUNT(*) > 0
  ),
  "assignment.5"("#️⃣", "⚙️", "i") AS (
    SELECT "gather.1"."#️⃣" AS "#️⃣",
           "gather.1"."⚙️" AS "⚙️",
           CAST((("gather.1"."i") / (("gather.1"."n") :: float)) AS int) AS "i"
    FROM   "gather.1"
  ),
  "gather.2"("#️⃣", "⚙️", "i") AS (
    SELECT "assignment.5"."#️⃣" AS "#️⃣",
           "assignment.5"."⚙️" AS "⚙️",
           CAST((avg(("assignment.5"."i"))) AS int) AS "i"
    FROM   "assignment.5"
    GROUP  BY "assignment.5"."#️⃣",
              "assignment.5"."⚙️"
    HAVING COUNT(*) > 0
  ),
  "emit.1"("#️⃣", "⚙️", "📊.1") AS (
    SELECT "gather.2"."#️⃣" AS "#️⃣",
           "gather.2"."⚙️" AS "⚙️",
           "gather.2"."i" AS "📊.1"
    FROM   "gather.2"
  ),
  "stop.1"("⚙️") AS (
    SELECT "emit.1"."⚙️"
    FROM   "emit.1"
    WHERE  FALSE
  )
(SELECT "emit.1"."📊.1"
 FROM   "emit.1")