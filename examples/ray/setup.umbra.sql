DROP TABLE IF EXISTS triangles CASCADE;
CREATE TABLE triangles (
  id int PRIMARY KEY,
  material char(1),

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

DROP TABLE IF EXISTS spheres CASCADE;
CREATE TABLE spheres (
  id int PRIMARY KEY,
  material char(1),

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
