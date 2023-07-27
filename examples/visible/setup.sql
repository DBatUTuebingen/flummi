CREATE TYPE point AS struct("x" DOUBLE, "y" DOUBLE);

DROP TABLE IF EXISTS controlp;
CREATE TABLE controlp (
  x INT,
  y INT,
  Z DOUBLE,
  PRIMARY KEY (x, y)
);

INSERT INTO controlp(x,y,z)
  SELECT x, y,
         round(2 * cos(2 * (pi()/(10 - 1)) * x) * sin((pi()/(10 - 1)) * y)) AS z
  FROM   range(10) AS _(x),
         range(10) AS __(y);


-- INSERT INTO controlp(x,y,z) VALUES
--   (1, 1, 2),
--   (1, 2, 2),
--   (2, 1, 2),
--   (2, 2, 2);
