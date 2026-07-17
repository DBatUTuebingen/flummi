WITH RECURSIVE
  "🔄"("#️⃣", "component", "components", "node", "🏷️", "📊.1", "📊.2") AS (
    (SELECT CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int) AS "component",
            CAST((NULL) AS int) AS "components",
            CAST((NULL) AS int) AS "node",
            CAST(('start.1') AS text) AS "🏷️",
            CAST((NULL) AS int) AS "📊.1",
            CAST((NULL) AS int[]) AS "📊.2")
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
       "assignment.1"("#️⃣", "component", "node", "⚙️") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                CAST((("fork.1"."node")) AS int) AS "component",
                "fork.1"."node" AS "node",
                "fork.1"."⚙️" AS "⚙️"
         FROM   "fork.1"
       ),
       "assignment.2"("#️⃣", "component", "components", "node", "⚙️") AS (
         SELECT "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."component" AS "component",
                CAST((bit_xor(("assignment.1"."component")) OVER ()) AS int) AS "components",
                "assignment.1"."node" AS "node",
                "assignment.1"."⚙️" AS "⚙️"
         FROM   "assignment.1"
       ),
       "start.2"("#️⃣", "component", "components", "node", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                "🔄"."component" AS "component",
                "🔄"."components" AS "components",
                "🔄"."node" AS "node",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "merge.1"("#️⃣", "component", "components", "node", "⚙️") AS (
         (SELECT "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."component" AS "component",
                 "assignment.2"."components" AS "components",
                 "assignment.2"."node" AS "node",
                 "assignment.2"."⚙️" AS "⚙️"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."component" AS "component",
                 "start.2"."components" AS "components",
                 "start.2"."node" AS "node",
                 "start.2"."⚙️" AS "⚙️"
          FROM   "start.2")
       ),
       "fork.2"("#️⃣", "component", "components", "node", "⚙️") AS (
         SELECT "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."component" AS "component",
                "merge.1"."components" AS "components",
                CAST(("ℚ"."node") AS int) AS "node",
                "merge.1"."⚙️" AS "⚙️"
         FROM   "merge.1",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("merge.1"."node")
                         AND    there > ("merge.1"."component")) AS "ℚ"("node")
       ),
       "gather.1"("#️⃣", "component", "components", "node", "⚙️") AS (
         SELECT "fork.2"."#️⃣" AS "#️⃣",
                CAST((min(("fork.2"."component"))) AS int) AS "component",
                "fork.2"."components" AS "components",
                "fork.2"."node" AS "node",
                "fork.2"."⚙️" AS "⚙️"
         FROM   "fork.2"
         GROUP  BY "fork.2"."#️⃣",
                   "fork.2"."components",
                   "fork.2"."node",
                   "fork.2"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "assignment.3"("#️⃣", "component", "components", "node", "old_components", "⚙️") AS (
         SELECT "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."component" AS "component",
                CAST((bit_xor(("gather.1"."component")) OVER ()) AS int) AS "components",
                "gather.1"."node" AS "node",
                CAST((("gather.1"."components")) AS int) AS "old_components",
                "gather.1"."⚙️" AS "⚙️"
         FROM   "gather.1"
       ),
       "assignment.4"("#️⃣", "component", "components", "node", "⚙️", "🔍") AS (
         SELECT "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."component" AS "component",
                "assignment.3"."components" AS "components",
                "assignment.3"."node" AS "node",
                "assignment.3"."⚙️" AS "⚙️",
                CAST((("assignment.3"."old_components") = ("assignment.3"."components")) AS boolean) AS "🔍"
         FROM   "assignment.3"
       ),
       "where.1"("#️⃣", "component", "node", "⚙️") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."component" AS "component",
                "assignment.4"."node" AS "node",
                "assignment.4"."⚙️" AS "⚙️"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "gather.2"("#️⃣", "component", "nodes", "⚙️") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                "where.1"."component" AS "component",
                CAST((list(("where.1"."node"))) AS int[]) AS "nodes",
                "where.1"."⚙️" AS "⚙️"
         FROM   "where.1"
         GROUP  BY "where.1"."#️⃣",
                   "where.1"."component",
                   "where.1"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "emit.1"("#️⃣", "⚙️", "📊.1", "📊.2") AS (
         SELECT "gather.2"."#️⃣" AS "#️⃣",
                "gather.2"."⚙️" AS "⚙️",
                "gather.2"."component" AS "📊.1",
                "gather.2"."nodes" AS "📊.2"
         FROM   "gather.2"
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       ),
       "where.2"("#️⃣", "component", "components", "node", "⚙️") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."component" AS "component",
                "assignment.4"."components" AS "components",
                "assignment.4"."node" AS "node",
                "assignment.4"."⚙️" AS "⚙️"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS DISTINCT FROM TRUE
       ),
       "jump.1"("#️⃣", "component", "components", "node", "🏷️") AS (
         SELECT "where.2"."#️⃣" AS "#️⃣",
                "where.2"."component" AS "component",
                "where.2"."components" AS "components",
                "where.2"."node" AS "node",
                'start.2' AS "🏷️"
         FROM   "where.2"
       )
     (SELECT CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST((NULL) AS int) AS "component",
             CAST((NULL) AS int) AS "components",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."📊.1") AS int) AS "📊.1",
             CAST(("emit.1"."📊.2") AS int[]) AS "📊.2"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST(("jump.1"."component") AS int) AS "component",
             CAST(("jump.1"."components") AS int) AS "components",
             CAST(("jump.1"."node") AS int) AS "node",
             CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST((NULL) AS int) AS "📊.1",
             CAST((NULL) AS int[]) AS "📊.2"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊.1",
       "🔄"."📊.2"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;