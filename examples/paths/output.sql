WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊.1", "length", "first", "path", "last") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int[]) AS "📊.1",
            CAST((NULL) AS int) AS "length",
            CAST((NULL) AS int) AS "first",
            CAST((NULL) AS int[]) AS "path",
            CAST((NULL) AS int) AS "last")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "🔄"."length" AS "length",
                "🔄"."first" AS "first",
                "🔄"."path" AS "path",
                "🔄"."last" AS "last",
                NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "start.3"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "🔄"."length" AS "length",
                "🔄"."first" AS "first",
                "🔄"."path" AS "path",
                "🔄"."last" AS "last",
                NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.3'
       ),
       "fork.1"("first", "⚙️", "#️⃣") AS (
         SELECT "ℚ"."first" AS "first",
                "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣"
         FROM   "start.1",
                (SELECT id FROM nodes) AS "ℚ"("first")
       ),
       "issynced.1"("length", "first", "path", "last", "⚙️", "🔍", "#️⃣") AS (
         SELECT "start.3"."length" AS "length",
                "start.3"."first" AS "first",
                "start.3"."path" AS "path",
                "start.3"."last" AS "last",
                "start.3"."⚙️" AS "⚙️",
                NOT EXISTS ((SELECT NULL
                             FROM   "🔄"
                             WHERE  "🔄"."🏷️" <> 'start.3')) AS "🔍",
                "start.3"."#️⃣" AS "#️⃣"
         FROM   "start.3"
       ),
       "assignment.1"("first", "last", "⚙️", "#️⃣") AS (
         SELECT "fork.1"."first" AS "first",
                CAST((("fork.1"."first")) AS int) AS "last",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."#️⃣" AS "#️⃣"
         FROM   "fork.1"
       ),
       "where.3"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "issynced.1"."length" AS "length",
                "issynced.1"."first" AS "first",
                "issynced.1"."path" AS "path",
                "issynced.1"."last" AS "last",
                "issynced.1"."⚙️" AS "⚙️",
                "issynced.1"."#️⃣" AS "#️⃣"
         FROM   "issynced.1"
         WHERE  "issynced.1"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "issynced.1"."length" AS "length",
                "issynced.1"."first" AS "first",
                "issynced.1"."path" AS "path",
                "issynced.1"."last" AS "last",
                "issynced.1"."⚙️" AS "⚙️",
                "issynced.1"."#️⃣" AS "#️⃣"
         FROM   "issynced.1"
         WHERE  "issynced.1"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.2"("length", "first", "last", "⚙️", "#️⃣") AS (
         SELECT CAST((0) AS int) AS "length",
                "assignment.1"."first" AS "first",
                "assignment.1"."last" AS "last",
                "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."#️⃣" AS "#️⃣"
         FROM   "assignment.1"
       ),
       "gather.1"("⚙️", "path", "#️⃣") AS (
         SELECT "where.3"."⚙️" AS "⚙️",
                CAST((ARGMIN(("where.3"."path"), ("where.3"."length"))) AS int[]) AS "path",
                "where.3"."#️⃣" AS "#️⃣"
         FROM   "where.3"
         GROUP  BY "where.3"."first",
                   "where.3"."last",
                   "where.3"."⚙️",
                   "where.3"."#️⃣"
         HAVING COUNT(*) > 0
       ),
       "jump.3"("path", "last", "first", "🏷️", "length", "#️⃣") AS (
         SELECT "where.4"."path" AS "path",
                "where.4"."last" AS "last",
                "where.4"."first" AS "first",
                'start.3' AS "🏷️",
                "where.4"."length" AS "length",
                "where.4"."#️⃣" AS "#️⃣"
         FROM   "where.4"
       ),
       "assignment.3"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "assignment.2"."length" AS "length",
                "assignment.2"."first" AS "first",
                CAST((array[("assignment.2"."last")]) AS int[]) AS "path",
                "assignment.2"."last" AS "last",
                "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."#️⃣" AS "#️⃣"
         FROM   "assignment.2"
       ),
       "emit.1"("#️⃣", "⚙️", "📊.1") AS (
         SELECT "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."⚙️" AS "⚙️",
                "gather.1"."path" AS "📊.1"
         FROM   "gather.1"
       ),
       "merge.1"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         (SELECT "start.2"."length" AS "length",
                 "start.2"."first" AS "first",
                 "start.2"."path" AS "path",
                 "start.2"."last" AS "last",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.3"."length" AS "length",
                 "assignment.3"."first" AS "first",
                 "assignment.3"."path" AS "path",
                 "assignment.3"."last" AS "last",
                 "assignment.3"."⚙️" AS "⚙️",
                 "assignment.3"."#️⃣" AS "#️⃣"
          FROM   "assignment.3")
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       ),
       "fork.2"("edge", "length", "first", "path", "⚙️", "#️⃣") AS (
         SELECT "ℚ"."edge" AS "edge",
                "merge.1"."length" AS "length",
                "merge.1"."first" AS "first",
                "merge.1"."path" AS "path",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."#️⃣" AS "#️⃣"
         FROM   "merge.1",
                LATERAL (SELECT e FROM edges AS e WHERE here = ("merge.1"."last")) AS "ℚ"("edge")
       ),
       "assignment.4"("length", "edge", "first", "path", "⚙️", "#️⃣") AS (
         SELECT CAST((("fork.2"."length") + ("fork.2"."edge").length) AS int) AS "length",
                "fork.2"."edge" AS "edge",
                "fork.2"."first" AS "first",
                "fork.2"."path" AS "path",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."#️⃣" AS "#️⃣"
         FROM   "fork.2"
       ),
       "assignment.5"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "assignment.4"."length" AS "length",
                "assignment.4"."first" AS "first",
                "assignment.4"."path" AS "path",
                CAST((("assignment.4"."edge").there) AS int) AS "last",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."#️⃣" AS "#️⃣"
         FROM   "assignment.4"
       ),
       "assignment.6"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "assignment.5"."length" AS "length",
                "assignment.5"."first" AS "first",
                CAST((("assignment.5"."path") || array[("assignment.5"."last")]) AS int[]) AS "path",
                "assignment.5"."last" AS "last",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."#️⃣" AS "#️⃣"
         FROM   "assignment.5"
       ),
       "fork.3"("flip", "length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "ℚ"."flip" AS "flip",
                "assignment.6"."length" AS "length",
                "assignment.6"."first" AS "first",
                "assignment.6"."path" AS "path",
                "assignment.6"."last" AS "last",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."#️⃣" AS "#️⃣"
         FROM   "assignment.6",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("flip")
       ),
       "assignment.7"("length", "first", "path", "last", "⚙️", "🔍", "#️⃣") AS (
         SELECT "fork.3"."length" AS "length",
                "fork.3"."first" AS "first",
                "fork.3"."path" AS "path",
                "fork.3"."last" AS "last",
                "fork.3"."⚙️" AS "⚙️",
                CAST((("fork.3"."flip")) AS boolean) AS "🔍",
                "fork.3"."#️⃣" AS "#️⃣"
         FROM   "fork.3"
       ),
       "where.1"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "assignment.7"."length" AS "length",
                "assignment.7"."first" AS "first",
                "assignment.7"."path" AS "path",
                "assignment.7"."last" AS "last",
                "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."#️⃣" AS "#️⃣"
         FROM   "assignment.7"
         WHERE  "assignment.7"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("length", "first", "path", "last", "⚙️", "#️⃣") AS (
         SELECT "assignment.7"."length" AS "length",
                "assignment.7"."first" AS "first",
                "assignment.7"."path" AS "path",
                "assignment.7"."last" AS "last",
                "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."#️⃣" AS "#️⃣"
         FROM   "assignment.7"
         WHERE  "assignment.7"."🔍" IS DISTINCT FROM TRUE
       ),
       "jump.1"("path", "last", "first", "🏷️", "length", "#️⃣") AS (
         SELECT "where.2"."path" AS "path",
                "where.2"."last" AS "last",
                "where.2"."first" AS "first",
                'start.2' AS "🏷️",
                "where.2"."length" AS "length",
                "where.2"."#️⃣" AS "#️⃣"
         FROM   "where.2"
       ),
       "jump.2"("path", "last", "first", "🏷️", "length", "#️⃣") AS (
         SELECT "where.1"."path" AS "path",
                "where.1"."last" AS "last",
                "where.1"."first" AS "first",
                'start.3' AS "🏷️",
                "where.1"."length" AS "length",
                "where.1"."#️⃣" AS "#️⃣"
         FROM   "where.1"
       )
     (SELECT CAST(("jump.3"."🏷️") AS text) AS "🏷️",
             CAST(("jump.3"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊.1",
             CAST(("jump.3"."length") AS int) AS "length",
             CAST(("jump.3"."first") AS int) AS "first",
             CAST(("jump.3"."path") AS int[]) AS "path",
             CAST(("jump.3"."last") AS int) AS "last"
      FROM   "jump.3")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊.1") AS int[]) AS "📊.1",
             CAST((NULL) AS int) AS "length",
             CAST((NULL) AS int) AS "first",
             CAST((NULL) AS int[]) AS "path",
             CAST((NULL) AS int) AS "last"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊.1",
             CAST(("jump.1"."length") AS int) AS "length",
             CAST(("jump.1"."first") AS int) AS "first",
             CAST(("jump.1"."path") AS int[]) AS "path",
             CAST(("jump.1"."last") AS int) AS "last"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST(("jump.2"."🏷️") AS text) AS "🏷️",
             CAST(("jump.2"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊.1",
             CAST(("jump.2"."length") AS int) AS "length",
             CAST(("jump.2"."first") AS int) AS "first",
             CAST(("jump.2"."path") AS int[]) AS "path",
             CAST(("jump.2"."last") AS int) AS "last"
      FROM   "jump.2"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;