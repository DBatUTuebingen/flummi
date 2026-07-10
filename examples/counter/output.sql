WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊.1", "v") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int) AS "📊.1",
            CAST((NULL) AS int) AS "v")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("⚙️", "#️⃣", "v") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."v" AS "v"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("⚙️", "#️⃣", "v") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣",
                CAST((0) AS int) AS "v"
         FROM   "start.1"
       ),
       "merge.1"("⚙️", "#️⃣", "v") AS (
         (SELECT "assignment.1"."⚙️" AS "⚙️",
                 "assignment.1"."#️⃣" AS "#️⃣",
                 "assignment.1"."v" AS "v"
          FROM   "assignment.1")
           UNION ALL
         (SELECT "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."v" AS "v"
          FROM   "start.2")
       ),
       "emit.1"("⚙️", "#️⃣", "📊.1", "v") AS (
         SELECT "merge.1"."⚙️" AS "⚙️",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."v" AS "📊.1",
                "merge.1"."v" AS "v"
         FROM   "merge.1"
       ),
       "assignment.2"("⚙️", "#️⃣", "v") AS (
         SELECT "emit.1"."⚙️" AS "⚙️",
                "emit.1"."#️⃣" AS "#️⃣",
                CAST((("emit.1"."v") + 1) AS int) AS "v"
         FROM   "emit.1"
       ),
       "assignment.3"("⚙️", "v", "🔍", "#️⃣") AS (
         SELECT "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."v" AS "v",
                CAST((("assignment.2"."v") < 10) AS boolean) AS "🔍",
                "assignment.2"."#️⃣" AS "#️⃣"
         FROM   "assignment.2"
       ),
       "where.1"("⚙️", "#️⃣", "v") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."v" AS "v"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("⚙️") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS DISTINCT FROM TRUE
       ),
       "jump.1"("#️⃣", "🏷️", "v") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                'start.2' AS "🏷️",
                "where.1"."v" AS "v"
         FROM   "where.1"
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.2"."⚙️"
         FROM   "where.2"
         WHERE  FALSE
       )
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊.1") AS int) AS "📊.1",
             CAST((NULL) AS int) AS "v"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int) AS "📊.1",
             CAST(("jump.1"."v") AS int) AS "v"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;