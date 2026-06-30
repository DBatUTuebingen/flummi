WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "active", "node", "k") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int) AS "📊",
            CAST((NULL) AS boolean) AS "active",
            CAST((NULL) AS int) AS "node",
            CAST((NULL) AS int) AS "k")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("⚙️", "active", "node", "k", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."active" AS "active",
                "🔄"."node" AS "node",
                "🔄"."k" AS "k",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("⚙️", "#️⃣", "k") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣",
                CAST((2) AS int) AS "k"
         FROM   "start.1"
       ),
       "fork.1"("⚙️", "#️⃣", "node", "k") AS (
         SELECT "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."#️⃣" AS "#️⃣",
                "ℚ"."node" AS "node",
                "assignment.1"."k" AS "k"
         FROM   "assignment.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "assignment.2"("⚙️", "active", "node", "k", "#️⃣") AS (
         SELECT "fork.1"."⚙️" AS "⚙️",
                CAST((TRUE) AS boolean) AS "active",
                "fork.1"."node" AS "node",
                "fork.1"."k" AS "k",
                "fork.1"."#️⃣" AS "#️⃣"
         FROM   "fork.1"
       ),
       "merge.1"("⚙️", "active", "node", "k", "#️⃣") AS (
         (SELECT "start.2"."⚙️" AS "⚙️",
                 "start.2"."active" AS "active",
                 "start.2"."node" AS "node",
                 "start.2"."k" AS "k",
                 "start.2"."#️⃣" AS "#️⃣"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.2"."⚙️" AS "⚙️",
                 "assignment.2"."active" AS "active",
                 "assignment.2"."node" AS "node",
                 "assignment.2"."k" AS "k",
                 "assignment.2"."#️⃣" AS "#️⃣"
          FROM   "assignment.2")
       ),
       "assignment.3"("⚙️", "active", "node", "k", "old_nodes", "#️⃣") AS (
         SELECT "merge.1"."⚙️" AS "⚙️",
                "merge.1"."active" AS "active",
                "merge.1"."node" AS "node",
                "merge.1"."k" AS "k",
                CAST((countif(("merge.1"."active")) OVER ()) AS int) AS "old_nodes",
                "merge.1"."#️⃣" AS "#️⃣"
         FROM   "merge.1"
       ),
       "fork.2"("⚙️", "active", "node", "k", "old_nodes", "#️⃣") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."active" AS "active",
                "ℚ"."node" AS "node",
                "assignment.3"."k" AS "k",
                "assignment.3"."old_nodes" AS "old_nodes",
                "assignment.3"."#️⃣" AS "#️⃣"
         FROM   "assignment.3",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("assignment.3"."node")) AS "ℚ"("node")
       ),
       "gather.1"("⚙️", "k", "node", "old_nodes", "#️⃣", "degree") AS (
         SELECT "fork.2"."⚙️" AS "⚙️",
                "fork.2"."k" AS "k",
                "fork.2"."node" AS "node",
                "fork.2"."old_nodes" AS "old_nodes",
                "fork.2"."#️⃣" AS "#️⃣",
                countif(("fork.2"."active")) AS "degree"
         FROM   "fork.2"
         GROUP  BY "fork.2"."⚙️",
                   "fork.2"."node",
                   "fork.2"."k",
                   "fork.2"."old_nodes",
                   "fork.2"."#️⃣"
         HAVING COUNT(*) > 0
       ),
       "assignment.4"("⚙️", "active", "node", "k", "old_nodes", "#️⃣") AS (
         SELECT "gather.1"."⚙️" AS "⚙️",
                CAST((("gather.1"."degree") >= ("gather.1"."k") + 1) AS boolean) AS "active",
                "gather.1"."node" AS "node",
                "gather.1"."k" AS "k",
                "gather.1"."old_nodes" AS "old_nodes",
                "gather.1"."#️⃣" AS "#️⃣"
         FROM   "gather.1"
       ),
       "assignment.5"("⚙️", "active", "node", "k", "old_nodes", "#️⃣", "new_nodes") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."active" AS "active",
                "assignment.4"."node" AS "node",
                "assignment.4"."k" AS "k",
                "assignment.4"."old_nodes" AS "old_nodes",
                "assignment.4"."#️⃣" AS "#️⃣",
                CAST((countif(("assignment.4"."active")) OVER ()) AS int) AS "new_nodes"
         FROM   "assignment.4"
       ),
       "assignment.6"("⚙️", "active", "node", "cond", "k", "#️⃣") AS (
         SELECT "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."active" AS "active",
                "assignment.5"."node" AS "node",
                CAST((("assignment.5"."old_nodes") > ("assignment.5"."new_nodes")) AS boolean) AS "cond",
                "assignment.5"."k" AS "k",
                "assignment.5"."#️⃣" AS "#️⃣"
         FROM   "assignment.5"
       ),
       "where.1"("#️⃣", "node", "active", "k") AS (
         SELECT "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."node" AS "node",
                "assignment.6"."active" AS "active",
                "assignment.6"."k" AS "k"
         FROM   "assignment.6"
         WHERE  "assignment.6"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("⚙️", "active", "node", "#️⃣") AS (
         SELECT "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."active" AS "active",
                "assignment.6"."node" AS "node",
                "assignment.6"."#️⃣" AS "#️⃣"
         FROM   "assignment.6"
         WHERE  "assignment.6"."cond" IS DISTINCT FROM TRUE
       ),
       "jump.1"("#️⃣", "k", "active", "node", "🏷️") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                "where.1"."k" AS "k",
                "where.1"."active" AS "active",
                "where.1"."node" AS "node",
                'start.2' AS "🏷️"
         FROM   "where.1"
       ),
       "where.3"("⚙️", "#️⃣", "node") AS (
         SELECT "where.2"."⚙️" AS "⚙️",
                "where.2"."#️⃣" AS "#️⃣",
                "where.2"."node" AS "node"
         FROM   "where.2"
         WHERE  "where.2"."active" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("⚙️") AS (
         SELECT "where.2"."⚙️" AS "⚙️"
         FROM   "where.2"
         WHERE  "where.2"."active" IS DISTINCT FROM TRUE
       ),
       "emit.1"("⚙️", "📊", "#️⃣") AS (
         SELECT "where.3"."⚙️" AS "⚙️",
                "where.3"."node" AS "📊",
                "where.3"."#️⃣" AS "#️⃣"
         FROM   "where.3"
       ),
       "stop.2"("⚙️") AS (
         SELECT "where.4"."⚙️"
         FROM   "where.4"
         WHERE  FALSE
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       )
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int) AS "📊",
             CAST(("jump.1"."active") AS boolean) AS "active",
             CAST(("jump.1"."node") AS int) AS "node",
             CAST(("jump.1"."k") AS int) AS "k"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS int) AS "📊",
             CAST((NULL) AS boolean) AS "active",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS int) AS "k"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;
