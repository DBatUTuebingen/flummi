DROP TYPE IF EXISTS point;
CREATE TYPE point AS struct(x REAL, y REAL);

DROP TABLE IF EXISTS points;
CREATE TABLE points(
  x REAL,
  y REAL,
  PRIMARY KEY (x, y)
);

SELECT setseed(0.42);

INSERT INTO points
SELECT DISTINCT random() * 10_000, random() * 10_000
FROM   range(100_000);
