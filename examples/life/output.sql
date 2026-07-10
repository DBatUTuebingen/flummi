WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊.1", "width", "alive", "x", "y", "height", "iterations") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS text) AS "📊.1",
            CAST((NULL) AS int) AS "width",
            CAST((NULL) AS boolean) AS "alive",
            CAST((NULL) AS int) AS "x",
            CAST((NULL) AS int) AS "y",
            CAST((NULL) AS int) AS "height",
            CAST((NULL) AS int) AS "iterations")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("⚙️", "width", "alive", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT NULL AS "⚙️",
                "🔄"."width" AS "width",
                "🔄"."alive" AS "alive",
                "🔄"."x" AS "x",
                "🔄"."y" AS "y",
                "🔄"."height" AS "height",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."iterations" AS "iterations"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("⚙️", "width", "height", "#️⃣", "iterations") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                CAST((10) AS int) AS "width",
                CAST((10) AS int) AS "height",
                "start.1"."#️⃣" AS "#️⃣",
                CAST((100) AS int) AS "iterations"
         FROM   "start.1"
       ),
       "fork.1"("⚙️", "width", "x", "height", "#️⃣", "iterations") AS (
         SELECT "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."width" AS "width",
                "ℚ"."x" AS "x",
                "assignment.1"."height" AS "height",
                "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."iterations" AS "iterations"
         FROM   "assignment.1",
                LATERAL (FROM range(("assignment.1"."width"))) AS "ℚ"("x")
       ),
       "fork.2"("⚙️", "width", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "fork.1"."⚙️" AS "⚙️",
                "fork.1"."width" AS "width",
                "fork.1"."x" AS "x",
                "ℚ"."y" AS "y",
                "fork.1"."height" AS "height",
                "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."iterations" AS "iterations"
         FROM   "fork.1",
                LATERAL (FROM range(("fork.1"."height"))) AS "ℚ"("y")
       ),
       "assignment.2"("⚙️", "width", "alive", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "fork.2"."⚙️" AS "⚙️",
                "fork.2"."width" AS "width",
                CAST(((("fork.2"."x"), ("fork.2"."y")) = ANY (VALUES
                                  ((1,0)),
                                           ((2,1)),
                         ((0,2)), ((1,2)), ((2,2))
                       )) AS boolean) AS "alive",
                "fork.2"."x" AS "x",
                "fork.2"."y" AS "y",
                "fork.2"."height" AS "height",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."iterations" AS "iterations"
         FROM   "fork.2"
       ),
       "merge.1"("⚙️", "width", "alive", "x", "y", "height", "#️⃣", "iterations") AS (
         (SELECT "assignment.2"."⚙️" AS "⚙️",
                 "assignment.2"."width" AS "width",
                 "assignment.2"."alive" AS "alive",
                 "assignment.2"."x" AS "x",
                 "assignment.2"."y" AS "y",
                 "assignment.2"."height" AS "height",
                 "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."iterations" AS "iterations"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."⚙️" AS "⚙️",
                 "start.2"."width" AS "width",
                 "start.2"."alive" AS "alive",
                 "start.2"."x" AS "x",
                 "start.2"."y" AS "y",
                 "start.2"."height" AS "height",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."iterations" AS "iterations"
          FROM   "start.2")
       ),
       "fork.3"("width", "alive", "y", "height", "flip", "#️⃣", "iterations", "⚙️", "x") AS (
         SELECT "merge.1"."width" AS "width",
                "merge.1"."alive" AS "alive",
                "merge.1"."y" AS "y",
                "merge.1"."height" AS "height",
                "ℚ"."flip" AS "flip",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."iterations" AS "iterations",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."x" AS "x"
         FROM   "merge.1",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("flip")
       ),
       "assignment.3"("width", "alive", "y", "height", "#️⃣", "🔍", "iterations", "⚙️", "x") AS (
         SELECT "fork.3"."width" AS "width",
                "fork.3"."alive" AS "alive",
                "fork.3"."y" AS "y",
                "fork.3"."height" AS "height",
                "fork.3"."#️⃣" AS "#️⃣",
                CAST((("fork.3"."flip")) AS boolean) AS "🔍",
                "fork.3"."iterations" AS "iterations",
                "fork.3"."⚙️" AS "⚙️",
                "fork.3"."x" AS "x"
         FROM   "fork.3"
       ),
       "where.1"("⚙️", "width", "alive", "x", "y", "#️⃣") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."width" AS "width",
                "assignment.3"."alive" AS "alive",
                "assignment.3"."x" AS "x",
                "assignment.3"."y" AS "y",
                "assignment.3"."#️⃣" AS "#️⃣"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("⚙️", "width", "alive", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."width" AS "width",
                "assignment.3"."alive" AS "alive",
                "assignment.3"."x" AS "x",
                "assignment.3"."y" AS "y",
                "assignment.3"."height" AS "height",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."iterations" AS "iterations"
         FROM   "assignment.3"
         WHERE  "assignment.3"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.4"("width", "alive", "y", "height", "#️⃣", "🔍", "iterations", "⚙️", "x") AS (
         SELECT "where.2"."width" AS "width",
                "where.2"."alive" AS "alive",
                "where.2"."y" AS "y",
                "where.2"."height" AS "height",
                "where.2"."#️⃣" AS "#️⃣",
                CAST((("where.2"."iterations") = 0) AS boolean) AS "🔍",
                "where.2"."iterations" AS "iterations",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."x" AS "x"
         FROM   "where.2"
       ),
       "gather.2"("⚙️", "width", "y", "#️⃣", "buffer") AS (
         SELECT "where.1"."⚙️" AS "⚙️",
                "where.1"."width" AS "width",
                "where.1"."y" AS "y",
                "where.1"."#️⃣" AS "#️⃣",
                CAST((string_agg(if(("where.1"."alive"), '#', '.'), '' ORDER BY ("where.1"."x"))) AS text) AS "buffer"
         FROM   "where.1"
         GROUP  BY "where.1"."⚙️",
                   "where.1"."width",
                   "where.1"."y",
                   "where.1"."#️⃣"
         HAVING COUNT(*) > 0
       ),
       "gather.3"("⚙️", "width", "#️⃣", "buffer") AS (
         SELECT "gather.2"."⚙️" AS "⚙️",
                "gather.2"."width" AS "width",
                "gather.2"."#️⃣" AS "#️⃣",
                CAST((string_agg(("gather.2"."buffer"), E'\n' ORDER BY ("gather.2"."y"))) AS text) AS "buffer"
         FROM   "gather.2"
         GROUP  BY "gather.2"."⚙️",
                   "gather.2"."width",
                   "gather.2"."#️⃣"
         HAVING COUNT(*) > 0
       ),
       "where.3"("⚙️") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("⚙️", "width", "alive", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."width" AS "width",
                "assignment.4"."alive" AS "alive",
                "assignment.4"."x" AS "x",
                "assignment.4"."y" AS "y",
                "assignment.4"."height" AS "height",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."iterations" AS "iterations"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.5"("⚙️", "width", "alive", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "where.4"."⚙️" AS "⚙️",
                "where.4"."width" AS "width",
                "where.4"."alive" AS "alive",
                "where.4"."x" AS "x",
                "where.4"."y" AS "y",
                "where.4"."height" AS "height",
                "where.4"."#️⃣" AS "#️⃣",
                CAST((("where.4"."iterations") - 1) AS int) AS "iterations"
         FROM   "where.4"
       ),
       "emit.1"("width", "⚙️", "#️⃣", "📊.1") AS (
         SELECT "gather.3"."width" AS "width",
                "gather.3"."⚙️" AS "⚙️",
                "gather.3"."#️⃣" AS "#️⃣",
                "gather.3"."buffer" AS "📊.1"
         FROM   "gather.3"
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.3"."⚙️"
         FROM   "where.3"
         WHERE  FALSE
       ),
       "assignment.11"("⚙️", "#️⃣", "buffer") AS (
         SELECT "emit.1"."⚙️" AS "⚙️",
                "emit.1"."#️⃣" AS "#️⃣",
                CAST((repeat('-', ("emit.1"."width"))) AS text) AS "buffer"
         FROM   "emit.1"
       ),
       "fork.4"("width", "alive", "y", "height", "#️⃣", "iterations", "⚙️", "dx", "x") AS (
         SELECT "assignment.5"."width" AS "width",
                "assignment.5"."alive" AS "alive",
                "assignment.5"."y" AS "y",
                "assignment.5"."height" AS "height",
                "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."iterations" AS "iterations",
                "assignment.5"."⚙️" AS "⚙️",
                "ℚ"."dx" AS "dx",
                "assignment.5"."x" AS "x"
         FROM   "assignment.5",
                (FROM generate_series(-1, 1)) AS "ℚ"("dx")
       ),
       "emit.2"("⚙️", "#️⃣", "📊.1") AS (
         SELECT "assignment.11"."⚙️" AS "⚙️",
                "assignment.11"."#️⃣" AS "#️⃣",
                "assignment.11"."buffer" AS "📊.1"
         FROM   "assignment.11"
       ),
       "fork.5"("width", "alive", "y", "height", "#️⃣", "iterations", "dy", "⚙️", "dx", "x") AS (
         SELECT "fork.4"."width" AS "width",
                "fork.4"."alive" AS "alive",
                "fork.4"."y" AS "y",
                "fork.4"."height" AS "height",
                "fork.4"."#️⃣" AS "#️⃣",
                "fork.4"."iterations" AS "iterations",
                "ℚ"."dy" AS "dy",
                "fork.4"."⚙️" AS "⚙️",
                "fork.4"."dx" AS "dx",
                "fork.4"."x" AS "x"
         FROM   "fork.4",
                (FROM generate_series(-1, 1)) AS "ℚ"("dy")
       ),
       "assignment.6"("width", "alive", "y", "height", "#️⃣", "iterations", "dy", "⚙️", "dx", "x") AS (
         SELECT "fork.5"."width" AS "width",
                "fork.5"."alive" AS "alive",
                CAST(((("fork.5"."height") + ("fork.5"."y") + ("fork.5"."dy")) % ("fork.5"."height")) AS int) AS "y",
                "fork.5"."height" AS "height",
                "fork.5"."#️⃣" AS "#️⃣",
                "fork.5"."iterations" AS "iterations",
                "fork.5"."dy" AS "dy",
                "fork.5"."⚙️" AS "⚙️",
                "fork.5"."dx" AS "dx",
                CAST(((("fork.5"."width")  + ("fork.5"."x") + ("fork.5"."dx")) % ("fork.5"."width")) AS int) AS "x"
         FROM   "fork.5"
       ),
       "stop.2"("⚙️") AS (
         SELECT "emit.2"."⚙️"
         FROM   "emit.2"
         WHERE  FALSE
       ),
       "assignment.7"("width", "alive", "y", "height", "#️⃣", "iterations", "original", "⚙️", "x") AS (
         SELECT "assignment.6"."width" AS "width",
                "assignment.6"."alive" AS "alive",
                "assignment.6"."y" AS "y",
                "assignment.6"."height" AS "height",
                "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."iterations" AS "iterations",
                CAST((("assignment.6"."dx") = 0 AND ("assignment.6"."dy") = 0) AS boolean) AS "original",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."x" AS "x"
         FROM   "assignment.6"
       ),
       "gather.1"("width", "alive", "y", "height", "#️⃣", "iterations", "neighbors", "⚙️", "x") AS (
         SELECT "assignment.7"."width" AS "width",
                CAST((any_value(("assignment.7"."alive")) FILTER (WHERE ("assignment.7"."original"))) AS boolean) AS "alive",
                "assignment.7"."y" AS "y",
                "assignment.7"."height" AS "height",
                "assignment.7"."#️⃣" AS "#️⃣",
                "assignment.7"."iterations" AS "iterations",
                CAST((count(*) FILTER (WHERE ("assignment.7"."alive") AND NOT ("assignment.7"."original"))) AS int) AS "neighbors",
                "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."x" AS "x"
         FROM   "assignment.7"
         GROUP  BY "assignment.7"."width",
                   "assignment.7"."y",
                   "assignment.7"."height",
                   "assignment.7"."#️⃣",
                   "assignment.7"."iterations",
                   "assignment.7"."⚙️",
                   "assignment.7"."x"
         HAVING COUNT(*) > 0
       ),
       "assignment.8"("width", "y", "height", "#️⃣", "🔍", "iterations", "neighbors", "⚙️", "x") AS (
         SELECT "gather.1"."width" AS "width",
                "gather.1"."y" AS "y",
                "gather.1"."height" AS "height",
                "gather.1"."#️⃣" AS "#️⃣",
                CAST((("gather.1"."alive")) AS boolean) AS "🔍",
                "gather.1"."iterations" AS "iterations",
                "gather.1"."neighbors" AS "neighbors",
                "gather.1"."⚙️" AS "⚙️",
                "gather.1"."x" AS "x"
         FROM   "gather.1"
       ),
       "where.5"("neighbors", "⚙️", "width", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "assignment.8"."neighbors" AS "neighbors",
                "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."width" AS "width",
                "assignment.8"."x" AS "x",
                "assignment.8"."y" AS "y",
                "assignment.8"."height" AS "height",
                "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."iterations" AS "iterations"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.6"("neighbors", "⚙️", "width", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "assignment.8"."neighbors" AS "neighbors",
                "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."width" AS "width",
                "assignment.8"."x" AS "x",
                "assignment.8"."y" AS "y",
                "assignment.8"."height" AS "height",
                "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."iterations" AS "iterations"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.10"("⚙️", "width", "alive", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "where.6"."⚙️" AS "⚙️",
                "where.6"."width" AS "width",
                CAST((("where.6"."neighbors") = 3) AS boolean) AS "alive",
                "where.6"."x" AS "x",
                "where.6"."y" AS "y",
                "where.6"."height" AS "height",
                "where.6"."#️⃣" AS "#️⃣",
                "where.6"."iterations" AS "iterations"
         FROM   "where.6"
       ),
       "assignment.9"("⚙️", "width", "alive", "x", "y", "height", "#️⃣", "iterations") AS (
         SELECT "where.5"."⚙️" AS "⚙️",
                "where.5"."width" AS "width",
                CAST((("where.5"."neighbors") BETWEEN 2 AND 3) AS boolean) AS "alive",
                "where.5"."x" AS "x",
                "where.5"."y" AS "y",
                "where.5"."height" AS "height",
                "where.5"."#️⃣" AS "#️⃣",
                "where.5"."iterations" AS "iterations"
         FROM   "where.5"
       ),
       "jump.1"("#️⃣", "width", "alive", "🏷️", "y", "x", "height", "iterations") AS (
         SELECT "assignment.10"."#️⃣" AS "#️⃣",
                "assignment.10"."width" AS "width",
                "assignment.10"."alive" AS "alive",
                'start.2' AS "🏷️",
                "assignment.10"."y" AS "y",
                "assignment.10"."x" AS "x",
                "assignment.10"."height" AS "height",
                "assignment.10"."iterations" AS "iterations"
         FROM   "assignment.10"
       ),
       "jump.2"("#️⃣", "width", "alive", "🏷️", "y", "x", "height", "iterations") AS (
         SELECT "assignment.9"."#️⃣" AS "#️⃣",
                "assignment.9"."width" AS "width",
                "assignment.9"."alive" AS "alive",
                'start.2' AS "🏷️",
                "assignment.9"."y" AS "y",
                "assignment.9"."x" AS "x",
                "assignment.9"."height" AS "height",
                "assignment.9"."iterations" AS "iterations"
         FROM   "assignment.9"
       )
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊.1") AS text) AS "📊.1",
             CAST((NULL) AS int) AS "width",
             CAST((NULL) AS boolean) AS "alive",
             CAST((NULL) AS int) AS "x",
             CAST((NULL) AS int) AS "y",
             CAST((NULL) AS int) AS "height",
             CAST((NULL) AS int) AS "iterations"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.2"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.2"."📊.1") AS text) AS "📊.1",
             CAST((NULL) AS int) AS "width",
             CAST((NULL) AS boolean) AS "alive",
             CAST((NULL) AS int) AS "x",
             CAST((NULL) AS int) AS "y",
             CAST((NULL) AS int) AS "height",
             CAST((NULL) AS int) AS "iterations"
      FROM   "emit.2")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS text) AS "📊.1",
             CAST(("jump.1"."width") AS int) AS "width",
             CAST(("jump.1"."alive") AS boolean) AS "alive",
             CAST(("jump.1"."x") AS int) AS "x",
             CAST(("jump.1"."y") AS int) AS "y",
             CAST(("jump.1"."height") AS int) AS "height",
             CAST(("jump.1"."iterations") AS int) AS "iterations"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST(("jump.2"."🏷️") AS text) AS "🏷️",
             CAST(("jump.2"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS text) AS "📊.1",
             CAST(("jump.2"."width") AS int) AS "width",
             CAST(("jump.2"."alive") AS boolean) AS "alive",
             CAST(("jump.2"."x") AS int) AS "x",
             CAST(("jump.2"."y") AS int) AS "y",
             CAST(("jump.2"."height") AS int) AS "height",
             CAST(("jump.2"."iterations") AS int) AS "iterations"
      FROM   "jump.2"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;