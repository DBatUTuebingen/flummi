.maxwidth 10000
.maxrows 10000

WITH RECURSIVE
  "%trampoline%"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
    (
      SELECT 'control', NULL :: bool, 'entry',
             (NULL) :: float AS "angle",
             (NULL) :: point AS "loc",
             (NULL) :: float AS "hhere",
             ((x1,10)) :: point AS "there",
             (16) :: int AS "resolution",
             (10) :: int AS "gridx",
             (NULL) :: float AS "max_angle",
             (NULL) :: point AS "step",
             (10) :: int AS "gridy",
             ((x2,0)) :: point AS "here",
             (NULL) :: int AS "i"
      FROM   range(16) AS __(i), LATERAL (SELECT (random() + 8 + i - i) :: int, (random() + 8 + i - i) :: int) AS _(x1, x2)
    )
      UNION ALL -- recursive union!
    (
      WITH
        "entry"("%kind%", "%result%", "%label%", "angle", "loc", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "angle",
                     "loc",
                     "hhere",
                     "there",
                     "resolution",
                     "gridx",
                     "max_angle",
                     "step",
                     "gridy",
                     "here",
                     "i"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'entry'
            )

          SELECT 'control', NULL, NULL,
                 "angle" AS "new%angle",
                 ("here") AS "new%loc",
                 "there" AS "new%there",
                 "resolution" AS "new%resolution",
                 ("gridx" - 1) AS "new%gridx",
                 (NULL :: float) AS "new%max_angle",
                 ((("there".x - "here".x) / "resolution", ("there".y - "here".y) / "resolution") :: point) AS "new%step",
                 ("gridy" - 1) AS "new%gridy",
                 "here" AS "new%here",
                 (1) AS "new%i"
          FROM   "%sources%"
        ),
        "inter0"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "angle", "loc", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "angle",
                     "loc",
                     "there",
                     "resolution",
                     "gridx",
                     "max_angle",
                     "step",
                     "gridy",
                     "here",
                     "i"
              FROM   "entry"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "angle" AS "new%angle",
                 "loc" AS "new%loc",
                 (SELECT SUM(("gridx"! / ((c.x!) * (("gridx" - c.x)!))) * (u ** c.x) * ((1 - u) ** ("gridx" - c.x)) *
                             ("gridy"! / ((c.y!) * (("gridy" - c.y)!))) * (v ** c.y) * ((1 - v) ** ("gridy" - c.y))) AS h
                  FROM   controlp AS c, LATERAL (SELECT "here".x / "gridx", "here".y / "gridy") AS _(u,v)) AS "new%hhere",
                 "there" AS "new%there",
                 "resolution" AS "new%resolution",
                 "gridx" AS "new%gridx",
                 "max_angle" AS "new%max_angle",
                 "step" AS "new%step",
                 "gridy" AS "new%gridy",
                 "here" AS "new%here",
                 "i" AS "new%i"
          FROM   "%sources%"
        ),
        "loop0_head"("%kind%", "%result%", "%label%", "angle", "max_angle", "loc", "hhere", "there", "resolution", "gridx", "step", "gridy", "here", "i", "condition%0") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "angle",
                     "loc",
                     "hhere",
                     "there",
                     "resolution",
                     "gridx",
                     "max_angle",
                     "step",
                     "gridy",
                     "here",
                     "i"
              FROM   "%trampoline%"
              WHERE  "%kind%" = 'control'
              AND    "%label%" = 'loop0_head'
            )

          SELECT 'control', NULL, NULL,
                 "angle" AS "new%angle",
                 "max_angle" AS "new%max_angle",
                 "loc" AS "new%loc",
                 "hhere" AS "new%hhere",
                 "there" AS "new%there",
                 "resolution" AS "new%resolution",
                 "gridx" AS "new%gridx",
                 "step" AS "new%step",
                 "gridy" AS "new%gridy",
                 "here" AS "new%here",
                 "i" AS "new%i",
                 ("i" > "resolution") AS "new%condition%0"
          FROM   "%sources%"
        ),
        "truthy0"("%kind%", "%result%", "%label%") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "angle", "max_angle") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "angle",
                     "max_angle"
              FROM   "loop0_head"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%0" IS DISTINCT FROM TRUE
            )

          SELECT 'data', ("angle" = "max_angle"), NULL
          FROM   "%sources%"
        ),
        "falsey0"("%kind%", "%result%", "%label%", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "loc",
                     "hhere",
                     "there",
                     "resolution",
                     "gridx",
                     "max_angle",
                     "step",
                     "gridy",
                     "here",
                     "i"
              FROM   "loop0_head"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT (NOT "condition%0" IS DISTINCT FROM TRUE)
            )

          SELECT 'control', NULL, NULL,
                 (("loc".x + "step".x, "loc".y + "step".y) :: point) AS "new%loc",
                 "hhere" AS "new%hhere",
                 "there" AS "new%there",
                 "resolution" AS "new%resolution",
                 "gridx" AS "new%gridx",
                 "max_angle" AS "new%max_angle",
                 "step" AS "new%step",
                 "gridy" AS "new%gridy",
                 "here" AS "new%here",
                 ("i" + 1) AS "new%i"
          FROM   "%sources%"
        ),
        "inter8"("%kind%", "%result%", "%label%", "hhere", "loc", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i", "hloc") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "loc",
                     "hhere",
                     "there",
                     "resolution",
                     "gridx",
                     "max_angle",
                     "step",
                     "gridy",
                     "here",
                     "i"
              FROM   "falsey0"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "hhere" AS "new%hhere",
                 "loc" AS "new%loc",
                 "there" AS "new%there",
                 "resolution" AS "new%resolution",
                 "gridx" AS "new%gridx",
                 "max_angle" AS "new%max_angle",
                 "step" AS "new%step",
                 "gridy" AS "new%gridy",
                 "here" AS "new%here",
                 "i" AS "new%i",
                 (SELECT SUM(("gridx"! / ((c.x!) * (("gridx" - c.x)!))) * (u ** c.x) * ((1 - u) ** ("gridx" - c.x)) *
                             ("gridy"! / ((c.y!) * (("gridy" - c.y)!))) * (v ** c.y) * ((1 - v) ** ("gridy" - c.y))) AS h
                  FROM   controlp AS c, LATERAL (SELECT "loc".x / "gridx", "loc".y / "gridy") AS _(u,v)) AS "new%hloc"
          FROM   "%sources%"
        ),
        "inter9"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "hhere", "loc", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i", "hloc") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "hhere",
                     "loc",
                     "there",
                     "resolution",
                     "gridx",
                     "max_angle",
                     "step",
                     "gridy",
                     "here",
                     "i",
                     "hloc"
              FROM   "inter8"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 (degrees(atan(("hloc" - "hhere") / sqrt(("loc".x - "here".x)** 2 + ("loc".y - "here".y)** 2)))) AS "new%angle",
                 "loc" AS "new%loc",
                 "hhere" AS "new%hhere",
                 "there" AS "new%there",
                 "resolution" AS "new%resolution",
                 "gridx" AS "new%gridx",
                 "max_angle" AS "new%max_angle",
                 "step" AS "new%step",
                 "gridy" AS "new%gridy",
                 "here" AS "new%here",
                 "i" AS "new%i"
          FROM   "%sources%"
        ),
        "inter10"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "step", "gridy", "here", "i", "max_angle", "condition%1") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "angle",
                     "loc",
                     "hhere",
                     "there",
                     "resolution",
                     "gridx",
                     "max_angle",
                     "step",
                     "gridy",
                     "here",
                     "i"
              FROM   "inter9"
              WHERE  "%kind%" = 'control'
            )

          SELECT 'control', NULL, NULL,
                 "angle" AS "new%angle",
                 "loc" AS "new%loc",
                 "hhere" AS "new%hhere",
                 "there" AS "new%there",
                 "resolution" AS "new%resolution",
                 "gridx" AS "new%gridx",
                 "step" AS "new%step",
                 "gridy" AS "new%gridy",
                 "here" AS "new%here",
                 "i" AS "new%i",
                 "max_angle" AS "new%max_angle",
                 ("max_angle" IS NULL OR "angle" > "max_angle") AS "new%condition%1"
          FROM   "%sources%"
        ),
        "truthy1"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i") AS (
          WITH
            "%sources%"("%kind%", "%result%", "%label%", "angle", "loc", "hhere", "there", "resolution", "gridx", "step", "gridy", "here", "i") AS (
              SELECT "%kind%", "%result%", "%label%",
                     "angle",
                     "loc",
                     "hhere",
                     "there",
                     "resolution",
                     "gridx",
                     "step",
                     "gridy",
                     "here",
                     "i"
              FROM   "inter10"
              WHERE  "%kind%" = 'control'
              AND    TRUE AND NOT "condition%1" IS DISTINCT FROM TRUE
            )

          SELECT 'control', NULL, NULL,
                 "angle" AS "new%angle",
                 "loc" AS "new%loc",
                 "hhere" AS "new%hhere",
                 "there" AS "new%there",
                 "resolution" AS "new%resolution",
                 "gridx" AS "new%gridx",
                 ("angle") AS "new%max_angle",
                 "step" AS "new%step",
                 "gridy" AS "new%gridy",
                 "here" AS "new%here",
                 "i" AS "new%i"
          FROM   "%sources%"
        )

      -- jumps
      SELECT 'control', NULL, 'loop0_head', "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i"
      FROM   "inter0"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      SELECT 'control', NULL, 'loop0_head', "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i"
      FROM   "inter10"
      WHERE  "%kind%" = 'control'
      AND    TRUE AND NOT (NOT "condition%1" IS DISTINCT FROM TRUE)
        UNION ALL
      SELECT 'control', NULL, 'loop0_head', "angle", "loc", "hhere", "there", "resolution", "gridx", "max_angle", "step", "gridy", "here", "i"
      FROM   "truthy1"
      WHERE  "%kind%" = 'control'
      AND    TRUE
        UNION ALL
      -- emits
      SELECT "%kind%", "%result%", "%label%", NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
      FROM   "truthy0"
      WHERE  "%kind%" = 'data'
    )
  )

SELECT * FROM "%trampoline%" LIMIT 500;

-- SELECT "%result%" FROM "%trampoline%" WHERE "%kind%" = 'data';
