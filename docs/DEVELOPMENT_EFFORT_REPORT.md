# Development Effort Report: ASCII Diagrams Corrector (OpusDriven)

## Project Summary

| Metric              | Value                            |
|---------------------|----------------------------------|
| Source modules      | 27 Python files                  |
| Test files          | 23 Python files                  |
| Total Python LoC    | 4,159 (code only, excl. blanks/comments) |
| Total files         | 82                               |
| Test count          | 368                              |
| Test levels         | Unit, Integration, E2E           |
| Dependencies        | Typer, Pydantic, structlog       |
| Tooling             | ruff, black, isort, mypy (strict), pre-commit, pytest |

## 1. Manual Development Effort

### Required Developer Profile

**Level:** Senior Python Developer (5+ years)

**Required skills:**

| Skill                          | Depth   | Why                                                        |
|--------------------------------|---------|------------------------------------------------------------|
| Python 3.12+                   | Expert  | Protocols, dataclasses, frozensets, type annotations       |
| Algorithm design               | Strong  | Line detection, clustering, consensus histograms, alignment|
| Clean Architecture / DDD       | Strong  | Protocol-based layers, domain value objects, frozen DCs    |
| CLI frameworks (Typer)         | Medium  | 3 subcommands with options, variadic args                  |
| TDD / pytest                   | Strong  | 368 tests across 3 levels, fixtures, mocking               |
| Markdown parsing               | Medium  | Fenced block extraction, classification, in-place rewrite  |
| Code quality tooling           | Medium  | Ruff, Black, isort, mypy strict, pre-commit config         |
| 2D grid/matrix manipulation    | Strong  | Core data structure; row/column scanning, cell shifting    |

**Estimated manual timeline (senior developer):**

| Phase                                       | Effort        |
|---------------------------------------------|---------------|
| Domain modeling (Grid, Line, Cell, Position) | 1.5 - 2 days  |
| Detection layer (LineDetector, ParallelLineFinder) | 1.5 - 2 days  |
| Correction layer (Alignment, StrayChar, RowShift, ShiftCorrector) | 2 - 3 days  |
| CorrectionEngine orchestration              | 0.5 day       |
| IO layer (MarkdownParser, Classifier, Corrector, Backup) | 1 - 1.5 days |
| CLI commands (correct, analyze, fix-md)     | 0.5 - 1 day   |
| Test suite (368 tests, fixtures, conftest)  | 2.5 - 3.5 days|
| Project config, tooling, docs               | 0.5 - 1 day   |
| **Total**                                   | **10 - 15 working days** |

A mid-level developer would likely need 3-5 weeks. The algorithmic parts (line detection, parallel finding with tolerance/overlap, column consensus for row shift detection) are the hardest to get right and require iterative debugging.

## 2. AI-Driven Development (Claude Code)

### Required Operator Profile

**Level:** Mid-level developer comfortable with AI-assisted workflows

**Required skills:**

| Skill                      | Depth     | Why                                                     |
|----------------------------|-----------|---------------------------------------------------------|
| Python reading comprehension | Medium  | Review generated code, spot logical errors              |
| Architecture / design taste  | Medium  | Guide Claude toward clean structure, approve/reject plans|
| Prompt engineering           | Basic+  | Describe features, constraints, and edge cases clearly  |
| Testing intuition            | Basic+  | Know when to ask for more tests or different scenarios  |
| Git workflow                 | Basic   | Commit, review diffs, manage branches                   |
| Domain understanding         | Medium  | Understand ASCII diagrams enough to verify correctness  |

The operator does NOT need deep algorithm design skills or TDD expertise -- Claude Code handles implementation, test writing, and tooling configuration. The operator's role shifts from *writing* to *directing, reviewing, and validating*.

### What Claude Code handled autonomously

- Full implementation of all 27 source modules and 23 test files
- Protocol-based architecture with proper layer separation
- All 368 tests (unit/integration/e2e) including edge cases
- pyproject.toml, ruff/black/isort/mypy/pre-commit configuration
- CLAUDE.md, README, ARCHITECTURE.md documentation
- Iterative correction of ASCII diagrams in the docs themselves (commit `084a0d8`)

## 3. Real Development Speed (Claude Max Subscription)

This section captures the actual operator experience: how much human time and attention the project required when built with Claude Code on a **Claude Max subscription** ($100/month or $200/month flat rate).

### Measured Constraints

- Each of the 5 commits was produced by **1-5 operator prompts**
- Each prompt required approximately **1-5 minutes** of operator time (thinking, typing, reviewing)
- Claude Code executes autonomously between prompts (reading files, writing code, running tests)

### Per-Commit Breakdown

