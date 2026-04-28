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
       "start.2"("cells", "empty_cells", "$control", "$iteration") AS (
         SELECT "@loop"."cells" AS "cells",
                "@loop"."empty_cells" AS "empty_cells",
                NULL AS "$control",
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
       "assignment.2"("cells", "empty_cells", "$control", "$iteration") AS (
         SELECT "assignment.1"."cells" AS "cells",
                CAST((SELECT list(cell - 1) FILTER (value = 0)
                       FROM   unnest(("assignment.1"."cells")) WITH ORDINALITY AS _(value, cell)) AS int[]) AS "empty_cells",
                "assignment.1"."$control" AS "$control",
                "assignment.1"."$iteration" AS "$iteration"
         FROM   "assignment.1"
       ),
       "merge.1"("cells", "empty_cells", "$control", "$iteration") AS (
         (SELECT "assignment.2"."cells" AS "cells",
                 "assignment.2"."empty_cells" AS "empty_cells",
                 "assignment.2"."$control" AS "$control",
                 "assignment.2"."$iteration" AS "$iteration"
          FROM   "assignment.2")
           UNION ALL
         (SELECT "start.2"."cells" AS "cells",
                 "start.2"."empty_cells" AS "empty_cells",
                 "start.2"."$control" AS "$control",
                 "start.2"."$iteration" AS "$iteration"
          FROM   "start.2")
       ),
       "fork.1"("empty_cells", "idx", "$iteration", "cells", "$control") AS (
         SELECT "merge.1"."empty_cells" AS "empty_cells",
                "@expression"."idx" AS "idx",
                "merge.1"."$iteration" AS "$iteration",
                "merge.1"."cells" AS "cells",
                "merge.1"."$control" AS "$control"
         FROM   "merge.1",
                LATERAL (FROM unnest(("merge.1"."empty_cells"))) AS "@expression"("idx")
       ),
       "assignment.3"("cell", "empty_cells", "idx", "$iteration", "cells", "$control") AS (
         SELECT CAST((("fork.1"."empty_cells")[("fork.1"."idx")]) AS int) AS "cell",
                "fork.1"."empty_cells" AS "empty_cells",
                "fork.1"."idx" AS "idx",
                "fork.1"."$iteration" AS "$iteration",
                "fork.1"."cells" AS "cells",
                "fork.1"."$control" AS "$control"
         FROM   "fork.1"
       ),
       "assignment.4"("cell", "empty_cells", "$iteration", "cells", "$control") AS (
         SELECT "assignment.3"."cell" AS "cell",
                CAST((("assignment.3"."empty_cells")[:("assignment.3"."idx")] || ("assignment.3"."empty_cells")[("assignment.3"."idx")+2:]) AS int[]) AS "empty_cells",
                "assignment.3"."$iteration" AS "$iteration",
                "assignment.3"."cells" AS "cells",
                "assignment.3"."$control" AS "$control"
         FROM   "assignment.3"
       ),
       "fork.2"("cell", "empty_cells", "$iteration", "cells", "$control", "value") AS (
         SELECT "assignment.4"."cell" AS "cell",
                "assignment.4"."empty_cells" AS "empty_cells",
                "assignment.4"."$iteration" AS "$iteration",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."$control" AS "$control",
                "@expression"."value" AS "value"
         FROM   "assignment.4",
                LATERAL (FROM generate_series(1, 9)) AS "@expression"("value")
       ),
       "assignment.5"("cell", "empty_cells", "$iteration", "cells", "ok", "$control", "value") AS (
         SELECT "fork.2"."cell" AS "cell",
                "fork.2"."empty_cells" AS "empty_cells",
                "fork.2"."$iteration" AS "$iteration",
                "fork.2"."cells" AS "cells",
                CAST((NOT EXISTS (
                         FROM  generate_series(1, 9) AS _(o)
                         WHERE ("fork.2"."value") IN (("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + o                 ],
                                       ("fork.2"."cells")[("fork.2"."cell") % 9                             + (o-1)*9 + 1       ],
                                       ("fork.2"."cells")[((("fork.2"."cell")//3) % 3) * 3 + (("fork.2"."cell")//27) * 27 + o + ((o-1)//3) * 6])
                       )) AS boolean) AS "ok",
                "fork.2"."$control" AS "$control",
                "fork.2"."value" AS "value"
         FROM   "fork.2"
       ),
       "where.1"("cell", "empty_cells", "$iteration", "cells", "$control", "value") AS (
         SELECT "assignment.5"."cell" AS "cell",
                "assignment.5"."empty_cells" AS "empty_cells",
                "assignment.5"."$iteration" AS "$iteration",
                "assignment.5"."cells" AS "cells",
                "assignment.5"."$control" AS "$control",
                "assignment.5"."value" AS "value"
         FROM   "assignment.5"
         WHERE  "assignment.5"."ok" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("$control") AS (
         SELECT "assignment.5"."$control" AS "$control"
         FROM   "assignment.5"
         WHERE  "assignment.5"."ok" IS DISTINCT FROM TRUE
       ),
       "assignment.6"("cells", "empty_cells", "$control", "$iteration") AS (
         SELECT CAST((concat(("where.1"."cells")[:("where.1"."cell")], [("where.1"."value")], ("where.1"."cells")[("where.1"."cell")+2:])) AS int[]) AS "cells",
                "where.1"."empty_cells" AS "empty_cells",
                "where.1"."$control" AS "$control",
                "where.1"."$iteration" AS "$iteration"
         FROM   "where.1"
       ),
       "assignment.7"("empty_cells", "cells", "$iteration", "done", "$control") AS (
         SELECT "assignment.6"."empty_cells" AS "empty_cells",
                "assignment.6"."cells" AS "cells",
                "assignment.6"."$iteration" AS "$iteration",
                CAST((length(("assignment.6"."empty_cells")) = 0) AS boolean) AS "done",
                "assignment.6"."$control" AS "$control"
         FROM   "assignment.6"
       ),
       "where.3"("cells", "$control", "$iteration") AS (
         SELECT "assignment.7"."cells" AS "cells",
                "assignment.7"."$control" AS "$control",
                "assignment.7"."$iteration" AS "$iteration"
         FROM   "assignment.7"
         WHERE  "assignment.7"."done" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("cells", "empty_cells", "$control", "$iteration") AS (
         SELECT "assignment.7"."cells" AS "cells",
                "assignment.7"."empty_cells" AS "empty_cells",
                "assignment.7"."$control" AS "$control",
                "assignment.7"."$iteration" AS "$iteration"
         FROM   "assignment.7"
         WHERE  "assignment.7"."done" IS DISTINCT FROM TRUE
       ),
       "emit.1"("$result", "$iteration") AS (
         SELECT "where.3"."cells" AS "$result",
                "where.3"."$iteration" AS "$iteration"
         FROM   "where.3"
       ),
       "jump.1"("cells", "$iteration", "$label", "empty_cells") AS (
         SELECT "where.4"."cells" AS "cells",
                "where.4"."$iteration" AS "$iteration",
                'start.2' AS "$label",
                "where.4"."empty_cells" AS "empty_cells"
         FROM   "where.4"
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