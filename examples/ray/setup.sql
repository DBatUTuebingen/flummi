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