| Commit    | Lines changed  | Prompts (est.) | Operator time        | Tokens per prompt (est.) | Commit tokens (est.) |
|-----------|----------------|----------------|----------------------|--------------------------|----------------------|
| `0cc8519` | +4,943         | 3 - 5          | 9 - 25 min           | 150K - 250K              | 600K - 1M            |
| `2d360cc` | +1,228 net     | 2 - 4          | 4 - 20 min           | 80K - 150K               | 200K - 500K          |
| `ed7a08a` | +489           | 1 - 2          | 1 - 10 min           | 50K - 100K               | 50K - 200K           |
| `084a0d8` | +31 / -31      | 1              | 1 - 5 min            | 30K - 60K                | 30K - 60K            |
| `2c6c8eb` | +1,715 net     | 2 - 4          | 4 - 20 min           | 100K - 200K              | 300K - 600K          |
| **Total** | **+8,375 net** | **9 - 16**     | **19 - 80 min**      |                          | **1.2M - 2.4M**      |

**Realistic mid-range: ~12 prompts, ~36 minutes of operator keyboard time, ~1.6M tokens.**

### How tokens accumulate per prompt

Each operator prompt triggers a multi-step autonomous cycle inside Claude Code:

```
Operator prompt (1-5 min typing)
  -> Claude reads relevant files         (~5K-15K tokens input)
  -> Claude generates code/tests         (~3K-10K tokens output)
  -> Claude runs tests via Bash          (~2K-5K tokens I/O)
  -> Claude reads errors, iterates       (~5K-15K tokens)
  -> ... repeats 3-8 internal turns ...
  -> Final result returned to operator
  ≈ 50K-250K tokens per operator prompt
```

### Claude Max subscription economics

