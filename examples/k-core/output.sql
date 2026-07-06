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
       "start.2"("node", "⚙️", "#️⃣", "k") AS (
         SELECT "🔄"."node" AS "node",
                NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."k" AS "k"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("⚙️", "#️⃣", "k") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣",
                CAST((2) AS int) AS "k"
         FROM   "start.1"
       ),
       "fork.1"("node", "⚙️", "#️⃣", "k") AS (
         SELECT "ℚ"."node" AS "node",
                "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."k" AS "k"
         FROM   "assignment.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "merge.1"("node", "⚙️", "#️⃣", "k") AS (
         (SELECT "fork.1"."node" AS "node",
                 "fork.1"."⚙️" AS "⚙️",
                 "fork.1"."#️⃣" AS "#️⃣",
                 "fork.1"."k" AS "k"
          FROM   "fork.1")
           UNION ALL
         (SELECT "start.2"."node" AS "node",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."k" AS "k"
          FROM   "start.2")
       ),
       "fork.2"("node", "⚙️", "#️⃣", "k") AS (
         SELECT "ℚ"."node" AS "node",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."k" AS "k"
         FROM   "merge.1",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("merge.1"."node")) AS "ℚ"("node")
       ),
       "gather.1"("degree", "⚙️", "k", "node", "#️⃣") AS (
         SELECT CAST((count(*)) AS int) AS "degree",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."k" AS "k",
                "fork.2"."node" AS "node",
                "fork.2"."#️⃣" AS "#️⃣"
         FROM   "fork.2"
         GROUP  BY "fork.2"."⚙️",
                   "fork.2"."k",
                   "fork.2"."node",
                   "fork.2"."#️⃣"
         HAVING COUNT(*) > 0
       ),
       "assignment.2"("⚙️", "k", "active", "node", "#️⃣") AS (
         SELECT "gather.1"."⚙️" AS "⚙️",
                "gather.1"."k" AS "k",
                CAST((("gather.1"."degree") >= ("gather.1"."k") + 1) AS boolean) AS "active",
                "gather.1"."node" AS "node",
                "gather.1"."#️⃣" AS "#️⃣"
         FROM   "gather.1"
       ),
       "assignment.3"("⚙️", "k", "active", "node", "#️⃣", "stable") AS (
         SELECT "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."k" AS "k",
                "assignment.2"."active" AS "active",
                "assignment.2"."node" AS "node",
                "assignment.2"."#️⃣" AS "#️⃣",
                CAST((bool_and(("assignment.2"."active")) OVER ()) AS boolean) AS "stable"
         FROM   "assignment.2"
       ),
       "assignment.4"("⚙️", "k", "🔍", "node", "#️⃣", "stable") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."k" AS "k",
                CAST((("assignment.3"."active")) AS boolean) AS "🔍",
                "assignment.3"."node" AS "node",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."stable" AS "stable"
         FROM   "assignment.3"
       ),
       "where.1"("⚙️", "k", "node", "#️⃣", "stable") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."k" AS "k",
                "assignment.4"."node" AS "node",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."stable" AS "stable"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("⚙️") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.5"("⚙️", "k", "🔍", "node", "#️⃣") AS (
         SELECT "where.1"."⚙️" AS "⚙️",
                "where.1"."k" AS "k",
                CAST((("where.1"."stable")) AS boolean) AS "🔍",
                "where.1"."node" AS "node",
                "where.1"."#️⃣" AS "#️⃣"
         FROM   "where.1"
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.2"."⚙️"
         FROM   "where.2"
         WHERE  FALSE
       ),
       "where.3"("node", "⚙️", "#️⃣") AS (
         SELECT "assignment.5"."node" AS "node",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."#️⃣" AS "#️⃣"
         FROM   "assignment.5"
         WHERE  "assignment.5"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("node", "⚙️", "#️⃣", "k") AS (
         SELECT "assignment.5"."node" AS "node",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."k" AS "k"
         FROM   "assignment.5"
         WHERE  "assignment.5"."🔍" IS DISTINCT FROM TRUE
       ),
       "emit.1"("⚙️", "#️⃣", "📊") AS (
         SELECT "where.3"."⚙️" AS "⚙️",
                "where.3"."#️⃣" AS "#️⃣",
                "where.3"."node" AS "📊"
         FROM   "where.3"
       ),
       "jump.1"("k", "node", "🏷️", "#️⃣") AS (
         SELECT "where.4"."k" AS "k",
                "where.4"."node" AS "node",
                'start.2' AS "🏷️",
                "where.4"."#️⃣" AS "#️⃣"
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