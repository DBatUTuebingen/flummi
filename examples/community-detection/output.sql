WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "community", "node") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int[]) AS "📊",
            CAST((NULL) AS int) AS "community",
            CAST((NULL) AS int) AS "node")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("⚙️", "#️⃣", "community", "node") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."community" AS "community",
                "🔄"."node" AS "node"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "fork.1"("⚙️", "#️⃣", "node") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣",
                "ℚ"."node" AS "node"
         FROM   "start.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "assignment.1"("⚙️", "#️⃣", "community", "node") AS (
         SELECT "fork.1"."⚙️" AS "⚙️",
                "fork.1"."#️⃣" AS "#️⃣",
                CAST((("fork.1"."node")) AS int) AS "community",
                "fork.1"."node" AS "node"
         FROM   "fork.1"
       ),
       "merge.1"("⚙️", "#️⃣", "community", "node") AS (
         (SELECT "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."community" AS "community",
                 "start.2"."node" AS "node"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.1"."⚙️" AS "⚙️",
                 "assignment.1"."#️⃣" AS "#️⃣",
                 "assignment.1"."community" AS "community",
                 "assignment.1"."node" AS "node"
          FROM   "assignment.1")
       ),
       "assignment.2"("old_communitys", "⚙️", "#️⃣", "community", "node") AS (
         SELECT CAST((bit_xor(DISTINCT ("merge.1"."community")) OVER ()) AS int) AS "old_communitys",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."community" AS "community",
                "merge.1"."node" AS "node"
         FROM   "merge.1"
       ),
       "fork.2"("old_communitys", "⚙️", "#️⃣", "cond", "community", "node") AS (
         SELECT "assignment.2"."old_communitys" AS "old_communitys",
                "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."#️⃣" AS "#️⃣",
                "ℚ"."cond" AS "cond",
                "assignment.2"."community" AS "community",
                "assignment.2"."node" AS "node"
         FROM   "assignment.2",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("cond")
       ),
       "where.1"("old_communitys", "⚙️", "#️⃣", "community", "node") AS (
         SELECT "fork.2"."old_communitys" AS "old_communitys",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."community" AS "community",
                "fork.2"."node" AS "node"
         FROM   "fork.2"
         WHERE  "fork.2"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("old_communitys", "⚙️", "#️⃣", "community", "node") AS (
         SELECT "fork.2"."old_communitys" AS "old_communitys",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."community" AS "community",
                "fork.2"."node" AS "node"
         FROM   "fork.2"
         WHERE  "fork.2"."cond" IS DISTINCT FROM TRUE
       ),
       "fork.3"("old_communitys", "⚙️", "#️⃣", "community", "node") AS (
         SELECT "where.2"."old_communitys" AS "old_communitys",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."#️⃣" AS "#️⃣",
                "where.2"."community" AS "community",
                "ℚ"."node" AS "node"
         FROM   "where.2",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("where.2"."node")) AS "ℚ"("node")
       ),
       "gather.1"("old_communitys", "⚙️", "#️⃣", "community", "node") AS (
         SELECT "fork.3"."old_communitys" AS "old_communitys",
                "fork.3"."⚙️" AS "⚙️",
                "fork.3"."#️⃣" AS "#️⃣",
                mode(("fork.3"."community") ORDER BY ("fork.3"."community")) AS "community",
                "fork.3"."node" AS "node"
         FROM   "fork.3"
         GROUP  BY "fork.3"."old_communitys",
                   "fork.3"."⚙️",
                   "fork.3"."#️⃣",
                   "fork.3"."node"
         HAVING COUNT(*) > 0
       ),
       "merge.2"("old_communitys", "⚙️", "#️⃣", "community", "node") AS (
         (SELECT "gather.1"."old_communitys" AS "old_communitys",
                 "gather.1"."⚙️" AS "⚙️",
                 "gather.1"."#️⃣" AS "#️⃣",
                 "gather.1"."community" AS "community",
                 "gather.1"."node" AS "node"
          FROM   "gather.1")
           UNION ALL
         (SELECT "where.1"."old_communitys" AS "old_communitys",
                 "where.1"."⚙️" AS "⚙️",
                 "where.1"."#️⃣" AS "#️⃣",
                 "where.1"."community" AS "community",
                 "where.1"."node" AS "node"
          FROM   "where.1")
       ),
       "gather.2"("old_communitys", "⚙️", "#️⃣", "community", "node") AS (
         SELECT "merge.2"."old_communitys" AS "old_communitys",
                "merge.2"."⚙️" AS "⚙️",
                "merge.2"."#️⃣" AS "#️⃣",
                min(("merge.2"."community")) AS "community",
                "merge.2"."node" AS "node"
         FROM   "merge.2"
         GROUP  BY "merge.2"."old_communitys",
                   "merge.2"."⚙️",
                   "merge.2"."#️⃣",
                   "merge.2"."node"
         HAVING COUNT(*) > 0
       ),
       "assignment.3"("old_communitys", "new_communitys", "⚙️", "#️⃣", "community", "node") AS (
         SELECT "gather.2"."old_communitys" AS "old_communitys",
                CAST((bit_xor(DISTINCT ("gather.2"."community")) OVER ()) AS int) AS "new_communitys",
                "gather.2"."⚙️" AS "⚙️",
                "gather.2"."#️⃣" AS "#️⃣",
                "gather.2"."community" AS "community",
                "gather.2"."node" AS "node"
         FROM   "gather.2"
       ),
       "assignment.4"("⚙️", "#️⃣", "cond", "community", "node") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."#️⃣" AS "#️⃣",
                CAST((("assignment.3"."old_communitys") <> ("assignment.3"."new_communitys")) AS boolean) AS "cond",
                "assignment.3"."community" AS "community",
                "assignment.3"."node" AS "node"
         FROM   "assignment.3"
       ),
       "where.3"("#️⃣", "community", "node") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."community" AS "community",
                "assignment.4"."node" AS "node"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("⚙️", "#️⃣", "community", "node") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."community" AS "community",
                "assignment.4"."node" AS "node"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS DISTINCT FROM TRUE
       ),
       "gather.3"("⚙️", "#️⃣", "nodes") AS (
         SELECT "where.4"."⚙️" AS "⚙️",
                "where.4"."#️⃣" AS "#️⃣",
                list(("where.4"."node")) AS "nodes"
         FROM   "where.4"
         GROUP  BY "where.4"."⚙️",
                   "where.4"."#️⃣",
                   "where.4"."community"
         HAVING COUNT(*) > 0
       ),
       "jump.1"("node", "#️⃣", "community", "🏷️") AS (
         SELECT "where.3"."node" AS "node",
                "where.3"."#️⃣" AS "#️⃣",
                "where.3"."community" AS "community",
                'start.2' AS "🏷️"
         FROM   "where.3"
       ),
       "emit.1"("⚙️", "📊", "#️⃣") AS (
         SELECT "gather.3"."⚙️" AS "⚙️",
                "gather.3"."nodes" AS "📊",
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
             CAST(("jump.1"."community") AS int) AS "community",
             CAST(("jump.1"."node") AS int) AS "node"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS int[]) AS "📊",
             CAST((NULL) AS int) AS "community",
             CAST((NULL) AS int) AS "node"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;