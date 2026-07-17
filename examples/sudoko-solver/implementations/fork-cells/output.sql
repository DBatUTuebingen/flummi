WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊.1", "cells", "empty_cells") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int[]) AS "📊.1",
            CAST((NULL) AS int[]) AS "cells",
            CAST((NULL) AS int[]) AS "empty_cells")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("⚙️", "cells", "empty_cells", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."cells" AS "cells",
                "🔄"."empty_cells" AS "empty_cells",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("⚙️", "cells", "#️⃣") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                CAST((SELECT cells
                       FROM   sudoku
                       LIMIT  1) AS int[]) AS "cells",
                "start.1"."#️⃣" AS "#️⃣"
         FROM   "start.1"
       ),
       "assignment.2"("⚙️", "cells", "empty_cells", "#️⃣") AS (
         SELECT "assignment.1"."⚙️" AS "⚙️",
                "assignment.1"."cells" AS "cells",
                CAST((SELECT list(cell - 1) FILTER (value = 0)
                       FROM   unnest(("assignment.1"."cells")) WITH ORDINALITY AS _(value, cell)) AS int[]) AS "empty_cells",
                "assignment.1"."#️⃣" AS "#️⃣"
         FROM   "assignment.1"
       ),
       "merge.1"("⚙️", "cells", "empty_cells", "#️⃣") AS (
         (SELECT "assignment.2"."⚙️" AS "⚙️",
                 "assignment.2"."cells" AS "cells",
                 "assignment.2"."empty_cells" AS "empty_cells",
                 "assignment.2"."#️⃣" AS "#️⃣"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."⚙️" AS "⚙️",
                 "start.2"."cells" AS "cells",
                 "start.2"."empty_cells" AS "empty_cells",
                 "start.2"."#️⃣" AS "#️⃣"
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
       "assignment.3"("#️⃣", "cell", "⚙️", "cells", "empty_cells", "idx") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                CAST((("fork.1"."empty_cells")[("fork.1"."idx")]) AS int) AS "cell",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."cells" AS "cells",
                "fork.1"."empty_cells" AS "empty_cells",
                "fork.1"."idx" AS "idx"
         FROM   "fork.1"
       ),
       "assignment.4"("cell", "⚙️", "cells", "empty_cells", "#️⃣") AS (
         SELECT "assignment.3"."cell" AS "cell",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."cells" AS "cells",
                CAST((("assignment.3"."empty_cells")[:("assignment.3"."idx")] || ("assignment.3"."empty_cells")[("assignment.3"."idx")+2:]) AS int[]) AS "empty_cells",
                "assignment.3"."#️⃣" AS "#️⃣"
         FROM   "assignment.3"
       ),
       "fork.2"("value", "cell", "⚙️", "cells", "empty_cells", "#️⃣") AS (
         SELECT CAST(("ℚ"."value") AS int) AS "value",
                "assignment.4"."cell" AS "cell",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."empty_cells" AS "empty_cells",
                "assignment.4"."#️⃣" AS "#️⃣"
         FROM   "assignment.4",
                (FROM generate_series(1, 9)) AS "ℚ"("value")
       ),
       "assignment.5"("value", "cell", "ok", "⚙️", "cells", "empty_cells", "#️⃣") AS (
         SELECT "fork.2"."value" AS "value",
                "fork.2"."cell" AS "cell",
                CAST((NOT EXISTS (
                         FROM  generate_series(1, 9) AS _(o)
                         WHERE ("fork.2"."value") IN (("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + o                 ],
                                       ("fork.2"."cells")[("fork.2"."cell") % 9                             + (o-1)*9 + 1       ],
                                       ("fork.2"."cells")[((("fork.2"."cell")//3) % 3) * 3 + (("fork.2"."cell")//27) * 27 + o + ((o-1)//3) * 6])
                       )) AS boolean) AS "ok",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."cells" AS "cells",
                "fork.2"."empty_cells" AS "empty_cells",
                "fork.2"."#️⃣" AS "#️⃣"
         FROM   "fork.2"
       ),
       "assignment.6"("empty_cells", "value", "cell", "⚙️", "cells", "🔍", "#️⃣") AS (
         SELECT "assignment.5"."empty_cells" AS "empty_cells",
                "assignment.5"."value" AS "value",
                "assignment.5"."cell" AS "cell",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."cells" AS "cells",
                CAST((("assignment.5"."ok")) AS boolean) AS "🔍",
                "assignment.5"."#️⃣" AS "#️⃣"
         FROM   "assignment.5"
       ),
       "where.1"("value", "cell", "⚙️", "cells", "empty_cells", "#️⃣") AS (
         SELECT "assignment.6"."value" AS "value",
                "assignment.6"."cell" AS "cell",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."cells" AS "cells",
                "assignment.6"."empty_cells" AS "empty_cells",
                "assignment.6"."#️⃣" AS "#️⃣"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("⚙️") AS (
         SELECT "assignment.6"."⚙️" AS "⚙️"
         FROM   "assignment.6"
         WHERE  "assignment.6"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.7"("⚙️", "cells", "empty_cells", "#️⃣") AS (
         SELECT "where.1"."⚙️" AS "⚙️",
                CAST((concat(("where.1"."cells")[:("where.1"."cell")], [("where.1"."value")], ("where.1"."cells")[("where.1"."cell")+2:])) AS int[]) AS "cells",
                "where.1"."empty_cells" AS "empty_cells",
                "where.1"."#️⃣" AS "#️⃣"
         FROM   "where.1"
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.2"."⚙️"
         FROM   "where.2"
         WHERE  FALSE
       ),
       "assignment.8"("empty_cells", "⚙️", "cells", "🔍", "#️⃣") AS (
         SELECT "assignment.7"."empty_cells" AS "empty_cells",
                "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."cells" AS "cells",
                CAST((length(("assignment.7"."empty_cells")) = 0) AS boolean) AS "🔍",
                "assignment.7"."#️⃣" AS "#️⃣"
         FROM   "assignment.7"
       ),
       "where.3"("⚙️", "cells", "#️⃣") AS (
         SELECT "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."cells" AS "cells",
                "assignment.8"."#️⃣" AS "#️⃣"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("⚙️", "cells", "empty_cells", "#️⃣") AS (
         SELECT "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."cells" AS "cells",
                "assignment.8"."empty_cells" AS "empty_cells",
                "assignment.8"."#️⃣" AS "#️⃣"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS DISTINCT FROM TRUE
       ),
       "emit.1"("⚙️", "📊.1", "#️⃣") AS (
         SELECT "where.3"."⚙️" AS "⚙️",
                "where.3"."cells" AS "📊.1",
                "where.3"."#️⃣" AS "#️⃣"
         FROM   "where.3"
       ),
       "jump.1"("🏷️", "#️⃣", "cells", "empty_cells") AS (
         SELECT 'start.2' AS "🏷️",
                "where.4"."#️⃣" AS "#️⃣",
                "where.4"."cells" AS "cells",
                "where.4"."empty_cells" AS "empty_cells"
         FROM   "where.4"
       ),
       "stop.2"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       )
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊.1") AS int[]) AS "📊.1",
             CAST((NULL) AS int[]) AS "cells",
             CAST((NULL) AS int[]) AS "empty_cells"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊.1",
             CAST(("jump.1"."cells") AS int[]) AS "cells",
             CAST(("jump.1"."empty_cells") AS int[]) AS "empty_cells"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;