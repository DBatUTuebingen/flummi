WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "node", "component") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int[]) AS "📊",
            CAST((NULL) AS int) AS "node",
            CAST((NULL) AS int) AS "component")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("node", "⚙️", "component", "#️⃣") AS (
         SELECT "🔄"."node" AS "node",
                NULL AS "⚙️",
                "🔄"."component" AS "component",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "fork.1"("node", "⚙️", "#️⃣") AS (
         SELECT "ℚ"."node" AS "node",
                "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣"
         FROM   "start.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "assignment.1"("node", "⚙️", "#️⃣", "component") AS (
         SELECT "fork.1"."node" AS "node",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."#️⃣" AS "#️⃣",
                CAST((("fork.1"."node")) AS int) AS "component"
         FROM   "fork.1"
       ),
       "merge.1"("node", "⚙️", "#️⃣", "component") AS (
         (SELECT "assignment.1"."node" AS "node",
                 "assignment.1"."⚙️" AS "⚙️",
                 "assignment.1"."#️⃣" AS "#️⃣",
                 "assignment.1"."component" AS "component"
          FROM   "assignment.1")
           UNION ALL
         (SELECT "start.2"."node" AS "node",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."component" AS "component"
          FROM   "start.2")
       ),
       "assignment.2"("⚙️", "old_components", "#️⃣", "node", "component") AS (
         SELECT "merge.1"."⚙️" AS "⚙️",
                CAST((sum(DISTINCT ("merge.1"."component")) OVER ()) AS uhugeint) AS "old_components",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."node" AS "node",
                "merge.1"."component" AS "component"
         FROM   "merge.1"
       ),
       "fork.2"("⚙️", "old_components", "#️⃣", "node", "component") AS (
         SELECT "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."old_components" AS "old_components",
                "assignment.2"."#️⃣" AS "#️⃣",
                "ℚ"."node" AS "node",
                "assignment.2"."component" AS "component"
         FROM   "assignment.2",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("assignment.2"."node")
                         AND    there > ("assignment.2"."component")) AS "ℚ"("node")
       ),
       "gather.1"("⚙️", "old_components", "#️⃣", "node", "component") AS (
         SELECT "fork.2"."⚙️" AS "⚙️",
                "fork.2"."old_components" AS "old_components",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."node" AS "node",
                min(("fork.2"."component")) AS "component"
         FROM   "fork.2"
         GROUP  BY "fork.2"."⚙️",
                   "fork.2"."old_components",
                   "fork.2"."node",
                   "fork.2"."#️⃣"
         HAVING COUNT(*) > 0
       ),
       "assignment.3"("⚙️", "old_components", "node", "new_components", "component", "#️⃣") AS (
         SELECT "gather.1"."⚙️" AS "⚙️",
                "gather.1"."old_components" AS "old_components",
                "gather.1"."node" AS "node",
                CAST((sum(DISTINCT ("gather.1"."component")) OVER ()) AS uhugeint) AS "new_components",
                "gather.1"."component" AS "component",
                "gather.1"."#️⃣" AS "#️⃣"
         FROM   "gather.1"
       ),
       "assignment.4"("⚙️", "#️⃣", "node", "cond", "component") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."node" AS "node",
                CAST((("assignment.3"."old_components") <> ("assignment.3"."new_components")) AS boolean) AS "cond",
                "assignment.3"."component" AS "component"
         FROM   "assignment.3"
       ),
       "where.1"("node", "component", "#️⃣") AS (
         SELECT "assignment.4"."node" AS "node",
                "assignment.4"."component" AS "component",
                "assignment.4"."#️⃣" AS "#️⃣"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("node", "⚙️", "#️⃣", "component") AS (
         SELECT "assignment.4"."node" AS "node",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."component" AS "component"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS DISTINCT FROM TRUE
       ),
       "gather.2"("⚙️", "nodes", "#️⃣") AS (
         SELECT "where.2"."⚙️" AS "⚙️",
                list(("where.2"."node")) AS "nodes",
                "where.2"."#️⃣" AS "#️⃣"
         FROM   "where.2"
         GROUP  BY "where.2"."⚙️",
                   "where.2"."#️⃣",
                   "where.2"."component"
         HAVING COUNT(*) > 0
       ),
       "jump.1"("🏷️", "node", "component", "#️⃣") AS (
         SELECT 'start.2' AS "🏷️",
                "where.1"."node" AS "node",
                "where.1"."component" AS "component",
                "where.1"."#️⃣" AS "#️⃣"
         FROM   "where.1"
       ),
       "emit.1"("⚙️", "#️⃣", "📊") AS (
         SELECT "gather.2"."⚙️" AS "⚙️",
                "gather.2"."#️⃣" AS "#️⃣",
                "gather.2"."nodes" AS "📊"
         FROM   "gather.2"
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
             CAST(("jump.1"."component") AS int) AS "component"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS int[]) AS "📊",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS int) AS "component"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;