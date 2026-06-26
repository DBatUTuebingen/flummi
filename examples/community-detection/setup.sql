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
FROM   generate_series(1, 100_00) AS _(x);

-- connect ~1% of node pairs with a directed edge from the smaller to the higher node id
INSERT INTO edges
SELECT here.id, there.id
FROM   nodes AS here,
       nodes AS there
WHERE  random() < 0.01
AND    here.id < there.id
AND    (here.id % 1000 != there.id % 1000 OR random() < 0.5);

-- add inverted edges (we're working with undirected graphs here!)
INSERT INTO edges
SELECT there, here
FROM   edges;
