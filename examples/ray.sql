WITH RECURSIVE
  "%loop%"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
    (SELECT 'jump' AS "%kind%",
            'entry' AS "%label%",
            CAST(NULL AS real) AS "color_b",
            CAST(NULL AS real) AS "color_g",
            CAST(NULL AS real) AS "color_r",
            CAST((direction.x) AS real) AS "direction_x",
            CAST((direction.y) AS real) AS "direction_y",
            CAST((direction.z) AS real) AS "direction_z",
            CAST((0.000001) AS real) AS "epsilon",
            CAST(NULL AS int) AS "id",
            CAST(NULL AS real) AS "light_x",
            CAST(NULL AS real) AS "light_y",
            CAST(NULL AS real) AS "light_z",
            CAST(NULL AS material) AS "material",
            CAST((10) AS int) AS "max_rec_depth",
            CAST(NULL AS real) AS "min_dist",
            CAST(NULL AS real) AS "normal_x",
            CAST(NULL AS real) AS "normal_y",
            CAST(NULL AS real) AS "normal_z",
            CAST((cam.x) AS real) AS "origin_x",
            CAST((cam.y) AS real) AS "origin_y",
            CAST((cam.z) AS real) AS "origin_z",
            CAST(NULL AS real) AS "pixel_b",
            CAST(NULL AS real) AS "pixel_g",
            CAST(NULL AS real) AS "pixel_r",
            CAST(NULL AS bool) AS "shadow_ray",
            CAST((true) AS bool) AS "shadows",
            CAST(NULL AS int) AS "step",
            CAST((x) AS int) AS "x",
            CAST((y) AS int) AS "y",
            CAST(NULL AS struct(x int, y int, r real, g real, b real)) AS "%result%")
      UNION ALL -- recursive union!
    (WITH
      "%loop%"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        SELECT * FROM "%loop%"
      ),
      "entry"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "%loop%"
            WHERE  "%kind%"='jump'
            AND    "%label%"='entry'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((SELECT s FROM spheres AS s WHERE material = 'l') AS sphere) AS "light",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((0) AS real) AS "pixel_b",
                   CAST((0) AS real) AS "pixel_g",
                   CAST((0) AS real) AS "pixel_r",
                   CAST((false) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((0) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter0', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter0"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "entry"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter0'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light").center_x) AS real) AS "light_x",
                   CAST((("%inputs%"."light").center_y) AS real) AS "light_y",
                   CAST((("%inputs%"."light").center_z) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'ray_loop_head', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "ray_loop_head"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "%loop%"
            WHERE  "%kind%"='jump'
            AND    "%label%"='ray_loop_head'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter0"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_head'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((SELECT MAX(t.id) FROM triangles AS t) AS int) AS "id",
                   CAST((sqrt(("%inputs%"."direction_x") ** 2 + ("%inputs%"."direction_y") ** 2 + ("%inputs%"."direction_z") ** 2)) AS real) AS "length",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST(('n') AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST(('Infinity' :: real) AS real) AS "min_dist",
                   CAST((0) AS real) AS "normal_x",
                   CAST((0) AS real) AS "normal_y",
                   CAST((0) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter9', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter9"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "ray_loop_head"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter9'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x") / ("%inputs%"."length")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y") / ("%inputs%"."length")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z") / ("%inputs%"."length")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'triangle_loop_head', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "triangle_loop_head"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "%loop%"
            WHERE  "%kind%"='jump'
            AND    "%label%"='triangle_loop_head'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter9"
            WHERE  "%kind%"='goto'
            AND    "%label%"='triangle_loop_head'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((SELECT t FROM triangles AS t WHERE t.id = ("%inputs%"."id")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter19', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter19"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "triangle_loop_head"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter19'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."triangle").p2_x - ("%inputs%"."triangle").p1_x) AS real) AS "e1_x",
                   CAST((("%inputs%"."triangle").p2_y - ("%inputs%"."triangle").p1_y) AS real) AS "e1_y",
                   CAST((("%inputs%"."triangle").p2_z - ("%inputs%"."triangle").p1_z) AS real) AS "e1_z",
                   CAST((("%inputs%"."triangle").p3_x - ("%inputs%"."triangle").p1_x) AS real) AS "e2_x",
                   CAST((("%inputs%"."triangle").p3_y - ("%inputs%"."triangle").p1_y) AS real) AS "e2_y",
                   CAST((("%inputs%"."triangle").p3_z - ("%inputs%"."triangle").p1_z) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter20', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter20"("%kind%", "%label%", "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter19"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter20'
          ),
          "%assign%"("P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."direction_y") * ("%inputs%"."e2_z") - ("%inputs%"."direction_z") * ("%inputs%"."e2_y")) AS real) AS "P_x",
                   CAST((("%inputs%"."direction_z") * ("%inputs%"."e2_x") - ("%inputs%"."direction_x") * ("%inputs%"."e2_z")) AS real) AS "P_y",
                   CAST((("%inputs%"."direction_x") * ("%inputs%"."e2_y") - ("%inputs%"."direction_y") * ("%inputs%"."e2_x")) AS real) AS "P_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter21', "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter21"("%kind%", "%label%", "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter20"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter21'
          ),
          "%assign%"("P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."P_x")) AS real) AS "P_x",
                   CAST((("%inputs%"."P_y")) AS real) AS "P_y",
                   CAST((("%inputs%"."P_z")) AS real) AS "P_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."e1_x") * ("%inputs%"."P_x") + ("%inputs%"."e1_y") * ("%inputs%"."P_y") + ("%inputs%"."e1_z") * ("%inputs%"."P_z")) AS real) AS "det",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter29', "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter29"("%kind%", "%label%", "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter21"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter29'
          ),
          "%assign%"("P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "condition%0", "condition%1") AS (
            SELECT CAST((("%inputs%"."P_x")) AS real) AS "P_x",
                   CAST((("%inputs%"."P_y")) AS real) AS "P_y",
                   CAST((("%inputs%"."P_z")) AS real) AS "P_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."det")) AS real) AS "det",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((abs(("%inputs%"."det")) <= ("%inputs%"."epsilon")) AS bool) AS "condition%0",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%1"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey0', "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%0"
          UNION ALL
        SELECT 'goto', 'falsey6', "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%0" AND NOT "condition%1"
          UNION ALL
        SELECT 'goto', 'truthy6', "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%0" AND "condition%1"
      ),
      "falsey0"("%kind%", "%label%", "P_x", "P_y", "P_z", "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "P_x", "P_y", "P_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter29"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey0'
          ),
          "%assign%"("P_x", "P_y", "P_z", "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."P_x")) AS real) AS "P_x",
                   CAST((("%inputs%"."P_y")) AS real) AS "P_y",
                   CAST((("%inputs%"."P_z")) AS real) AS "P_z",
                   CAST((("%inputs%"."origin_x") - ("%inputs%"."triangle").p1_x) AS real) AS "T1_x",
                   CAST((("%inputs%"."origin_y") - ("%inputs%"."triangle").p1_y) AS real) AS "T1_y",
                   CAST((("%inputs%"."origin_z") - ("%inputs%"."triangle").p1_z) AS real) AS "T1_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."det")) AS real) AS "det",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter30', "P_x", "P_y", "P_z", "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter30"("%kind%", "%label%", "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("P_x", "P_y", "P_z", "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "P_x", "P_y", "P_z", "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "falsey0"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter30'
          ),
          "%assign%"("T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y") AS (
            SELECT CAST((("%inputs%"."T1_x")) AS real) AS "T1_x",
                   CAST((("%inputs%"."T1_y")) AS real) AS "T1_y",
                   CAST((("%inputs%"."T1_z")) AS real) AS "T1_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."det")) AS real) AS "det",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST(((("%inputs%"."T1_x") * ("%inputs%"."P_x") + ("%inputs%"."T1_y") * ("%inputs%"."P_y") + ("%inputs%"."T1_z") * ("%inputs%"."P_z")) / ("%inputs%"."det")) AS real) AS "u",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter32', "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter32"("%kind%", "%label%", "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y") AS (
            SELECT "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y"
            FROM   "inter30"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter32'
          ),
          "%assign%"("T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", "condition%2", "condition%3") AS (
            SELECT CAST((("%inputs%"."T1_x")) AS real) AS "T1_x",
                   CAST((("%inputs%"."T1_y")) AS real) AS "T1_y",
                   CAST((("%inputs%"."T1_z")) AS real) AS "T1_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."det")) AS real) AS "det",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."u")) AS real) AS "u",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."u") NOT BETWEEN 0 AND 1) AS bool) AS "condition%2",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%3"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey1', "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%2"
          UNION ALL
        SELECT 'goto', 'falsey6', "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%2" AND NOT "condition%3"
          UNION ALL
        SELECT 'goto', 'truthy6', "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%2" AND "condition%3"
      ),
      "falsey1"("%kind%", "%label%", "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y") AS (
            SELECT "T1_x", "T1_y", "T1_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y"
            FROM   "inter32"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey1'
          ),
          "%assign%"("Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y") AS (
            SELECT CAST((("%inputs%"."T1_y") * ("%inputs%"."e1_z") - ("%inputs%"."T1_z") * ("%inputs%"."e1_y")) AS real) AS "Q_x",
                   CAST((("%inputs%"."T1_z") * ("%inputs%"."e1_x") - ("%inputs%"."T1_x") * ("%inputs%"."e1_z")) AS real) AS "Q_y",
                   CAST((("%inputs%"."T1_x") * ("%inputs%"."e1_y") - ("%inputs%"."T1_y") * ("%inputs%"."e1_x")) AS real) AS "Q_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."det")) AS real) AS "det",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."u")) AS real) AS "u",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter34', "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter34"("%kind%", "%label%", "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "v", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y") AS (
            SELECT "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "x", "y"
            FROM   "falsey1"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter34'
          ),
          "%assign%"("Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "v", "x", "y") AS (
            SELECT CAST((("%inputs%"."Q_x")) AS real) AS "Q_x",
                   CAST((("%inputs%"."Q_y")) AS real) AS "Q_y",
                   CAST((("%inputs%"."Q_z")) AS real) AS "Q_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."det")) AS real) AS "det",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."u")) AS real) AS "u",
                   CAST(((("%inputs%"."direction_x") * ("%inputs%"."Q_x") + ("%inputs%"."direction_y") * ("%inputs%"."Q_y") + ("%inputs%"."direction_z") * ("%inputs%"."Q_z")) / ("%inputs%"."det")) AS real) AS "v",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter36', "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "v", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter36"("%kind%", "%label%", "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "v", "x", "y") AS (
            SELECT "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "u", "v", "x", "y"
            FROM   "inter34"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter36'
          ),
          "%assign%"("Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "condition%4", "condition%5") AS (
            SELECT CAST((("%inputs%"."Q_x")) AS real) AS "Q_x",
                   CAST((("%inputs%"."Q_y")) AS real) AS "Q_y",
                   CAST((("%inputs%"."Q_z")) AS real) AS "Q_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."det")) AS real) AS "det",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((0 > ("%inputs%"."v") OR ("%inputs%"."v") + ("%inputs%"."u") > 1) AS bool) AS "condition%4",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%5"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey2', "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%4"
          UNION ALL
        SELECT 'goto', 'falsey6', "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%4" AND NOT "condition%5"
          UNION ALL
        SELECT 'goto', 'truthy6', "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%4" AND "condition%5"
      ),
      "falsey2"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "det", "direction_x", "direction_y", "direction_z", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter36"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey2'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST(((("%inputs%"."e2_x") * ("%inputs%"."Q_x") + ("%inputs%"."e2_y") * ("%inputs%"."Q_y") + ("%inputs%"."e2_z") * ("%inputs%"."Q_z")) / ("%inputs%"."det")) AS real) AS "dist",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter38', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter38"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "falsey2"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter38'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "condition%6", "condition%7") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."dist")) AS real) AS "dist",
                   CAST((("%inputs%"."e1_x")) AS real) AS "e1_x",
                   CAST((("%inputs%"."e1_y")) AS real) AS "e1_y",
                   CAST((("%inputs%"."e1_z")) AS real) AS "e1_z",
                   CAST((("%inputs%"."e2_x")) AS real) AS "e2_x",
                   CAST((("%inputs%"."e2_y")) AS real) AS "e2_y",
                   CAST((("%inputs%"."e2_z")) AS real) AS "e2_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."dist") <= ("%inputs%"."epsilon") OR ("%inputs%"."dist") >= ("%inputs%"."min_dist")) AS bool) AS "condition%6",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%7"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey3', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%6"
          UNION ALL
        SELECT 'goto', 'falsey6', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%6" AND NOT "condition%7"
          UNION ALL
        SELECT 'goto', 'truthy6', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%6" AND "condition%7"
      ),
      "falsey3"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "max_rec_depth", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "e1_x", "e1_y", "e1_z", "e2_x", "e2_y", "e2_z", "epsilon", "id", "light_x", "light_y", "light_z", "max_rec_depth", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter38"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey3'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."triangle").material) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."e2_y") * ("%inputs%"."e1_z") - ("%inputs%"."e2_z") * ("%inputs%"."e1_y")) AS real) AS "normal_x",
                   CAST((("%inputs%"."e2_z") * ("%inputs%"."e1_x") - ("%inputs%"."e2_x") * ("%inputs%"."e1_z")) AS real) AS "normal_y",
                   CAST((("%inputs%"."e2_x") * ("%inputs%"."e1_y") - ("%inputs%"."e2_y") * ("%inputs%"."e1_x")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter39', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter39"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "falsey3"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter39'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((sqrt(("%inputs%"."normal_x") ** 2 + ("%inputs%"."normal_y") ** 2 + ("%inputs%"."normal_z") ** 2)) AS real) AS "length",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter40', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter40"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter39"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter40'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x") / ("%inputs%"."length")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y") / ("%inputs%"."length")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z") / ("%inputs%"."length")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter44', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter44"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter40"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter44'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "condition%8", "condition%9", "condition%10") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."normal_x") * ("%inputs%"."direction_x") + ("%inputs%"."normal_y") * ("%inputs%"."direction_y") + ("%inputs%"."normal_z") * ("%inputs%"."direction_z") > 0) AS bool) AS "condition%8",
                   CAST((("%inputs%"."material") = 'm') AS bool) AS "condition%9",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%10"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey6', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%8" AND NOT "condition%9" AND NOT "condition%10"
          UNION ALL
        SELECT 'goto', 'truthy4', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%8"
          UNION ALL
        SELECT 'goto', 'truthy5', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%8" AND "condition%9"
          UNION ALL
        SELECT 'goto', 'truthy6', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%8" AND NOT "condition%9" AND "condition%10"
      ),
      "truthy4"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter44"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy4'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", "condition%11", "condition%12") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x") * -1) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y") * -1) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z") * -1) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."triangle")) AS triangle) AS "triangle",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."material") = 'm') AS bool) AS "condition%11",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%12"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey6', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%11" AND NOT "condition%12"
          UNION ALL
        SELECT 'goto', 'truthy5', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%11"
          UNION ALL
        SELECT 'goto', 'truthy6', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%11" AND "condition%12"
      ),
      "truthy5"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y") AS (
            SELECT "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "truthy4"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy5'
              UNION ALL
            SELECT "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "triangle", "x", "y"
            FROM   "inter44"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy5'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "condition%13") AS (
            SELECT CAST((("%inputs%"."triangle").b) AS real) AS "color_b",
                   CAST((("%inputs%"."triangle").g) AS real) AS "color_g",
                   CAST((("%inputs%"."triangle").r) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%13"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey6', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%13"
          UNION ALL
        SELECT 'goto', 'truthy6', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%13"
      ),
      "truthy6"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter32"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter36"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter44"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter38"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter29"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "truthy4"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "truthy5"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy6'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((SELECT MAX(s.id) FROM spheres AS s) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'sphere_loop_head', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "sphere_loop_head"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "%loop%"
            WHERE  "%kind%"='jump'
            AND    "%label%"='sphere_loop_head'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "truthy6"
            WHERE  "%kind%"='goto'
            AND    "%label%"='sphere_loop_head'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((SELECT t FROM spheres AS t WHERE t.id = ("%inputs%"."id")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter57', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter57"("%kind%", "%label%", "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "sphere_loop_head"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter57'
          ),
          "%assign%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."sphere").center_x - ("%inputs%"."origin_x")) AS real) AS "L_x",
                   CAST((("%inputs%"."sphere").center_y - ("%inputs%"."origin_y")) AS real) AS "L_y",
                   CAST((("%inputs%"."sphere").center_z - ("%inputs%"."origin_z")) AS real) AS "L_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter58', "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter58"("%kind%", "%label%", "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "inter57"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter58'
          ),
          "%assign%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y") AS (
            SELECT CAST((("%inputs%"."L_x")) AS real) AS "L_x",
                   CAST((("%inputs%"."L_y")) AS real) AS "L_y",
                   CAST((("%inputs%"."L_z")) AS real) AS "L_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."L_x") * ("%inputs%"."direction_x") + ("%inputs%"."L_y") * ("%inputs%"."direction_y") + ("%inputs%"."L_z") * ("%inputs%"."direction_z")) AS real) AS "tca",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter59', "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter59"("%kind%", "%label%", "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y") AS (
            SELECT "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y"
            FROM   "inter58"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter59'
          ),
          "%assign%"("color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."L_x") ** 2 + ("%inputs%"."L_y") ** 2 + ("%inputs%"."L_z") ** 2 - ("%inputs%"."tca") ** 2) AS real) AS "d2",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."tca")) AS real) AS "tca",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter61', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter61"("%kind%", "%label%", "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y"
            FROM   "inter59"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter61'
          ),
          "%assign%"("color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", "condition%14", "condition%15", "condition%16", "condition%17", "condition%18", "condition%19", "condition%20") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."d2")) AS real) AS "d2",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."tca")) AS real) AS "tca",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."d2") > ("%inputs%"."sphere").radius ** 2) AS bool) AS "condition%14",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%15",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "condition%16",
                   CAST((("%inputs%"."material") <> 'l') AS bool) AS "condition%17",
                   CAST((("%inputs%"."material") = 'l') AS bool) AS "condition%18",
                   CAST((("%inputs%"."material") = 'm') AS bool) AS "condition%19",
                   CAST((("%inputs%"."material") = 'r') AS bool) AS "condition%20"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey10', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%14" AND NOT "condition%15"
          UNION ALL
        SELECT 'goto', 'falsey7', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%14"
          UNION ALL
        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%14" AND "condition%15" AND "condition%16" AND NOT "condition%17"
          UNION ALL
        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%14" AND "condition%15" AND NOT "condition%16" AND NOT "condition%18" AND NOT "condition%19" AND NOT "condition%20"
          UNION ALL
        SELECT 'goto', 'truthy12', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%14" AND "condition%15" AND "condition%16" AND "condition%17"
          UNION ALL
        SELECT 'goto', 'truthy13', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%14" AND "condition%15" AND NOT "condition%16" AND "condition%18"
          UNION ALL
        SELECT 'goto', 'truthy14', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%14" AND "condition%15" AND NOT "condition%16" AND NOT "condition%18" AND "condition%19"
          UNION ALL
        SELECT 'goto', 'truthy16', "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%14" AND "condition%15" AND NOT "condition%16" AND NOT "condition%18" AND NOT "condition%19" AND "condition%20"
      ),
      "falsey7"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "thc", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "d2", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "x", "y"
            FROM   "inter61"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey7'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "thc", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."tca")) AS real) AS "tca",
                   CAST((sqrt(("%inputs%"."sphere").radius ** 2 - ("%inputs%"."d2"))) AS real) AS "thc",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter63', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "thc", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter63"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "thc", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "tca", "thc", "x", "y"
            FROM   "falsey7"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter63'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((least(("%inputs%"."tca") + ("%inputs%"."thc"), greatest(("%inputs%"."tca") - ("%inputs%"."thc"), 0))) AS real) AS "dist",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter64', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter64"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "inter63"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter64'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "condition%21", "condition%22", "condition%23", "condition%24", "condition%25", "condition%26", "condition%27") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."dist")) AS real) AS "dist",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."dist") NOT BETWEEN ("%inputs%"."epsilon") AND ("%inputs%"."min_dist")) AS bool) AS "condition%21",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%22",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "condition%23",
                   CAST((("%inputs%"."material") <> 'l') AS bool) AS "condition%24",
                   CAST((("%inputs%"."material") = 'l') AS bool) AS "condition%25",
                   CAST((("%inputs%"."material") = 'm') AS bool) AS "condition%26",
                   CAST((("%inputs%"."material") = 'r') AS bool) AS "condition%27"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey10', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%21" AND NOT "condition%22"
          UNION ALL
        SELECT 'goto', 'falsey8', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%21"
          UNION ALL
        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%21" AND "condition%22" AND "condition%23" AND NOT "condition%24"
          UNION ALL
        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%21" AND "condition%22" AND NOT "condition%23" AND NOT "condition%25" AND NOT "condition%26" AND NOT "condition%27"
          UNION ALL
        SELECT 'goto', 'truthy12', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%21" AND "condition%22" AND "condition%23" AND "condition%24"
          UNION ALL
        SELECT 'goto', 'truthy13', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%21" AND "condition%22" AND NOT "condition%23" AND "condition%25"
          UNION ALL
        SELECT 'goto', 'truthy14', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%21" AND "condition%22" AND NOT "condition%23" AND NOT "condition%25" AND "condition%26"
          UNION ALL
        SELECT 'goto', 'truthy16', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%21" AND "condition%22" AND NOT "condition%23" AND NOT "condition%25" AND NOT "condition%26" AND "condition%27"
      ),
      "falsey8"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "max_rec_depth", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "dist", "epsilon", "id", "light_x", "light_y", "light_z", "max_rec_depth", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "inter64"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey8'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."sphere").material) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."direction_x") * ("%inputs%"."dist")) AS real) AS "normal_x",
                   CAST((("%inputs%"."direction_y") * ("%inputs%"."dist")) AS real) AS "normal_y",
                   CAST((("%inputs%"."direction_z") * ("%inputs%"."dist")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter65', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter65"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "falsey8"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter65'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x") - ("%inputs%"."sphere").center_x) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y") - ("%inputs%"."sphere").center_y) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z") - ("%inputs%"."sphere").center_z) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter66', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter66"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "inter65"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter66'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x") + ("%inputs%"."origin_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y") + ("%inputs%"."origin_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z") + ("%inputs%"."origin_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter67', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter67"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "inter66"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter67'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((sqrt(("%inputs%"."normal_x") ** 2 + ("%inputs%"."normal_y") ** 2 + ("%inputs%"."normal_z") ** 2)) AS real) AS "length",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter68', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter68"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "inter67"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter68'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", "condition%28", "condition%29", "condition%30", "condition%31", "condition%32", "condition%33", "condition%34") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x") / ("%inputs%"."length")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y") / ("%inputs%"."length")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z") / ("%inputs%"."length")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."sphere")) AS sphere) AS "sphere",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."material") = 'm') AS bool) AS "condition%28",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%29",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "condition%30",
                   CAST((("%inputs%"."material") <> 'l') AS bool) AS "condition%31",
                   CAST((("%inputs%"."material") = 'l') AS bool) AS "condition%32",
                   CAST((("%inputs%"."material") = 'm') AS bool) AS "condition%33",
                   CAST((("%inputs%"."material") = 'r') AS bool) AS "condition%34"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey10', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%28" AND NOT "condition%29"
          UNION ALL
        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%28" AND "condition%29" AND "condition%30" AND NOT "condition%31"
          UNION ALL
        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%28" AND "condition%29" AND NOT "condition%30" AND NOT "condition%32" AND NOT "condition%33" AND NOT "condition%34"
          UNION ALL
        SELECT 'goto', 'truthy12', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%28" AND "condition%29" AND "condition%30" AND "condition%31"
          UNION ALL
        SELECT 'goto', 'truthy13', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%28" AND "condition%29" AND NOT "condition%30" AND "condition%32"
          UNION ALL
        SELECT 'goto', 'truthy14', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%28" AND "condition%29" AND NOT "condition%30" AND NOT "condition%32" AND "condition%33"
          UNION ALL
        SELECT 'goto', 'truthy16', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%28" AND "condition%29" AND NOT "condition%30" AND NOT "condition%32" AND NOT "condition%33" AND "condition%34"
          UNION ALL
        SELECT 'goto', 'truthy9', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%28"
      ),
      "truthy9"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y") AS (
            SELECT "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "sphere", "step", "x", "y"
            FROM   "inter68"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy9'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "condition%35", "condition%36", "condition%37", "condition%38", "condition%39", "condition%40") AS (
            SELECT CAST((("%inputs%"."sphere").b) AS real) AS "color_b",
                   CAST((("%inputs%"."sphere").g) AS real) AS "color_g",
                   CAST((("%inputs%"."sphere").r) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."id") = 0) AS bool) AS "condition%35",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "condition%36",
                   CAST((("%inputs%"."material") <> 'l') AS bool) AS "condition%37",
                   CAST((("%inputs%"."material") = 'l') AS bool) AS "condition%38",
                   CAST((("%inputs%"."material") = 'm') AS bool) AS "condition%39",
                   CAST((("%inputs%"."material") = 'r') AS bool) AS "condition%40"
            FROM "%inputs%"
          )

        SELECT 'goto', 'falsey10', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%35"
          UNION ALL
        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%35" AND "condition%36" AND NOT "condition%37"
          UNION ALL
        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%35" AND NOT "condition%36" AND NOT "condition%38" AND NOT "condition%39" AND NOT "condition%40"
          UNION ALL
        SELECT 'goto', 'truthy12', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%35" AND "condition%36" AND "condition%37"
          UNION ALL
        SELECT 'goto', 'truthy13', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%35" AND NOT "condition%36" AND "condition%38"
          UNION ALL
        SELECT 'goto', 'truthy14', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%35" AND NOT "condition%36" AND NOT "condition%38" AND "condition%39"
          UNION ALL
        SELECT 'goto', 'truthy16', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%35" AND NOT "condition%36" AND NOT "condition%38" AND NOT "condition%39" AND "condition%40"
      ),
      "truthy16"("%kind%", "%label%", "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "u", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "truthy9"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy16'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter61"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy16'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter68"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy16'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter64"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy16'
          ),
          "%assign%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "u", "x", "y") AS (
            SELECT CAST((("%inputs%"."direction_x") * ("%inputs%"."min_dist")) AS real) AS "L_x",
                   CAST((("%inputs%"."direction_y") * ("%inputs%"."min_dist")) AS real) AS "L_y",
                   CAST((("%inputs%"."direction_z") * ("%inputs%"."min_dist")) AS real) AS "L_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((2 * (("%inputs%"."direction_x") * ("%inputs%"."normal_x") + ("%inputs%"."direction_y") * ("%inputs%"."normal_y") + ("%inputs%"."direction_z") * ("%inputs%"."normal_z"))) AS real) AS "u",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter118', "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "u", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter118"("%kind%", "%label%", "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "u", "x", "y") AS (
            SELECT "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "u", "x", "y"
            FROM   "truthy16"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter118'
          ),
          "%assign%"("Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."normal_x") * ("%inputs%"."u")) AS real) AS "Q_x",
                   CAST((("%inputs%"."normal_y") * ("%inputs%"."u")) AS real) AS "Q_y",
                   CAST((("%inputs%"."normal_z") * ("%inputs%"."u")) AS real) AS "Q_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x") + ("%inputs%"."L_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y") + ("%inputs%"."L_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z") + ("%inputs%"."L_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter119', "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter119"("%kind%", "%label%", "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "Q_x", "Q_y", "Q_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter118"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter119'
          ),
          "%assign%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."normal_x") * ("%inputs%"."epsilon")) AS real) AS "L_x",
                   CAST((("%inputs%"."normal_y") * ("%inputs%"."epsilon")) AS real) AS "L_y",
                   CAST((("%inputs%"."normal_z") * ("%inputs%"."epsilon")) AS real) AS "L_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x") - ("%inputs%"."Q_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y") - ("%inputs%"."Q_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z") - ("%inputs%"."Q_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter120', "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter120"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter119"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter120'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "condition%41") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x") + ("%inputs%"."L_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y") + ("%inputs%"."L_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z") + ("%inputs%"."L_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."step") < ("%inputs%"."max_rec_depth")) AS bool) AS "condition%41"
            FROM "%inputs%"
          )

        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%41"
          UNION ALL
        SELECT 'goto', 'truthy17', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%41"
      ),
      "truthy17"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter120"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy17'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step") + 1) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'jump', 'ray_loop_head', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "truthy14"("%kind%", "%label%", "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "truthy9"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy14'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter61"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy14'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter68"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy14'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter64"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy14'
          ),
          "%assign%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."direction_x") * ("%inputs%"."min_dist")) AS real) AS "L_x",
                   CAST((("%inputs%"."direction_y") * ("%inputs%"."min_dist")) AS real) AS "L_y",
                   CAST((("%inputs%"."direction_z") * ("%inputs%"."min_dist")) AS real) AS "L_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter92', "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter92"("%kind%", "%label%", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "truthy14"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter92'
          ),
          "%assign%"("color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x") + ("%inputs%"."L_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y") + ("%inputs%"."L_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z") + ("%inputs%"."L_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter93', "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter93"("%kind%", "%label%", "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter92"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter93'
          ),
          "%assign%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."normal_x") * ("%inputs%"."epsilon")) AS real) AS "L_x",
                   CAST((("%inputs%"."normal_y") * ("%inputs%"."epsilon")) AS real) AS "L_y",
                   CAST((("%inputs%"."normal_z") * ("%inputs%"."epsilon")) AS real) AS "L_z",
                   CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter94', "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter94"("%kind%", "%label%", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT "L_x", "L_y", "L_z", "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter93"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter94'
          ),
          "%assign%"("color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x") + ("%inputs%"."L_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y") + ("%inputs%"."L_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z") + ("%inputs%"."L_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter95', "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter95"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter94"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter95'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."light_x") - ("%inputs%"."origin_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."light_y") - ("%inputs%"."origin_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."light_z") - ("%inputs%"."origin_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter96', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter96"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter95"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter96'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((sqrt(("%inputs%"."direction_x") ** 2 + ("%inputs%"."direction_y") ** 2 + ("%inputs%"."direction_z") ** 2)) AS real) AS "length",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter97', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter97"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "length", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter96"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter97'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x") / ("%inputs%"."length")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y") / ("%inputs%"."length")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z") / ("%inputs%"."length")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter98', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter98"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "u", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "x", "y"
            FROM   "inter97"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter98'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "u", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((greatest(0, ("%inputs%"."direction_x") * ("%inputs%"."normal_x") + ("%inputs%"."direction_y") * ("%inputs%"."normal_y") + ("%inputs%"."direction_z") * ("%inputs%"."normal_z"))) AS real) AS "u",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'inter99', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "u", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "inter99"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "u", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "shadows", "step", "u", "x", "y"
            FROM   "inter98"
            WHERE  "%kind%"='goto'
            AND    "%label%"='inter99'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadows", "step", "x", "y", "condition%42") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."color_b") * ("%inputs%"."u")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."color_g") * ("%inputs%"."u")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."color_r") * ("%inputs%"."u")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y",
                   CAST((("%inputs%"."shadows")) AS bool) AS "condition%42"
            FROM "%inputs%"
          )

        SELECT 'goto', 'ray_loop_exit', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND NOT "condition%42"
          UNION ALL
        SELECT 'goto', 'truthy15', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE AND "condition%42"
      ),
      "truthy15"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadows", "step", "x", "y"
            FROM   "inter99"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy15'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id")) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((true) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'jump', 'ray_loop_head', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "truthy13"("%kind%", "%label%", "pixel_b", "pixel_g", "pixel_r", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("x", "y") AS (
            SELECT "x", "y"
            FROM   "truthy9"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy13'
              UNION ALL
            SELECT "x", "y"
            FROM   "inter61"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy13'
              UNION ALL
            SELECT "x", "y"
            FROM   "inter68"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy13'
              UNION ALL
            SELECT "x", "y"
            FROM   "inter64"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy13'
          ),
          "%assign%"("pixel_b", "pixel_g", "pixel_r", "x", "y") AS (
            SELECT CAST((1) AS real) AS "pixel_b",
                   CAST((1) AS real) AS "pixel_g",
                   CAST((1) AS real) AS "pixel_r",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'ray_loop_exit', "pixel_b", "pixel_g", "pixel_r", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "truthy12"("%kind%", "%label%", "pixel_b", "pixel_g", "pixel_r", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("x", "y") AS (
            SELECT "x", "y"
            FROM   "truthy9"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy12'
              UNION ALL
            SELECT "x", "y"
            FROM   "inter61"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy12'
              UNION ALL
            SELECT "x", "y"
            FROM   "inter68"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy12'
              UNION ALL
            SELECT "x", "y"
            FROM   "inter64"
            WHERE  "%kind%"='goto'
            AND    "%label%"='truthy12'
          ),
          "%assign%"("pixel_b", "pixel_g", "pixel_r", "x", "y") AS (
            SELECT CAST((0) AS real) AS "pixel_b",
                   CAST((0) AS real) AS "pixel_g",
                   CAST((0) AS real) AS "pixel_r",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'goto', 'ray_loop_exit', "pixel_b", "pixel_g", "pixel_r", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "ray_loop_exit"("%kind%", "%label%", "%result%") AS (
        WITH
          "%inputs%"("pixel_b", "pixel_g", "pixel_r", "x", "y") AS (
            SELECT "pixel_b", "pixel_g", "pixel_r", "x", "y"
            FROM   "inter99"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_exit'
              UNION ALL
            SELECT "pixel_b", "pixel_g", "pixel_r", "x", "y"
            FROM   "inter64"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_exit'
              UNION ALL
            SELECT "pixel_b", "pixel_g", "pixel_r", "x", "y"
            FROM   "truthy13"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_exit'
              UNION ALL
            SELECT "pixel_b", "pixel_g", "pixel_r", "x", "y"
            FROM   "inter61"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_exit'
              UNION ALL
            SELECT "pixel_b", "pixel_g", "pixel_r", "x", "y"
            FROM   "truthy9"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_exit'
              UNION ALL
            SELECT "pixel_b", "pixel_g", "pixel_r", "x", "y"
            FROM   "truthy12"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_exit'
              UNION ALL
            SELECT "pixel_b", "pixel_g", "pixel_r", "x", "y"
            FROM   "inter120"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_exit'
              UNION ALL
            SELECT "pixel_b", "pixel_g", "pixel_r", "x", "y"
            FROM   "inter68"
            WHERE  "%kind%"='goto'
            AND    "%label%"='ray_loop_exit'
          )
        SELECT 'emit', NULL,
               CAST(({x: ("%inputs%"."x"), y: ("%inputs%"."y"), r: ("%inputs%"."pixel_r"), g: ("%inputs%"."pixel_g"), b: ("%inputs%"."pixel_b")}) AS struct(x int, y int, r real, g real, b real))
        FROM   "%inputs%"
      ),
      "falsey10"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "truthy9"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey10'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter61"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey10'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter68"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey10'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter64"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey10'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id") - 1) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'jump', 'sphere_loop_head', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      ),
      "falsey6"("%kind%", "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", "%result%") AS (
        WITH
          "%inputs%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter32"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter36"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter44"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter38"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "inter29"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "truthy4"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey6'
              UNION ALL
            SELECT "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y"
            FROM   "truthy5"
            WHERE  "%kind%"='goto'
            AND    "%label%"='falsey6'
          ),
          "%assign%"("color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y") AS (
            SELECT CAST((("%inputs%"."color_b")) AS real) AS "color_b",
                   CAST((("%inputs%"."color_g")) AS real) AS "color_g",
                   CAST((("%inputs%"."color_r")) AS real) AS "color_r",
                   CAST((("%inputs%"."direction_x")) AS real) AS "direction_x",
                   CAST((("%inputs%"."direction_y")) AS real) AS "direction_y",
                   CAST((("%inputs%"."direction_z")) AS real) AS "direction_z",
                   CAST((("%inputs%"."epsilon")) AS real) AS "epsilon",
                   CAST((("%inputs%"."id") - 1) AS int) AS "id",
                   CAST((("%inputs%"."light_x")) AS real) AS "light_x",
                   CAST((("%inputs%"."light_y")) AS real) AS "light_y",
                   CAST((("%inputs%"."light_z")) AS real) AS "light_z",
                   CAST((("%inputs%"."material")) AS material) AS "material",
                   CAST((("%inputs%"."max_rec_depth")) AS int) AS "max_rec_depth",
                   CAST((("%inputs%"."min_dist")) AS real) AS "min_dist",
                   CAST((("%inputs%"."normal_x")) AS real) AS "normal_x",
                   CAST((("%inputs%"."normal_y")) AS real) AS "normal_y",
                   CAST((("%inputs%"."normal_z")) AS real) AS "normal_z",
                   CAST((("%inputs%"."origin_x")) AS real) AS "origin_x",
                   CAST((("%inputs%"."origin_y")) AS real) AS "origin_y",
                   CAST((("%inputs%"."origin_z")) AS real) AS "origin_z",
                   CAST((("%inputs%"."pixel_b")) AS real) AS "pixel_b",
                   CAST((("%inputs%"."pixel_g")) AS real) AS "pixel_g",
                   CAST((("%inputs%"."pixel_r")) AS real) AS "pixel_r",
                   CAST((("%inputs%"."shadow_ray")) AS bool) AS "shadow_ray",
                   CAST((("%inputs%"."shadows")) AS bool) AS "shadows",
                   CAST((("%inputs%"."step")) AS int) AS "step",
                   CAST((("%inputs%"."x")) AS int) AS "x",
                   CAST((("%inputs%"."y")) AS int) AS "y"
            FROM "%inputs%"
          )

        SELECT 'jump', 'triangle_loop_head', "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
        FROM   "%assign%"
        WHERE  TRUE
      )

     SELECT 'jump', "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
     FROM   "falsey6"
     WHERE  "%kind%"='jump'
       UNION ALL
     SELECT 'jump', "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
     FROM   "falsey10"
     WHERE  "%kind%"='jump'
       UNION ALL
     SELECT 'jump', "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
     FROM   "truthy15"
     WHERE  "%kind%"='jump'
       UNION ALL
     SELECT 'jump', "%label%", "color_b", "color_g", "color_r", "direction_x", "direction_y", "direction_z", "epsilon", "id", "light_x", "light_y", "light_z", "material", "max_rec_depth", "min_dist", "normal_x", "normal_y", "normal_z", "origin_x", "origin_y", "origin_z", "pixel_b", "pixel_g", "pixel_r", "shadow_ray", "shadows", "step", "x", "y", CAST(NULL AS struct(x int, y int, r real, g real, b real))
     FROM   "truthy17"
     WHERE  "%kind%"='jump'
       UNION ALL
     SELECT 'emit', NULL, CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS int), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS material), CAST(NULL AS int), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS real), CAST(NULL AS bool), CAST(NULL AS bool), CAST(NULL AS int), CAST(NULL AS int), CAST(NULL AS int), "%result%"
     FROM   "ray_loop_exit"
     WHERE  "%kind%"='emit'
    )
  )

SELECT "%result%" FROM "%loop%" WHERE "%kind%"='emit';
