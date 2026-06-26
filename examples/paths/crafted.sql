WITH RECURSIVE
  loop(first, last, length, path) AS (
    SELECT id AS first,
           id AS last,
           0 AS length,
           array[id] AS path
    FROM   nodes
      UNION ALL
    SELECT loop.first,
           e.there AS last,
           loop.length + e.length AS length,
           loop.path || array[e.there] AS path
    FROM   loop, edges AS e
    WHERE  loop.last = e.here
  )

SELECT argmin(path, length)
FROM   loop
WHERE  length > 0
GROUP  BY first, last;
