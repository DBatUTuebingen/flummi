DROP TYPE IF EXISTS point;
CREATE TYPE point AS struct(x DOUBLE, y DOUBLE);

DROP TABLE IF EXISTS points;
CREATE TABLE points(
  x DOUBLE,
  y DOUBLE,
  PRIMARY KEY (x, y)
);

INSERT INTO points
SELECT DISTINCT random() * 100_000, random() * 100_000
FROM   range(10_000_000);
