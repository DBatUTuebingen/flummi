SET VARIABLE k = 5;

DROP MACRO IF EXISTS dist;
CREATE MACRO dist(p, c) AS (p.x - c.x) * (p.x - c.x) + (p.y - c.y) * (p.y - c.y);

-- ⚠️ Only DuckDB v2.0 supports USING KEY with UNION semantics
--     (stop once the point-to-cluster assigment does not change)
--
-- NB. This uses median(...) not avg(...) due to
--     floating arithmetic inaccuracies
WITH RECURSIVE centroids(id, x, y) USING KEY (id, median(x), median(y)) AS (
  (SELECT row_number() OVER (), x, y
   FROM   points
   ORDER  BY random()
   LIMIT  $k
  )
    UNION
  SELECT argmin(c.id, dist(p, c)), p.x, p.y
  FROM   recurring.centroids AS c, points AS p
  GROUP BY p.x, p.y
)
SELECT DISTINCT ON (p.x, p.y) c.*, p.x, p.y
FROM   centroids AS c, points AS p
ORDER  BY dist(p, c);
