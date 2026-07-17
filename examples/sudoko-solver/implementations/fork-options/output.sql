WITH RECURSIVE
  "🔄"("#️⃣", "🏷️", "📊.1", "cells", "id") AS (
    (SELECT CAST((0) AS int) AS "#️⃣",
            CAST(('start.1') AS text) AS "🏷️",
            CAST((NULL) AS struct(id int, cells int[])) AS "📊.1",
            CAST((NULL) AS int[]) AS "cells",
            CAST((NULL) AS int) AS "id")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "fork.1"("#️⃣", "⚙️", "cells") AS (
         SELECT "start.1"."#️⃣" AS "#️⃣",
                "start.1"."⚙️" AS "⚙️",
                CAST(("ℚ"."cells") AS int[]) AS "cells"
         FROM   "start.1",
                (SELECT cells
                 FROM   sudoku) AS "ℚ"("cells")
       ),
       "assignment.1"("#️⃣", "⚙️", "cells", "id") AS (
         SELECT "fork.1"."#️⃣" AS "#️⃣",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."cells" AS "cells",
                CAST((row_number() OVER ()) AS int) AS "id"
         FROM   "fork.1"
       ),
       "start.2"("#️⃣", "⚙️", "cells", "id") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️",
                "🔄"."cells" AS "cells",
                "🔄"."id" AS "id"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "merge.1"("#️⃣", "⚙️", "cells", "id") AS (
         (SELECT "assignment.1"."#️⃣" AS "#️⃣",
                 "assignment.1"."⚙️" AS "⚙️",
                 "assignment.1"."cells" AS "cells",
                 "assignment.1"."id" AS "id"
          FROM   "assignment.1")
           UNION ALL
         (SELECT "start.2"."#️⃣" AS "#️⃣",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."cells" AS "cells",
                 "start.2"."id" AS "id"
          FROM   "start.2")
       ),
       "assignment.2"("#️⃣", "⚙️", "cells", "cell", "id") AS (
         SELECT "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."cells" AS "cells",
                CAST((list_position(("merge.1"."cells"), 0)-1) AS int) AS "cell",
                "merge.1"."id" AS "id"
         FROM   "merge.1"
       ),
       "assignment.3"("#️⃣", "⚙️", "cells", "cell", "done", "id") AS (
         SELECT "assignment.2"."#️⃣" AS "#️⃣",
                "assignment.2"."⚙️" AS "⚙️",
                "assignment.2"."cells" AS "cells",
                "assignment.2"."cell" AS "cell",
                CAST((("assignment.2"."cell") IS NULL) AS boolean) AS "done",
                "assignment.2"."id" AS "id"
         FROM   "assignment.2"
       ),
       "assignment.4"("#️⃣", "⚙️", "🔍", "cells", "cell", "id") AS (
         SELECT "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."⚙️" AS "⚙️",
                CAST((("assignment.3"."done")) AS boolean) AS "🔍",
                "assignment.3"."cells" AS "cells",
                "assignment.3"."cell" AS "cell",
                "assignment.3"."id" AS "id"
         FROM   "assignment.3"
       ),
       "where.1"("#️⃣", "⚙️", "cells", "id") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."id" AS "id"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "assignment.7"("#️⃣", "⚙️", "result") AS (
         SELECT "where.1"."#️⃣" AS "#️⃣",
                "where.1"."⚙️" AS "⚙️",
                CAST(({id: ("where.1"."id"), cells: ("where.1"."cells")}) AS struct(id int, cells int[])) AS "result"
         FROM   "where.1"
       ),
       "emit.1"("#️⃣", "⚙️", "📊.1") AS (
         SELECT "assignment.7"."#️⃣" AS "#️⃣",
                "assignment.7"."⚙️" AS "⚙️",
                "assignment.7"."result" AS "📊.1"
         FROM   "assignment.7"
       ),
       "stop.2"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       ),
       "where.2"("#️⃣", "⚙️", "cells", "cell", "id") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."cells" AS "cells",
                "assignment.4"."cell" AS "cell",
                "assignment.4"."id" AS "id"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS DISTINCT FROM TRUE
       ),
       "fork.2"("#️⃣", "⚙️", "cells", "cell", "value", "id") AS (
         SELECT "where.2"."#️⃣" AS "#️⃣",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."cells" AS "cells",
                "where.2"."cell" AS "cell",
                CAST(("ℚ"."value") AS int) AS "value",
                "where.2"."id" AS "id"
         FROM   "where.2",
                (FROM generate_series(1, 9)) AS "ℚ"("value")
       ),
       "assignment.5"("#️⃣", "⚙️", "🔍", "cells", "cell", "value", "id") AS (
         SELECT "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."⚙️" AS "⚙️",
                CAST((NOT EXISTS (
                         FROM  generate_series(1, 9) AS _(o)
                         WHERE ("fork.2"."value") IN (("fork.2"."cells")[(("fork.2"."cell") // 9) * 9                      + o                 ],
                                       ("fork.2"."cells")[("fork.2"."cell") % 9                             + (o-1)*9 + 1       ],
                                       ("fork.2"."cells")[((("fork.2"."cell")//3) % 3) * 3 + (("fork.2"."cell")//27) * 27 + o + ((o-1)//3) * 6])
                       )) AS boolean) AS "🔍",
                "fork.2"."cells" AS "cells",
                "fork.2"."cell" AS "cell",
                "fork.2"."value" AS "value",
                "fork.2"."id" AS "id"
         FROM   "fork.2"
       ),
       "where.3"("#️⃣", "⚙️", "cells", "cell", "value", "id") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."⚙️" AS "⚙️",
                "assignment.5"."cells" AS "cells",
                "assignment.5"."cell" AS "cell",
                "assignment.5"."value" AS "value",
                "assignment.5"."id" AS "id"
         FROM   "assignment.5"
         WHERE  "assignment.5"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "assignment.6"("#️⃣", "⚙️", "cells", "id") AS (
         SELECT "where.3"."#️⃣" AS "#️⃣",
                "where.3"."⚙️" AS "⚙️",
                CAST((concat(("where.3"."cells")[:("where.3"."cell")], [("where.3"."value")], ("where.3"."cells")[("where.3"."cell")+2:])) AS int[]) AS "cells",
                "where.3"."id" AS "id"
         FROM   "where.3"
       ),
       "jump.1"("#️⃣", "🏷️", "cells", "id") AS (
         SELECT "assignment.6"."#️⃣" AS "#️⃣",
                'start.2' AS "🏷️",
                "assignment.6"."cells" AS "cells",
                "assignment.6"."id" AS "id"
         FROM   "assignment.6"
       ),
       "where.4"("⚙️") AS (
         SELECT "assignment.5"."⚙️" AS "⚙️"
         FROM   "assignment.5"
         WHERE  "assignment.5"."🔍" IS DISTINCT FROM TRUE
       ),
       "stop.1"("⚙️") AS (
         SELECT "where.4"."⚙️"
         FROM   "where.4"
         WHERE  FALSE
       )
     (SELECT CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."📊.1") AS struct(id int, cells int[])) AS "📊.1",
             CAST((NULL) AS int[]) AS "cells",
             CAST((NULL) AS int) AS "id"
      FROM   "emit.1")
       UNION ALL
     (SELECT CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST((NULL) AS struct(id int, cells int[])) AS "📊.1",
             CAST(("jump.1"."cells") AS int[]) AS "cells",
             CAST(("jump.1"."id") AS int) AS "id"
      FROM   "jump.1"))
  )
SELECT "🔄"."📊.1"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;