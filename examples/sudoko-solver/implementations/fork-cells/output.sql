WITH RECURSIVE
  "🔄"("", "󰐤", "󱕍", "cells", "empty_cells") AS (
    (SELECT CAST(('start.1') AS text) AS "",
            CAST((0) AS int) AS "󰐤",
            CAST((NULL) AS int[]) AS "󱕍",
            CAST((NULL) AS int[]) AS "cells",
            CAST((NULL) AS int[]) AS "empty_cells")
      UNION ALL
    (WITH
       "start.1"("󰐤", "") AS (
         SELECT "🔄"."󰐤" AS "󰐤",
                NULL AS ""
         FROM   "🔄"
         WHERE  "🔄"."" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("󰐤", "cells", "", "empty_cells") AS (
         SELECT "🔄"."󰐤" AS "󰐤",
                "🔄"."cells" AS "cells",
                NULL AS "",
                "🔄"."empty_cells" AS "empty_cells"
         FROM   "🔄"
         WHERE  "🔄"."" IS NOT DISTINCT FROM 'start.2'
       ),
       "assignment.1"("cells", "󰐤", "") AS (
         SELECT CAST((SELECT cells
                       FROM   sudoku
                       LIMIT  1) AS int[]) AS "cells",
                "start.1"."󰐤" AS "󰐤",
                "start.1"."" AS ""
         FROM   "start.1"
       ),
       "assignment.2"("cells", "󰐤", "", "empty_cells") AS (
         SELECT "assignment.1"."cells" AS "cells",
                "assignment.1"."󰐤" AS "󰐤",
                "assignment.1"."" AS "",
                CAST((SELECT list(cell - 1) FILTER (value = 0)
                       FROM   unnest(("assignment.1"."cells")) WITH ORDINALITY AS _(value, cell)) AS int[]) AS "empty_cells"
         FROM   "assignment.1"
       ),
       "merge.1"("cells", "󰐤", "", "empty_cells") AS (
         (SELECT "assignment.2"."cells" AS "cells",
                 "assignment.2"."󰐤" AS "󰐤",
                 "assignment.2"."" AS "",
                 "assignment.2"."empty_cells" AS "empty_cells"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."cells" AS "cells",
                 "start.2"."󰐤" AS "󰐤",
                 "start.2"."" AS "",
                 "start.2"."empty_cells" AS "empty_cells"
          FROM   "start.2")
       ),
       "fork.1"("empty_cells", "󰐤", "cells", "idx", "") AS (
         SELECT "merge.1"."empty_cells" AS "empty_cells",
                "merge.1"."󰐤" AS "󰐤",
                "merge.1"."cells" AS "cells",
                "ℚ"."idx" AS "idx",
                "merge.1"."" AS ""
         FROM   "merge.1",
                LATERAL (FROM unnest(("merge.1"."empty_cells"))) AS "ℚ"("idx")
       ),
       "assignment.3"("󰐤", "cell", "cells", "idx", "", "empty_cells") AS (
         SELECT "fork.1"."󰐤" AS "󰐤",
                CAST((("fork.1"."empty_cells")[("fork.1"."idx")]) AS int) AS "cell",
                "fork.1"."cells" AS "cells",
                "fork.1"."idx" AS "idx",
                "fork.1"."" AS "",
                "fork.1"."empty_cells" AS "empty_cells"
         FROM   "fork.1"
       ),
       "assignment.4"("empty_cells", "cell", "󰐤", "cells", "") AS (
         SELECT CAST((("assignment.3"."empty_cells")[:("assignment.3"."idx")] || ("assignment.3"."empty_cells")[("assignment.3"."idx")+2:]) AS int[]) AS "empty_cells",
                "assignment.3"."cell" AS "cell",
                "assignment.3"."󰐤" AS "󰐤",
                "assignment.3"."cells" AS "cells",
                "assignment.3"."" AS ""
         FROM   "assignment.3"
       ),
       "fork.2"("empty_cells", "cell", "󰐤", "cells", "", "value") AS (
         SELECT "assignment.4"."empty_cells" AS "empty_cells",
                "assignment.4"."cell" AS "cell",
                "assignment.4"."󰐤" AS "󰐤",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."" AS "",
                "ℚ"."value" AS "value"
         FROM   "assignment.4",
                LATERAL (FROM generate_series(1, 9)) AS "ℚ"("value")
       ),
       "assignment.5"("empty_cells", "cell", "󰐤", "cells", "", "ok", "value") AS (
         SELECT "fork.2"."empty_cells" AS "empty_cells",
                "fork.2"."cell" AS "cell",
                "fork.2"."󰐤" AS "󰐤",
                "fork.2"."cells" AS "cells",
                "fork.2"."" AS "",
                CAST((NOT EXISTS (
                         FROM  generate_series(1, 9) AS _(o)
                         WHERE ("fork.2"."value") IN (("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + o                 ],
                                       ("fork.2"."cells")[("fork.2"."cell") % 9                             + (o-1)*9 + 1       ],
                                       ("fork.2"."cells")[((("fork.2"."cell")//3) % 3) * 3 + (("fork.2"."cell")//27) * 27 + o + ((o-1)//3) * 6])
                       )) AS boolean) AS "ok",
                "fork.2"."value" AS "value"
         FROM   "fork.2"
       ),
       "where.1"("󰐤", "cell", "cells", "", "empty_cells", "value") AS (
         SELECT "assignment.5"."󰐤" AS "󰐤",
                "assignment.5"."cell" AS "cell",
                "assignment.5"."cells" AS "cells",
                "assignment.5"."" AS "",
                "assignment.5"."empty_cells" AS "empty_cells",
                "assignment.5"."value" AS "value"
         FROM   "assignment.5"
         WHERE  "assignment.5"."ok" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("") AS (
         SELECT "assignment.5"."" AS ""
         FROM   "assignment.5"
         WHERE  "assignment.5"."ok" IS DISTINCT FROM TRUE
       ),
       "assignment.6"("cells", "", "󰐤", "empty_cells") AS (
         SELECT CAST((concat(("where.1"."cells")[:("where.1"."cell")], [("where.1"."value")], ("where.1"."cells")[("where.1"."cell")+2:])) AS int[]) AS "cells",
                "where.1"."" AS "",
                "where.1"."󰐤" AS "󰐤",
                "where.1"."empty_cells" AS "empty_cells"
         FROM   "where.1"
       ),
       "stop.1"("") AS (
         SELECT "where.2".""
         FROM   "where.2"
         WHERE  FALSE
       ),
       "assignment.7"("󰐤", "empty_cells", "done", "cells", "") AS (
         SELECT "assignment.6"."󰐤" AS "󰐤",
                "assignment.6"."empty_cells" AS "empty_cells",
                CAST((length(("assignment.6"."empty_cells")) = 0) AS boolean) AS "done",
                "assignment.6"."cells" AS "cells",
                "assignment.6"."" AS ""
         FROM   "assignment.6"
       ),
       "where.3"("cells", "", "󰐤") AS (
         SELECT "assignment.7"."cells" AS "cells",
                "assignment.7"."" AS "",
                "assignment.7"."󰐤" AS "󰐤"
         FROM   "assignment.7"
         WHERE  "assignment.7"."done" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("cells", "󰐤", "empty_cells") AS (
         SELECT "assignment.7"."cells" AS "cells",
                "assignment.7"."󰐤" AS "󰐤",
                "assignment.7"."empty_cells" AS "empty_cells"
         FROM   "assignment.7"
         WHERE  "assignment.7"."done" IS DISTINCT FROM TRUE
       ),
       "emit.1"("󱕍", "", "󰐤") AS (
         SELECT "where.3"."cells" AS "󱕍",
                "where.3"."" AS "",
                "where.3"."󰐤" AS "󰐤"
         FROM   "where.3"
       ),
       "jump.1"("cells", "󰐤", "empty_cells", "") AS (
         SELECT "where.4"."cells" AS "cells",
                "where.4"."󰐤" AS "󰐤",
                "where.4"."empty_cells" AS "empty_cells",
                'start.2' AS ""
         FROM   "where.4"
       ),
       "stop.2"("") AS (
         SELECT "emit.1".""
         FROM   "emit.1"
         WHERE  FALSE
       )
     (SELECT CAST((NULL) AS text) AS "",
             CAST(("emit.1"."󰐤") AS int) AS "󰐤",
             CAST(("emit.1"."󱕍") AS int[]) AS "󱕍",
             CAST((NULL) AS int[]) AS "cells",
             CAST((NULL) AS int[]) AS "empty_cells"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."") AS text) AS "",
             CAST(("jump.1"."󰐤" + 1) AS int) AS "󰐤",
             CAST((NULL) AS int[]) AS "󱕍",
             CAST(("jump.1"."cells") AS int[]) AS "cells",
             CAST(("jump.1"."empty_cells") AS int[]) AS "empty_cells"
      FROM   "jump.1"))
  )
SELECT "🔄"."󱕍"
FROM   "🔄"
WHERE  "🔄"."" IS NULL;