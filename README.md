# Flummi
_A to-SQL Compiler Prototype._

_Flummi_ is a research compiler prototype for to-SQL compilation, implementing methods we've researched and developed at the [database chair of the University of Tübingen](https://db.cs.uni-tuebingen.de/)---see the list of related publications [below](#related-publications).

## Usage

The flummi compiler in this repository can be used either as a _python library_ or directly as a _command line tool_. Either way, to use our compiler, you will need to add it to your local environment. We currently have no intention of publishing this as a package on [PyPI](https://pypi.org), so we recommend you install it as a `git` dependency via:

```bash
pip install flummi@git+"<remote here>/flummi"
```

**Library mode.**

As a python library, we expose only the function `compile` and the module `IR` containing our intermediate representations. The `compile` function is straightforward; as the name implies it takes a program and _compiles_ it, yielding the compiled query string. The programs can either be supplied in the form of a source string (you can find a description of the syntax [down below](#the-flummi-language)) or an AST.

```python
from flummi import compile

query = compile("""
  {
    DECLARE v : §int§;
    LET v = §0§[];
    EMIT v;
    LET v = §{0} + 1§[v];
    EMIT v;
    STOP
  }
""")
```

To map errors back to original source locations during exception handling, we track the provenance of every AST/IR node in a common attribute called `location` of type `flummi.library.errors.Location | None`. When present, we use the provenance information to render more helpful error messages, but we do not require it! To make the pretty error messages work when supplying `compile` with a custom AST, you need to add a proper code location to each AST node and also pass your source code using the `source` keyword argument.

```py
from flummi import compile
from flummi.IR import AST
from flummi.library.errors import Location

source = "EMIT v"

ast = AST.Program(
    AST.Emit(
        AST.Variable("v", location=Location(line=1, column=6)),
        location=Location(line=1, column=1),
    ),
    location=Location(line=1, column=1),
)

query = compile(ast, source=source)
```

```
flummi.compiler.analysis.AnalysisError: AnalysisError:
Found read from uninitialised variable 'v'.
1 | EMIT v
---------^
```

**Tool mode.**

As a tool, you can pass a Flummi source file to the compiler which in turn will output the compiled SQL query to stdout or an optional file.

```
-- contents of input.fl
{
  DECLARE v : §int§;
  LET v = §0§[];
  EMIT v;
  LET v = §{0} + 1§[v];
  EMIT v;
  STOP
}
```

```bash
$ flummi input.fl [output.sql]
WITH
  "start.1"("󰐤", "") AS (
    SELECT 0 AS "󰐤",
           NULL AS ""
  ),
...
```

For debugging purposes, or if you just a bit nosy, the compiler can also spit out a graphically renditions of the IR used during our compilation. To render these we rely on being able to find a working version of [graphviz](https://graphviz.org/) somewhere on your path—so make sure to have that installed if you want to use this feature.

## The Flummi Language

This compiler prototype uses a "minimum viable language" as an input, as such it isn't really ergonomic to program---but that isn't our goal here! Some of the "unergonomic" things you will need to contend with are that we only have infinite loops with loop controls (`BREAK`/`CONTINUE`), our conditionals always need two branches, all variables are scoped globally, etc. The following is a complete EBNF-esque grammar of the Flummi language.

```
𝑠 := { 𝑠; …; 𝑠 }
   | DECLARE 𝑣 : 𝑡
   | LET 𝑣 = 𝑒
   | EMIT 𝑣
   | STOP
   | NOOP
   | IF 𝑣 THEN 𝑠 ELSE 𝑠
   | LOOP 𝑠
   | BREAK
   | CONTINUE
   | FORK 𝑣 = 𝑞
   | GATHER 𝑣 = 𝑎 [ BY 𝑣, …, 𝑣 ]
   | SYNC [ BY 𝑣, …, 𝑣 ]

𝑣 := <variable>
𝑡 := §<SQL type>§
𝑒 := §<scalar SQL expression>§[<free variables>]
𝑞 := §<non-scalar SQL expression>§[<free variables>]
𝑎 := §<SQL aggregate expression>§[<free variables>]
```

**Embedded SQL**

The grammar contains a few `§...§[...]` bits that we call "black boxes" in most of our work. Syntactically we represent these in two parts, the first `§...§` being a bit of SQL code with free variables (free wrt. the code snippet itself) replaced by `{𝑖}` and the second being a list of the free variables in the order of `𝑖`. So the expression `§{0} + 1§[v]` maps to the SQL expression that increments the variable `v`, i.e., `v + 1`. Note that for types we don't expect free variables, since that doesn't make much sense for our purposes.

**Data-Driven Concurrency**

Up until `LOOP`, `BREAK`, `CONTINUE`, the grammar above probably doesn't need much explaining. After that we get a triplet of statements that you may not be able to make much sense of. TL;DR together, `FORK`, `GATHER`, and `SYNC` represent a data-driven version of the ubiquitous [fork-join model](https://en.wikipedia.org/wiki/Fork-join_model) for concurrency enabled by our compilation method. The work on this has yet to be published, so you won't find much information on this feature elsewhere. As a brief starter, consider the following:

- `FORK …` allows you to _fork_ the current program state into multiple sibling program states at any given time for each row in the result of a table-valued SQL expression.
- `GATHER … [BY …]` allows you to _join_ (bad overlap in DB-lingo here, so we call it gather) sibling program states together by combining data from each of them using a SQL aggregate expression. Further you can _group_ sibling program states by providing an additional grouping key.
- `SYNC [BY …]` allows you to enforce synchronicity between sibling program states, again with the option to _group_ sibling program states using a grouping key.

The latter is necessary due to our handling of loops during compilation; the SQL queries we compile to execute loop iterations of all siblings in lock step, which can lead to situations where siblings diverge wrt. their current progress through the program. Without the `SYNC` statement, such divergence would be unrecoverable, thus making it impossible to _join_ these divergent sibling program states.

## Related Publications
- Tim Fischer and Denis Hirn. 2025. BIRNE: Mixed-paradigm Workload Execution in SQL Engines. In Proceedings of the 19th International Symposium on Database Programming Languages (DBPL '25). Association for Computing Machinery, New York, NY, USA, Article 4, 1–11. https://doi.org/10.1145/3735106.3736535
- Tim Fischer, Denis Hirn, and Torsten Grust. 2024. SQL Engines Excel at the Execution of Imperative Programs. Proc. VLDB Endow. 17, 13 (September 2024), 4696–4708. https://doi.org/10.14778/3704965.3704976
