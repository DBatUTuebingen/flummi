WITH RECURSIVE
  "@loop"("$label", "$iteration", "$result", "cells", "empty_cells") AS (
    (SELECT CAST(('start.1') AS text) AS "$label",
            CAST((0) AS int) AS "$iteration",
            CAST((NULL) AS int[]) AS "$result",
            CAST((NULL) AS int[]) AS "cells",
            CAST((NULL) AS int[]) AS "empty_cells")
      UNION ALL
    (WITH
       "start.1"("$control", "$iteration") AS (
         SELECT NULL AS "$control",
                "@loop"."$iteration" AS "$iteration"
         FROM   "@loop"
         WHERE  "@loop"."$label" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("cells", "$control", "empty_cells", "$iteration") AS (
         SELECT "@loop"."cells" AS "cells",
                NULL AS "$control",
                "@loop"."empty_cells" AS "empty_cells",
                "@loop"."$iteration" AS "$iteration"
         FROM   "@loop"
         WHERE  "@loop"."$label" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("cells", "$control", "$iteration") AS (
         SELECT CAST((SELECT cells
                       FROM   sudoku
                       LIMIT  1) AS int[]) AS "cells",
                "start.1"."$control" AS "$control",
                "start.1"."$iteration" AS "$iteration"
         FROM   "start.1"
       ),
       "assignment.2"("cells", "$control", "empty_cells", "$iteration") AS (
         SELECT "assignment.1"."cells" AS "cells",
                "assignment.1"."$control" AS "$control",
                CAST((SELECT list(cell - 1) FILTER (value = 0)
                       FROM   unnest(("assignment.1"."cells")) WITH ORDINALITY AS _(value, cell)) AS int[]) AS "empty_cells",
                "assignment.1"."$iteration" AS "$iteration"
         FROM   "assignment.1"
       ),
       "merge.1"("cells", "$control", "empty_cells", "$iteration") AS (
         (SELECT "assignment.2"."cells" AS "cells",
                 "assignment.2"."$control" AS "$control",
                 "assignment.2"."empty_cells" AS "empty_cells",
                 "assignment.2"."$iteration" AS "$iteration"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."cells" AS "cells",
                 "start.2"."$control" AS "$control",
                 "start.2"."empty_cells" AS "empty_cells",
                 "start.2"."$iteration" AS "$iteration"
          FROM   "start.2")
       ),
       "assignment.3"("$iteration", "empty_cells", "cell", "cells", "$control") AS (
         SELECT "merge.1"."$iteration" AS "$iteration",
                "merge.1"."empty_cells" AS "empty_cells",
                CAST((("merge.1"."empty_cells")[1]) AS int) AS "cell",
                "merge.1"."cells" AS "cells",
                "merge.1"."$control" AS "$control"
         FROM   "merge.1"
       ),
       "assignment.4"("$iteration", "empty_cells", "cell", "cells", "$control") AS (
         SELECT "assignment.3"."$iteration" AS "$iteration",
                CAST((("assignment.3"."empty_cells")[2:]) AS int[]) AS "empty_cells",
                "assignment.3"."cell" AS "cell",
                "assignment.3"."cells" AS "cells",
                "assignment.3"."$control" AS "$control"
         FROM   "assignment.3"
       ),
       "fork.1"("value", "empty_cells", "$iteration", "cell", "cells", "$control") AS (
         SELECT "@expression"."value" AS "value",
                "assignment.4"."empty_cells" AS "empty_cells",
                "assignment.4"."$iteration" AS "$iteration",
                "assignment.4"."cell" AS "cell",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."$control" AS "$control"
         FROM   "assignment.4",
                LATERAL (FROM generate_series(1, 9)) AS "@expression"("value")
       ),
       "fork.2"("value", "empty_cells", "$iteration", "cell", "offset", "cells", "$control") AS (
         SELECT "fork.1"."value" AS "value",
                "fork.1"."empty_cells" AS "empty_cells",
                "fork.1"."$iteration" AS "$iteration",
                "fork.1"."cell" AS "cell",
                "@expression"."offset" AS "offset",
                "fork.1"."cells" AS "cells",
                "fork.1"."$control" AS "$control"
         FROM   "fork.1",
                LATERAL (FROM generate_series(1, 9)) AS "@expression"("offset")
       ),
       "assignment.5"("value", "empty_cells", "row_ok", "cell", "offset", "$iteration", "cells", "$control") AS (
         SELECT "fork.2"."value" AS "value",
                "fork.2"."empty_cells" AS "empty_cells",
                CAST((("fork.2"."value") <> ("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + ("fork.2"."offset")                   ]) AS boolean) AS "row_ok",
                "fork.2"."cell" AS "cell",
                "fork.2"."offset" AS "offset",
                "fork.2"."$iteration" AS "$iteration",
                "fork.2"."cells" AS "cells",
                "fork.2"."$control" AS "$control"
         FROM   "fork.2"
       ),
       "assignment.6"("row_ok", "$control", "value", "empty_cells", "$iteration", "cell", "offset", "col_ok", "cells") AS (
         SELECT "assignment.5"."row_ok" AS "row_ok",
                "assignment.5"."$control" AS "$control",
                "assignment.5"."value" AS "value",
                "assignment.5"."empty_cells" AS "empty_cells",
                "assignment.5"."$iteration" AS "$iteration",
                "assignment.5"."cell" AS "cell",
                "assignment.5"."offset" AS "offset",
                CAST((("assignment.5"."value") <> ("assignment.5"."cells")[("assignment.5"."cell") % 9                             + (("assignment.5"."offset")-1)*9 + 1         ]) AS boolean) AS "col_ok",
                "assignment.5"."cells" AS "cells"
         FROM   "assignment.5"
       ),
       "assignment.7"("row_ok", "$control", "value", "empty_cells", "$iteration", "cell", "col_ok", "box_ok", "cells") AS (
         SELECT "assignment.6"."row_ok" AS "row_ok",
                "assignment.6"."$control" AS "$control",
                "assignment.6"."value" AS "value",
                "assignment.6"."empty_cells" AS "empty_cells",
                "assignment.6"."$iteration" AS "$iteration",
                "assignment.6"."cell" AS "cell",
                "assignment.6"."col_ok" AS "col_ok",
                CAST((("assignment.6"."value") <> ("assignment.6"."cells")[((("assignment.6"."cell")//3) % 3) * 3 + (("assignment.6"."cell")//27) * 27 + ("assignment.6"."offset") + ((("assignment.6"."offset")-1)//3) * 6]) AS boolean) AS "box_ok",
                "assignment.6"."cells" AS "cells"
         FROM   "assignment.6"
       ),
       "gather.1"("$control", "ok", "value", "empty_cells", "$iteration", "cell", "cells") AS (
         SELECT "assignment.7"."$control" AS "$control",
                bool_and(("assignment.7"."row_ok") AND ("assignment.7"."col_ok") AND ("assignment.7"."box_ok")) AS "ok",
                "assignment.7"."value" AS "value",
                "assignment.7"."empty_cells" AS "empty_cells",
                NULL AS "$iteration",
                "assignment.7"."cell" AS "cell",
                "assignment.7"."cells" AS "cells"
         FROM   "assignment.7"
         GROUP  BY "assignment.7"."cells",
                   "assignment.7"."empty_cells",
                   "assignment.7"."cell",
                   "assignment.7"."value",
                   "assignment.7"."$control"
         HAVING COUNT(*) > 0
       ),
       "where.1"("value", "empty_cells", "$iteration", "cell", "cells", "$control") AS (
         SELECT "gather.1"."value" AS "value",
                "gather.1"."empty_cells" AS "empty_cells",
                "gather.1"."$iteration" AS "$iteration",
                "gather.1"."cell" AS "cell",
                "gather.1"."cells" AS "cells",
                "gather.1"."$control" AS "$control"
         FROM   "gather.1"
         WHERE  "gather.1"."ok" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("$control") AS (
         SELECT "gather.1"."$control" AS "$control"
         FROM   "gather.1"
         WHERE  "gather.1"."ok" IS DISTINCT FROM TRUE
       ),
       "assignment.8"("$control", "cells", "$iteration", "empty_cells") AS (
         SELECT "where.1"."$control" AS "$control",
                CAST((concat(("where.1"."cells")[:("where.1"."cell")], [("where.1"."value")], ("where.1"."cells")[("where.1"."cell")+2:])) AS int[]) AS "cells",
                "where.1"."$iteration" AS "$iteration",
                "where.1"."empty_cells" AS "empty_cells"
         FROM   "where.1"
       ),
       "stop.1"("$control") AS (
         SELECT "where.2"."$control"
         FROM   "where.2"
         WHERE  FALSE
       ),
       "assignment.9"("$iteration", "empty_cells", "done", "cells", "$control") AS (
         SELECT "assignment.8"."$iteration" AS "$iteration",
                "assignment.8"."empty_cells" AS "empty_cells",
                CAST((length(("assignment.8"."empty_cells")) = 0) AS boolean) AS "done",
                "assignment.8"."cells" AS "cells",
                "assignment.8"."$control" AS "$control"
         FROM   "assignment.8"
       ),
       "where.3"("$control", "cells", "$iteration") AS (
         SELECT "assignment.9"."$control" AS "$control",
                "assignment.9"."cells" AS "cells",
                "assignment.9"."$iteration" AS "$iteration"
         FROM   "assignment.9"
         WHERE  "assignment.9"."done" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("cells", "$iteration", "empty_cells") AS (
         SELECT "assignment.9"."cells" AS "cells",
                "assignment.9"."$iteration" AS "$iteration",
                "assignment.9"."empty_cells" AS "empty_cells"
         FROM   "assignment.9"
         WHERE  "assignment.9"."done" IS DISTINCT FROM TRUE
       ),
       "emit.1"("$iteration", "$result") AS (
         SELECT "where.3"."$iteration" AS "$iteration",
                "where.3"."cells" AS "$result"
         FROM   "where.3"
       ),
       "jump.1"("cells", "$iteration", "empty_cells", "$label") AS (
         SELECT "where.4"."cells" AS "cells",
                "where.4"."$iteration" AS "$iteration",
                "where.4"."empty_cells" AS "empty_cells",
                'start.2' AS "$label"
         FROM   "where.4"
       ),
       "stop.2"("$control") AS (
         SELECT "where.3"."$control"
         FROM   "where.3"
         WHERE  FALSE
       )
     (SELECT CAST((NULL) AS text) AS "$label",
             CAST(("emit.1"."$iteration") AS int) AS "$iteration",
             CAST(("emit.1"."$result") AS int[]) AS "$result",
             CAST((NULL) AS int[]) AS "cells",
             CAST((NULL) AS int[]) AS "empty_cells"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."$label") AS text) AS "$label",
             CAST(("jump.1"."$iteration" + 1) AS int) AS "$iteration",
             CAST((NULL) AS int[]) AS "$result",
             CAST(("jump.1"."cells") AS int[]) AS "cells",
             CAST(("jump.1"."empty_cells") AS int[]) AS "empty_cells"
      FROM   "jump.1"))
  )
SELECT "@loop"."$result"
FROM   "@loop"
WHERE  "@loop"."$label" IS NULL;