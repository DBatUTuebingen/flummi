WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "size", "node", "active", "k") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int) AS "📊",
            CAST((NULL) AS int) AS "size",
            CAST((NULL) AS int) AS "node",
            CAST((NULL) AS boolean) AS "active",
            CAST((NULL) AS int) AS "k")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("⚙️", "#️⃣", "size", "node", "active", "k") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."size" AS "size",
                "🔄"."node" AS "node",
                "🔄"."active" AS "active",
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
       "fork.1"("⚙️", "k", "#️⃣", "node") AS (
         SELECT "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."k" AS "k",
                "assignment.1"."#️⃣" AS "#️⃣",
                "ℚ"."node" AS "node"
         FROM   "assignment.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "assignment.2"("⚙️", "node", "#️⃣", "k", "active") AS (
         SELECT "fork.1"."⚙️" AS "⚙️",
                "fork.1"."node" AS "node",
                "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."k" AS "k",
                CAST((TRUE) AS boolean) AS "active"
         FROM   "fork.1"
       ),
       "assignment.3"("⚙️", "#️⃣", "size", "node", "active", "k") AS (
         SELECT "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."#️⃣" AS "#️⃣",
                CAST((count(*) OVER ()) AS int) AS "size",
                "assignment.2"."node" AS "node",
                "assignment.2"."active" AS "active",
                "assignment.2"."k" AS "k"
         FROM   "assignment.2"
       ),
       "merge.1"("⚙️", "node", "#️⃣", "size", "k", "active") AS (
         (SELECT "start.2"."⚙️" AS "⚙️",
                 "start.2"."node" AS "node",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."size" AS "size",
                 "start.2"."k" AS "k",
                 "start.2"."active" AS "active"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.3"."⚙️" AS "⚙️",
                 "assignment.3"."node" AS "node",
                 "assignment.3"."#️⃣" AS "#️⃣",
                 "assignment.3"."size" AS "size",
                 "assignment.3"."k" AS "k",
                 "assignment.3"."active" AS "active"
          FROM   "assignment.3")
       ),
       "fork.2"("⚙️", "node", "#️⃣", "size", "k", "active") AS (
         SELECT "merge.1"."⚙️" AS "⚙️",
                "ℚ"."node" AS "node",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."size" AS "size",
                "merge.1"."k" AS "k",
                "merge.1"."active" AS "active"
         FROM   "merge.1",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("merge.1"."node")) AS "ℚ"("node")
       ),
       "gather.1"("⚙️", "node", "#️⃣", "size", "k", "degree") AS (
         SELECT "fork.2"."⚙️" AS "⚙️",
                "fork.2"."node" AS "node",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."size" AS "size",
                "fork.2"."k" AS "k",
                CAST((countif(("fork.2"."active"))) AS int) AS "degree"
         FROM   "fork.2"
         GROUP  BY "fork.2"."⚙️",
                   "fork.2"."#️⃣",
                   "fork.2"."size",
                   "fork.2"."node",
                   "fork.2"."k"
         HAVING COUNT(*) > 0
       ),
       "assignment.4"("⚙️", "node", "size", "#️⃣", "active", "k") AS (
         SELECT "gather.1"."⚙️" AS "⚙️",
                "gather.1"."node" AS "node",
                "gather.1"."size" AS "size",
                "gather.1"."#️⃣" AS "#️⃣",
                CAST((("gather.1"."degree") >= ("gather.1"."k") + 1) AS boolean) AS "active",
                "gather.1"."k" AS "k"
         FROM   "gather.1"
       ),
       "assignment.5"("⚙️", "node", "size", "#️⃣", "active", "old_size", "k") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."node" AS "node",
                CAST((countif(("assignment.4"."active")) OVER ()) AS int) AS "size",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."active" AS "active",
                CAST((("assignment.4"."size")) AS int) AS "old_size",
                "assignment.4"."k" AS "k"
         FROM   "assignment.4"
       ),
       "assignment.6"("⚙️", "node", "🔍", "size", "#️⃣", "active", "k") AS (
         SELECT "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."node" AS "node",
                CAST((("assignment.5"."old_size") = ("assignment.5"."size")) AS boolean) AS "🔍",
                "assignment.5"."size" AS "size",
                "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."active" AS "active",
                "assignment.5"."k" AS "k"
         FROM   "assignment.5"
       ),
       "where.1"("active", "node", "⚙️", "#️⃣") AS (
         SELECT "assignment.6"."active" AS "active",
                "assignment.6"."node" AS "node",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."#️⃣" AS "#️⃣"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("⚙️", "#️⃣", "size", "node", "active", "k") AS (
         SELECT "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."size" AS "size",
                "assignment.6"."node" AS "node",
                "assignment.6"."active" AS "active",
                "assignment.6"."k" AS "k"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.7"("⚙️", "#️⃣", "🔍", "node") AS (
         SELECT "where.1"."⚙️" AS "⚙️",
                "where.1"."#️⃣" AS "#️⃣",
                CAST((("where.1"."active")) AS boolean) AS "🔍",
                "where.1"."node" AS "node"
         FROM   "where.1"
       ),
       "jump.1"("node", "k", "#️⃣", "active", "size", "🏷️") AS (
         SELECT "where.2"."node" AS "node",
                "where.2"."k" AS "k",
                "where.2"."#️⃣" AS "#️⃣",
                "where.2"."active" AS "active",
                "where.2"."size" AS "size",
                'start.2' AS "🏷️"
         FROM   "where.2"
       ),
       "where.3"("⚙️", "node", "#️⃣") AS (
         SELECT "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."node" AS "node",
                "assignment.7"."#️⃣" AS "#️⃣"
         FROM   "assignment.7"
         WHERE  "assignment.7"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("⚙️") AS (
         SELECT "assignment.7"."⚙️" AS "⚙️"
         FROM   "assignment.7"
         WHERE  "assignment.7"."🔍" IS DISTINCT FROM TRUE
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
             CAST(("jump.1"."size") AS int) AS "size",
             CAST(("jump.1"."node") AS int) AS "node",
             CAST(("jump.1"."active") AS boolean) AS "active",
             CAST(("jump.1"."k") AS int) AS "k"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS int) AS "📊",
             CAST((NULL) AS int) AS "size",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS boolean) AS "active",
             CAST((NULL) AS int) AS "k"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;