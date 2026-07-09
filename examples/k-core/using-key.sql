-- Algorithm k-core: The k-core is a maximal set of vertices such that its
-- induced subgraph only contains vertices with degree larger than or equal to k.
--
-- Also see https://en.wikipedia.org/wiki/Degeneracy_%28graph_theory%29


-- Sample 5-node graph (undirected):
--
--    1--2  4
--    | /   |
--    3     5

DROP TABLE IF EXISTS edges CASCADE;
DROP TABLE IF EXISTS nodes CASCADE;

CREATE TABLE nodes (
  node int PRIMARY KEY
);

CREATE TABLE edges (
   "from" int,
   "to"   int,
   FOREIGN KEY ("from") REFERENCES nodes,
   FOREIGN KEY ("to")   REFERENCES nodes
);

INSERT INTO nodes(node)
  FROM generate_series(1,5);

INSERT INTO edges("from", "to")
  VALUES (1,2),
         (2,3),
         (3,1),
         (4,5);

-- Make graph undirected
INSERT INTO edges("to", "from")
  FROM edges;

FROM nodes;
FROM edges;


-----------------------------------------------------------------------
-- Sample undirected 10-node graph taken from the Neo4j docs at
-- https://neo4j.com/docs/graph-data-science/current/algorithms/k-core/
--
-- 1-core: 10 nodes
-- 2-core:  6 nodes
-- 3-core:  4 nodes
-- 4-core:  0 nodes

DROP TABLE IF EXISTS edges CASCADE;
DROP TABLE IF EXISTS nodes CASCADE;

CREATE TABLE nodes (
  node text PRIMARY KEY
);

CREATE TABLE edges (
   "from" text,
   "to"   text,
   FOREIGN KEY ("from") REFERENCES nodes,
   FOREIGN KEY ("to")   REFERENCES nodes
);

INSERT INTO nodes(node) VALUES
  ('Alice'),  ('Bridget'), ('Charles'), ('Doug'), ('Eli'),
  ('Filip'), ('Greg'), ('Harry'), ('Ian'), ('James');

INSERT INTO edges("from", "to") VALUES
  ('Alice', 'Bridget'),
  ('Bridget', 'Charles'),
  ('Charles', 'Doug'),
  ('Charles', 'Harry'),
  ('Doug', 'Eli'),
  ('Doug', 'Filip'),
  ('Doug', 'Greg'),
  ('Eli', 'Filip'),
  ('Eli', 'Greg'),
  ('Filip', 'Greg'),
  ('Greg', 'Harry'),
  ('Ian', 'James');

-- Make undirected
INSERT INTO edges("to", "from")
  FROM edges;

FROM nodes;
FROM edges;

-----------------------------------------------------------------------

-- Pseudcode:
--
-- active[v] = degree[v] >= k
-- repeat until no change:
--   degree[v] = count(active neighbors of v)
--   active[v] = active[v] and degree[v] >= k

SET VARIABLE k = 2;

WITH RECURSIVE k_core(node, active) USING KEY (node) AS (
  SELECT v.node, count(*) >= $k AS active    -- count(*) ≡ deg(v)
  FROM   nodes AS v, edges AS e
  WHERE  v.node = e."from"
  GROUP BY v.node

    UNION ALL

  SELECT v.node, v.active AND count(*) >= $k AS new_active
  FROM   k_core AS v, edges AS e, k_core AS n
  WHERE (v.node, n.node) = (e."from", e."to") AND n.active
  GROUP BY v.node, v.active
  HAVING new_active <> v.active
)
FROM k_core
WHERE active;
