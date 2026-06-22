WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "length", "path", "last", "first") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int[]) AS "📊",
            CAST((NULL) AS int) AS "length",
            CAST((NULL) AS int[]) AS "path",
            CAST((NULL) AS int) AS "last",
            CAST((NULL) AS int) AS "first")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("length", "⚙️", "path", "#️⃣", "last", "first") AS (
         SELECT "🔄"."length" AS "length",
                NULL AS "⚙️",
                "🔄"."path" AS "path",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."last" AS "last",
                "🔄"."first" AS "first"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "start.3"("length", "⚙️", "path", "#️⃣", "last", "first") AS (
         SELECT "🔄"."length" AS "length",
                NULL AS "⚙️",
                "🔄"."path" AS "path",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."last" AS "last",
                "🔄"."first" AS "first"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.3'
       ),
       "fork.1"("#️⃣", "first") AS (
         SELECT "start.1"."#️⃣" AS "#️⃣",
                "ℚ"."first" AS "first"
         FROM   "start.1",
                (SELECT id FROM nodes) AS "ℚ"("first")
       ),
       "issynced.1"("length", "⚙️", "🔍.1", "path", "#️⃣", "last", "first") AS (
         SELECT "start.3"."length" AS "length",
                "start.3"."⚙️" AS "⚙️",
                NOT EXISTS ((SELECT NULL
                             FROM   "🔄"
                             WHERE  "🔄"."🏷️" <> 'start.3')) AS "🔍.1",
                "start.3"."path" AS "path",
                "start.3"."#️⃣" AS "#️⃣",
                "start.3"."last" AS "last",
                "start.3"."first" AS "first"
         FROM   "start.3"
       ),
       "assignment.1"("#️⃣", "last", "first") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                CAST((("fork.1"."first")) AS int) AS "last",
                "fork.1"."first" AS "first"
         FROM   "fork.1"
       ),
       "where.3"("length", "⚙️", "path", "#️⃣", "last", "first") AS (
         SELECT "issynced.1"."length" AS "length",
                "issynced.1"."⚙️" AS "⚙️",
                "issynced.1"."path" AS "path",
                "issynced.1"."#️⃣" AS "#️⃣",
                "issynced.1"."last" AS "last",
                "issynced.1"."first" AS "first"
         FROM   "issynced.1"
         WHERE  "issynced.1"."🔍.1" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("length", "path", "#️⃣", "last", "first") AS (
         SELECT "issynced.1"."length" AS "length",
                "issynced.1"."path" AS "path",
                "issynced.1"."#️⃣" AS "#️⃣",
                "issynced.1"."last" AS "last",
                "issynced.1"."first" AS "first"
         FROM   "issynced.1"
         WHERE  "issynced.1"."🔍.1" IS DISTINCT FROM TRUE
       ),
       "assignment.2"("length", "#️⃣", "last", "first") AS (
         SELECT CAST((0) AS int) AS "length",
                "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."last" AS "last",
                "assignment.1"."first" AS "first"
         FROM   "assignment.1"
       ),
       "gather.1"("path", "⚙️", "#️⃣") AS (
         SELECT ARGMIN(("where.3"."path"), ("where.3"."length")) AS "path",
                "where.3"."⚙️" AS "⚙️",
                "where.3"."#️⃣" AS "#️⃣"
         FROM   "where.3"
         GROUP  BY "where.3"."#️⃣",
                   "where.3"."⚙️",
                   "where.3"."last",
                   "where.3"."first"
         HAVING COUNT(*) > 0
       ),
       "jump.3"("first", "🏷️", "path", "#️⃣", "length", "last") AS (
         SELECT "where.4"."first" AS "first",
                'start.3' AS "🏷️",
                "where.4"."path" AS "path",
                "where.4"."#️⃣" AS "#️⃣",
                "where.4"."length" AS "length",
                "where.4"."last" AS "last"
         FROM   "where.4"
       ),
       "assignment.3"("length", "path", "#️⃣", "last", "first") AS (
         SELECT "assignment.2"."length" AS "length",
                CAST((array[("assignment.2"."last")]) AS int[]) AS "path",
                "assignment.2"."#️⃣" AS "#️⃣",
                "assignment.2"."last" AS "last",
                "assignment.2"."first" AS "first"
         FROM   "assignment.2"
       ),
       "emit.1"("#️⃣", "⚙️", "📊") AS (
         SELECT "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."⚙️" AS "⚙️",
                "gather.1"."path" AS "📊"
         FROM   "gather.1"
       ),
       "merge.1"("length", "path", "#️⃣", "last", "first") AS (
         (SELECT "assignment.3"."length" AS "length",
                 "assignment.3"."path" AS "path",
                 "assignment.3"."#️⃣" AS "#️⃣",
                 "assignment.3"."last" AS "last",
                 "assignment.3"."first" AS "first"
          FROM   "assignment.3")
           UNION ALL
         (SELECT "start.2"."length" AS "length",
                 "start.2"."path" AS "path",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."last" AS "last",
                 "start.2"."first" AS "first"
          FROM   "start.2")
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       ),
       "fork.2"("cond", "length", "path", "#️⃣", "last", "first") AS (
         SELECT "ℚ"."cond" AS "cond",
                "merge.1"."length" AS "length",
                "merge.1"."path" AS "path",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."last" AS "last",
                "merge.1"."first" AS "first"
         FROM   "merge.1",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("cond")
       ),
       "where.1"("length", "path", "#️⃣", "last", "first") AS (
         SELECT "fork.2"."length" AS "length",
                "fork.2"."path" AS "path",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."last" AS "last",
                "fork.2"."first" AS "first"
         FROM   "fork.2"
         WHERE  "fork.2"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("length", "path", "#️⃣", "last", "first") AS (
         SELECT "fork.2"."length" AS "length",
                "fork.2"."path" AS "path",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."last" AS "last",
                "fork.2"."first" AS "first"
         FROM   "fork.2"
         WHERE  "fork.2"."cond" IS DISTINCT FROM TRUE
       ),
       "fork.3"("length", "edge", "path", "#️⃣", "first") AS (
         SELECT "where.2"."length" AS "length",
                "ℚ"."edge" AS "edge",
                "where.2"."path" AS "path",
                "where.2"."#️⃣" AS "#️⃣",
                "where.2"."first" AS "first"
         FROM   "where.2",
                LATERAL (SELECT e FROM edges AS e WHERE here = ("where.2"."last")) AS "ℚ"("edge")
       ),
       "jump.2"("first", "🏷️", "path", "#️⃣", "length", "last") AS (
         SELECT "where.1"."first" AS "first",
                'start.3' AS "🏷️",
                "where.1"."path" AS "path",
                "where.1"."#️⃣" AS "#️⃣",
                "where.1"."length" AS "length",
                "where.1"."last" AS "last"
         FROM   "where.1"
       ),
       "assignment.4"("length", "edge", "path", "#️⃣", "first") AS (
         SELECT CAST((("fork.3"."length") + ("fork.3"."edge").length) AS int) AS "length",
                "fork.3"."edge" AS "edge",
                "fork.3"."path" AS "path",
                "fork.3"."#️⃣" AS "#️⃣",
                "fork.3"."first" AS "first"
         FROM   "fork.3"
       ),
       "assignment.5"("length", "path", "#️⃣", "last", "first") AS (
         SELECT "assignment.4"."length" AS "length",
                "assignment.4"."path" AS "path",
                "assignment.4"."#️⃣" AS "#️⃣",
                CAST((("assignment.4"."edge").there) AS int) AS "last",
                "assignment.4"."first" AS "first"
         FROM   "assignment.4"
       ),
       "assignment.6"("length", "path", "#️⃣", "last", "first") AS (
         SELECT "assignment.5"."length" AS "length",
                CAST((("assignment.5"."path") || array[("assignment.5"."last")]) AS int[]) AS "path",
                "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."last" AS "last",
                "assignment.5"."first" AS "first"
         FROM   "assignment.5"
       ),
       "jump.1"("first", "🏷️", "path", "#️⃣", "length", "last") AS (
         SELECT "assignment.6"."first" AS "first",
                'start.2' AS "🏷️",
                "assignment.6"."path" AS "path",
                "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."length" AS "length",
                "assignment.6"."last" AS "last"
         FROM   "assignment.6"
       )
     (SELECT CAST(("jump.3"."🏷️") AS text) AS "🏷️",
             CAST(("jump.3"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊",
             CAST(("jump.3"."length") AS int) AS "length",
             CAST(("jump.3"."path") AS int[]) AS "path",
             CAST(("jump.3"."last") AS int) AS "last",
             CAST(("jump.3"."first") AS int) AS "first"
      FROM   "jump.3")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS int[]) AS "📊",
             CAST((NULL) AS int) AS "length",
             CAST((NULL) AS int[]) AS "path",
             CAST((NULL) AS int) AS "last",
             CAST((NULL) AS int) AS "first"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.2"."🏷️") AS text) AS "🏷️",
             CAST(("jump.2"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊",
             CAST(("jump.2"."length") AS int) AS "length",
             CAST(("jump.2"."path") AS int[]) AS "path",
             CAST(("jump.2"."last") AS int) AS "last",
             CAST(("jump.2"."first") AS int) AS "first"
      FROM   "jump.2")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊",
             CAST(("jump.1"."length") AS int) AS "length",
             CAST(("jump.1"."path") AS int[]) AS "path",
             CAST(("jump.1"."last") AS int) AS "last",
             CAST(("jump.1"."first") AS int) AS "first"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;