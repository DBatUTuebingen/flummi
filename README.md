# Flummi

_A to-SQL Compiler Prototype._

_Flummi_ is a research compiler prototype for to-SQL compilation, implementing methods we've researched and developed at the [database chair of the University of Tübingen](https://db.cs.uni-tuebingen.de/)---see the list of related publications [below](#related-publications). Our compilation strategy takes imperative procedural programs with embedded SQL expressions and transforms them to a single monolithic SQL query.

> [!IMPORTANT]
> The input language to our compiler only includes the bare minimum necessary and is thus not very developer friendly! Being a research vehicle for our ideas before anything else, we opted to not box ourselves in and define [our own simple, bare-bones language](#the-flummi-language) that includes only the absolute core necessities for imperative programming. Most, if not all other, more "complicated" language constructs/features common to more developer friendly languages can be easily desugared to our language and are thus not of interest to this project---though we of course have ongoing research on that side of the fence as well. 😉

## Usage

The Flummi compiler in this repository can be used either as a _python library_ or directly as a _command line tool_. Either way, to use our compiler, you will need to add it to your local environment. You can install it from [PyPI](https://pypi.org/flummi) or as a `git` dependency:

```bash
$ pip install flummi
$ pip install flummi@git+https://github.com/DBatUTuebingen/flummi
```

**Library mode.**

As a python library, we expose the function `compile` which is straightforward; as the name implies it takes a program, _compiles_ it and spits our the compiled query string. The input programs can either be supplied in the form of a source string (you can find a description of the syntax [down below](#the-flummi-language)) or an AST.

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
        [AST.Variable("v", location=Location(line=1, column=6))],
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

To use the Flummi compiler as a CLI tool, you will need to install it with the extra-dependencies `cli`, i.e., `pip install flummi[cli]`. When using the compiler via the CLI, you can pass it a Flummi source file which it will in turn compile and dump the compiled SQL query to stdout or an optional file.

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
$ flummi compile input.fl [output.sql]
WITH
  "start.1"("#️⃣", "⚙️") AS (
    SELECT 0 AS "#️⃣",
           NULL AS "⚙️"
  ),
...
```

For debugging purposes, or if you just a bit nosy, the compiler can also spit out graphical renditions of the IR used during our compilation. To render these we rely on being able to find a working version of [graphviz](https://graphviz.org/) somewhere on your path—so make sure to have that installed if you want to use this feature.

## The Flummi Language

This compiler prototype uses a "minimum viable language" as an input, as such it isn't really ergonomic to program---but that isn't our goal here! Some of the "unergonomic" caveats you will need to contend with are that we only have infinite loops with loop controls (`BREAK`/`CONTINUE`), all variables are scoped globally, etc.---see the comprehensive listing [below](#programming-in-flummi). The following is a complete EBNF-esque grammar of the Flummi language.

```
𝑠 := { 𝑠; …; 𝑠 }
   | DECLARE 𝑣, …, 𝑣 : 𝑡
   | LET 𝑣 = 𝑒, …, 𝑣 = 𝑒
   | EMIT 𝑣, …, 𝑣
   | STOP
   | NOOP
   | IF 𝑒 THEN 𝑠 [ ELSE 𝑠 ]
   | LOOP 𝑠
   | BREAK
   | CONTINUE
   | FORK 𝑣, …, 𝑣 = 𝑞
   | GATHER [ 𝑣 = 𝑎, …, 𝑣 = 𝑎 ] [ BY 𝑣, …, 𝑣 ]
   | SYNC [ BY 𝑣, …, 𝑣 ]

𝑣 := <variable>
𝑡 := §<SQL type>§
𝑒 := 𝑣 | §<scalar SQL expression>§[<free variables>]
𝑞 := §<non-scalar SQL expression>§[<free variables>]
𝑎 := §<SQL aggregate expression>§[<free variables>]
```

Keywords are case-insensitive and `--` starts a line comment. Blocks must
contain one or more semicolon-separated statements.

**Embedded SQL**

To keep things focussed on what SQL can't already handle itself---i.e., statement-level control-flow---we co-opt SQL's expression language as our own. The grammar reflects this via the `§...§[...]` bits that we call "black boxes" in most of our work. A black box can either have no free variables, use an explicit positional list, or discover named free variables inline:

- `§random()§` and `§random()§[]` contain no free variables.
- `§{0} + 1§[v]` uses positional placeholders: `{0}` refers to the first variable in the suffix, so the expression is equivalent to `v + 1`.
- `§{v} + 1§` uses an inline named placeholder. The compiler discovers `v` automatically; repeated references to `{v}` refer to the same variable.

These forms work for scalar, non-scalar, and aggregate SQL expressions. A bare variable is also a scalar expression, so `LET next = current` and `IF active THEN ...` need no SQL black box. Types are always SQL snippets and cannot have free variables.

**Data-Driven Concurrency**

Up until `LOOP`, `BREAK`, `CONTINUE`, the grammar above probably doesn't need much explaining. After that we get a triplet of statements that you may not be able to make much sense of. TL;DR together, `FORK`, `GATHER`, and `SYNC` represent a data-driven version of the ubiquitous [fork-join model](https://en.wikipedia.org/wiki/Fork-join_model) for concurrency enabled by our compilation method. The work on this has yet to be published, so you won't find much information on this feature elsewhere. As a brief starter, consider the following:

- `FORK v₁, …, vₙ = …` allows you to _fork_ the current program state into multiple sibling program states at any given time for each row in the result of a table-valued SQL expression. Each listed variable receives the matching result column.
- `GATHER v₁ = …, …, vₙ = … [BY …]` allows you to _join_ (bad overlap in DB-lingo here, so we call it gather) sibling program states together by combining data from each of them using SQL aggregate expressions. Further you can _group_ sibling program states by providing an additional grouping key.
- `SYNC [BY …]` allows you to enforce synchronicity between sibling program states, again with the option to _group_ sibling program states using a grouping key.

`GATHER` also implicitly preserves every non-aggregate variable that remains live after the statement: such a variable becomes an additional grouping key, so it need not be repeated in `BY`. The latter is necessary due to our handling of loops during compilation; the SQL queries we compile to execute loop iterations of all siblings in lock step, which can lead to situations where siblings diverge wrt. their current progress through the program. Without the `SYNC` statement, such divergence would be unrecoverable, thus making it impossible to _join_ these divergent sibling program states.

### Flummi Caveats

The developer ergonomics of our input language leave much to be desired, but for the sake of reproducible research fellow researchers (or any interested readers, in fact) should at least be able to grok our example programs. In that light, consider the following important even if you don't plan on programming in Flummi yourself!

**Global Scoping**

Though unnatural to most developers, it makes compiling a lot easier when we don't need to consider the scoping of variables. Since scoping rules of other programming languages can be encoded in a single global scope through the use of dedicated variable naming schemes, programs in our language only have one global scope. So anywhere you see a given variable `𝑣` in a Flummi program, it is that exact same `𝑣` as everywhere else in the program. Variables must be declared exactly once before they are written, and they must be initialized before they are read.

Multiple bindings in one `LET` are evaluated against the state before that `LET`; the new values become visible together. For example, `LET left = right, right = left` swaps the two values.

**Emit and Stop**

Since we're aiming to bring procedural programs into the database, the most natural shape the output of such a program is tabular. To include this as a first-class concept in our compiler, we decided on having our program spit out (`EMIT`) values incrementally---think `yield` in python, just with the suspension of local control-flow. As a consequence of this design, we don't have a `RETURN` statement as it would duplicate behavior of `EMIT`, rather we have `STOP` which only halts control-flow and nothing else.

**Multi-Variable Emits**

An `EMIT` can yield multiple variables, separated by commas, but every `EMIT` in a program must yield the same number of variables with the same types in the same positions.

**Infinite Loops**

Our input language only includes one construct for looping/iteration---`LOOP`---which implements a simple infinite loop. In addition to which, we include common iteration controls in `BREAK` and `CONTINUE`---which jump after a loop or back to its head, respectively. Both controls are valid only inside a loop. Combining these controls with some conditionals and assignments, allows you to model any other kind of loop!

**Limited Expression Use**

We heavily restrict where in our language you can use expressions: in the right-hand sides of `LET` and `GATHER`, as the query of `FORK`, and as the condition of `IF`. This, in combination with all variables also needing explicit declarations, makes programs pretty wordy.

## Related Publications

- Tim Fischer and Denis Hirn. 2025. BIRNE: Mixed-paradigm Workload Execution in SQL Engines. In Proceedings of the 19th International Symposium on Database Programming Languages (DBPL '25). Association for Computing Machinery, New York, NY, USA, Article 4, 1–11. https://doi.org/10.1145/3735106.3736535
- Tim Fischer, Denis Hirn, and Torsten Grust. 2024. SQL Engines Excel at the Execution of Imperative Programs. Proc. VLDB Endow. 17, 13 (September 2024), 4696–4708. https://doi.org/10.14778/3704965.3704976
