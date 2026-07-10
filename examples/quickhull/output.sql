WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊.1", "left", "right") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS point) AS "📊.1",
            CAST((NULL) AS point) AS "left",
            CAST((NULL) AS point) AS "right")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("#️⃣", "left", "⚙️", "right") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                "🔄"."left" AS "left",
                NULL AS "⚙️",
                "🔄"."right" AS "right"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("⚙️", "#️⃣", "min") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣",
                CAST((SELECT argmin(p, p.x) FROM points AS p) AS point) AS "min"
         FROM   "start.1"
       ),
       "emit.1"("min", "⚙️", "#️⃣", "📊.1") AS (
         SELECT "assignment.1"."min" AS "min",
                "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."min" AS "📊.1"
         FROM   "assignment.1"
       ),
       "assignment.2"("⚙️", "max", "#️⃣", "min") AS (
         SELECT "emit.1"."⚙️" AS "⚙️",
                CAST((SELECT argmax(p, p.x) FROM points AS p) AS point) AS "max",
                "emit.1"."#️⃣" AS "#️⃣",
                "emit.1"."min" AS "min"
         FROM   "emit.1"
       ),
       "emit.2"("max", "📊.1", "⚙️", "#️⃣", "min") AS (
         SELECT "assignment.2"."max" AS "max",
                "assignment.2"."max" AS "📊.1",
                "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."#️⃣" AS "#️⃣",
                "assignment.2"."min" AS "min"
         FROM   "assignment.2"
       ),
       "fork.1"("flip", "max", "#️⃣", "⚙️", "min") AS (
         SELECT "ℚ"."flip" AS "flip",
                "emit.2"."max" AS "max",
                "emit.2"."#️⃣" AS "#️⃣",
                "emit.2"."⚙️" AS "⚙️",
                "emit.2"."min" AS "min"
         FROM   "emit.2",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("flip")
       ),
       "where.1"("#️⃣", "max", "⚙️", "min") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."max" AS "max",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."min" AS "min"
         FROM   "fork.1"
         WHERE  "fork.1"."flip" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("#️⃣", "max", "⚙️", "min") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."max" AS "max",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."min" AS "min"
         FROM   "fork.1"
         WHERE  "fork.1"."flip" IS DISTINCT FROM TRUE
       ),
       "assignment.3"("#️⃣", "left", "max", "⚙️") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                CAST((("where.1"."min")) AS point) AS "left",
                "where.1"."max" AS "max",
                "where.1"."⚙️" AS "⚙️"
         FROM   "where.1"
       ),
       "assignment.5"("#️⃣", "left", "⚙️", "min") AS (
         SELECT "where.2"."#️⃣" AS "#️⃣",
                CAST((("where.2"."max")) AS point) AS "left",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."min" AS "min"
         FROM   "where.2"
       ),
       "assignment.4"("#️⃣", "right", "⚙️", "left") AS (
         SELECT "assignment.3"."#️⃣" AS "#️⃣",
                CAST((("assignment.3"."max")) AS point) AS "right",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."left" AS "left"
         FROM   "assignment.3"
       ),
       "assignment.6"("#️⃣", "right", "⚙️", "left") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                CAST((("assignment.5"."min")) AS point) AS "right",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."left" AS "left"
         FROM   "assignment.5"
       ),
       "merge.1"("#️⃣", "left", "⚙️", "right") AS (
         (SELECT "assignment.4"."#️⃣" AS "#️⃣",
                 "assignment.4"."left" AS "left",
                 "assignment.4"."⚙️" AS "⚙️",
                 "assignment.4"."right" AS "right"
          FROM   "assignment.4")
           UNION ALL
         (SELECT "assignment.6"."#️⃣" AS "#️⃣",
                 "assignment.6"."left" AS "left",
                 "assignment.6"."⚙️" AS "⚙️",
                 "assignment.6"."right" AS "right"
          FROM   "assignment.6")
       ),
       "merge.2"("#️⃣", "left", "⚙️", "right") AS (
         (SELECT "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."left" AS "left",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."right" AS "right"
          FROM   "start.2")
           UNION ALL
         (SELECT "merge.1"."#️⃣" AS "#️⃣",
                 "merge.1"."left" AS "left",
                 "merge.1"."⚙️" AS "⚙️",
                 "merge.1"."right" AS "right"
          FROM   "merge.1")
       ),
       "assignment.7"("next", "right", "left", "⚙️", "#️⃣") AS (
         SELECT CAST((WITH
                         distances(point, distance) AS (
                           SELECT p,
                                  (
                                    dy * p.x -
                                    dx * p.y +
                                    ("merge.2"."right").x * ("merge.2"."left").y -
                                    ("merge.2"."right").y * ("merge.2"."left").x
                                  ) / sqrt(dx * dx + dy * dy)
                           FROM   points AS p,
                                  (SELECT ("merge.2"."right").y - ("merge.2"."left").y AS dy,
                                          ("merge.2"."right").x - ("merge.2"."left").x AS dx)
                           WHERE  p <> ("merge.2"."left")
                           AND    p <> ("merge.2"."right")
                         )
                       SELECT point
                       FROM   distances
                       WHERE  distance > 0
                       ORDER  BY distance DESC
                       LIMIT  1) AS point) AS "next",
                "merge.2"."right" AS "right",
                "merge.2"."left" AS "left",
                "merge.2"."⚙️" AS "⚙️",
                "merge.2"."#️⃣" AS "#️⃣"
         FROM   "merge.2"
       ),
       "assignment.8"("next", "cond", "left", "#️⃣", "right", "⚙️") AS (
         SELECT "assignment.7"."next" AS "next",
                CAST((("assignment.7"."next") IS NULL) AS boolean) AS "cond",
                "assignment.7"."left" AS "left",
                "assignment.7"."#️⃣" AS "#️⃣",
                "assignment.7"."right" AS "right",
                "assignment.7"."⚙️" AS "⚙️"
         FROM   "assignment.7"
       ),
       "where.3"("⚙️") AS (
         SELECT "assignment.8"."⚙️" AS "⚙️"
         FROM   "assignment.8"
         WHERE  "assignment.8"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("next", "left", "#️⃣", "right") AS (
         SELECT "assignment.8"."next" AS "next",
                "assignment.8"."left" AS "left",
                "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."right" AS "right"
         FROM   "assignment.8"
         WHERE  "assignment.8"."cond" IS DISTINCT FROM TRUE
       ),
       "emit.3"("next", "left", "right", "#️⃣", "📊.1") AS (
         SELECT "where.4"."next" AS "next",
                "where.4"."left" AS "left",
                "where.4"."right" AS "right",
                "where.4"."#️⃣" AS "#️⃣",
                "where.4"."next" AS "📊.1"
         FROM   "where.4"
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.3"."⚙️"
         FROM   "where.3"
         WHERE  FALSE
       ),
       "fork.2"("next", "flip", "right", "left", "#️⃣") AS (
         SELECT "emit.3"."next" AS "next",
                "ℚ"."flip" AS "flip",
                "emit.3"."right" AS "right",
                "emit.3"."left" AS "left",
                "emit.3"."#️⃣" AS "#️⃣"
         FROM   "emit.3",
                (VALUES (TRUE), (FALSE)) AS "ℚ"("flip")
       ),
       "where.5"("next", "right", "#️⃣") AS (
         SELECT "fork.2"."next" AS "next",
                "fork.2"."right" AS "right",
                "fork.2"."#️⃣" AS "#️⃣"
         FROM   "fork.2"
         WHERE  "fork.2"."flip" IS NOT DISTINCT FROM TRUE
       ),
       "where.6"("next", "left", "#️⃣") AS (
         SELECT "fork.2"."next" AS "next",
                "fork.2"."left" AS "left",
                "fork.2"."#️⃣" AS "#️⃣"
         FROM   "fork.2"
         WHERE  "fork.2"."flip" IS DISTINCT FROM TRUE
       ),
       "assignment.10"("right", "#️⃣", "left") AS (
         SELECT CAST((("where.6"."next")) AS point) AS "right",
                "where.6"."#️⃣" AS "#️⃣",
                "where.6"."left" AS "left"
         FROM   "where.6"
       ),
       "assignment.9"("left", "#️⃣", "right") AS (
         SELECT CAST((("where.5"."next")) AS point) AS "left",
                "where.5"."#️⃣" AS "#️⃣",
                "where.5"."right" AS "right"
         FROM   "where.5"
       ),
       "jump.1"("#️⃣", "right", "🏷️", "left") AS (
         SELECT "assignment.10"."#️⃣" AS "#️⃣",
                "assignment.10"."right" AS "right",
                'start.2' AS "🏷️",
                "assignment.10"."left" AS "left"
         FROM   "assignment.10"
       ),
       "jump.2"("#️⃣", "right", "🏷️", "left") AS (
         SELECT "assignment.9"."#️⃣" AS "#️⃣",
                "assignment.9"."right" AS "right",
                'start.2' AS "🏷️",
                "assignment.9"."left" AS "left"
         FROM   "assignment.9"
       )
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊.1") AS point) AS "📊.1",
             CAST((NULL) AS point) AS "left",
             CAST((NULL) AS point) AS "right"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.2"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.2"."📊.1") AS point) AS "📊.1",
             CAST((NULL) AS point) AS "left",
             CAST((NULL) AS point) AS "right"
      FROM   "emit.2")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.3"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.3"."📊.1") AS point) AS "📊.1",
             CAST((NULL) AS point) AS "left",
             CAST((NULL) AS point) AS "right"
      FROM   "emit.3")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS point) AS "📊.1",
             CAST(("jump.1"."left") AS point) AS "left",
             CAST(("jump.1"."right") AS point) AS "right"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST(("jump.2"."🏷️") AS text) AS "🏷️",
             CAST(("jump.2"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS point) AS "📊.1",
             CAST(("jump.2"."left") AS point) AS "left",
             CAST(("jump.2"."right") AS point) AS "right"
      FROM   "jump.2"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;