WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊.1", "width", "iterations", "y", "height", "x", "alive") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS text) AS "📊.1",
            CAST((NULL) AS int) AS "width",
            CAST((NULL) AS int) AS "iterations",
            CAST((NULL) AS int) AS "y",
            CAST((NULL) AS int) AS "height",
            CAST((NULL) AS int) AS "x",
            CAST((NULL) AS boolean) AS "alive")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("width", "#️⃣", "⚙️", "iterations", "y", "height", "x", "alive") AS (
         SELECT "🔄"."width" AS "width",
                "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️",
                "🔄"."iterations" AS "iterations",
                "🔄"."y" AS "y",
                "🔄"."height" AS "height",
                "🔄"."x" AS "x",
                "🔄"."alive" AS "alive"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("#️⃣", "iterations", "⚙️", "height", "width") AS (
         SELECT "start.1"."#️⃣" AS "#️⃣",
                CAST((100) AS int) AS "iterations",
                "start.1"."⚙️" AS "⚙️",
                CAST((10) AS int) AS "height",
                CAST((10) AS int) AS "width"
         FROM   "start.1"
       ),
       "fork.1"("width", "#️⃣", "iterations", "⚙️", "height", "x") AS (
         SELECT "assignment.1"."width" AS "width",
                "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."iterations" AS "iterations",
                "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."height" AS "height",
                CAST(("ℚ"."x") AS int) AS "x"
         FROM   "assignment.1",
                LATERAL (FROM range(("assignment.1"."width"))) AS "ℚ"("x")
       ),
       "fork.2"("#️⃣", "iterations", "⚙️", "y", "height", "x", "width") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."iterations" AS "iterations",
                "fork.1"."⚙️" AS "⚙️",
                CAST(("ℚ"."y") AS int) AS "y",
                "fork.1"."height" AS "height",
                "fork.1"."x" AS "x",
                "fork.1"."width" AS "width"
         FROM   "fork.1",
                LATERAL (FROM range(("fork.1"."height"))) AS "ℚ"("y")
       ),
       "assignment.2"("width", "#️⃣", "⚙️", "iterations", "y", "height", "x", "alive") AS (
         SELECT "fork.2"."width" AS "width",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."iterations" AS "iterations",
                "fork.2"."y" AS "y",
                "fork.2"."height" AS "height",
                "fork.2"."x" AS "x",
                CAST(((("fork.2"."x"), ("fork.2"."y")) = ANY (VALUES
                                  ((1,0)),
                                           ((2,1)),
                         ((0,2)), ((1,2)), ((2,2))
                       )) AS boolean) AS "alive"
         FROM   "fork.2"
       ),
       "merge.1"("width", "#️⃣", "⚙️", "iterations", "y", "height", "x", "alive") AS (
         (SELECT "start.2"."width" AS "width",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."iterations" AS "iterations",
                 "start.2"."y" AS "y",
                 "start.2"."height" AS "height",
                 "start.2"."x" AS "x",
                 "start.2"."alive" AS "alive"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.2"."width" AS "width",
                 "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."⚙️" AS "⚙️",
                 "assignment.2"."iterations" AS "iterations",
                 "assignment.2"."y" AS "y",
                 "assignment.2"."height" AS "height",
                 "assignment.2"."x" AS "x",
                 "assignment.2"."alive" AS "alive"
          FROM   "assignment.2")
       ),
       "fork.3"("alive", "flip", "#️⃣", "⚙️", "iterations", "y", "height", "x", "width") AS (
         SELECT "merge.1"."alive" AS "alive",
                CAST(("ℚ"."flip") AS boolean) AS "flip",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."iterations" AS "iterations",
                "merge.1"."y" AS "y",
                "merge.1"."height" AS "height",
                "merge.1"."x" AS "x",
                "merge.1"."width" AS "width"
         FROM   "merge.1",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("flip")
       ),
       "assignment.3"("alive", "#️⃣", "⚙️", "🔍", "iterations", "y", "height", "x", "width") AS (
         SELECT "fork.3"."alive" AS "alive",
                "fork.3"."#️⃣" AS "#️⃣",
                "fork.3"."⚙️" AS "⚙️",
                CAST((("fork.3"."flip")) AS boolean) AS "🔍",
                "fork.3"."iterations" AS "iterations",
                "fork.3"."y" AS "y",
                "fork.3"."height" AS "height",
                "fork.3"."x" AS "x",
                "fork.3"."width" AS "width"
         FROM   "fork.3"
       ),
       "where.1"("width", "#️⃣", "⚙️", "y", "x", "alive") AS (
         SELECT "assignment.3"."width" AS "width",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."y" AS "y",
                "assignment.3"."x" AS "x",
                "assignment.3"."alive" AS "alive"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("width", "alive", "#️⃣", "⚙️", "iterations", "y", "height", "x") AS (
         SELECT "assignment.3"."width" AS "width",
                "assignment.3"."alive" AS "alive",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."iterations" AS "iterations",
                "assignment.3"."y" AS "y",
                "assignment.3"."height" AS "height",
                "assignment.3"."x" AS "x"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.4"("alive", "#️⃣", "⚙️", "iterations", "🔍", "y", "x", "height", "width") AS (
         SELECT "where.2"."alive" AS "alive",
                "where.2"."#️⃣" AS "#️⃣",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."iterations" AS "iterations",
                CAST((("where.2"."iterations") = 0) AS boolean) AS "🔍",
                "where.2"."y" AS "y",
                "where.2"."x" AS "x",
                "where.2"."height" AS "height",
                "where.2"."width" AS "width"
         FROM   "where.2"
       ),
       "gather.2"("width", "#️⃣", "⚙️", "y", "buffer") AS (
         SELECT "where.1"."width" AS "width",
                "where.1"."#️⃣" AS "#️⃣",
                "where.1"."⚙️" AS "⚙️",
                "where.1"."y" AS "y",
                CAST((string_agg(if(("where.1"."alive"), '#', '.'), '' ORDER BY ("where.1"."x"))) AS text) AS "buffer"
         FROM   "where.1"
         GROUP  BY "where.1"."#️⃣",
                   "where.1"."⚙️",
                   "where.1"."y",
                   "where.1"."width"
         HAVING COUNT(*) > 0
       ),
       "gather.3"("width", "#️⃣", "⚙️", "buffer") AS (
         SELECT "gather.2"."width" AS "width",
                "gather.2"."#️⃣" AS "#️⃣",
                "gather.2"."⚙️" AS "⚙️",
                CAST((string_agg(("gather.2"."buffer"), E'\n' ORDER BY ("gather.2"."y"))) AS text) AS "buffer"
         FROM   "gather.2"
         GROUP  BY "gather.2"."#️⃣",
                   "gather.2"."⚙️",
                   "gather.2"."width"
         HAVING COUNT(*) > 0
       ),
       "where.3"("⚙️") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("width", "alive", "#️⃣", "iterations", "⚙️", "y", "height", "x") AS (
         SELECT "assignment.4"."width" AS "width",
                "assignment.4"."alive" AS "alive",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."iterations" AS "iterations",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."y" AS "y",
                "assignment.4"."height" AS "height",
                "assignment.4"."x" AS "x"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.5"("alive", "#️⃣", "iterations", "⚙️", "y", "height", "x", "width") AS (
         SELECT "where.4"."alive" AS "alive",
                "where.4"."#️⃣" AS "#️⃣",
                CAST((("where.4"."iterations") - 1) AS int) AS "iterations",
                "where.4"."⚙️" AS "⚙️",
                "where.4"."y" AS "y",
                "where.4"."height" AS "height",
                "where.4"."x" AS "x",
                "where.4"."width" AS "width"
         FROM   "where.4"
       ),
       "emit.1"("📊.1", "#️⃣", "⚙️", "width") AS (
         SELECT "gather.3"."buffer" AS "📊.1",
                "gather.3"."#️⃣" AS "#️⃣",
                "gather.3"."⚙️" AS "⚙️",
                "gather.3"."width" AS "width"
         FROM   "gather.3"
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.3"."⚙️"
         FROM   "where.3"
         WHERE  FALSE
       ),
       "assignment.11"("#️⃣", "⚙️", "buffer") AS (
         SELECT "emit.1"."#️⃣" AS "#️⃣",
                "emit.1"."⚙️" AS "⚙️",
                CAST((repeat('-', ("emit.1"."width"))) AS text) AS "buffer"
         FROM   "emit.1"
       ),
       "fork.4"("#️⃣", "⚙️", "iterations", "y", "width", "dx", "height", "x", "alive") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."iterations" AS "iterations",
                "assignment.5"."y" AS "y",
                "assignment.5"."width" AS "width",
                CAST(("ℚ"."dx") AS int) AS "dx",
                "assignment.5"."height" AS "height",
                "assignment.5"."x" AS "x",
                "assignment.5"."alive" AS "alive"
         FROM   "assignment.5",
                (FROM generate_series(-1, 1)) AS "ℚ"("dx")
       ),
       "emit.2"("📊.1", "#️⃣", "⚙️") AS (
         SELECT "assignment.11"."buffer" AS "📊.1",
                "assignment.11"."#️⃣" AS "#️⃣",
                "assignment.11"."⚙️" AS "⚙️"
         FROM   "assignment.11"
       ),
       "fork.5"("alive", "#️⃣", "⚙️", "iterations", "y", "x", "dx", "dy", "height", "width") AS (
         SELECT "fork.4"."alive" AS "alive",
                "fork.4"."#️⃣" AS "#️⃣",
                "fork.4"."⚙️" AS "⚙️",
                "fork.4"."iterations" AS "iterations",
                "fork.4"."y" AS "y",
                "fork.4"."x" AS "x",
                "fork.4"."dx" AS "dx",
                CAST(("ℚ"."dy") AS int) AS "dy",
                "fork.4"."height" AS "height",
                "fork.4"."width" AS "width"
         FROM   "fork.4",
                (FROM generate_series(-1, 1)) AS "ℚ"("dy")
       ),
       "assignment.6"("#️⃣", "⚙️", "iterations", "y", "width", "dx", "height", "dy", "x", "alive") AS (
         SELECT "fork.5"."#️⃣" AS "#️⃣",
                "fork.5"."⚙️" AS "⚙️",
                "fork.5"."iterations" AS "iterations",
                CAST(((("fork.5"."height") + ("fork.5"."y") + ("fork.5"."dy")) % ("fork.5"."height")) AS int) AS "y",
                "fork.5"."width" AS "width",
                "fork.5"."dx" AS "dx",
                "fork.5"."height" AS "height",
                "fork.5"."dy" AS "dy",
                CAST(((("fork.5"."width")  + ("fork.5"."x") + ("fork.5"."dx")) % ("fork.5"."width")) AS int) AS "x",
                "fork.5"."alive" AS "alive"
         FROM   "fork.5"
       ),
       "stop.2"("⚙️") AS (
         SELECT "emit.2"."⚙️"
         FROM   "emit.2"
         WHERE  FALSE
       ),
       "assignment.7"("alive", "#️⃣", "⚙️", "iterations", "y", "original", "height", "x", "width") AS (
         SELECT "assignment.6"."alive" AS "alive",
                "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."iterations" AS "iterations",
                "assignment.6"."y" AS "y",
                CAST((("assignment.6"."dx") = 0 AND ("assignment.6"."dy") = 0) AS boolean) AS "original",
                "assignment.6"."height" AS "height",
                "assignment.6"."x" AS "x",
                "assignment.6"."width" AS "width"
         FROM   "assignment.6"
       ),
       "gather.1"("alive", "#️⃣", "neighbors", "⚙️", "iterations", "y", "height", "x", "width") AS (
         SELECT CAST((any_value(("assignment.7"."alive")) FILTER (WHERE ("assignment.7"."original"))) AS boolean) AS "alive",
                "assignment.7"."#️⃣" AS "#️⃣",
                CAST((count(*) FILTER (WHERE ("assignment.7"."alive") AND NOT ("assignment.7"."original"))) AS int) AS "neighbors",
                "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."iterations" AS "iterations",
                "assignment.7"."y" AS "y",
                "assignment.7"."height" AS "height",
                "assignment.7"."x" AS "x",
                "assignment.7"."width" AS "width"
         FROM   "assignment.7"
         GROUP  BY "assignment.7"."#️⃣",
                   "assignment.7"."⚙️",
                   "assignment.7"."iterations",
                   "assignment.7"."y",
                   "assignment.7"."height",
                   "assignment.7"."x",
                   "assignment.7"."width"
         HAVING COUNT(*) > 0
       ),
       "assignment.8"("#️⃣", "neighbors", "⚙️", "iterations", "y", "🔍", "height", "x", "width") AS (
         SELECT "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."neighbors" AS "neighbors",
                "gather.1"."⚙️" AS "⚙️",
                "gather.1"."iterations" AS "iterations",
                "gather.1"."y" AS "y",
                CAST((("gather.1"."alive")) AS boolean) AS "🔍",
                "gather.1"."height" AS "height",
                "gather.1"."x" AS "x",
                "gather.1"."width" AS "width"
         FROM   "gather.1"
       ),
       "where.5"("#️⃣", "neighbors", "⚙️", "iterations", "y", "height", "x", "width") AS (
         SELECT "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."neighbors" AS "neighbors",
                "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."iterations" AS "iterations",
                "assignment.8"."y" AS "y",
                "assignment.8"."height" AS "height",
                "assignment.8"."x" AS "x",
                "assignment.8"."width" AS "width"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.6"("#️⃣", "neighbors", "⚙️", "iterations", "y", "height", "x", "width") AS (
         SELECT "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."neighbors" AS "neighbors",
                "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."iterations" AS "iterations",
                "assignment.8"."y" AS "y",
                "assignment.8"."height" AS "height",
                "assignment.8"."x" AS "x",
                "assignment.8"."width" AS "width"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.10"("width", "#️⃣", "⚙️", "iterations", "y", "height", "x", "alive") AS (
         SELECT "where.6"."width" AS "width",
                "where.6"."#️⃣" AS "#️⃣",
                "where.6"."⚙️" AS "⚙️",
                "where.6"."iterations" AS "iterations",
                "where.6"."y" AS "y",
                "where.6"."height" AS "height",
                "where.6"."x" AS "x",
                CAST((("where.6"."neighbors") = 3) AS boolean) AS "alive"
         FROM   "where.6"
       ),
       "assignment.9"("width", "#️⃣", "⚙️", "iterations", "y", "height", "x", "alive") AS (
         SELECT "where.5"."width" AS "width",
                "where.5"."#️⃣" AS "#️⃣",
                "where.5"."⚙️" AS "⚙️",
                "where.5"."iterations" AS "iterations",
                "where.5"."y" AS "y",
                "where.5"."height" AS "height",
                "where.5"."x" AS "x",
                CAST((("where.5"."neighbors") BETWEEN 2 AND 3) AS boolean) AS "alive"
         FROM   "where.5"
       ),
       "jump.1"("🏷️", "#️⃣", "width", "iterations", "y", "height", "x", "alive") AS (
         SELECT 'start.2' AS "🏷️",
                "assignment.9"."#️⃣" AS "#️⃣",
                "assignment.9"."width" AS "width",
                "assignment.9"."iterations" AS "iterations",
                "assignment.9"."y" AS "y",
                "assignment.9"."height" AS "height",
                "assignment.9"."x" AS "x",
                "assignment.9"."alive" AS "alive"
         FROM   "assignment.9"
       ),
       "jump.2"("🏷️", "#️⃣", "width", "iterations", "y", "height", "x", "alive") AS (
         SELECT 'start.2' AS "🏷️",
                "assignment.10"."#️⃣" AS "#️⃣",
                "assignment.10"."width" AS "width",
                "assignment.10"."iterations" AS "iterations",
                "assignment.10"."y" AS "y",
                "assignment.10"."height" AS "height",
                "assignment.10"."x" AS "x",
                "assignment.10"."alive" AS "alive"
         FROM   "assignment.10"
       )
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊.1") AS text) AS "📊.1",
             CAST((NULL) AS int) AS "width",
             CAST((NULL) AS int) AS "iterations",
             CAST((NULL) AS int) AS "y",
             CAST((NULL) AS int) AS "height",
             CAST((NULL) AS int) AS "x",
             CAST((NULL) AS boolean) AS "alive"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.2"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.2"."📊.1") AS text) AS "📊.1",
             CAST((NULL) AS int) AS "width",
             CAST((NULL) AS int) AS "iterations",
             CAST((NULL) AS int) AS "y",
             CAST((NULL) AS int) AS "height",
             CAST((NULL) AS int) AS "x",
             CAST((NULL) AS boolean) AS "alive"
      FROM   "emit.2")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS text) AS "📊.1",
             CAST(("jump.1"."width") AS int) AS "width",
             CAST(("jump.1"."iterations") AS int) AS "iterations",
             CAST(("jump.1"."y") AS int) AS "y",
             CAST(("jump.1"."height") AS int) AS "height",
             CAST(("jump.1"."x") AS int) AS "x",
             CAST(("jump.1"."alive") AS boolean) AS "alive"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST(("jump.2"."🏷️") AS text) AS "🏷️",
             CAST(("jump.2"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS text) AS "📊.1",
             CAST(("jump.2"."width") AS int) AS "width",
             CAST(("jump.2"."iterations") AS int) AS "iterations",
             CAST(("jump.2"."y") AS int) AS "y",
             CAST(("jump.2"."height") AS int) AS "height",
             CAST(("jump.2"."x") AS int) AS "x",
             CAST(("jump.2"."alive") AS boolean) AS "alive"
      FROM   "jump.2"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;