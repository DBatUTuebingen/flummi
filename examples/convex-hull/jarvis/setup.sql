CREATE TYPE point AS struct("x" DOUBLE, "y" DOUBLE);

CREATE MACRO left_of(p, p1, p2) AS (
  ((p1)."x" - (p)."x") * ((p2)."y" - (p)."y") - ((p1)."y" - (p)."y") * ((p2)."x" - (p)."x") > 0
);

-- point set S
DROP TABLE IF EXISTS points;
CREATE TABLE points (
  label text PRIMARY KEY,
  loc   point
);

INSERT INTO points(label, loc) VALUES
  ('p₀', (1,3) :: point),
  ('p₁', (2,7) :: point),
  ('p₂', (4,1) :: point),
  ('p₃', (4,6) :: point),
  ('p₄', (5,4) :: point),
  ('p₅', (5,8) :: point),
  ('p₆', (8,6) :: point),
  ('p₇', (9,2) :: point),
  ('p₈', (9,7) :: point);

-- 10 ┤
--    │
--    │        p₅
--    │  p₁            p₈
--    │      p₃      p₆
--  5 ┤
--    │        p₄
--    │p₀
--    │                p₇
--    │      p₂
--  0 ┼─────────┬─────────┬
--    0         5        10

-- INSERT INTO points(label, loc)
--   SELECT 'p' || i :: text, (random() * 1024, random() * 1024) :: point
--   FROM   generate_series(1, 2048) AS _(i);
