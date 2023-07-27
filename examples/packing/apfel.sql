.timer on
WITH RECURSIVE run("rec?",
                   "label",
                   "res",
                   "orderkey",
                   "capacity",
                   "n",
                   "items",
                   "max_size",
                   "max_subset",
                   "subset",
                   "size",
                   "pack",
                   "linenumber") AS
(
    (SELECT "ifresult29".*
     FROM orders AS o,
          LATERAL
          (SELECT (count(*)) :: int4 AS "count"
                   FROM lineitem AS "l"
                   WHERE "l"."l_orderkey" = o.o_orderkey) AS "let26"("n_1"),
          LATERAL
          (SELECT ("n_1" = 0 OR 60 < (SELECT max("p"."p_size") AS "max"
                                      FROM lineitem AS "l", part AS "p"
                                      WHERE ("l"."l_orderkey" = o.o_orderkey
                                             AND
                                             "l"."l_partkey" = "p"."p_partkey"))) AS "q5_1"
          ) AS "let28"("q5_1"),
          LATERAL
          ((SELECT False,
                   NULL :: text,
                   NULL :: text AS "result",
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: text,
                   NULL :: int4
            WHERE NOT "q5_1" IS DISTINCT FROM True)
             UNION ALL
           (SELECT True,
                   'while6_head',
                   NULL :: text,
                   o.o_orderkey,
                   60,
                   "n_1",
                   (1 << "n_1") - 1 AS "items_2",
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: int4,
                   NULL :: text,
                   NULL :: int4
            WHERE "q5_1" IS DISTINCT FROM True)
          ) AS "ifresult29"
      WHERE o.o_orderstatus = 'F')
      UNION ALL
    (SELECT "result".*
     FROM run AS "run"("rec?",
                       "label",
                       "res",
                       "orderkey",
                       "capacity",
                       "n",
                       "items",
                       "max_size",
                       "max_subset",
                       "subset",
                       "size",
                       "pack",
                       "linenumber"),
          LATERAL
          ((SELECT "ifresult2".*
            FROM LATERAL
                 (SELECT "linenumber" < "n" AS "pred19_9") AS "let1"("pred19_9"),
                 LATERAL
                 ((SELECT True,
                          'for18_head',
                          NULL :: text,
                          "orderkey",
                          "capacity",
                          "n",
                          "items",
                          "max_size",
                          "max_subset",
                          "subset",
                          "size",
                          "pack"
                          ||
                          (CASE WHEN ("max_subset" & (1 << "linenumber"))
                                     <>
                                     0 THEN '#'
                                ELSE '.'
                          END) AS "pack_11",
                          "linenumber" + 1 AS "linenumber_11"
                   WHERE NOT "pred19_9" IS DISTINCT FROM True)
                    UNION ALL
                  (SELECT True,
                          'while6_head',
                          NULL :: text,
                          "orderkey",
                          "capacity",
                          "n",
                          "items" & (~ "max_subset") AS "items_12",
                          "max_size",
                          "max_subset",
                          "subset",
                          "size",
                          "pack",
                          "linenumber"
                   WHERE "pred19_9" IS DISTINCT FROM True)
                    UNION ALL
                  (SELECT False,
                          NULL :: text,
                          "pack",
                          "orderkey",
                          "capacity",
                          "n",
                          "items" AS "items_12",
                          "max_size",
                          "max_subset",
                          "subset",
                          "size",
                          "pack",
                          "linenumber"
                   WHERE "pred19_9" IS DISTINCT FROM True)
                 ) AS "ifresult2"
            WHERE "run"."label" = 'for18_head')
             UNION ALL
           ((SELECT "ifresult12".*
             FROM LATERAL
                  (SELECT (sum("p"."p_size")) :: int4 AS "sum"
                   FROM lineitem AS "l", part AS "p"
                   WHERE ("l"."l_orderkey" = "orderkey"
                          AND
                          ("subset" & (1 << ("l"."l_linenumber" - 1))) <> 0
                          AND
                          "l"."l_partkey" = "p"."p_partkey")) AS "let10"("size_5"),
                  LATERAL
                  (SELECT ("size_5" <= "capacity" AND "size_5" > "max_size") AS "q13_5"
                  ) AS "let11"("q13_5"),
                  LATERAL
                  ((SELECT "ifresult16".*
                    FROM LATERAL (SELECT "subset" = "items" AS "q17_6") AS "let15"("q17_6"),
                         LATERAL
                         ((SELECT True,
                                  'for18_head',
                                  NULL :: text,
                                  "orderkey",
                                  "capacity",
                                  "n",
                                  "items",
                                  "size_5" AS "max_size_13",
                                  "subset" AS "max_subset_13",
                                  "subset",
                                  "size_5",
                                  '',
                                  0
                           WHERE NOT "q17_6" IS DISTINCT FROM True)
                            UNION ALL
                          (SELECT True,
                                  'loop8_body',
                                  NULL :: text,
                                  "orderkey",
                                  "capacity",
                                  "n",
                                  "items",
                                  "size_5" AS "max_size_13",
                                  "subset" AS "max_subset_13",
                                  "items" & ("subset" - "items") AS "subset_8",
                                  "size_5",
                                  "pack",
                                  "linenumber"
                           WHERE "q17_6" IS DISTINCT FROM True)
                         ) AS "ifresult16"
                    WHERE NOT "q13_5" IS DISTINCT FROM True)
                     UNION ALL
                   (SELECT "ifresult21".*
                    FROM LATERAL
                         (SELECT "subset" = "items" AS "q17_6") AS "let20"("q17_6"),
                         LATERAL
                         ((SELECT True,
                                  'for18_head',
                                  NULL :: text,
                                  "orderkey",
                                  "capacity",
                                  "n",
                                  "items",
                                  "max_size",
                                  "max_subset",
                                  "subset",
                                  "size_5",
                                  '',
                                  0
                           WHERE NOT "q17_6" IS DISTINCT FROM True)
                            UNION ALL
                          (SELECT True,
                                  'loop8_body',
                                  NULL :: text,
                                  "orderkey",
                                  "capacity",
                                  "n",
                                  "items",
                                  "max_size",
                                  "max_subset",
                                  "items" & ("subset" - "items") AS "subset_8",
                                  "size_5",
                                  "pack",
                                  "linenumber"
                           WHERE "q17_6" IS DISTINCT FROM True)
                         ) AS "ifresult21"
                    WHERE "q13_5" IS DISTINCT FROM True)
                  ) AS "ifresult12"
             WHERE "run"."label" = 'loop8_body')
             UNION ALL
           (SELECT "ifresult34".*
            FROM LATERAL
                 (SELECT "items" <> 0 AS "pred7_3") AS "let33"("pred7_3"),
                 LATERAL
                 ((SELECT True,
                          'loop8_body',
                          NULL :: text,
                          "orderkey",
                          "capacity",
                          "n",
                          "items",
                          0,
                          0,
                          "items" & (- "items") AS "subset_4",
                          "size",
                          "pack",
                          "linenumber"
                   WHERE NOT "pred7_3" IS DISTINCT FROM True)
                    UNION ALL
                  (SELECT False,
                          NULL :: text,
                          NULL :: text AS "result",
                          "run"."orderkey",
                          "run"."capacity",
                          "run"."n",
                          "run"."items",
                          "run"."max_size",
                          "run"."max_subset",
                          "run"."subset",
                          "run"."size",
                          "run"."pack",
                          "run"."linenumber"
                   WHERE "pred7_3" IS DISTINCT FROM True)
                 ) AS "ifresult34"
            WHERE "run"."label" = 'while6_head'))
          ) AS "result"("rec?",
                        "label",
                        "res",
                        "orderkey",
                        "capacity",
                        "n",
                        "items",
                        "max_size",
                        "max_subset",
                        "subset",
                        "size",
                        "pack",
                        "linenumber")
     WHERE "run"."rec?")
)
SELECT "run"."res" AS "res"
FROM run AS "run"
WHERE NOT "run"."rec?" AND "run"."res" IS NOT NULL;
