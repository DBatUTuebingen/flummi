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
FROM   generate_series(1, 10_000_00) AS _(x);

-- connect ~10% of node pairs with a directed edge from the smaller to the higher node id
INSERT INTO edges
SELECT here.id, there.id
FROM   nodes AS here,
       nodes AS there
WHERE  random() < 0.1
AND    here.id < there.id
AND    here.id % 1000 = there.id % 1000;

-- duplicate and flip all directed edges
INSERT INTO edges
SELECT there, here
FROM   edges;

-- all nodes are reachable from themselves
INSERT INTO edges
SELECT id, id
FROM   nodes;