| Factor                          | Value                                         |
|---------------------------------|-----------------------------------------------|
| Subscription cost               | $100/month (standard) or $200/month (higher)  |
| Project total tokens            | ~1.2M - 2.4M                                  |
| Project duration                | 1 calendar day                                |
| Prompts used                    | 9 - 16                                        |
| Operator keyboard time          | ~19 - 80 min (mid-range: ~36 min)             |
| Effective project cost          | Fraction of monthly fee (subscription shared across all month's work) |
| Equivalent API cost (Opus)      | $30 - $80                                     |
| Equivalent API cost (Sonnet)    | $6 - $20                                      |

The entire project consumed a small portion of a single day's usage within a monthly subscription. At the Max tier, there is no per-token anxiety -- the operator focuses on quality of prompts rather than minimizing token count.

## 4. Actual Time and Token Expenditure (Commit Analysis)

### Commit Timeline

```
Commit  Time (UTC+2)           Gap       Lines (+/-)      Description
------  ---------------------  --------  ---------------  ----------------------------------
0cc8519 Feb 6  08:24           --        +4,943           Initial commit (core + CLI + tests)
2d360cc Feb 7  00:34           16h 10m   +1,352 / -124    fix-md command + IO layer + tests
ed7a08a Feb 7  00:50              16m    +489             Architecture docs + E2E fixture
084a0d8 Feb 7  08:48           7h 58m    +31 / -31        Fix diagram alignment in docs
2c6c8eb Feb 7  09:10              22m    +1,775 / -60     StrayCharFinder + RowShiftCorrector
------                                   ---------------
TOTAL                                    +8,590 / -215
```

### Time Analysis

| Window                        | Duration  | Activity                                    |
|-------------------------------|-----------|---------------------------------------------|
| Session 1: Feb 6, 08:24-00:50| ~16.5 h   | Core build, fix-md feature, docs            |
| AFK (sleep): 00:50-08:48     | ~8 h      | Operator away from keyboard                 |
| Session 2: Feb 7, 08:48-09:10| ~22 min   | Diagram fixes, new correctors, README       |
| **Wall clock total**          | **~25 h** |                                             |
| **Active time (excl. sleep)** | **~17 h** |                                             |

Within the 16.5h Session 1, the operator was likely intermittently away (meals, breaks, reviewing output). Claude Code runs autonomously between prompts, so much of the wall clock is unattended generation and test cycles. Based on the prompt-count analysis in Section 3, the operator's actual keyboard engagement was **~19-80 minutes** (mid-range ~36 min).

### Estimated Token Usage

| Commit   | Lines changed | Est. prompts | Est. tokens (input + output) |
|----------|---------------|--------------|------------------------------|
| `0cc8519`| +4,943        | 3 - 5        | 600K - 1M                    |
| `2d360cc`| +1,228 net    | 2 - 4        | 200K - 500K                  |
| `ed7a08a`| +489          | 1 - 2        | 50K - 200K                   |
| `084a0d8`| +31/-31       | 1            | 30K - 60K                    |
| `2c6c8eb`| +1,715 net    | 2 - 4        | 300K - 600K                  |
| **Total**|               | **9 - 16**   | **1.2M - 2.4M**              |

### This Report: Session Token Accounting

This development effort report was itself generated by Claude Code in a separate session:

| Metric                     | Value                                   |
|----------------------------|-----------------------------------------|
| Operator prompts           | 2 (initial request + refinement)        |
| Operator keyboard time     | ~3 - 8 min                              |
| Claude Code internal turns | ~15 - 20 (file reads, git log, cloc, pytest, report writing) |
| Estimated session tokens   | ~100K - 200K                            |
| Wall clock time            | ~5 - 10 min                             |

## 5. Final Comparison

| Dimension | Manual (Senior Dev) | AI-Driven (API Pay-per-token) | AI-Driven (Claude Max) |
|---|---|---|---|
| **Developer skill required** | Senior (5+ yr Python, algorithms, TDD) | Mid-level (review + direct) | Mid-level (review + direct) |
| **Calendar time** | 2 - 3 weeks | ~1 day | ~1 day |
| **Operator active keyboard time** | 80 - 120 hours | 6 - 10 hours (monitoring) | **19 - 80 min** (prompts only) |
| **Prompts / interactions** | N/A (continuous coding) | Dozens of review cycles | **9 - 16 prompts** |
| **Lines of code produced** | 4,159 | 4,159 | 4,159 |
| **Tests from day one** | Likely fewer initially | 368 | 368 |
| **Architecture quality** | Depends on developer | Protocol-driven, consistent | Protocol-driven, consistent |
| **Tooling setup** | Often deferred | Included from commit 1 | Included from commit 1 |
| **Token consumption** | N/A | 1.2M - 2.4M | 1.2M - 2.4M |
| **Monetary cost** | $4,000 - $9,000 (labor) | $30 - $80 (Opus API) | Fraction of $100-$200/month subscription |
| **Cost model** | Hourly / salaried | Variable (per-token) | **Fixed (flat monthly)** |
| **Risk: subtle algorithm bugs** | Lower (human reasoning) | Higher (needs review) | Higher (needs review) |
| **Risk: over-engineering** | Moderate | Moderate-to-high | Moderate-to-high |
| **Report generation cost** | N/A | ~$3 - $8 (API) | Included in subscription |

### Key Takeaway

Under a Claude Max subscription, the operator's total keyboard engagement for the entire project -- 4,159 lines of Python, 368 tests, full tooling, documentation -- was approximately **25-50 minutes**. That is roughly the time it takes to write a single detailed design document. The subscription model eliminates per-token cost concerns, letting the operator focus entirely on prompt quality and architectural direction. The same scope would require a senior developer **10-15 working days** of focused effort, at 50-100x the cost.

---

## Appendix 1: Prompts from Report Generation Session (Sonnet Driven)

This appendix contains all operator prompts from the session that generated this development effort report.

### Prompt 1: Initial Request

```
Use the agent to provide then next information:
1. Briefly required manual efforts of the required develope specifying it's skills
2. The same for AI-driven development (claude code exactly)
3. Estimate of the real spended tokens and time based on commits. Big pauses are
   connected with operator AFK (away from keyboar due to the need to sleep)
Save as a MarDown report.
Thank you!
```

**Operator note**: User executed `/clear` command before this prompt.

### Prompt 2: Refinement Request (First Attempt - Interrupted)

```
Add the third criteria, please, real speed of the development using Claude Max
subscription. Each commit was formed by 1-5 prompts, time for the prompt is
approximately 1-5 minutes. Include token estimate. Be precise, strictly follow
this promp's instructions, maximun attention. Thank you very much!
```

**Status**: Request interrupted by user mid-execution.

### Prompt 3: Refinement Request (Final)

```
Add the third criteria, please, real speed of the development using Claude Max
subscription. Each commit was formed by 1-5 prompts, time for the prompt is
approximately 1-5 minutes. Include token estimate. Be precise, strictly follow
this promp's instructions, maximun attention. Add final comparison table. Add the
tokens spend for this report generation session (the dialogue above). Thank you
very much!
```

### Prompt 4: Appendix Request (!PlanMode)

```
Add all the promps from the current dialogue to the end of the document. Call it
Appendix 1. Be precise. Thank you!
```

---

**Session Summary:**
- Total operator prompts: 4 (1 initial + 3 refinements)
- Operator keyboard time: ~5 - 12 minutes
- Claude Code autonomous actions: ~20 tool calls (git log, cloc, file reads, writes)
- Estimated session tokens: ~110K - 220K (including this appendix addition)
