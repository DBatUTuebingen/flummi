DROP TABLE IF EXISTS nodes;
CREATE TABLE nodes(
  id INT PRIMARY KEY
);

DROP TABLE IF EXISTS edges;
CREATE TABLE edges(
  here   INT,
  there  INT,
  length INT NOT NULL,
  PRIMARY KEY (here, there)
);


INSERT INTO nodes SELECT x - 1 AS id FROM generate_series(1, 100) AS _(x);

INSERT INTO edges
SELECT here.id, there.id,
       (random() * 100) :: int
FROM   nodes AS here,
       nodes AS there
WHERE  random() < 0.2
AND    here.id < there.id;
