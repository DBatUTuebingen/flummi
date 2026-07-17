WITH RECURSIVE
  "🔄"("#️⃣", "active", "k", "node", "size", "🏷️", "📊.1") AS (
    (SELECT CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS boolean) AS "active",
            CAST((NULL) AS int) AS "k",
            CAST((NULL) AS int) AS "node",
            CAST((NULL) AS int) AS "size",
            CAST(('start.1') AS text) AS "🏷️",
            CAST((NULL) AS int) AS "📊.1")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "assignment.1"("#️⃣", "k", "⚙️") AS (
         SELECT "start.1"."#️⃣" AS "#️⃣",
                CAST((2) AS int) AS "k",
                "start.1"."⚙️" AS "⚙️"
         FROM   "start.1"
       ),
       "fork.1"("#️⃣", "k", "node", "⚙️") AS (
         SELECT "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."k" AS "k",
                CAST(("ℚ"."node") AS int) AS "node",
                "assignment.1"."⚙️" AS "⚙️"
         FROM   "assignment.1",
                (FROM nodes) AS "ℚ"("node")
       ),
       "assignment.2"("#️⃣", "active", "k", "node", "⚙️") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                CAST((TRUE) AS boolean) AS "active",
                "fork.1"."k" AS "k",
                "fork.1"."node" AS "node",
                "fork.1"."⚙️" AS "⚙️"
         FROM   "fork.1"
       ),
       "assignment.3"("#️⃣", "active", "k", "node", "size", "⚙️") AS (
         SELECT "assignment.2"."#️⃣" AS "#️⃣",
                "assignment.2"."active" AS "active",
                "assignment.2"."k" AS "k",
                "assignment.2"."node" AS "node",
                CAST((count(*) OVER ()) AS int) AS "size",
                "assignment.2"."⚙️" AS "⚙️"
         FROM   "assignment.2"
       ),
       "start.2"("#️⃣", "active", "k", "node", "size", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                "🔄"."active" AS "active",
                "🔄"."k" AS "k",
                "🔄"."node" AS "node",
                "🔄"."size" AS "size",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "merge.1"("#️⃣", "active", "k", "node", "size", "⚙️") AS (
         (SELECT "assignment.3"."#️⃣" AS "#️⃣",
                 "assignment.3"."active" AS "active",
                 "assignment.3"."k" AS "k",
                 "assignment.3"."node" AS "node",
                 "assignment.3"."size" AS "size",
                 "assignment.3"."⚙️" AS "⚙️"
          FROM   "assignment.3")
           UNION ALL
         (SELECT "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."active" AS "active",
                 "start.2"."k" AS "k",
                 "start.2"."node" AS "node",
                 "start.2"."size" AS "size",
                 "start.2"."⚙️" AS "⚙️"
          FROM   "start.2")
       ),
       "fork.2"("#️⃣", "active", "k", "node", "size", "⚙️") AS (
         SELECT "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."active" AS "active",
                "merge.1"."k" AS "k",
                CAST(("ℚ"."node") AS int) AS "node",
                "merge.1"."size" AS "size",
                "merge.1"."⚙️" AS "⚙️"
         FROM   "merge.1",
                LATERAL (SELECT there
                         FROM   edges
                         WHERE  here = ("merge.1"."node")) AS "ℚ"("node")
       ),
       "gather.1"("#️⃣", "degree", "k", "node", "size", "⚙️") AS (
         SELECT "fork.2"."#️⃣" AS "#️⃣",
                CAST((countif(("fork.2"."active"))) AS int) AS "degree",
                "fork.2"."k" AS "k",
                "fork.2"."node" AS "node",
                "fork.2"."size" AS "size",
                "fork.2"."⚙️" AS "⚙️"
         FROM   "fork.2"
         GROUP  BY "fork.2"."#️⃣",
                   "fork.2"."k",
                   "fork.2"."node",
                   "fork.2"."size",
                   "fork.2"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "assignment.4"("#️⃣", "active", "k", "node", "size", "⚙️") AS (
         SELECT "gather.1"."#️⃣" AS "#️⃣",
                CAST((("gather.1"."degree") >= ("gather.1"."k") + 1) AS boolean) AS "active",
                "gather.1"."k" AS "k",
                "gather.1"."node" AS "node",
                "gather.1"."size" AS "size",
                "gather.1"."⚙️" AS "⚙️"
         FROM   "gather.1"
       ),
       "assignment.5"("#️⃣", "active", "k", "node", "old_size", "size", "⚙️") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."active" AS "active",
                "assignment.4"."k" AS "k",
                "assignment.4"."node" AS "node",
                CAST((("assignment.4"."size")) AS int) AS "old_size",
                CAST((countif(("assignment.4"."active")) OVER ()) AS int) AS "size",
                "assignment.4"."⚙️" AS "⚙️"
         FROM   "assignment.4"
       ),
       "assignment.6"("#️⃣", "active", "k", "node", "size", "⚙️", "🔍") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."active" AS "active",
                "assignment.5"."k" AS "k",
                "assignment.5"."node" AS "node",
                "assignment.5"."size" AS "size",
                "assignment.5"."⚙️" AS "⚙️",
                CAST((("assignment.5"."old_size") = ("assignment.5"."size")) AS boolean) AS "🔍"
         FROM   "assignment.5"
       ),
       "where.1"("#️⃣", "active", "node", "⚙️") AS (
         SELECT "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."active" AS "active",
                "assignment.6"."node" AS "node",
                "assignment.6"."⚙️" AS "⚙️"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "assignment.7"("#️⃣", "node", "⚙️", "🔍") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                "where.1"."node" AS "node",
                "where.1"."⚙️" AS "⚙️",
                CAST((("where.1"."active")) AS boolean) AS "🔍"
         FROM   "where.1"
       ),
       "where.2"("#️⃣", "active", "k", "node", "size", "⚙️") AS (
         SELECT "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."active" AS "active",
                "assignment.6"."k" AS "k",
                "assignment.6"."node" AS "node",
                "assignment.6"."size" AS "size",
                "assignment.6"."⚙️" AS "⚙️"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS DISTINCT FROM TRUE
       ),
       "jump.1"("#️⃣", "active", "k", "node", "size", "🏷️") AS (
         SELECT "where.2"."#️⃣" AS "#️⃣",
                "where.2"."active" AS "active",
                "where.2"."k" AS "k",
                "where.2"."node" AS "node",
                "where.2"."size" AS "size",
                'start.2' AS "🏷️"
         FROM   "where.2"
       ),
       "where.3"("#️⃣", "node", "⚙️") AS (
         SELECT "assignment.7"."#️⃣" AS "#️⃣",
                "assignment.7"."node" AS "node",
                "assignment.7"."⚙️" AS "⚙️"
         FROM   "assignment.7"
         WHERE  "assignment.7"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "emit.1"("#️⃣", "⚙️", "📊.1") AS (
         SELECT "where.3"."#️⃣" AS "#️⃣",
                "where.3"."⚙️" AS "⚙️",
                "where.3"."node" AS "📊.1"
         FROM   "where.3"
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       ),
       "where.4"("⚙️") AS (
         SELECT "assignment.7"."⚙️" AS "⚙️"
         FROM   "assignment.7"
         WHERE  "assignment.7"."🔍" IS DISTINCT FROM TRUE
       ),
       "stop.2"("⚙️") AS (
         SELECT "where.4"."⚙️"
         FROM   "where.4"
         WHERE  FALSE
       )
     (SELECT CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST(("jump.1"."active") AS boolean) AS "active",
             CAST(("jump.1"."k") AS int) AS "k",
             CAST(("jump.1"."node") AS int) AS "node",
             CAST(("jump.1"."size") AS int) AS "size",
             CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST((NULL) AS int) AS "📊.1"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST((NULL) AS boolean) AS "active",
             CAST((NULL) AS int) AS "k",
             CAST((NULL) AS int) AS "node",
             CAST((NULL) AS int) AS "size",
             CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."📊.1") AS int) AS "📊.1"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;