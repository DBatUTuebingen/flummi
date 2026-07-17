WITH RECURSIVE
  "🔄"("#️⃣", "🏷️", "📊.1", "cells", "empty_cells") AS (
    (SELECT CAST((0) AS int) AS "#️⃣",
            CAST(('start.1') AS text) AS "🏷️",
            CAST((NULL) AS int[]) AS "📊.1",
            CAST((NULL) AS int[]) AS "cells",
            CAST((NULL) AS int[]) AS "empty_cells")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "assignment.1"("#️⃣", "⚙️", "cells") AS (
         SELECT "start.1"."#️⃣" AS "#️⃣",
                "start.1"."⚙️" AS "⚙️",
                CAST((SELECT cells
                       FROM   sudoku
                       LIMIT  1) AS int[]) AS "cells"
         FROM   "start.1"
       ),
       "assignment.2"("#️⃣", "⚙️", "cells", "empty_cells") AS (
         SELECT "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."cells" AS "cells",
                CAST((SELECT list(cell - 1) FILTER (value = 0)
                       FROM   unnest(("assignment.1"."cells")) WITH ORDINALITY AS _(value, cell)) AS int[]) AS "empty_cells"
         FROM   "assignment.1"
       ),
       "start.2"("#️⃣", "⚙️", "cells", "empty_cells") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️",
                "🔄"."cells" AS "cells",
                "🔄"."empty_cells" AS "empty_cells"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "merge.1"("#️⃣", "⚙️", "cells", "empty_cells") AS (
         (SELECT "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."⚙️" AS "⚙️",
                 "assignment.2"."cells" AS "cells",
                 "assignment.2"."empty_cells" AS "empty_cells"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."cells" AS "cells",
                 "start.2"."empty_cells" AS "empty_cells"
          FROM   "start.2")
       ),
       "fork.1"("#️⃣", "⚙️", "cells", "empty_cells", "idx") AS (
         SELECT "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."cells" AS "cells",
                "merge.1"."empty_cells" AS "empty_cells",
                CAST(("ℚ"."idx") AS int) AS "idx"
         FROM   "merge.1",
                LATERAL (FROM unnest(("merge.1"."empty_cells"))) AS "ℚ"("idx")
       ),
       "assignment.3"("#️⃣", "⚙️", "cells", "empty_cells", "idx", "cell") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."cells" AS "cells",
                "fork.1"."empty_cells" AS "empty_cells",
                "fork.1"."idx" AS "idx",
                CAST((("fork.1"."empty_cells")[("fork.1"."idx")]) AS int) AS "cell"
         FROM   "fork.1"
       ),
       "assignment.4"("#️⃣", "⚙️", "cells", "empty_cells", "cell") AS (
         SELECT "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."cells" AS "cells",
                CAST((("assignment.3"."empty_cells")[:("assignment.3"."idx")] || ("assignment.3"."empty_cells")[("assignment.3"."idx")+2:]) AS int[]) AS "empty_cells",
                "assignment.3"."cell" AS "cell"
         FROM   "assignment.3"
       ),
       "fork.2"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."empty_cells" AS "empty_cells",
                "assignment.4"."cell" AS "cell",
                CAST(("ℚ"."value") AS int) AS "value"
         FROM   "assignment.4",
                (FROM generate_series(1, 9)) AS "ℚ"("value")
       ),
       "assignment.5"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value", "ok") AS (
         SELECT "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."cells" AS "cells",
                "fork.2"."empty_cells" AS "empty_cells",
                "fork.2"."cell" AS "cell",
                "fork.2"."value" AS "value",
                CAST((NOT EXISTS (
                         FROM  generate_series(1, 9) AS _(o)
                         WHERE ("fork.2"."value") IN (("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + o                 ],
                                       ("fork.2"."cells")[("fork.2"."cell") % 9                             + (o-1)*9 + 1       ],
                                       ("fork.2"."cells")[((("fork.2"."cell")//3) % 3) * 3 + (("fork.2"."cell")//27) * 27 + o + ((o-1)//3) * 6])
                       )) AS boolean) AS "ok"
         FROM   "fork.2"
       ),
       "assignment.6"("#️⃣", "⚙️", "🔍", "cells", "empty_cells", "cell", "value") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."⚙️" AS "⚙️",
                CAST((("assignment.5"."ok")) AS boolean) AS "🔍",
                "assignment.5"."cells" AS "cells",
                "assignment.5"."empty_cells" AS "empty_cells",
                "assignment.5"."cell" AS "cell",
                "assignment.5"."value" AS "value"
         FROM   "assignment.5"
       ),
       "where.1"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value") AS (
         SELECT "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."cells" AS "cells",
                "assignment.6"."empty_cells" AS "empty_cells",
                "assignment.6"."cell" AS "cell",
                "assignment.6"."value" AS "value"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "assignment.7"("#️⃣", "⚙️", "cells", "empty_cells") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                "where.1"."⚙️" AS "⚙️",
                CAST((concat(("where.1"."cells")[:("where.1"."cell")], [("where.1"."value")], ("where.1"."cells")[("where.1"."cell")+2:])) AS int[]) AS "cells",
                "where.1"."empty_cells" AS "empty_cells"
         FROM   "where.1"
       ),
       "assignment.8"("#️⃣", "⚙️", "🔍", "cells", "empty_cells") AS (
         SELECT "assignment.7"."#️⃣" AS "#️⃣",
                "assignment.7"."⚙️" AS "⚙️",
                CAST((length(("assignment.7"."empty_cells")) = 0) AS boolean) AS "🔍",
                "assignment.7"."cells" AS "cells",
                "assignment.7"."empty_cells" AS "empty_cells"
         FROM   "assignment.7"
       ),
       "where.2"("⚙️") AS (
         SELECT "assignment.6"."⚙️" AS "⚙️"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS DISTINCT FROM TRUE
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.2"."⚙️"
         FROM   "where.2"
         WHERE  FALSE
       ),
       "where.3"("#️⃣", "⚙️", "cells") AS (
         SELECT "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."cells" AS "cells"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "emit.1"("#️⃣", "⚙️", "📊.1") AS (
         SELECT "where.3"."#️⃣" AS "#️⃣",
                "where.3"."⚙️" AS "⚙️",
                "where.3"."cells" AS "📊.1"
         FROM   "where.3"
       ),
       "stop.2"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       ),
       "where.4"("#️⃣", "⚙️", "cells", "empty_cells") AS (
         SELECT "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."cells" AS "cells",
                "assignment.8"."empty_cells" AS "empty_cells"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS DISTINCT FROM TRUE
       ),
       "jump.1"("#️⃣", "🏷️", "cells", "empty_cells") AS (
         SELECT "where.4"."#️⃣" AS "#️⃣",
                'start.2' AS "🏷️",
                "where.4"."cells" AS "cells",
                "where.4"."empty_cells" AS "empty_cells"
         FROM   "where.4"
       )
     (SELECT CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."📊.1") AS int[]) AS "📊.1",
             CAST((NULL) AS int[]) AS "cells",
             CAST((NULL) AS int[]) AS "empty_cells"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST((NULL) AS int[]) AS "📊.1",
             CAST(("jump.1"."cells") AS int[]) AS "cells",
             CAST(("jump.1"."empty_cells") AS int[]) AS "empty_cells"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;