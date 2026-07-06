WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "node", "state", "community") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int[]) AS "📊",
            CAST((NULL) AS int) AS "node",
            CAST((NULL) AS int) AS "state",
            CAST((NULL) AS int) AS "community")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("node", "⚙️", "state", "#️⃣", "community") AS (
         SELECT "🔄"."node" AS "node",
                NULL AS "⚙️",
                "🔄"."state" AS "state",
                "🔄"."#️⃣" AS "#️⃣",
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
       "assignment.1"("node", "#️⃣", "community", "⚙️") AS (
         SELECT "fork.1"."node" AS "node",
                "fork.1"."#️⃣" AS "#️⃣",
                CAST((("fork.1"."node")) AS int) AS "community",
                "fork.1"."⚙️" AS "⚙️"
         FROM   "fork.1"
       ),
       "assignment.2"("node", "⚙️", "#️⃣", "state", "community") AS (
         SELECT "assignment.1"."node" AS "node",
                "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."#️⃣" AS "#️⃣",
                CAST((bit_xor(("assignment.1"."community")) OVER ()) AS int) AS "state",
                "assignment.1"."community" AS "community"
         FROM   "assignment.1"
       ),
       "merge.1"("node", "⚙️", "#️⃣", "state", "community") AS (
         (SELECT "assignment.2"."node" AS "node",
                 "assignment.2"."⚙️" AS "⚙️",
                 "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."state" AS "state",
                 "assignment.2"."community" AS "community"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."node" AS "node",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."state" AS "state",
                 "start.2"."community" AS "community"
          FROM   "start.2")
       ),
       "fork.2"("node", "⚙️", "state", "cond", "#️⃣", "community") AS (
         SELECT "merge.1"."node" AS "node",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."state" AS "state",
                "ℚ"."cond" AS "cond",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."community" AS "community"
         FROM   "merge.1",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("cond")
       ),
       "assignment.3"("node", "⚙️", "state", "#️⃣", "community", "🔍") AS (
         SELECT "fork.2"."node" AS "node",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."state" AS "state",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."community" AS "community",
                CAST((("fork.2"."cond")) AS boolean) AS "🔍"
         FROM   "fork.2"
       ),
       "where.1"("node", "⚙️", "#️⃣", "state", "community") AS (
         SELECT "assignment.3"."node" AS "node",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."state" AS "state",
                "assignment.3"."community" AS "community"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("node", "⚙️", "#️⃣", "state", "community") AS (
         SELECT "assignment.3"."node" AS "node",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."state" AS "state",
                "assignment.3"."community" AS "community"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS DISTINCT FROM TRUE
       ),
       "fork.3"("node", "⚙️", "#️⃣", "state", "community") AS (
         SELECT "ℚ"."node" AS "node",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."#️⃣" AS "#️⃣",
                "where.2"."state" AS "state",
                "where.2"."community" AS "community"
         FROM   "where.2",
                LATERAL (SELECT there FROM edges WHERE here = ("where.2"."node")
                             UNION ALL
                         SELECT here FROM edges WHERE there = ("where.2"."node")) AS "ℚ"("node")
       ),
       "gather.1"("node", "⚙️", "#️⃣", "state", "community") AS (
         SELECT "fork.3"."node" AS "node",
                "fork.3"."⚙️" AS "⚙️",
                "fork.3"."#️⃣" AS "#️⃣",
                "fork.3"."state" AS "state",
                CAST((mode(("fork.3"."community") ORDER BY ("fork.3"."community"))) AS int) AS "community"
         FROM   "fork.3"
         GROUP  BY "fork.3"."node",
                   "fork.3"."⚙️",
                   "fork.3"."#️⃣",
                   "fork.3"."state"
         HAVING COUNT(*) > 0
       ),
       "merge.2"("node", "⚙️", "#️⃣", "state", "community") AS (
         (SELECT "gather.1"."node" AS "node",
                 "gather.1"."⚙️" AS "⚙️",
                 "gather.1"."#️⃣" AS "#️⃣",
                 "gather.1"."state" AS "state",
                 "gather.1"."community" AS "community"
          FROM   "gather.1")
           UNION ALL
         (SELECT "where.1"."node" AS "node",
                 "where.1"."⚙️" AS "⚙️",
                 "where.1"."#️⃣" AS "#️⃣",
                 "where.1"."state" AS "state",
                 "where.1"."community" AS "community"
          FROM   "where.1")
       ),
       "gather.2"("node", "⚙️", "#️⃣", "state", "community") AS (
         SELECT "merge.2"."node" AS "node",
                "merge.2"."⚙️" AS "⚙️",
                "merge.2"."#️⃣" AS "#️⃣",
                "merge.2"."state" AS "state",
                CAST((min(("merge.2"."community"))) AS int) AS "community"
         FROM   "merge.2"
         GROUP  BY "merge.2"."node",
                   "merge.2"."⚙️",
                   "merge.2"."#️⃣",
                   "merge.2"."state"
         HAVING COUNT(*) > 0
       ),
       "assignment.4"("node", "⚙️", "old_state", "#️⃣", "state", "community") AS (
         SELECT "gather.2"."node" AS "node",
                "gather.2"."⚙️" AS "⚙️",
                CAST((("gather.2"."state")) AS int) AS "old_state",
                "gather.2"."#️⃣" AS "#️⃣",
                CAST((bit_xor(("gather.2"."community")) OVER ()) AS int) AS "state",
                "gather.2"."community" AS "community"
         FROM   "gather.2"
       ),
       "assignment.5"("node", "⚙️", "state", "cond", "#️⃣", "community") AS (
         SELECT "assignment.4"."node" AS "node",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."state" AS "state",
                CAST((("assignment.4"."old_state") = ("assignment.4"."state")) AS boolean) AS "cond",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."community" AS "community"
         FROM   "assignment.4"
       ),
       "assignment.6"("node", "⚙️", "state", "#️⃣", "community", "🔍") AS (
         SELECT "assignment.5"."node" AS "node",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."state" AS "state",
                "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."community" AS "community",
                CAST((("assignment.5"."cond")) AS boolean) AS "🔍"
         FROM   "assignment.5"
       ),
       "where.3"("node", "#️⃣", "community", "⚙️") AS (
         SELECT "assignment.6"."node" AS "node",
                "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."community" AS "community",
                "assignment.6"."⚙️" AS "⚙️"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("node", "⚙️", "state", "#️⃣", "community") AS (
         SELECT "assignment.6"."node" AS "node",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."state" AS "state",
                "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."community" AS "community"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS DISTINCT FROM TRUE
       ),
       "gather.3"("nodes", "⚙️", "#️⃣") AS (
         SELECT CAST((list(("where.3"."node") ORDER BY ("where.3"."node"))) AS int[]) AS "nodes",
                "where.3"."⚙️" AS "⚙️",
                "where.3"."#️⃣" AS "#️⃣"
         FROM   "where.3"
         GROUP  BY "where.3"."#️⃣",
                   "where.3"."community",
                   "where.3"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "jump.1"("🏷️", "node", "state", "#️⃣", "community") AS (
         SELECT 'start.2' AS "🏷️",
                "where.4"."node" AS "node",
                "where.4"."state" AS "state",
                "where.4"."#️⃣" AS "#️⃣",
                "where.4"."community" AS "community"
         FROM   "where.4"
       ),
       "emit.1"("📊", "⚙️", "#️⃣") AS (
         SELECT "gather.3"."nodes" AS "📊",
                "gather.3"."⚙️" AS "⚙️",
                "gather.3"."#️⃣" AS "#️⃣"
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
             CAST(("jump.1"."state") AS int) AS "state",
             CAST(("jump.1"."community") AS int) AS "community"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS int[]) AS "📊",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS int) AS "state",
             CAST((NULL) AS int) AS "community"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;