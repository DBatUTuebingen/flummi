WITH RECURSIVE
  "@loop"("$label", "$iteration", "$result", "id", "cells") AS (
    (SELECT CAST(('start.1') AS text) AS "$label",
            CAST((0) AS int) AS "$iteration",
            CAST((NULL) AS struct(id int, cells int[])) AS "$result",
            CAST((NULL) AS int) AS "id",
            CAST((NULL) AS int[]) AS "cells")
      UNION ALL
    (WITH
       "start.1"("$iteration", "$control") AS (
         SELECT "@loop"."$iteration" AS "$iteration",
                NULL AS "$control"
         FROM   "@loop"
         WHERE  "@loop"."$label" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("id", "$iteration", "cells", "$control") AS (
         SELECT "@loop"."id" AS "id",
                "@loop"."$iteration" AS "$iteration",
                "@loop"."cells" AS "cells",
                NULL AS "$control"
         FROM   "@loop"
         WHERE  "@loop"."$label" IS NOT DISTINCT FROM 'start.2'
       ),
       "fork.1"("$iteration", "cells", "$control") AS (
         SELECT "start.1"."$iteration" AS "$iteration",
                "@expression"."cells" AS "cells",
                "start.1"."$control" AS "$control"
         FROM   "start.1",
                LATERAL (SELECT cells
                         FROM   sudoku) AS "@expression"("cells")
       ),
       "assignment.1"("id", "$iteration", "cells", "$control") AS (
         SELECT CAST((row_number() OVER ()) AS int) AS "id",
                "fork.1"."$iteration" AS "$iteration",
                "fork.1"."cells" AS "cells",
                "fork.1"."$control" AS "$control"
         FROM   "fork.1"
       ),
       "merge.1"("id", "$iteration", "cells", "$control") AS (
         (SELECT "start.2"."id" AS "id",
                 "start.2"."$iteration" AS "$iteration",
                 "start.2"."cells" AS "cells",
                 "start.2"."$control" AS "$control"
          FROM   "start.2")
           UNION ALL
         (SELECT "assignment.1"."id" AS "id",
                 "assignment.1"."$iteration" AS "$iteration",
                 "assignment.1"."cells" AS "cells",
                 "assignment.1"."$control" AS "$control"
          FROM   "assignment.1")
       ),
       "assignment.2"("id", "cells", "$control", "$iteration", "cell") AS (
         SELECT "merge.1"."id" AS "id",
                "merge.1"."cells" AS "cells",
                "merge.1"."$control" AS "$control",
                "merge.1"."$iteration" AS "$iteration",
                CAST((list_position(("merge.1"."cells"), 0)-1) AS int) AS "cell"
         FROM   "merge.1"
       ),
       "assignment.3"("id", "cells", "$control", "$iteration", "done", "cell") AS (
         SELECT "assignment.2"."id" AS "id",
                "assignment.2"."cells" AS "cells",
                "assignment.2"."$control" AS "$control",
                "assignment.2"."$iteration" AS "$iteration",
                CAST((("assignment.2"."cell") IS NULL) AS boolean) AS "done",
                "assignment.2"."cell" AS "cell"
         FROM   "assignment.2"
       ),
       "where.1"("id", "$iteration", "cells", "$control") AS (
         SELECT "assignment.3"."id" AS "id",
                "assignment.3"."$iteration" AS "$iteration",
                "assignment.3"."cells" AS "cells",
                "assignment.3"."$control" AS "$control"
         FROM   "assignment.3"
         WHERE  "assignment.3"."done" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("id", "cells", "$control", "$iteration", "cell") AS (
         SELECT "assignment.3"."id" AS "id",
                "assignment.3"."cells" AS "cells",
                "assignment.3"."$control" AS "$control",
                "assignment.3"."$iteration" AS "$iteration",
                "assignment.3"."cell" AS "cell"
         FROM   "assignment.3"
         WHERE  "assignment.3"."done" IS DISTINCT FROM TRUE
       ),
       "assignment.6"("$iteration", "result", "$control") AS (
         SELECT "where.1"."$iteration" AS "$iteration",
                CAST(({id: ("where.1"."id"), cells: ("where.1"."cells")}) AS struct(id int, cells int[])) AS "result",
                "where.1"."$control" AS "$control"
         FROM   "where.1"
       ),
       "fork.2"("id", "cells", "$control", "$iteration", "value", "cell") AS (
         SELECT "where.2"."id" AS "id",
                "where.2"."cells" AS "cells",
                "where.2"."$control" AS "$control",
                "where.2"."$iteration" AS "$iteration",
                "@expression"."value" AS "value",
                "where.2"."cell" AS "cell"
         FROM   "where.2",
                LATERAL (FROM generate_series(1, 9)) AS "@expression"("value")
       ),
       "assignment.4"("id", "cells", "$control", "ok", "$iteration", "value", "cell") AS (
         SELECT "fork.2"."id" AS "id",
                "fork.2"."cells" AS "cells",
                "fork.2"."$control" AS "$control",
                CAST((NOT EXISTS (
                         FROM  generate_series(1, 9) AS _(o)
                         WHERE ("fork.2"."value") IN (("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + o                 ],
                                       ("fork.2"."cells")[("fork.2"."cell") % 9                             + (o-1)*9 + 1       ],
                                       ("fork.2"."cells")[((("fork.2"."cell")//3) % 3) * 3 + (("fork.2"."cell")//27) * 27 + o + ((o-1)//3) * 6])
                       )) AS boolean) AS "ok",
                "fork.2"."$iteration" AS "$iteration",
                "fork.2"."value" AS "value",
                "fork.2"."cell" AS "cell"
         FROM   "fork.2"
       ),
       "emit.1"("$iteration", "$result", "$control") AS (
         SELECT "assignment.6"."$iteration" AS "$iteration",
                "assignment.6"."result" AS "$result",
                "assignment.6"."$control" AS "$control"
         FROM   "assignment.6"
       ),
       "stop.2"("$control") AS (
         SELECT "emit.1"."$control"
         FROM   "emit.1"
         WHERE  FALSE
       ),
       "where.3"("id", "cells", "$iteration", "value", "cell") AS (
         SELECT "assignment.4"."id" AS "id",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."$iteration" AS "$iteration",
                "assignment.4"."value" AS "value",
                "assignment.4"."cell" AS "cell"
         FROM   "assignment.4"
         WHERE  "assignment.4"."ok" IS NOT DISTINCT FROM TRUE
       ),
       "where.4"("$control") AS (
         SELECT "assignment.4"."$control" AS "$control"
         FROM   "assignment.4"
         WHERE  "assignment.4"."ok" IS DISTINCT FROM TRUE
       ),
       "assignment.5"("id", "$iteration", "cells") AS (
         SELECT "where.3"."id" AS "id",
                "where.3"."$iteration" AS "$iteration",
                CAST((concat(("where.3"."cells")[:("where.3"."cell")], [("where.3"."value")], ("where.3"."cells")[("where.3"."cell")+2:])) AS int[]) AS "cells"
         FROM   "where.3"
       ),
       "stop.1"("$control") AS (
         SELECT "where.4"."$control"
         FROM   "where.4"
         WHERE  FALSE
       ),
       "jump.1"("id", "$iteration", "cells", "$label") AS (
         SELECT "assignment.5"."id" AS "id",
                "assignment.5"."$iteration" AS "$iteration",
                "assignment.5"."cells" AS "cells",
                'start.2' AS "$label"
         FROM   "assignment.5"
       )
     (SELECT CAST((NULL) AS text) AS "$label",
             CAST(("emit.1"."$iteration") AS int) AS "$iteration",
             CAST(("emit.1"."$result") AS struct(id int, cells int[])) AS "$result",
             CAST((NULL) AS int) AS "id",
             CAST((NULL) AS int[]) AS "cells"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."$label") AS text) AS "$label",
             CAST(("jump.1"."$iteration" + 1) AS int) AS "$iteration",
             CAST((NULL) AS struct(id int, cells int[])) AS "$result",
             CAST(("jump.1"."id") AS int) AS "id",
             CAST(("jump.1"."cells") AS int[]) AS "cells"
      FROM   "jump.1"))
  )
SELECT "@loop"."$result"
FROM   "@loop"
WHERE  "@loop"."$label" IS NULL;