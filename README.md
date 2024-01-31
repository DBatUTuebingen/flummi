# ⚙️ `flummi/compiler`

## Usage

```
$ python -m flummi -h

usage: flummi [-h] [-o OUTPUT] [-v] infile

CTE-focussed compilation of imperative programs to recursive SQL.

positional arguments:
  infile

options:
  -h, --help                  show this help message and exit
  -o OUTPUT, --output OUTPUT  The file to write the compilation result to.
  -v, --verbose               Control the level of verbosity.
```


## Syntax/Semantics of PL/Flummi

### Grammar

```
𝑃 ≔ CALL (𝐸, …, 𝐸) IN 𝐹

𝐹 ≔ FUN (𝑣: τ, …, 𝑣: τ) -> τ: 𝑆

𝑆 ≔ 𝑣 : τ
  | 𝑣 <- 𝐸
  | EMIT 𝐸
  | IF 𝐸 THEN 𝑆 ELSE 𝑆
  | LOOP 𝑣 𝑆
  | CONTINUE 𝑣
  | BREAK 𝑣
  | STOP
  | NOOP
  | { 𝑆; …; 𝑆 }

𝐸 ≔ §<SQL expression>§[𝑣, …, 𝑣]

τ ≔ §<SQL type>§

𝑣 ≔ <variable>
```

### Semantics

```
 ⟨ 𝑆⁰ | { STOP } | { 𝑣₁ ↦ 𝐸₁, …, 𝑣ₙ ↦ 𝐸ₙ} | ∅ ⟩ → ⟨ 𝑆 | 𝒫 | ℬ | 𝒪 ⟩
             ⟨ 𝑆 | 𝒫 | ℬ | 𝒪 ⟩ → ⟨ 𝑆′ | 𝒫′ | ℬ′ | 𝒪′ ⟩
                                ⋮
         ⟨ 𝑆⁺ | 𝒫⁺ | ℬ⁺ | 𝒪⁺ ⟩ → ⟨ STOP | ∅ | ℬ⁺⁺ | 𝒪⁺⁺ ⟩
────────────────────────────────────────────────────────────────────────  (Execute-Program)
    CALL (𝐸₁, …, 𝐸ₙ) IN FUN (𝑣₁: τ₁, …, 𝑣ₙ: τₙ) -> τₑ: 𝑆⁰ ⇒ 𝒪⁺⁺


                        𝐸 ↦ₑ 𝐸′
─────────────────────────────────────────────────────────────── (Eval-Assign)
 ⟨ 𝑣 <- 𝐸 | s ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ s | 𝒫 | ℬ ∪ { 𝑣 ↦ 𝐸′ } | 𝒪 ⟩


                      𝐸 ↦ₑ 𝐸′
───────────────────────────────────────────────────────── (Eval-Emit)
 ⟨ EMIT 𝐸 | s ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ s | 𝒫 | ℬ| 𝒪 ∪ { 𝐸′ } ⟩


─────────────────────────────────────────────── (Eval-NoOp)
 ⟨ NOOP | s ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ s | 𝒫 | ℬ | 𝒪 ⟩


──────────────────────────────────────────────── (Eval-Declare)
 ⟨ 𝑣 : τ | s ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ s | 𝒫 | ℬ | 𝒪 ⟩


────────────────────────────────────────────────── (Eval-Stop)
 ⟨ STOP | s ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ STOP | 𝒫 | ℬ | 𝒪 ⟩


───────────────────────────────────────────────────────────────────────── (Eval-Block)
 ⟨ { 𝑆₁; 𝑆₂; …; 𝑆ₙ } | 𝒫 | ℬ | 𝒪 ⟩ → ⟨ 𝑆₁ | 𝑆₂ ⊕ … ⊕ 𝑆ₙ ⊕ 𝒫 | ℬ | 𝒪 ⟩


────────────────────────────────────────────────────────── (Eval-Intro-Loop)
 ⟨ LOOP 𝑣 𝑆 | 𝒫 | ℬ | 𝒪 ⟩ → ⟨ 𝑆 | LOOP 𝑣 𝑆 ⊕ 𝒫 | ℬ | 𝒪 ⟩


                              𝑣 = 𝑣′
──────────────────────────────────────────────────────────────────── (Eval-Continue-Loop-1)
 ⟨ CONTINUE 𝑣′ | LOOP 𝑣 𝑆 ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ LOOP 𝑣 𝑆 | 𝒫 | ℬ | 𝒪 ⟩


────────────────────────────────────────────────────────────── (Eval-Continue-Loop-2)
 ⟨ CONTINUE 𝑣 | 𝑆 ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ CONTINUE 𝑣 | 𝒫 | ℬ | 𝒪 ⟩


                          𝑣 = 𝑣′
────────────────────────────────────────────────────────────────  (Eval-Break-Loop-1)
 ⟨ BREAK 𝑣′ | LOOP 𝑣 𝑆 ⊕ 𝑆′ ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ 𝑆′ | 𝒫 | ℬ | 𝒪 ⟩


──────────────────────────────────────────────────────── (Eval-Break-Loop-2)
 ⟨ BREAK 𝑣 | 𝑆 ⊕ 𝒫 | ℬ | 𝒪 ⟩ → ⟨ BREAK 𝑣 | 𝒫 | ℬ | 𝒪 ⟩


              𝐸 ↦𝑒 𝐸′              𝐸′ = TRUE
──────────────────────────────────────────────────────────── (Eval-If-True)
 ⟨ IF 𝐸 THEN 𝑆₁ ELSE 𝑆₂ | 𝒫 | ℬ | 𝒪 ⟩ → ⟨ 𝑆₁ | 𝒫 | ℬ | 𝒪 ⟩


              𝐸 ↦𝑒 𝐸′              𝐸′ = FALSE
──────────────────────────────────────────────────────────── (Eval-If-False)
 ⟨ IF 𝐸 THEN 𝑆₁ ELSE 𝑆₂ | 𝒫 | ℬ | 𝒪 ⟩ → ⟨ 𝑆₂ | 𝒫 | ℬ | 𝒪 ⟩
```