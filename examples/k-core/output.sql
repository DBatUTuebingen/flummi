WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "k", "node") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int) AS "📊",
            CAST((NULL) AS int) AS "k",
            CAST((NULL) AS int) AS "node")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("k", "⚙️", "#️⃣", "node") AS (
         SELECT "🔄"."k" AS "k",
                NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."node" AS "node"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("k", "#️⃣", "⚙️") AS (
         SELECT CAST((2) AS int) AS "k",
                "start.1"."#️⃣" AS "#️⃣",
                "start.1"."⚙️" AS "⚙️"
         FROM   "start.1"
       ),
       "fork.1"("k", "⚙️", "#️⃣", "node") AS (
         SELECT "assignment.1"."k" AS "k",
                "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."#️⃣" AS "#️⃣",
                "ℚ"."node" AS "node"
         FROM   "assignment.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "merge.1"("k", "⚙️", "#️⃣", "node") AS (
         (SELECT "fork.1"."k" AS "k",
                 "fork.1"."⚙️" AS "⚙️",
                 "fork.1"."#️⃣" AS "#️⃣",
                 "fork.1"."node" AS "node"
          FROM   "fork.1")
           UNION ALL
         (SELECT "start.2"."k" AS "k",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."node" AS "node"
          FROM   "start.2")
       ),
       "fork.2"("k", "⚙️", "#️⃣", "node") AS (
         SELECT "merge.1"."k" AS "k",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."#️⃣" AS "#️⃣",
                "ℚ"."node" AS "node"
         FROM   "merge.1",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("merge.1"."node")) AS "ℚ"("node")
       ),
       "gather.1"("k", "#️⃣", "⚙️", "degree", "node") AS (
         SELECT "fork.2"."k" AS "k",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."⚙️" AS "⚙️",
                count(*) AS "degree",
                "fork.2"."node" AS "node"
         FROM   "fork.2"
         GROUP  BY "fork.2"."k",
                   "fork.2"."#️⃣",
                   "fork.2"."⚙️",
                   "fork.2"."node"
         HAVING COUNT(*) > 0
       ),
       "assignment.2"("active", "k", "#️⃣", "⚙️", "node") AS (
         SELECT CAST((("gather.1"."degree") >= ("gather.1"."k") + 1) AS boolean) AS "active",
                "gather.1"."k" AS "k",
                "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."⚙️" AS "⚙️",
                "gather.1"."node" AS "node"
         FROM   "gather.1"
       ),
       "assignment.3"("active", "k", "#️⃣", "⚙️", "stable", "node") AS (
         SELECT "assignment.2"."active" AS "active",
                "assignment.2"."k" AS "k",
                "assignment.2"."#️⃣" AS "#️⃣",
                "assignment.2"."⚙️" AS "⚙️",
                CAST((bool_and(("assignment.2"."active")) OVER ()) AS boolean) AS "stable",
                "assignment.2"."node" AS "node"
         FROM   "assignment.2"
       ),
       "where.1"("k", "#️⃣", "⚙️", "stable", "node") AS (
         SELECT "assignment.3"."k" AS "k",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."stable" AS "stable",
                "assignment.3"."node" AS "node"
         FROM   "assignment.3"
         WHERE  "assignment.3"."active" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("⚙️") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️"
         FROM   "assignment.3"
         WHERE  "assignment.3"."active" IS DISTINCT FROM TRUE
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.2"."⚙️"
         FROM   "where.2"
         WHERE  FALSE
       ),
       "where.3"("⚙️", "#️⃣", "node") AS (
         SELECT "where.1"."⚙️" AS "⚙️",
                "where.1"."#️⃣" AS "#️⃣",
                "where.1"."node" AS "node"
         FROM   "where.1"
         WHERE  "where.1"."stable" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("k", "#️⃣", "node") AS (
         SELECT "where.1"."k" AS "k",
                "where.1"."#️⃣" AS "#️⃣",
                "where.1"."node" AS "node"
         FROM   "where.1"
         WHERE  "where.1"."stable" IS DISTINCT FROM TRUE
       ),
       "emit.1"("⚙️", "📊", "#️⃣") AS (
         SELECT "where.3"."⚙️" AS "⚙️",
                "where.3"."node" AS "📊",
                "where.3"."#️⃣" AS "#️⃣"
         FROM   "where.3"
       ),
       "jump.1"("#️⃣", "🏷️", "node", "k") AS (
         SELECT "where.4"."#️⃣" AS "#️⃣",
                'start.2' AS "🏷️",
                "where.4"."node" AS "node",
                "where.4"."k" AS "k"
         FROM   "where.4"
       ),
       "stop.2"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       )
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS int) AS "📊",
             CAST((NULL) AS int) AS "k",
             CAST((NULL) AS int) AS "node"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int) AS "📊",
             CAST(("jump.1"."k") AS int) AS "k",
             CAST(("jump.1"."node") AS int) AS "node"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;