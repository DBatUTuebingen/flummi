WITH RECURSIVE
  "🔄"("#️⃣", "community", "node", "state", "🏷️", "📊.1") AS (
    (SELECT CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int) AS "community",
            CAST((NULL) AS int) AS "node",
            CAST((NULL) AS int) AS "state",
            CAST(('start.1') AS text) AS "🏷️",
            CAST((NULL) AS int[]) AS "📊.1")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "fork.1"("#️⃣", "node", "⚙️") AS (
         SELECT "start.1"."#️⃣" AS "#️⃣",
                CAST(("ℚ"."node") AS int) AS "node",
                "start.1"."⚙️" AS "⚙️"
         FROM   "start.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "assignment.1"("#️⃣", "community", "node", "⚙️") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                CAST((("fork.1"."node")) AS int) AS "community",
                "fork.1"."node" AS "node",
                "fork.1"."⚙️" AS "⚙️"
         FROM   "fork.1"
       ),
       "assignment.2"("#️⃣", "community", "node", "state", "⚙️") AS (
         SELECT "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."community" AS "community",
                "assignment.1"."node" AS "node",
                CAST((bit_xor(("assignment.1"."community")) OVER ()) AS int) AS "state",
                "assignment.1"."⚙️" AS "⚙️"
         FROM   "assignment.1"
       ),
       "start.2"("#️⃣", "community", "node", "state", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                "🔄"."community" AS "community",
                "🔄"."node" AS "node",
                "🔄"."state" AS "state",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "merge.1"("#️⃣", "community", "node", "state", "⚙️") AS (
         (SELECT "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."community" AS "community",
                 "assignment.2"."node" AS "node",
                 "assignment.2"."state" AS "state",
                 "assignment.2"."⚙️" AS "⚙️"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."community" AS "community",
                 "start.2"."node" AS "node",
                 "start.2"."state" AS "state",
                 "start.2"."⚙️" AS "⚙️"
          FROM   "start.2")
       ),
       "fork.2"("#️⃣", "community", "flip", "node", "state", "⚙️") AS (
         SELECT "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."community" AS "community",
                CAST(("ℚ"."flip") AS boolean) AS "flip",
                "merge.1"."node" AS "node",
                "merge.1"."state" AS "state",
                "merge.1"."⚙️" AS "⚙️"
         FROM   "merge.1",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("flip")
       ),
       "assignment.3"("#️⃣", "community", "node", "state", "⚙️", "🔍") AS (
         SELECT "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."community" AS "community",
                "fork.2"."node" AS "node",
                "fork.2"."state" AS "state",
                "fork.2"."⚙️" AS "⚙️",
                CAST((("fork.2"."flip")) AS boolean) AS "🔍"
         FROM   "fork.2"
       ),
       "where.1"("#️⃣", "community", "node", "state", "⚙️") AS (
         SELECT "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."community" AS "community",
                "assignment.3"."node" AS "node",
                "assignment.3"."state" AS "state",
                "assignment.3"."⚙️" AS "⚙️"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "fork.3"("#️⃣", "community", "node", "state", "⚙️") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                "where.1"."community" AS "community",
                CAST(("ℚ"."node") AS int) AS "node",
                "where.1"."state" AS "state",
                "where.1"."⚙️" AS "⚙️"
         FROM   "where.1",
                LATERAL (SELECT there FROM edges WHERE here = ("where.1"."node")
                             UNION ALL
                         SELECT here FROM edges WHERE there = ("where.1"."node")) AS "ℚ"("node")
       ),
       "gather.1"("#️⃣", "community", "node", "state", "⚙️") AS (
         SELECT "fork.3"."#️⃣" AS "#️⃣",
                CAST((mode(("fork.3"."community") ORDER BY ("fork.3"."community"))) AS int) AS "community",
                "fork.3"."node" AS "node",
                "fork.3"."state" AS "state",
                "fork.3"."⚙️" AS "⚙️"
         FROM   "fork.3"
         GROUP  BY "fork.3"."#️⃣",
                   "fork.3"."node",
                   "fork.3"."state",
                   "fork.3"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "where.2"("#️⃣", "community", "node", "state", "⚙️") AS (
         SELECT "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."community" AS "community",
                "assignment.3"."node" AS "node",
                "assignment.3"."state" AS "state",
                "assignment.3"."⚙️" AS "⚙️"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS DISTINCT FROM TRUE
       ),
       "merge.2"("#️⃣", "community", "node", "state", "⚙️") AS (
         (SELECT "gather.1"."#️⃣" AS "#️⃣",
                 "gather.1"."community" AS "community",
                 "gather.1"."node" AS "node",
                 "gather.1"."state" AS "state",
                 "gather.1"."⚙️" AS "⚙️"
          FROM   "gather.1")
           UNION ALL
         (SELECT "where.2"."#️⃣" AS "#️⃣",
                 "where.2"."community" AS "community",
                 "where.2"."node" AS "node",
                 "where.2"."state" AS "state",
                 "where.2"."⚙️" AS "⚙️"
          FROM   "where.2")
       ),
       "gather.2"("#️⃣", "community", "node", "state", "⚙️") AS (
         SELECT "merge.2"."#️⃣" AS "#️⃣",
                CAST((min(("merge.2"."community"))) AS int) AS "community",
                "merge.2"."node" AS "node",
                "merge.2"."state" AS "state",
                "merge.2"."⚙️" AS "⚙️"
         FROM   "merge.2"
         GROUP  BY "merge.2"."#️⃣",
                   "merge.2"."node",
                   "merge.2"."state",
                   "merge.2"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "assignment.4"("#️⃣", "community", "node", "old_state", "state", "⚙️") AS (
         SELECT "gather.2"."#️⃣" AS "#️⃣",
                "gather.2"."community" AS "community",
                "gather.2"."node" AS "node",
                CAST((("gather.2"."state")) AS int) AS "old_state",
                CAST((bit_xor(("gather.2"."community")) OVER ()) AS int) AS "state",
                "gather.2"."⚙️" AS "⚙️"
         FROM   "gather.2"
       ),
       "assignment.5"("#️⃣", "community", "node", "state", "⚙️", "🔍") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."community" AS "community",
                "assignment.4"."node" AS "node",
                "assignment.4"."state" AS "state",
                "assignment.4"."⚙️" AS "⚙️",
                CAST((("assignment.4"."old_state") = ("assignment.4"."state")) AS boolean) AS "🔍"
         FROM   "assignment.4"
       ),
       "where.3"("#️⃣", "community", "node", "⚙️") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."community" AS "community",
                "assignment.5"."node" AS "node",
                "assignment.5"."⚙️" AS "⚙️"
         FROM   "assignment.5"
         WHERE  "assignment.5"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "gather.3"("#️⃣", "nodes", "⚙️") AS (
         SELECT "where.3"."#️⃣" AS "#️⃣",
                CAST((list(("where.3"."node") ORDER BY ("where.3"."node"))) AS int[]) AS "nodes",
                "where.3"."⚙️" AS "⚙️"
         FROM   "where.3"
         GROUP  BY "where.3"."#️⃣",
                   "where.3"."community",
                   "where.3"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "emit.1"("#️⃣", "⚙️", "📊.1") AS (
         SELECT "gather.3"."#️⃣" AS "#️⃣",
                "gather.3"."⚙️" AS "⚙️",
                "gather.3"."nodes" AS "📊.1"
         FROM   "gather.3"
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       ),
       "where.4"("#️⃣", "community", "node", "state", "⚙️") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."community" AS "community",
                "assignment.5"."node" AS "node",
                "assignment.5"."state" AS "state",
                "assignment.5"."⚙️" AS "⚙️"
         FROM   "assignment.5"
         WHERE  "assignment.5"."🔍" IS DISTINCT FROM TRUE
       ),
       "jump.1"("#️⃣", "community", "node", "state", "🏷️") AS (
         SELECT "where.4"."#️⃣" AS "#️⃣",
                "where.4"."community" AS "community",
                "where.4"."node" AS "node",
                "where.4"."state" AS "state",
                'start.2' AS "🏷️"
         FROM   "where.4"
       )
     (SELECT CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST((NULL) AS int) AS "community",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS int) AS "state",
             CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."📊.1") AS int[]) AS "📊.1"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST(("jump.1"."community") AS int) AS "community",
             CAST(("jump.1"."node") AS int) AS "node",
             CAST(("jump.1"."state") AS int) AS "state",
             CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST((NULL) AS int[]) AS "📊.1"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;