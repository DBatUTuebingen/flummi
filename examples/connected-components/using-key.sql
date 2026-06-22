WITH RECURSIVE cc(node, comp) USING KEY (node) AS (
  SELECT id, id AS comp
  FROM   nodes AS n
    UNION ALL
  SELECT DISTINCT ON (node) u.node, v.comp
  FROM   recurring.cc AS u, edges AS e, cc AS v
  WHERE  (e.here, e.there) = (u.node, v.node)
  AND    v.comp < u.comp
)
SELECT list(node)
FROM   cc
GROUP  BY comp;
