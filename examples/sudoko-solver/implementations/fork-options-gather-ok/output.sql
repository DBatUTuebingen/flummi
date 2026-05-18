WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "empty_cells", "cells") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS int[]) AS "📊",
            CAST((NULL) AS int[]) AS "empty_cells",
            CAST((NULL) AS int[]) AS "cells")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("⚙️", "#️⃣", "cells", "empty_cells") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣",
                "🔄"."cells" AS "cells",
                "🔄"."empty_cells" AS "empty_cells"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("⚙️", "#️⃣", "cells") AS (
         SELECT "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣",
                CAST((SELECT cells
                       FROM   sudoku
                       LIMIT  1) AS int[]) AS "cells"
         FROM   "start.1"
       ),
       "assignment.2"("⚙️", "empty_cells", "#️⃣", "cells") AS (
         SELECT "assignment.1"."⚙️" AS "⚙️",
                CAST((SELECT list(cell - 1) FILTER (value = 0)
                       FROM   unnest(("assignment.1"."cells")) WITH ORDINALITY AS _(value, cell)) AS int[]) AS "empty_cells",
                "assignment.1"."#️⃣" AS "#️⃣",
                "assignment.1"."cells" AS "cells"
         FROM   "assignment.1"
       ),
       "merge.1"("⚙️", "empty_cells", "#️⃣", "cells") AS (
         (SELECT "start.2"."⚙️" AS "⚙️",
                 "start.2"."empty_cells" AS "empty_cells",
                 "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."cells" AS "cells"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.2"."⚙️" AS "⚙️",
                 "assignment.2"."empty_cells" AS "empty_cells",
                 "assignment.2"."#️⃣" AS "#️⃣",
                 "assignment.2"."cells" AS "cells"
          FROM   "assignment.2")
       ),
       "assignment.3"("empty_cells", "#️⃣", "cells", "⚙️", "cell") AS (
         SELECT "merge.1"."empty_cells" AS "empty_cells",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."cells" AS "cells",
                "merge.1"."⚙️" AS "⚙️",
                CAST((("merge.1"."empty_cells")[1]) AS int) AS "cell"
         FROM   "merge.1"
       ),
       "assignment.4"("empty_cells", "#️⃣", "cells", "⚙️", "cell") AS (
         SELECT CAST((("assignment.3"."empty_cells")[2:]) AS int[]) AS "empty_cells",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."cells" AS "cells",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."cell" AS "cell"
         FROM   "assignment.3"
       ),
       "fork.1"("value", "empty_cells", "#️⃣", "cells", "⚙️", "cell") AS (
         SELECT "ℚ"."value" AS "value",
                "assignment.4"."empty_cells" AS "empty_cells",
                "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."cell" AS "cell"
         FROM   "assignment.4",
                LATERAL (FROM generate_series(1, 9)) AS "ℚ"("value")
       ),
       "fork.2"("value", "empty_cells", "#️⃣", "cells", "⚙️", "offset", "cell") AS (
         SELECT "fork.1"."value" AS "value",
                "fork.1"."empty_cells" AS "empty_cells",
                "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."cells" AS "cells",
                "fork.1"."⚙️" AS "⚙️",
                "ℚ"."offset" AS "offset",
                "fork.1"."cell" AS "cell"
         FROM   "fork.1",
                LATERAL (FROM generate_series(1, 9)) AS "ℚ"("offset")
       ),
       "assignment.5"("value", "empty_cells", "#️⃣", "cells", "⚙️", "row_ok", "offset", "cell") AS (
         SELECT "fork.2"."value" AS "value",
                "fork.2"."empty_cells" AS "empty_cells",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."cells" AS "cells",
                "fork.2"."⚙️" AS "⚙️",
                CAST((("fork.2"."value") <> ("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + ("fork.2"."offset")                   ]) AS boolean) AS "row_ok",
                "fork.2"."offset" AS "offset",
                "fork.2"."cell" AS "cell"
         FROM   "fork.2"
       ),
       "assignment.6"("cells", "col_ok", "row_ok", "offset", "value", "empty_cells", "#️⃣", "⚙️", "cell") AS (
         SELECT "assignment.5"."cells" AS "cells",
                CAST((("assignment.5"."value") <> ("assignment.5"."cells")[("assignment.5"."cell") % 9                             + (("assignment.5"."offset")-1)*9 + 1         ]) AS boolean) AS "col_ok",
                "assignment.5"."row_ok" AS "row_ok",
                "assignment.5"."offset" AS "offset",
                "assignment.5"."value" AS "value",
                "assignment.5"."empty_cells" AS "empty_cells",
                "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."cell" AS "cell"
         FROM   "assignment.5"
       ),
       "assignment.7"("cells", "box_ok", "row_ok", "⚙️", "value", "empty_cells", "#️⃣", "col_ok", "cell") AS (
         SELECT "assignment.6"."cells" AS "cells",
                CAST((("assignment.6"."value") <> ("assignment.6"."cells")[((("assignment.6"."cell")//3) % 3) * 3 + (("assignment.6"."cell")//27) * 27 + ("assignment.6"."offset") + ((("assignment.6"."offset")-1)//3) * 6]) AS boolean) AS "box_ok",
                "assignment.6"."row_ok" AS "row_ok",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."value" AS "value",
                "assignment.6"."empty_cells" AS "empty_cells",
                "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."col_ok" AS "col_ok",
                "assignment.6"."cell" AS "cell"
         FROM   "assignment.6"
       ),
       "gather.1"("cells", "ok", "value", "empty_cells", "#️⃣", "⚙️", "cell") AS (
         SELECT "assignment.7"."cells" AS "cells",
                bool_and(("assignment.7"."row_ok") AND ("assignment.7"."col_ok") AND ("assignment.7"."box_ok")) AS "ok",
                "assignment.7"."value" AS "value",
                "assignment.7"."empty_cells" AS "empty_cells",
                NULL AS "#️⃣",
                "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."cell" AS "cell"
         FROM   "assignment.7"
         GROUP  BY "assignment.7"."cells",
                   "assignment.7"."empty_cells",
                   "assignment.7"."cell",
                   "assignment.7"."value",
                   "assignment.7"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "where.1"("value", "empty_cells", "#️⃣", "cells", "⚙️", "cell") AS (
         SELECT "gather.1"."value" AS "value",
                "gather.1"."empty_cells" AS "empty_cells",
                "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."cells" AS "cells",
                "gather.1"."⚙️" AS "⚙️",
                "gather.1"."cell" AS "cell"
         FROM   "gather.1"
         WHERE  "gather.1"."ok" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("⚙️") AS (
         SELECT "gather.1"."⚙️" AS "⚙️"
         FROM   "gather.1"
         WHERE  "gather.1"."ok" IS DISTINCT FROM TRUE
       ),
       "assignment.8"("⚙️", "empty_cells", "#️⃣", "cells") AS (
         SELECT "where.1"."⚙️" AS "⚙️",
                "where.1"."empty_cells" AS "empty_cells",
                "where.1"."#️⃣" AS "#️⃣",
                CAST((concat(("where.1"."cells")[:("where.1"."cell")], [("where.1"."value")], ("where.1"."cells")[("where.1"."cell")+2:])) AS int[]) AS "cells"
         FROM   "where.1"
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.2"."⚙️"
         FROM   "where.2"
         WHERE  FALSE
       ),
       "assignment.9"("empty_cells", "#️⃣", "cells", "done", "⚙️") AS (
         SELECT "assignment.8"."empty_cells" AS "empty_cells",
                "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."cells" AS "cells",
                CAST((length(("assignment.8"."empty_cells")) = 0) AS boolean) AS "done",
                "assignment.8"."⚙️" AS "⚙️"
         FROM   "assignment.8"
       ),
       "where.3"("⚙️", "#️⃣", "cells") AS (
         SELECT "assignment.9"."⚙️" AS "⚙️",
                "assignment.9"."#️⃣" AS "#️⃣",
                "assignment.9"."cells" AS "cells"
         FROM   "assignment.9"
         WHERE  "assignment.9"."done" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("empty_cells", "#️⃣", "cells") AS (
         SELECT "assignment.9"."empty_cells" AS "empty_cells",
                "assignment.9"."#️⃣" AS "#️⃣",
                "assignment.9"."cells" AS "cells"
         FROM   "assignment.9"
         WHERE  "assignment.9"."done" IS DISTINCT FROM TRUE
       ),
       "emit.1"("⚙️", "#️⃣", "📊") AS (
         SELECT "where.3"."⚙️" AS "⚙️",
                "where.3"."#️⃣" AS "#️⃣",
                "where.3"."cells" AS "📊"
         FROM   "where.3"
       ),
       "jump.1"("cells", "#️⃣", "🏷️", "empty_cells") AS (
         SELECT "where.4"."cells" AS "cells",
                "where.4"."#️⃣" AS "#️⃣",
                'start.2' AS "🏷️",
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
             CAST(("emit.1"."📊") AS int[]) AS "📊",
             CAST((NULL) AS int[]) AS "empty_cells",
             CAST((NULL) AS int[]) AS "cells"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS int[]) AS "📊",
             CAST(("jump.1"."empty_cells") AS int[]) AS "empty_cells",
             CAST(("jump.1"."cells") AS int[]) AS "cells"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;