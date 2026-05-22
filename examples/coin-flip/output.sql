WITH
  "start.1"("⚙️", "#️⃣") AS (
    SELECT NULL AS "⚙️",
           0 AS "#️⃣"
  ),
  "assignment.1"("⚙️", "n", "#️⃣") AS (
    SELECT "start.1"."⚙️" AS "⚙️",
           CAST((10) AS int) AS "n",
           "start.1"."#️⃣" AS "#️⃣"
    FROM   "start.1"
  ),
  "fork.1"("i", "#️⃣", "⚙️", "n") AS (
    SELECT "ℚ"."i" AS "i",
           "assignment.1"."#️⃣" AS "#️⃣",
           "assignment.1"."⚙️" AS "⚙️",
           "assignment.1"."n" AS "n"
    FROM   "assignment.1",
           LATERAL (SELECT * FROM range(("assignment.1"."n"))) AS "ℚ"("i")
  ),
  "assignment.2"("⚙️", "#️⃣", "c", "n") AS (
    SELECT "fork.1"."⚙️" AS "⚙️",
           "fork.1"."#️⃣" AS "#️⃣",
           CAST((random() >= 0.5) AS boolean) AS "c",
           "fork.1"."n" AS "n"
    FROM   "fork.1"
  ),
  "where.1"("n", "⚙️", "#️⃣") AS (
    SELECT "assignment.2"."n" AS "n",
           "assignment.2"."⚙️" AS "⚙️",
           "assignment.2"."#️⃣" AS "#️⃣"
    FROM   "assignment.2"
    WHERE  "assignment.2"."c" IS NOT DISTINCT FROM TRUE
  ),
  "where.2"("n", "⚙️", "#️⃣") AS (
    SELECT "assignment.2"."n" AS "n",
           "assignment.2"."⚙️" AS "⚙️",
           "assignment.2"."#️⃣" AS "#️⃣"
    FROM   "assignment.2"
    WHERE  "assignment.2"."c" IS DISTINCT FROM TRUE
  ),
  "assignment.3"("n", "#️⃣", "⚙️", "s") AS (
    SELECT "where.1"."n" AS "n",
           "where.1"."#️⃣" AS "#️⃣",
           "where.1"."⚙️" AS "⚙️",
           CAST(('tails') AS text) AS "s"
    FROM   "where.1"
  ),
  "assignment.4"("n", "#️⃣", "⚙️", "s") AS (
    SELECT "where.2"."n" AS "n",
           "where.2"."#️⃣" AS "#️⃣",
           "where.2"."⚙️" AS "⚙️",
           CAST(('heads') AS text) AS "s"
    FROM   "where.2"
  ),
  "merge.1"("n", "#️⃣", "⚙️", "s") AS (
    (SELECT "assignment.3"."n" AS "n",
            "assignment.3"."#️⃣" AS "#️⃣",
            "assignment.3"."⚙️" AS "⚙️",
            "assignment.3"."s" AS "s"
     FROM   "assignment.3")
      UNION ALL
    (SELECT "assignment.4"."n" AS "n",
            "assignment.4"."#️⃣" AS "#️⃣",
            "assignment.4"."⚙️" AS "⚙️",
            "assignment.4"."s" AS "s"
     FROM   "assignment.4")
  ),
  "gather.1"("i", "#️⃣", "⚙️", "n") AS (
    SELECT count(*) AS "i",
           "merge.1"."#️⃣" AS "#️⃣",
           "merge.1"."⚙️" AS "⚙️",
           "merge.1"."n" AS "n"
    FROM   "merge.1"
    GROUP  BY "merge.1"."n",
              "merge.1"."#️⃣",
              "merge.1"."⚙️",
              "merge.1"."s"
    HAVING COUNT(*) > 0
  ),
  "assignment.5"("i", "⚙️", "#️⃣") AS (
    SELECT CAST((("gather.1"."i") / (("gather.1"."n") :: float)) AS int) AS "i",
           "gather.1"."⚙️" AS "⚙️",
           "gather.1"."#️⃣" AS "#️⃣"
    FROM   "gather.1"
  ),
  "gather.2"("i", "⚙️", "#️⃣") AS (
    SELECT avg(("assignment.5"."i")) AS "i",
           "assignment.5"."⚙️" AS "⚙️",
           "assignment.5"."#️⃣" AS "#️⃣"
    FROM   "assignment.5"
    GROUP  BY "assignment.5"."⚙️",
              "assignment.5"."#️⃣"
    HAVING COUNT(*) > 0
  ),
  "emit.1"("📊", "⚙️", "#️⃣") AS (
    SELECT "gather.2"."i" AS "📊",
           "gather.2"."⚙️" AS "⚙️",
           "gather.2"."#️⃣" AS "#️⃣"
    FROM   "gather.2"
  ),
  "stop.1"("⚙️") AS (
    SELECT "emit.1"."⚙️"
    FROM   "emit.1"
    WHERE  FALSE
  )
(SELECT "emit.1"."📊"
 FROM   "emit.1")