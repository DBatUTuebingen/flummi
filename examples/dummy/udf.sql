CREATE FUNCTION multiply(a INT, b INT)
RETURNS SETOF INT AS
$$
DECLARE
  c INT = 0;
BEGIN
  WHILE b > 0 LOOP
    c := a + c;
    RETURN NEXT c;
    b := b - 1;
  END LOOP;
END
$$ LANGUAGE PLpgSQL;
