DROP TABLE IF EXISTS nodes;
CREATE TABLE nodes(
  id INT PRIMARY KEY
);

DROP TABLE IF EXISTS edges;
CREATE TABLE edges(
  here   INT,
  there  INT,
  PRIMARY KEY (here, there)
);

INSERT INTO nodes
SELECT x - 1 AS id
FROM   generate_series(1, 100) AS _(x);

-- connect ~5% of node pairs with a directed edge from the smaller to the higher node id
INSERT INTO edges
SELECT here.id, there.id
FROM   nodes AS here,
       nodes AS there
WHERE  here.id < there.id
AND    random() < 0.05
AND    (here.id % 10 == there.id % 10 OR random() < 0.25);

-- add inverted edges (we're working with undirected graphs here!)
INSERT INTO edges
SELECT there, here
FROM   edges;
