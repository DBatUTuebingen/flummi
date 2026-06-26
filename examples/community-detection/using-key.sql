-- ⚠️ Needs DuckDB >1.5.x with PEG parser disabled
SET allow_parser_override_extension = 'default'; -- disable PEG parser

WITH RECURSIVE cdlp(node, L) USING KEY (node, min(L)) AS (
  SELECT n.id, n.id AS L
  FROM   nodes AS n
    UNION ALL
  SELECT v.node, mode(u.L) AS freq
  FROM   cdlp AS v, edges AS e, recurring.cdlp AS u
  WHERE  (e.here, e.there) = (v.node, u.node)  --  v <-- u, u ∊ Nᵢₙ(v)
  OR     (e.there, e.here) = (v.node, u.node)  --  v --> u, u ∊ Nₒᵤₜ(v)
  GROUP BY v.node, v.L
  HAVING freq < v.L
)
SELECT list(node)
FROM   cdlp
GROUP  BY L;
