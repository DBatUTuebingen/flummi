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
       "assignment.3"("#️⃣", "⚙️", "cells", "empty_cells", "cell") AS (
         SELECT "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."cells" AS "cells",
                "merge.1"."empty_cells" AS "empty_cells",
                CAST((("merge.1"."empty_cells")[1]) AS int) AS "cell"
         FROM   "merge.1"
       ),
       "assignment.4"("#️⃣", "⚙️", "cells", "empty_cells", "cell") AS (
         SELECT "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."⚙️" AS "⚙️",
                "assignment.3"."cells" AS "cells",
                CAST((("assignment.3"."empty_cells")[2:]) AS int[]) AS "empty_cells",
                "assignment.3"."cell" AS "cell"
         FROM   "assignment.3"
       ),
       "fork.1"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."empty_cells" AS "empty_cells",
                "assignment.4"."cell" AS "cell",
                CAST(("ℚ"."value") AS int) AS "value"
         FROM   "assignment.4",
                (FROM generate_series(1, 9)) AS "ℚ"("value")
       ),
       "fork.2"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value", "offset") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."cells" AS "cells",
                "fork.1"."empty_cells" AS "empty_cells",
                "fork.1"."cell" AS "cell",
                "fork.1"."value" AS "value",
                CAST(("ℚ"."offset") AS int) AS "offset"
         FROM   "fork.1",
                (FROM generate_series(1, 9)) AS "ℚ"("offset")
       ),
       "assignment.5"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value", "offset", "row_ok") AS (
         SELECT "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."⚙️" AS "⚙️",
                "fork.2"."cells" AS "cells",
                "fork.2"."empty_cells" AS "empty_cells",
                "fork.2"."cell" AS "cell",
                "fork.2"."value" AS "value",
                "fork.2"."offset" AS "offset",
                CAST((("fork.2"."value") <> ("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + ("fork.2"."offset")                   ]) AS boolean) AS "row_ok"
         FROM   "fork.2"
       ),
       "assignment.6"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value", "offset", "row_ok", "col_ok") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."cells" AS "cells",
                "assignment.5"."empty_cells" AS "empty_cells",
                "assignment.5"."cell" AS "cell",
                "assignment.5"."value" AS "value",
                "assignment.5"."offset" AS "offset",
                "assignment.5"."row_ok" AS "row_ok",
                CAST((("assignment.5"."value") <> ("assignment.5"."cells")[("assignment.5"."cell") % 9                             + (("assignment.5"."offset")-1)*9 + 1         ]) AS boolean) AS "col_ok"
         FROM   "assignment.5"
       ),
       "assignment.7"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value", "row_ok", "col_ok", "box_ok") AS (
         SELECT "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."cells" AS "cells",
                "assignment.6"."empty_cells" AS "empty_cells",
                "assignment.6"."cell" AS "cell",
                "assignment.6"."value" AS "value",
                "assignment.6"."row_ok" AS "row_ok",
                "assignment.6"."col_ok" AS "col_ok",
                CAST((("assignment.6"."value") <> ("assignment.6"."cells")[((("assignment.6"."cell")//3) % 3) * 3 + (("assignment.6"."cell")//27) * 27 + ("assignment.6"."offset") + ((("assignment.6"."offset")-1)//3) * 6]) AS boolean) AS "box_ok"
         FROM   "assignment.6"
       ),
       "gather.1"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value", "ok") AS (
         SELECT "assignment.7"."#️⃣" AS "#️⃣",
                "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."cells" AS "cells",
                "assignment.7"."empty_cells" AS "empty_cells",
                "assignment.7"."cell" AS "cell",
                "assignment.7"."value" AS "value",
                CAST((bool_and(("assignment.7"."row_ok") AND ("assignment.7"."col_ok") AND ("assignment.7"."box_ok"))) AS boolean) AS "ok"
         FROM   "assignment.7"
         GROUP  BY "assignment.7"."#️⃣",
                   "assignment.7"."cell",
                   "assignment.7"."cells",
                   "assignment.7"."empty_cells",
                   "assignment.7"."value",
                   "assignment.7"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "assignment.8"("#️⃣", "⚙️", "🔍", "cells", "empty_cells", "cell", "value") AS (
         SELECT "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."⚙️" AS "⚙️",
                CAST((("gather.1"."ok")) AS boolean) AS "🔍",
                "gather.1"."cells" AS "cells",
                "gather.1"."empty_cells" AS "empty_cells",
                "gather.1"."cell" AS "cell",
                "gather.1"."value" AS "value"
         FROM   "gather.1"
       ),
       "where.1"("#️⃣", "⚙️", "cells", "empty_cells", "cell", "value") AS (
         SELECT "assignment.8"."#️⃣" AS "#️⃣",
                "assignment.8"."⚙️" AS "⚙️",
                "assignment.8"."cells" AS "cells",
                "assignment.8"."empty_cells" AS "empty_cells",
                "assignment.8"."cell" AS "cell",
                "assignment.8"."value" AS "value"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "assignment.9"("#️⃣", "⚙️", "cells", "empty_cells") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                "where.1"."⚙️" AS "⚙️",
                CAST((concat(("where.1"."cells")[:("where.1"."cell")], [("where.1"."value")], ("where.1"."cells")[("where.1"."cell")+2:])) AS int[]) AS "cells",
                "where.1"."empty_cells" AS "empty_cells"
         FROM   "where.1"
       ),
       "assignment.10"("#️⃣", "⚙️", "🔍", "cells", "empty_cells") AS (
         SELECT "assignment.9"."#️⃣" AS "#️⃣",
                "assignment.9"."⚙️" AS "⚙️",
                CAST((length(("assignment.9"."empty_cells")) = 0) AS boolean) AS "🔍",
                "assignment.9"."cells" AS "cells",
                "assignment.9"."empty_cells" AS "empty_cells"
         FROM   "assignment.9"
       ),
       "where.2"("⚙️") AS (
         SELECT "assignment.8"."⚙️" AS "⚙️"
         FROM   "assignment.8"
         WHERE  "assignment.8"."🔍" IS DISTINCT FROM TRUE
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.2"."⚙️"
         FROM   "where.2"
         WHERE  FALSE
       ),
       "where.3"("#️⃣", "⚙️", "cells") AS (
         SELECT "assignment.10"."#️⃣" AS "#️⃣",
                "assignment.10"."⚙️" AS "⚙️",
                "assignment.10"."cells" AS "cells"
         FROM   "assignment.10"
         WHERE  "assignment.10"."🔍" IS NOT DISTINCT FROM TRUE
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
         SELECT "assignment.10"."#️⃣" AS "#️⃣",
                "assignment.10"."⚙️" AS "⚙️",
                "assignment.10"."cells" AS "cells",
                "assignment.10"."empty_cells" AS "empty_cells"
         FROM   "assignment.10"
         WHERE  "assignment.10"."🔍" IS DISTINCT FROM TRUE
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