WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊", "centroid") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS point[]) AS "📊",
            CAST((NULL) AS point) AS "centroid")
      UNION ALL
    (WITH
       "start.1"("⚙️", "#️⃣") AS (
         SELECT NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("centroid", "⚙️", "#️⃣") AS (
         SELECT "🔄"."centroid" AS "centroid",
                NULL AS "⚙️",
                "🔄"."#️⃣" AS "#️⃣"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "fork.1"("centroid", "⚙️", "#️⃣") AS (
         SELECT "ℚ"."centroid" AS "centroid",
                "start.1"."⚙️" AS "⚙️",
                "start.1"."#️⃣" AS "#️⃣"
         FROM   "start.1",
                (SELECT p FROM points AS p USING SAMPLE 10 ROWS) AS "ℚ"("centroid")
       ),
       "merge.1"("centroid", "⚙️", "#️⃣") AS (
         (SELECT "fork.1"."centroid" AS "centroid",
                 "fork.1"."⚙️" AS "⚙️",
                 "fork.1"."#️⃣" AS "#️⃣"
          FROM   "fork.1")
           UNION ALL
         (SELECT "start.2"."centroid" AS "centroid",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣"
          FROM   "start.2")
       ),
       "assignment.1"("old_centroids", "⚙️", "centroid", "#️⃣") AS (
         SELECT CAST((sum(("merge.1"."centroid").x + ("merge.1"."centroid").y) OVER ()) AS real) AS "old_centroids",
                "merge.1"."⚙️" AS "⚙️",
                "merge.1"."centroid" AS "centroid",
                "merge.1"."#️⃣" AS "#️⃣"
         FROM   "merge.1"
       ),
       "fork.2"("centroid", "#️⃣", "point", "old_centroids", "⚙️") AS (
         SELECT "assignment.1"."centroid" AS "centroid",
                "assignment.1"."#️⃣" AS "#️⃣",
                "ℚ"."point" AS "point",
                "assignment.1"."old_centroids" AS "old_centroids",
                "assignment.1"."⚙️" AS "⚙️"
         FROM   "assignment.1",
                (SELECT p FROM points AS p) AS "ℚ"("point")
       ),
       "assignment.2"("centroid", "#️⃣", "point", "distance", "old_centroids", "⚙️") AS (
         SELECT "fork.2"."centroid" AS "centroid",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."point" AS "point",
                CAST((sqrt((("fork.2"."point").x - ("fork.2"."centroid").x) ** 2 + (("fork.2"."point").y - ("fork.2"."centroid").y) ** 2)) AS real) AS "distance",
                "fork.2"."old_centroids" AS "old_centroids",
                "fork.2"."⚙️" AS "⚙️"
         FROM   "fork.2"
       ),
       "gather.1"("centroid", "#️⃣", "point", "old_centroids", "⚙️") AS (
         SELECT arg_min(("assignment.2"."centroid"), ("assignment.2"."distance")) AS "centroid",
                "assignment.2"."#️⃣" AS "#️⃣",
                "assignment.2"."point" AS "point",
                "assignment.2"."old_centroids" AS "old_centroids",
                "assignment.2"."⚙️" AS "⚙️"
         FROM   "assignment.2"
         GROUP  BY "assignment.2"."#️⃣",
                   "assignment.2"."point",
                   "assignment.2"."old_centroids",
                   "assignment.2"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "gather.2"("centroid", "new_centroid", "#️⃣", "old_centroids", "⚙️") AS (
         SELECT "gather.1"."centroid" AS "centroid",
                { 'x': avg(("gather.1"."point").x), 'y': avg(("gather.1"."point").y) } AS "new_centroid",
                "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."old_centroids" AS "old_centroids",
                "gather.1"."⚙️" AS "⚙️"
         FROM   "gather.1"
         GROUP  BY "gather.1"."centroid",
                   "gather.1"."#️⃣",
                   "gather.1"."old_centroids",
                   "gather.1"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "assignment.3"("centroid", "new_centroid", "new_centroids", "#️⃣", "old_centroids", "⚙️") AS (
         SELECT "gather.2"."centroid" AS "centroid",
                "gather.2"."new_centroid" AS "new_centroid",
                CAST((sum(("gather.2"."new_centroid").x + ("gather.2"."new_centroid").y) OVER ()) AS real) AS "new_centroids",
                "gather.2"."#️⃣" AS "#️⃣",
                "gather.2"."old_centroids" AS "old_centroids",
                "gather.2"."⚙️" AS "⚙️"
         FROM   "gather.2"
       ),
       "assignment.4"("centroid", "new_centroid", "#️⃣", "⚙️", "cond") AS (
         SELECT "assignment.3"."centroid" AS "centroid",
                "assignment.3"."new_centroid" AS "new_centroid",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."⚙️" AS "⚙️",
                CAST((abs(("assignment.3"."old_centroids") - ("assignment.3"."new_centroids")) > 0.000001) AS boolean) AS "cond"
         FROM   "assignment.3"
       ),
       "where.1"("new_centroid", "#️⃣") AS (
         SELECT "assignment.4"."new_centroid" AS "new_centroid",
                "assignment.4"."#️⃣" AS "#️⃣"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("centroid", "⚙️", "#️⃣") AS (
         SELECT "assignment.4"."centroid" AS "centroid",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."#️⃣" AS "#️⃣"
         FROM   "assignment.4"
         WHERE  "assignment.4"."cond" IS DISTINCT FROM TRUE
       ),
       "assignment.5"("centroid", "#️⃣") AS (
         SELECT CAST((("where.1"."new_centroid")) AS point) AS "centroid",
                "where.1"."#️⃣" AS "#️⃣"
         FROM   "where.1"
       ),
       "fork.3"("centroid", "⚙️", "#️⃣", "point") AS (
         SELECT "where.2"."centroid" AS "centroid",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."#️⃣" AS "#️⃣",
                "ℚ"."point" AS "point"
         FROM   "where.2",
                (SELECT p FROM points AS p) AS "ℚ"("point")
       ),
       "assignment.6"("centroid", "#️⃣", "point", "distance", "⚙️") AS (
         SELECT "fork.3"."centroid" AS "centroid",
                "fork.3"."#️⃣" AS "#️⃣",
                "fork.3"."point" AS "point",
                CAST((sqrt((("fork.3"."point").x - ("fork.3"."centroid").x) ** 2 + (("fork.3"."point").y - ("fork.3"."centroid").y) ** 2)) AS real) AS "distance",
                "fork.3"."⚙️" AS "⚙️"
         FROM   "fork.3"
       ),
       "jump.1"("#️⃣", "🏷️", "centroid") AS (
         SELECT "assignment.5"."#️⃣" AS "#️⃣",
                'start.2' AS "🏷️",
                "assignment.5"."centroid" AS "centroid"
         FROM   "assignment.5"
       ),
       "gather.3"("centroid", "⚙️", "#️⃣", "point") AS (
         SELECT arg_min(("assignment.6"."centroid"), ("assignment.6"."distance")) AS "centroid",
                "assignment.6"."⚙️" AS "⚙️",
                "assignment.6"."#️⃣" AS "#️⃣",
                "assignment.6"."point" AS "point"
         FROM   "assignment.6"
         GROUP  BY "assignment.6"."⚙️",
                   "assignment.6"."#️⃣",
                   "assignment.6"."point"
         HAVING COUNT(*) > 0
       ),
       "gather.4"("cluster", "⚙️", "#️⃣") AS (
         SELECT list(("gather.3"."point")) AS "cluster",
                "gather.3"."⚙️" AS "⚙️",
                "gather.3"."#️⃣" AS "#️⃣"
         FROM   "gather.3"
         GROUP  BY "gather.3"."centroid",
                   "gather.3"."⚙️",
                   "gather.3"."#️⃣"
         HAVING COUNT(*) > 0
       ),
       "emit.1"("⚙️", "#️⃣", "📊") AS (
         SELECT "gather.4"."⚙️" AS "⚙️",
                "gather.4"."#️⃣" AS "#️⃣",
                "gather.4"."cluster" AS "📊"
         FROM   "gather.4"
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       )
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS point[]) AS "📊",
             CAST(("jump.1"."centroid") AS point) AS "centroid"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊") AS point[]) AS "📊",
             CAST((NULL) AS point) AS "centroid"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;