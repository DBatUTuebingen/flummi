WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊.1", "📊.2", "components", "node", "component") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int) AS "📊.1",
            CAST((NULL) AS int[]) AS "📊.2",
            CAST((NULL) AS int) AS "components",
            CAST((NULL) AS int) AS "node",
            CAST((NULL) AS int) AS "component")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("components", "⚙️", "node", "#️⃣", "component") AS (
         SELECT "🔄"."components" AS "components",
                NULL AS "⚙️",
                "🔄"."node" AS "node",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."component" AS "component"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "fork.1"("node", "#️⃣", "⚙️") AS (
         SELECT CAST(("ℚ"."node") AS int) AS "node",
                "start.1"."#️⃣" AS "#️⃣",
                "start.1"."⚙️" AS "⚙️"
         FROM   "start.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "assignment.1"("⚙️", "node", "#️⃣", "component") AS (
         SELECT "fork.1"."⚙️" AS "⚙️",
                "fork.1"."node" AS "node",
                "fork.1"."#️⃣" AS "#️⃣",
                CAST((("fork.1"."node")) AS int) AS "component"
         FROM   "fork.1"
       ),
       "assignment.2"("components", "node", "#️⃣", "component", "⚙️") AS (
         SELECT CAST((bit_xor(("assignment.1"."component")) OVER ()) AS int) AS "components",
                "assignment.1"."node" AS "node",
                "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."component" AS "component",
                "assignment.1"."⚙️" AS "⚙️"
         FROM   "assignment.1"
       ),
       "merge.1"("components", "node", "#️⃣", "component", "⚙️") AS (
         (SELECT "assignment.2"."components" AS "components",
                 "assignment.2"."node" AS "node",
                 "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."component" AS "component",
                 "assignment.2"."⚙️" AS "⚙️"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."components" AS "components",
                 "start.2"."node" AS "node",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."component" AS "component",
                 "start.2"."⚙️" AS "⚙️"
          FROM   "start.2")
       ),
       "fork.2"("components", "⚙️", "node", "#️⃣", "component") AS (
         SELECT "merge.1"."components" AS "components",
                "merge.1"."⚙️" AS "⚙️",
                CAST(("ℚ"."node") AS int) AS "node",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."component" AS "component"
         FROM   "merge.1",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("merge.1"."node")
                         AND    there > ("merge.1"."component")) AS "ℚ"("node")
       ),
       "gather.1"("components", "⚙️", "node", "#️⃣", "component") AS (
         SELECT "fork.2"."components" AS "components",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."node" AS "node",
                "fork.2"."#️⃣" AS "#️⃣",
                CAST((min(("fork.2"."component"))) AS int) AS "component"
         FROM   "fork.2"
         GROUP  BY "fork.2"."components",
                   "fork.2"."node",
                   "fork.2"."#️⃣",
                   "fork.2"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "assignment.3"("components", "⚙️", "node", "#️⃣", "component", "old_components") AS (
         SELECT CAST((bit_xor(("gather.1"."component")) OVER ()) AS int) AS "components",
                "gather.1"."⚙️" AS "⚙️",
                "gather.1"."node" AS "node",
                "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."component" AS "component",
                CAST((("gather.1"."components")) AS int) AS "old_components"
         FROM   "gather.1"
       ),
       "assignment.4"("components", "node", "#️⃣", "component", "🔍", "⚙️") AS (
         SELECT "assignment.3"."components" AS "components",
                "assignment.3"."node" AS "node",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."component" AS "component",
                CAST((("assignment.3"."old_components") = ("assignment.3"."components")) AS boolean) AS "🔍",
                "assignment.3"."⚙️" AS "⚙️"
         FROM   "assignment.3"
       ),
       "where.1"("⚙️", "node", "#️⃣", "component") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."node" AS "node",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."component" AS "component"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("components", "⚙️", "node", "#️⃣", "component") AS (
         SELECT "assignment.4"."components" AS "components",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."node" AS "node",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."component" AS "component"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS DISTINCT FROM TRUE
       ),
       "gather.2"("nodes", "component", "#️⃣", "⚙️") AS (
         SELECT CAST((list(("where.1"."node"))) AS int[]) AS "nodes",
                "where.1"."component" AS "component",
                "where.1"."#️⃣" AS "#️⃣",
                "where.1"."⚙️" AS "⚙️"
         FROM   "where.1"
         GROUP  BY "where.1"."⚙️",
                   "where.1"."#️⃣",
                   "where.1"."component"
         HAVING COUNT(*) > 0
       ),
       "jump.1"("🏷️", "#️⃣", "components", "node", "component") AS (
         SELECT 'start.2' AS "🏷️",
                "where.2"."#️⃣" AS "#️⃣",
                "where.2"."components" AS "components",
                "where.2"."node" AS "node",
                "where.2"."component" AS "component"
         FROM   "where.2"
       ),
       "emit.1"("⚙️", "📊.2", "📊.1", "#️⃣") AS (
         SELECT "gather.2"."⚙️" AS "⚙️",
                "gather.2"."nodes" AS "📊.2",
                "gather.2"."component" AS "📊.1",
                "gather.2"."#️⃣" AS "#️⃣"
         FROM   "gather.2"
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       )
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int) AS "📊.1",
             CAST((NULL) AS int[]) AS "📊.2",
             CAST(("jump.1"."components") AS int) AS "components",
             CAST(("jump.1"."node") AS int) AS "node",
             CAST(("jump.1"."component") AS int) AS "component"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊.1") AS int) AS "📊.1",
             CAST(("emit.1"."📊.2") AS int[]) AS "📊.2",
             CAST((NULL) AS int) AS "components",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS int) AS "component"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊.1",
       "🔄"."📊.2"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;