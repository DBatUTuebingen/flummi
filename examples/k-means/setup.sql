DROP TYPE IF EXISTS point;
CREATE TYPE point AS struct(x REAL, y REAL);

DROP TABLE IF EXISTS points;
CREATE TABLE points(
  x REAL,
  y REAL,
  PRIMARY KEY (x, y)
);

INSERT INTO points
SELECT DISTINCT random() * 100_000, random() * 100_000
FROM   range(1_000_000);
