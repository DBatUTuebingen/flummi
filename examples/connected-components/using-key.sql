WITH RECURSIVE cc(node, comp) USING KEY (node, min(comp)) AS (
  SELECT id AS node, id AS comp
  FROM   nodes
    UNION ALL
  SELECT u.node, v.comp
  FROM   recurring.cc AS u, edges AS e, cc AS v
  WHERE  (e.here, e.there) = (u.node, v.node)
  AND    v.comp < u.comp
)
SELECT list(node)
FROM   cc
GROUP  BY comp;
