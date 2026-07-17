WITH RECURSIVE
  "🔄"("🏷️", "#️⃣", "📊.1", "📊.2", "centroid", "centroids") AS (
    (SELECT CAST(('start.1') AS text) AS "🏷️",
            CAST((0) AS int) AS "#️⃣",
            CAST((NULL) AS point) AS "📊.1",
            CAST((NULL) AS point[]) AS "📊.2",
            CAST((NULL) AS point) AS "centroid",
            CAST((NULL) AS real) AS "centroids")
      UNION ALL
    (WITH
       "start.1"("#️⃣", "⚙️") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                NULL AS "⚙️"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.1'
       ),
       "start.2"("#️⃣", "centroid", "⚙️", "centroids") AS (
         SELECT "🔄"."#️⃣" AS "#️⃣",
                "🔄"."centroid" AS "centroid",
                NULL AS "⚙️",
                "🔄"."centroids" AS "centroids"
         FROM   "🔄"
         WHERE  "🔄"."🏷️" IS NOT DISTINCT FROM 'start.2'
       ),
       "fork.1"("#️⃣", "centroid", "⚙️") AS (
         SELECT "start.1"."#️⃣" AS "#️⃣",
                CAST(("ℚ"."centroid") AS point) AS "centroid",
                "start.1"."⚙️" AS "⚙️"
         FROM   "start.1",
                (SELECT p FROM points AS p USING SAMPLE 10 ROWS) AS "ℚ"("centroid")
       ),
       "assignment.1"("centroids", "centroid", "⚙️", "#️⃣") AS (
         SELECT CAST((sum(("fork.1"."centroid").x + ("fork.1"."centroid").y) OVER ()) AS real) AS "centroids",
                "fork.1"."centroid" AS "centroid",
                "fork.1"."⚙️" AS "⚙️",
                "fork.1"."#️⃣" AS "#️⃣"
         FROM   "fork.1"
       ),
       "merge.1"("centroids", "centroid", "⚙️", "#️⃣") AS (
         (SELECT "assignment.1"."centroids" AS "centroids",
                 "assignment.1"."centroid" AS "centroid",
                 "assignment.1"."⚙️" AS "⚙️",
                 "assignment.1"."#️⃣" AS "#️⃣"
          FROM   "assignment.1")
           UNION ALL
         (SELECT "start.2"."centroids" AS "centroids",
                 "start.2"."centroid" AS "centroid",
                 "start.2"."⚙️" AS "⚙️",
                 "start.2"."#️⃣" AS "#️⃣"
          FROM   "start.2")
       ),
       "fork.2"("point", "centroids", "#️⃣", "centroid", "⚙️") AS (
         SELECT CAST(("ℚ"."point") AS point) AS "point",
                "merge.1"."centroids" AS "centroids",
                "merge.1"."#️⃣" AS "#️⃣",
                "merge.1"."centroid" AS "centroid",
                "merge.1"."⚙️" AS "⚙️"
         FROM   "merge.1",
                (SELECT p FROM points AS p) AS "ℚ"("point")
       ),
       "assignment.2"("point", "distance", "centroids", "#️⃣", "centroid", "⚙️") AS (
         SELECT "fork.2"."point" AS "point",
                CAST((sqrt((("fork.2"."point").x - ("fork.2"."centroid").x) ** 2 + (("fork.2"."point").y - ("fork.2"."centroid").y) ** 2)) AS real) AS "distance",
                "fork.2"."centroids" AS "centroids",
                "fork.2"."#️⃣" AS "#️⃣",
                "fork.2"."centroid" AS "centroid",
                "fork.2"."⚙️" AS "⚙️"
         FROM   "fork.2"
       ),
       "gather.1"("point", "centroids", "#️⃣", "centroid", "⚙️") AS (
         SELECT "assignment.2"."point" AS "point",
                "assignment.2"."centroids" AS "centroids",
                "assignment.2"."#️⃣" AS "#️⃣",
                CAST((arg_min(("assignment.2"."centroid"), ("assignment.2"."distance"))) AS point) AS "centroid",
                "assignment.2"."⚙️" AS "⚙️"
         FROM   "assignment.2"
         GROUP  BY "assignment.2"."point",
                   "assignment.2"."centroids",
                   "assignment.2"."#️⃣",
                   "assignment.2"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "gather.2"("new_centroid", "centroids", "#️⃣", "centroid", "⚙️") AS (
         SELECT CAST(({ 'x': avg(("gather.1"."point").x), 'y': avg(("gather.1"."point").y) }) AS point) AS "new_centroid",
                "gather.1"."centroids" AS "centroids",
                "gather.1"."#️⃣" AS "#️⃣",
                "gather.1"."centroid" AS "centroid",
                "gather.1"."⚙️" AS "⚙️"
         FROM   "gather.1"
         GROUP  BY "gather.1"."centroids",
                   "gather.1"."#️⃣",
                   "gather.1"."centroid",
                   "gather.1"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "assignment.3"("centroids", "new_centroid", "#️⃣", "old_centroids", "centroid", "⚙️") AS (
         SELECT CAST((sum(("gather.2"."new_centroid").x + ("gather.2"."new_centroid").y) OVER ()) AS real) AS "centroids",
                "gather.2"."new_centroid" AS "new_centroid",
                "gather.2"."#️⃣" AS "#️⃣",
                CAST((("gather.2"."centroids")) AS real) AS "old_centroids",
                "gather.2"."centroid" AS "centroid",
                "gather.2"."⚙️" AS "⚙️"
         FROM   "gather.2"
       ),
       "assignment.4"("new_centroid", "#️⃣", "centroids", "🔍", "centroid", "⚙️") AS (
         SELECT "assignment.3"."new_centroid" AS "new_centroid",
                "assignment.3"."#️⃣" AS "#️⃣",
                "assignment.3"."centroids" AS "centroids",
                CAST((abs(("assignment.3"."old_centroids") - ("assignment.3"."centroids")) <= 0.000001) AS boolean) AS "🔍",
                "assignment.3"."centroid" AS "centroid",
                "assignment.3"."⚙️" AS "⚙️"
         FROM   "assignment.3"
       ),
       "where.1"("#️⃣", "centroid", "⚙️") AS (
         SELECT "assignment.4"."#️⃣" AS "#️⃣",
                "assignment.4"."centroid" AS "centroid",
                "assignment.4"."⚙️" AS "⚙️"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS NOT DISTINCT FROM TRUE
       ),
       "where.2"("new_centroid", "centroids", "⚙️", "#️⃣") AS (
         SELECT "assignment.4"."new_centroid" AS "new_centroid",
                "assignment.4"."centroids" AS "centroids",
                "assignment.4"."⚙️" AS "⚙️",
                "assignment.4"."#️⃣" AS "#️⃣"
         FROM   "assignment.4"
         WHERE  "assignment.4"."🔍" IS DISTINCT FROM TRUE
       ),
       "assignment.5"("#️⃣", "centroid", "⚙️", "centroids") AS (
         SELECT "where.2"."#️⃣" AS "#️⃣",
                CAST((("where.2"."new_centroid")) AS point) AS "centroid",
                "where.2"."⚙️" AS "⚙️",
                "where.2"."centroids" AS "centroids"
         FROM   "where.2"
       ),
       "fork.3"("point", "#️⃣", "centroid", "⚙️") AS (
         SELECT CAST(("ℚ"."point") AS point) AS "point",
                "where.1"."#️⃣" AS "#️⃣",
                "where.1"."centroid" AS "centroid",
                "where.1"."⚙️" AS "⚙️"
         FROM   "where.1",
                (SELECT p FROM points AS p) AS "ℚ"("point")
       ),
       "assignment.6"("point", "distance", "#️⃣", "centroid", "⚙️") AS (
         SELECT "fork.3"."point" AS "point",
                CAST((sqrt((("fork.3"."point").x - ("fork.3"."centroid").x) ** 2 + (("fork.3"."point").y - ("fork.3"."centroid").y) ** 2)) AS real) AS "distance",
                "fork.3"."#️⃣" AS "#️⃣",
                "fork.3"."centroid" AS "centroid",
                "fork.3"."⚙️" AS "⚙️"
         FROM   "fork.3"
       ),
       "jump.1"("🏷️", "#️⃣", "centroid", "centroids") AS (
         SELECT 'start.2' AS "🏷️",
                "assignment.5"."#️⃣" AS "#️⃣",
                "assignment.5"."centroid" AS "centroid",
                "assignment.5"."centroids" AS "centroids"
         FROM   "assignment.5"
       ),
       "gather.3"("point", "#️⃣", "centroid", "⚙️") AS (
         SELECT "assignment.6"."point" AS "point",
                "assignment.6"."#️⃣" AS "#️⃣",
                CAST((arg_min(("assignment.6"."centroid"), ("assignment.6"."distance"))) AS point) AS "centroid",
                "assignment.6"."⚙️" AS "⚙️"
         FROM   "assignment.6"
         GROUP  BY "assignment.6"."point",
                   "assignment.6"."#️⃣",
                   "assignment.6"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "gather.4"("cluster", "#️⃣", "centroid", "⚙️") AS (
         SELECT CAST((list(("gather.3"."point"))) AS point[]) AS "cluster",
                "gather.3"."#️⃣" AS "#️⃣",
                "gather.3"."centroid" AS "centroid",
                "gather.3"."⚙️" AS "⚙️"
         FROM   "gather.3"
         GROUP  BY "gather.3"."#️⃣",
                   "gather.3"."centroid",
                   "gather.3"."⚙️"
         HAVING COUNT(*) > 0
       ),
       "emit.1"("📊.1", "#️⃣", "📊.2", "⚙️") AS (
         SELECT "gather.4"."centroid" AS "📊.1",
                "gather.4"."#️⃣" AS "#️⃣",
                "gather.4"."cluster" AS "📊.2",
                "gather.4"."⚙️" AS "⚙️"
         FROM   "gather.4"
       ),
       "stop.1"("⚙️") AS (
         SELECT "emit.1"."⚙️"
         FROM   "emit.1"
         WHERE  FALSE
       )
     (SELECT CAST(("jump.1"."🏷️") AS text) AS "🏷️",
             CAST(("jump.1"."#️⃣" + 1) AS int) AS "#️⃣",
             CAST((NULL) AS point) AS "📊.1",
             CAST((NULL) AS point[]) AS "📊.2",
             CAST(("jump.1"."centroid") AS point) AS "centroid",
             CAST(("jump.1"."centroids") AS real) AS "centroids"
      FROM   "jump.1")
       UNION ALL
     (SELECT CAST((NULL) AS text) AS "🏷️",
             CAST(("emit.1"."#️⃣") AS int) AS "#️⃣",
             CAST(("emit.1"."📊.1") AS point) AS "📊.1",
             CAST(("emit.1"."📊.2") AS point[]) AS "📊.2",
             CAST((NULL) AS point) AS "centroid",
             CAST((NULL) AS real) AS "centroids"
      FROM   "emit.1"))
  )
SELECT "🔄"."📊.1",
       "🔄"."📊.2"
FROM   "🔄"
WHERE  "🔄"."🏷️" IS NULL;