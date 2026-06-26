WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "node", "community") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int[]) AS "📊",
            CAST((NULL) AS int) AS "node",
            CAST((NULL) AS int) AS "community")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("node", "#️⃣", "⚙️", "community") AS (
         SELECT "🔄"."node" AS "node",
                "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️",
                "🔄"."community" AS "community"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "fork.1"("node", "#️⃣", "⚙️") AS (
         SELECT "ℚ"."node" AS "node",
                "start.1"."#️⃣" AS "#️⃣",
                "start.1"."⚙️" AS "⚙️"
         FROM   "start.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "assignment.1"("node", "#️⃣", "⚙️", "community") AS (
         SELECT "fork.1"."node" AS "node",
                "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."⚙️" AS "⚙️",
                CAST((("fork.1"."node")) AS int) AS "community"
         FROM   "fork.1"
       ),
       "merge.1"("node", "#️⃣", "⚙️", "community") AS (
         (SELECT "start.2"."node" AS "node",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."community" AS "community"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.1"."node" AS "node",
                 "assignment.1"."#️⃣" AS "#️⃣",
                 "assignment.1"."⚙️" AS "⚙️",
                 "assignment.1"."community" AS "community"
          FROM   "assignment.1")
       ),
       "assignment.2"("node", "#️⃣", "old_state", "⚙️", "community") AS (
         SELECT "merge.1"."node" AS "node",
                "merge.1"."#️⃣" AS "#️⃣",
                CAST((bit_xor(("merge.1"."community")) OVER ()) AS int) AS "old_state",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."community" AS "community"
         FROM   "merge.1"
       ),
       "fork.2"("node", "#️⃣", "old_state", "cond", "⚙️", "community") AS (
         SELECT "assignment.2"."node" AS "node",
                "assignment.2"."#️⃣" AS "#️⃣",
                "assignment.2"."old_state" AS "old_state",
                "ℚ"."cond" AS "cond",
                "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."community" AS "community"
         FROM   "assignment.2",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("cond")
       ),
       "where.1"("node", "#️⃣", "old_state", "⚙️", "community") AS (
         SELECT "fork.2"."node" AS "node",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."old_state" AS "old_state",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."community" AS "community"
         FROM   "fork.2"
         WHERE  "fork.2"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("node", "#️⃣", "old_state", "⚙️", "community") AS (
         SELECT "fork.2"."node" AS "node",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."old_state" AS "old_state",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."community" AS "community"
         FROM   "fork.2"
         WHERE  "fork.2"."cond" IS DISTINCT FROM TRUE
       ),
       "fork.3"("node", "#️⃣", "old_state", "⚙️", "community") AS (
         SELECT "ℚ"."node" AS "node",
                "where.2"."#️⃣" AS "#️⃣",
                "where.2"."old_state" AS "old_state",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."community" AS "community"
         FROM   "where.2",
                LATERAL (SELECT there FROM edges WHERE here = ("where.2"."node")
                             UNION ALL
                         SELECT here FROM edges WHERE there = ("where.2"."node")) AS "ℚ"("node")
       ),
       "gather.1"("node", "#️⃣", "old_state", "⚙️", "community") AS (
         SELECT "fork.3"."node" AS "node",
                "fork.3"."#️⃣" AS "#️⃣",
                "fork.3"."old_state" AS "old_state",
                "fork.3"."⚙️" AS "⚙️",
                mode(("fork.3"."community") ORDER BY ("fork.3"."community")) AS "community"
         FROM   "fork.3"
         GROUP  BY "fork.3"."node",
                   "fork.3"."#️⃣",
                   "fork.3"."old_state",
                   "fork.3"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "merge.2"("node", "#️⃣", "old_state", "⚙️", "community") AS (
         (SELECT "where.1"."node" AS "node",
                 "where.1"."#️⃣" AS "#️⃣",
                 "where.1"."old_state" AS "old_state",
                 "where.1"."⚙️" AS "⚙️",
                 "where.1"."community" AS "community"
          FROM   "where.1")
           UNION ALL
         (SELECT "gather.1"."node" AS "node",
                 "gather.1"."#️⃣" AS "#️⃣",
                 "gather.1"."old_state" AS "old_state",
                 "gather.1"."⚙️" AS "⚙️",
                 "gather.1"."community" AS "community"
          FROM   "gather.1")
       ),
       "gather.2"("node", "#️⃣", "old_state", "⚙️", "community") AS (
         SELECT "merge.2"."node" AS "node",
                "merge.2"."#️⃣" AS "#️⃣",
                "merge.2"."old_state" AS "old_state",
                "merge.2"."⚙️" AS "⚙️",
                min(("merge.2"."community")) AS "community"
         FROM   "merge.2"
         GROUP  BY "merge.2"."node",
                   "merge.2"."#️⃣",
                   "merge.2"."old_state",
                   "merge.2"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "assignment.3"("node", "#️⃣", "old_state", "new_state", "⚙️", "community") AS (
         SELECT "gather.2"."node" AS "node",
                "gather.2"."#️⃣" AS "#️⃣",
                "gather.2"."old_state" AS "old_state",
                CAST((bit_xor(("gather.2"."community")) OVER ()) AS int) AS "new_state",
                "gather.2"."⚙️" AS "⚙️",
                "gather.2"."community" AS "community"
         FROM   "gather.2"
       ),
       "assignment.4"("node", "#️⃣", "cond", "⚙️", "community") AS (
         SELECT "assignment.3"."node" AS "node",
                "assignment.3"."#️⃣" AS "#️⃣",
                CAST((("assignment.3"."old_state") = ("assignment.3"."new_state")) AS boolean) AS "cond",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."community" AS "community"
         FROM   "assignment.3"
       ),
       "where.3"("node", "#️⃣", "⚙️", "community") AS (
         SELECT "assignment.4"."node" AS "node",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."community" AS "community"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("node", "#️⃣", "community") AS (
         SELECT "assignment.4"."node" AS "node",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."community" AS "community"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS DISTINCT FROM TRUE
       ),
       "gather.3"("#️⃣", "nodes", "⚙️") AS (
         SELECT "where.3"."#️⃣" AS "#️⃣",
                list(("where.3"."node") ORDER BY ("where.3"."node")) AS "nodes",
                "where.3"."⚙️" AS "⚙️"
         FROM   "where.3"
         GROUP  BY "where.3"."#️⃣",
                   "where.3"."⚙️",
                   "where.3"."community"
         HAVING COUNT(*) > 0
       ),
       "jump.1"("🏷️", "node", "community", "#️⃣") AS (
         SELECT 'start.2' AS "🏷️",
                "where.4"."node" AS "node",
                "where.4"."community" AS "community",
                "where.4"."#️⃣" AS "#️⃣"
         FROM   "where.4"
       ),
       "emit.1"("#️⃣", "📊", "⚙️") AS (
         SELECT "gather.3"."#️⃣" AS "#️⃣",
                "gather.3"."nodes" AS "📊",
                "gather.3"."⚙️" AS "⚙️"
         FROM   "gather.3"
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       )
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊",
             CAST(("jump.1"."node") AS int) AS "node",
             CAST(("jump.1"."community") AS int) AS "community"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS int[]) AS "📊",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS int) AS "community"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;