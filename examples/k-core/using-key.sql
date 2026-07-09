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
-- Sample undirected 16-node graph ("2-core") taken from
-- https://en.wikipedia.org/wiki/Degeneracy_%28graph_theory%29


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
  FROM generate_series(1,16);

INSERT INTO edges("from", "to")
  VALUES ( 1, 2), ( 1, 3),
         ( 2, 3), ( 2, 9),
         ( 4, 5), ( 4, 6), ( 4,10), ( 4,13),
         ( 5, 6), ( 5, 7), ( 5,10), ( 5,14),
         ( 6, 7), ( 6, 8), ( 6, 9), ( 6,11),
         ( 7, 8),
         (11,12), (11,15),
         (15,16);

-- Make undirected
INSERT INTO edges("to", "from")
  FROM edges;

FROM nodes;
FROM edges;

-----------------------------------------------------------------------



-- Pseudcode:
--
-- active[v] = true
-- repeat until no change:
--   degree[v] = count(active neighbors of v)
--   active[v] = active[v] and degree[v] >= k

SET VARIABLE k = 2;

WITH RECURSIVE k_core(node, deg, active) USING KEY (node) AS (
  SELECT v.node, -1 AS deg, true AS active
  FROM   nodes AS v

    UNION ALL

  SELECT v.node, countif(n.active) AS degree, degree >= $k AS active
  FROM   k_core AS v, edges AS e, recurring.k_core AS n
  WHERE (v.node, n.node) = (e."from", e."to")
  GROUP BY v.node, v.active, v.deg
  HAVING degree <> v.deg
)
SELECT node
FROM k_core
WHERE active;
