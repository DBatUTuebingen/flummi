DROP SCHEMA IF EXISTS vec CASCADE;
CREATE SCHEMA vec;
CREATE MACRO vec.make(x, y, z) AS (x, y, z) :: struct(x real, y real, z real);
CREATE MACRO vec.add(a, b) AS vec.make(a.x + b.x, a.y + b.y, a.z + b.z);
CREATE MACRO vec.sub(a, b) AS vec.make(a.x - b.x, a.y - b.y, a.z - b.z);
CREATE MACRO vec.mul(v, f) AS vec.make(v.x * f, v.y * f, v.z * f);
CREATE MACRO vec.div(v, f) AS vec.make(v.x / f, v.y / f, v.z / f);
CREATE MACRO vec.dot(a, b) AS a.x * b.x + a.y * b.y + a.z * b.z;
CREATE MACRO vec.cross(a, b) AS vec.make(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x);
CREATE MACRO vec.mag(v) AS sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2);
CREATE MACRO vec.norm(v) AS vec.div(v, vec.mag(v));

DROP TYPE IF EXISTS material CASCADE;
CREATE TYPE material AS ENUM ('m', 'r', 'l', 'n');

DROP TYPE IF EXISTS triangle CASCADE;
CREATE TYPE triangle AS struct(
  id int,
  material material,

  r real,
  g real,
  b real,

  p1_x real,
  p1_y real,
  p1_z real,

  p2_x real,
  p2_y real,
  p2_z real,

  p3_x real,
  p3_y real,
  p3_z real
);

DROP TABLE IF EXISTS triangles CASCADE;
CREATE TABLE triangles (
  id int PRIMARY KEY,
  material material,

  r real,
  g real,
  b real,

  p1_x real,
  p1_y real,
  p1_z real,

  p2_x real,
  p2_y real,
  p2_z real,

  p3_x real,
  p3_y real,
  p3_z real
);

INSERT INTO triangles VALUES
  (0, 'm', 0.6 , 0.6, 0.6 ,  -10.0,  -1.0,-10.0,  10.0,  -1.0,-10.0,  0.0,-1.0,  5.0),
  (1, 'm', 0.6 , 0.6, 0.6 ,  -10.0,   1.0,-10.0,  10.0,   1.0,-10.0,  0.0, 1.0,  5.0),
  (2, 'm', 0.85, 0.5, 0.0 ,   -1.0, -10.0,-10.0,  -1.0,  10.0,-10.0, -1.0, 0.0,  5.0),
  (3, 'm', 0.2 , 0.6, 0.75,    1.0, -10.0,-10.0,   1.0,  10.0,-10.0,  1.0, 0.0,  5.0),
  (4, 'm', 0.6 , 0.6, 0.6 ,  -10.0, -10.0,  1.0,  10.0, -10.0,  1.0,  0.0, 5.0,  1.0),
  (5, 'm', 0.6 , 0.6, 0.6 , -100.0,-100.0,-10.0, 100.0,-100.0,-10.0,  0.0,50.0,-10.0);

DROP TYPE IF EXISTS sphere CASCADE;
CREATE TYPE sphere AS struct(
  id int,
  material material,

  r real,
  g real,
  b real,

  center_x real,
  center_y real,
  center_z real,

  radius real
);

DROP TABLE IF EXISTS spheres CASCADE;
CREATE TABLE spheres (
  id int PRIMARY KEY,
  material material,

  r real,
  g real,
  b real,

  center_x real,
  center_y real,
  center_z real,

  radius real
);

INSERT INTO spheres VALUES
  (0, 'r', NULL, NULL, NULL, -0.5,-0.6,  0.3, 0.40),
  (1, 'r', NULL, NULL, NULL,  0.4,-0.6, -0.6, 0.40),
  (2, 'm', 0.2 , 0.8 , 0.2 ,  1.0, 0.0,  0.5, 0.25),
  (3, 'l', NULL, NULL, NULL,  0.0, 0.95, 0.0, 0.35);


DROP TABLE IF EXISTS "init";
CREATE TABLE "init" (
  "index" int not null,
  x int not null,
  y int not null,
  origin_x real not null,
  origin_y real not null,
  origin_z real not null,
  direction_x real not null,
  direction_y real not null,
  direction_z real not null
);

INSERT INTO "init"
  SELECT  ROW_NUMBER() OVER () AS "index",
          (x) :: int AS "x",
          (y) :: int AS "y",
          (0.0) :: double AS "origin_x",
          (0.0) :: double AS "origin_y",
          (-4.5) :: double AS "origin_z",
          (direction.x) :: double AS "direction_x",
          (direction.y) :: double AS "direction_y",
          (direction.z) :: double AS "direction_z"
  FROM    (SELECT $width         AS width,
                  $height         AS height,
                  radians(50) AS fov
          ) AS "constants"(width,height,fov),
  LATERAL (SELECT vec.sub(
                    vec.make(0.0, 0.0,  0.0), -- looking at
                    vec.make(0.0, 0.0, -4.5)  -- camera position
                  ) AS rot_z,
                  vec.cross(
                    vec.make(0.0,-1.0,  0.0), -- up vector
                    rot_z
                  ) AS rot_x,
                  vec.cross(rot_z, rot_x)  AS rot_y
          ) AS "camera rotation"(rot_z, rot_x, rot_y),
  LATERAL (SELECT unnest(range(width ))) AS "xs"("x"),
  LATERAL (SELECT unnest(range(height))) AS "ys"("y"),
  LATERAL (SELECT sin((((x + 0.5) / width ) - 0.5) * fov * (width / height))) AS "_x"("offset_x"),
  LATERAL (SELECT sin((((y + 0.5) / height) - 0.5) * fov                   )) AS "_y"("offset_y"),
  LATERAL (SELECT vec.add(
                    vec.add(
                      vec.mul(
                        vec.norm(rot_x),
                        offset_x
                      ),
                      vec.mul(
                        vec.norm(rot_y),
                        offset_y
                      )
                    ),
                    vec.norm(rot_z)
                  ) AS "direction"
          ) AS "transient";
