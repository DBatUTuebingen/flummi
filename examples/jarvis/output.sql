WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "p0", "p") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS point) AS "📊",
            CAST((NULL) AS point) AS "p0",
            CAST((NULL) AS point) AS "p")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("⚙️", "p0", "p", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."p0" AS "p0",
                "🔄"."p" AS "p",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("⚙️", "p0", "#️⃣") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                CAST((SELECT p FROM points AS p ORDER BY p.x LIMIT 1) AS point) AS "p0",
                "start.1"."#️⃣" AS "#️⃣"
         FROM   "start.1"
       ),
       "assignment.2"("p", "p0", "#️⃣", "⚙️") AS (
         SELECT CAST((("assignment.1"."p0")) AS point) AS "p",
                "assignment.1"."p0" AS "p0",
                "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."⚙️" AS "⚙️"
         FROM   "assignment.1"
       ),
       "merge.1"("p", "p0", "#️⃣", "⚙️") AS (
         (SELECT "start.2"."p" AS "p",
                 "start.2"."p0" AS "p0",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."⚙️" AS "⚙️"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.2"."p" AS "p",
                 "assignment.2"."p0" AS "p0",
                 "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."⚙️" AS "⚙️"
          FROM   "assignment.2")
       ),
       "emit.1"("⚙️", "p0", "p", "📊", "#️⃣") AS (
         SELECT "merge.1"."⚙️" AS "⚙️",
                "merge.1"."p0" AS "p0",
                "merge.1"."p" AS "p",
                "merge.1"."p" AS "📊",
                "merge.1"."#️⃣" AS "#️⃣"
         FROM   "merge.1"
       ),
       "assignment.3"("p", "p0", "#️⃣", "⚙️") AS (
         SELECT CAST((SELECT p1
                       FROM   points AS p1
                       WHERE  p1 <> ("emit.1"."p")
                       AND    NOT EXISTS (
                                FROM  points AS p2
                                WHERE (("emit.1"."p").x - p2.x) * (p1.y - p2.y) -
                                      (("emit.1"."p").y - p2.y) * (p1.x - p2.x) > 0
                              )) AS point) AS "p",
                "emit.1"."p0" AS "p0",
                "emit.1"."#️⃣" AS "#️⃣",
                "emit.1"."⚙️" AS "⚙️"
         FROM   "emit.1"
       ),
       "assignment.4"("⚙️", "p0", "cond", "p", "#️⃣") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."p0" AS "p0",
                CAST((("assignment.3"."p") = ("assignment.3"."p0")) AS boolean) AS "cond",
                "assignment.3"."p" AS "p",
                "assignment.3"."#️⃣" AS "#️⃣"
         FROM   "assignment.3"
       ),
       "where.1"("⚙️") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("p", "p0", "#️⃣") AS (
         SELECT "assignment.4"."p" AS "p",
                "assignment.4"."p0" AS "p0",
                "assignment.4"."#️⃣" AS "#️⃣"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS DISTINCT FROM TRUE
       ),
       "jump.1"("#️⃣", "p", "🏷️", "p0") AS (
         SELECT "where.2"."#️⃣" AS "#️⃣",
                "where.2"."p" AS "p",
                'start.2' AS "🏷️",
                "where.2"."p0" AS "p0"
         FROM   "where.2"
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.1"."⚙️"
         FROM   "where.1"
         WHERE  FALSE
       )
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS point) AS "📊",
             CAST((NULL) AS point) AS "p0",
             CAST((NULL) AS point) AS "p"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS point) AS "📊",
             CAST(("jump.1"."p0") AS point) AS "p0",
             CAST(("jump.1"."p") AS point) AS "p"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;