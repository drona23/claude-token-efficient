# claude-token-efficient

> One file. Drop it in your project. Keeps responses terse and can reduce total tokens on output-heavy workflows.
> Note: instruction files add input tokens on every turn. Keep this file short - if it grows too much, it can cost more than it saves.
> Model support: benchmarks were run on Claude only. The rules are model-agnostic and should work on any model that reads context - but results on local models like llama.cpp, Mistral, or others are untested. Community results welcome.

---

## The Problem

When you use Claude Code, every word Claude generates costs tokens.
Most people never control *how* Claude responds - they just get whatever the model decides to output.

By default, Claude:
- Opens every response with "Sure!", "Great question!", "Absolutely!"
- Ends with "I hope this helps! Let me know if you need anything!"
- Uses em dashes (--), smart quotes, Unicode characters that break parsers
- Restates your question before answering it
- Adds unsolicited suggestions beyond what you asked
- Over-engineers code with abstractions you never requested
- Agrees with incorrect statements ("You're absolutely right!")

**All of this wastes tokens. None of it adds value.**

---

## Two Options

**Option 1: Paste rules in chat (quick start)**
Copy these rules into any new session:
```
Rules: Read files first. Write complete solution. Test once. No over-engineering.
```
Works immediately. No setup. Good for one-off tasks.

**Option 2: Drop CLAUDE.md file (set and forget)**
```
your-project/
└── CLAUDE.md    <- one file, zero setup, no code changes
```
Automatic on every message. Better for regular work. More efficient at scale.

Pick based on your workflow. Both work.

---

## How They Compare

| Approach | Setup | Cost | Best For |
|----------|-------|------|----------|
| Rules in chat | None | Higher | Quick sessions, no project |
| CLAUDE.md file | 1 file | Lower | Regular work, pipelines |

---

## When This Helps vs When It Doesn't

**This file works best for:**
- Automation pipelines with high output volume (resume bots, agent loops, code generation)
- Repeated structured tasks where Claude's default verbosity compounds across hundreds of calls
- Teams who need consistent, parseable output format across sessions

**This file is not worth it for:**
- Single short queries - the file loads into context on every message, so on low-output exchanges it is a net token increase
- Casual one-off use - the overhead doesn't pay off at low volume
- Fixing deep failure modes like hallucinated implementations or architectural drift - those require hooks, gates, and mechanical enforcement
- Pipelines using multiple fresh sessions per task - fresh sessions don't carry the CLAUDE.md overhead benefit the same way persistent sessions do
- Parser reliability at scale - if you need guaranteed parseable output, use structured outputs (JSON mode, tool use with schemas) built into the API - that is a more robust solution than prompt-based formatting rules
- Exploratory or architectural work where debate, pushback, and alternatives are the point - the override rule lets you ask for that any time, but if that's your primary workflow this file will feel restrictive

**The honest trade-off:**
The CLAUDE.md file itself consumes input tokens on every message. The savings come from reduced output tokens. The net is only positive when output volume is high enough to offset the persistent input cost. At low usage it costs more than it saves.

---

## Benchmark Results

Same 5 prompts. Run without CLAUDE.md (baseline) then with CLAUDE.md (optimized).

| Test | Baseline | Optimized | Reduction |
|------|----------|-----------|-----------|
| Explain async/await | 180 words | 65 words | 64% |
| Code review | 120 words | 30 words | 75% |
| What is a REST API | 110 words | 55 words | 50% |
| Hallucination correction | 55 words | 20 words | 64% |
| **Total** | **465 words** | **170 words** | **63%** |

**~295 words saved per 4 prompts. Same information. Zero signal loss.**

> **Methodology note:** This is a 5-prompt directional indicator (T1-T3, T5 for word reduction; T4 is a format test), not a statistically controlled study. Claude's output length varies naturally between identical prompts. No variance controls or repeated runs were applied. Treat the 63% as a directional signal for output-heavy use cases, not a precise universal measurement. The CLAUDE.md file itself adds input tokens on every message - net savings only apply when output volume is high enough to offset that persistent cost.

### External benchmark (Issue #1)

An [independent benchmark](https://github.com/adam-s/testing-claude-agent) ran 6 configs across 3 coding challenges (CSV reporter, SQLite window functions, Hono WebSocket counter). All configs passed all tests, so comparison was purely cost-to-green.

We ran our own v8 config head-to-head against C-structured (the previous best) on the same harness, same day, same model:

| Challenge | M-drona23-v8 | C-structured | Winner |
|-----------|-------------|-------------|--------|
| CSV Reporter | $0.244 | $0.282 | v8 |
| SQLite Windows | $0.406 | $0.376 | C-structured |
| WebSocket | $0.285 | $0.473 | v8 |
| **Total** | **$0.935** | **$1.131** | **v8 (-17.4%)** |

The v8 config uses 2 files (7 lines total). The biggest win comes from WebSocket where explicit pattern rules prevent expensive debugging loops.

This repo keeps the root `CLAUDE.md` to a small set of high-impact rules to minimize recurring input overhead.

### At Scale

| Usage | Tokens Saved/Day | Monthly Savings (Sonnet) |
|-------|-----------------|--------------------------|
| 100 prompts/day | ~9,600 tokens | ~$0.86 |
| 1,000 prompts/day | ~96,000 tokens | ~$8.64 |
| 3 projects combined | ~288,000 tokens | ~$25.92 |

---

## Before vs After

**Without CLAUDE.md - Code Review:**
```
Great question! I can see you're working with a loop. Let me take a look at that.
That's a thoughtful piece of code! However, I notice there's actually a subtle bug
here that's worth pointing out. The condition i <= arr.length should be i < arr.length.
Using <= means the loop will run one extra iteration... You might also want to consider
using modern array methods like forEach, map, or for...of which are cleaner...
Great catch on reviewing this - it's always good practice to double-check loop
boundaries! I hope this review was helpful. Feel free to share more code anytime!
```
**120 words.**

**With CLAUDE.md - Same prompt:**
```
Bug: <= causes an off-by-one error. On the final iteration arr[arr.length] is undefined.

Fix:
for (let i = 0; i < arr.length; i++)
```
**30 words. Same fix. 75% fewer tokens.**

---

## What It Fixes

| # | Problem | Fix |
|---|---------|-----|
| 1 | Starts coding without context | Think first; read files before writing |
| 2 | Verbose responses | Keep output concise |
| 3 | Rewrites large files unnecessarily | Prefer targeted edits |
| 4 | Re-reading the same files | Read each file once unless it changed |
| 5 | Declaring done without validation | Run tests before finishing |
| 6 | Sycophantic chatter | No flattering preamble/closing fluff |
| 7 | Over-engineered solutions | Favor simple direct fixes |
| 8 | Prompt conflict confusion | User instructions always override |

---

## Pro Tips From the Community

**Scope rules to your actual failure modes, not generic ones.**
Generic rules like "be concise" help but the real wins come from targeting specific failures you've actually hit. For example if Claude silently swallows errors in your pipeline, add a rule like: "when a step fails, stop immediately and report the full error with traceback before attempting any fix." Specific beats generic every time.

**CLAUDE.md files compose - use that.**
Claude reads multiple CLAUDE.md files at once - global (~/.claude/CLAUDE.md), project-level, and subdirectory-level. This means:
- Keep general preferences (tone, format, ASCII rules) in your global file
- Keep project-specific constraints ("never modify /config without confirmation") at the project level
- Keep task-specific rules in subdirectory files

This avoids bloating any single file and keeps rules close to where they apply.

---

## Profiles

Different project types need different levels of compression.
Pick the base file + a profile, or use the base alone.

| Profile | Best For |
|---------|----------|
| `CLAUDE.md` | Universal - works for any project |
| `profiles/CLAUDE.benchmark.md` | Token-to-green coding benchmarks |
| `profiles/CLAUDE.coding.md` | Dev projects, code review, debugging |
| `profiles/CLAUDE.agents.md` | Automation pipelines, multi-agent systems |
| `profiles/CLAUDE.analysis.md` | Data analysis, research, reporting |

### Versioned Configuration Sets

The `profiles/` directory also contains three versioned configuration sets representing different optimization strategies. Pick the one that matches your workflow:

| Version | Strategy | Tool Budget | Best For |
|---------|----------|-------------|----------|
| `J-drona23-v5` | Multi-file structured | 50 calls | Complex projects needing detailed workflow rules and agent definitions |
| `K-drona23-v6` | One-shot execution | 50 calls | Tasks that should complete in a single pass with minimal iteration |
| `M-drona23-v8` | Ultra-lean minimum-turn | 20 calls | Cost-sensitive pipelines where every tool call counts |

**How to choose:**
- Start with **v5** if you need structured multi-step workflows with clear agent protocols
- Use **v6** if you want faster execution with strict "done means done" rules (no polishing passing code)
- Use **v8** only if you need maximum cost efficiency and your tasks are simple enough for 20 tool calls

### Two Ways to Apply Rules

**Option A: CLAUDE.md file (recommended for regular use)**
- Drop file in project root
- Automatic on every message
- Cached efficiently
- Better for repeated tasks, pipelines

**Option B: Rules in prompt (for one-off sessions)**
- Copy-paste rules into chat
- Works without setup
- Clear what applies this session
- Good for quick tasks

**Cost comparison** (benchmarked on 3 coding challenges):

| Method | CSV | SQLite | WebSocket | Total | Cost vs v8 |
|--------|-----|--------|-----------|-------|-----------|
| Rules pasted in chat | $0.274 | $0.459 | $0.585 | $1.318 | +41% |
| **CLAUDE.md (v8)** | **$0.244** | **$0.406** | **$0.285** | **$0.935** | baseline |

Both pass all tests. Pick based on your workflow.

---

## How to Use

**Option 1 - Universal (any project):**
```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/drona23/claude-token-efficient/main/CLAUDE.md
```

**Option 2 - Clone and pick a profile:**
```bash
git clone https://github.com/drona23/claude-token-efficient
cp claude-token-efficient/profiles/CLAUDE.coding.md your-project/CLAUDE.md
```

**Option 3 - Manual:**
Copy the contents of `CLAUDE.md` from this repo into your project root.

---

## Override Rule

User instructions always win.
If you explicitly ask for a detailed explanation or verbose output, Claude will follow your instruction - the file never fights you.

---

## Contributing

Found a behavior that CLAUDE.md can fix?
Open an issue with:
1. The annoying behavior (what Claude does by default)
2. The prompt that triggers it
3. The fix rule you propose

Community submissions become part of the next version with full credit.

---

## Validation

Full benchmark results with before/after word counts:
See [BENCHMARK.md](./BENCHMARK.md)

---

## References and Credits

This project was built on real complaints from the Claude community.
Full credit to every source that contributed a fix:

- [GitHub #3382 - "Claude says You're absolutely right about everything"](https://github.com/anthropics/claude-code/issues/3382) - 350+ upvotes
- [GitHub #14759 - "Sycophantic behavior undermines usefulness as coding assistant"](https://github.com/anthropics/claude-code/issues/14759)
- [GitHub #9340 - "Add --quiet flag to suppress tool call output"](https://github.com/anthropics/claude-code/issues/9340)
- [GitHub #21818 - "Tool Output Verbosity Creates Visual Noise"](https://github.com/anthropics/claude-code/issues/21818)
- [GitHub #20542 - "Verbose output overwhelms session and consumes excessive tokens"](https://github.com/anthropics/claude-code/issues/20542)
- [The Register - "Claude Code's endless sycophancy annoys customers"](https://www.theregister.com/2025/08/13/claude_codes_copious_coddling_confounds/)
- [DEV Community - "7 Ways to Cut Your Claude Code Token Usage"](https://dev.to/boucle2026/7-ways-to-cut-your-claude-code-token-usage-elb)
- [Medium - "Stop Wasting Tokens: Optimize Claude Code Context by 60%"](https://medium.com/@jpranav97/stop-wasting-tokens-how-to-optimize-claude-code-context-by-60-bfad6fd477e5)
- [Anthropic Docs - Reduce Hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- [PromptHub - "Three Prompt Engineering Methods to Reduce Hallucinations"](https://www.prompthub.us/blog/three-prompt-engineering-methods-to-reduce-hallucinations)
- [GitHub Gist - Practical workflow for reducing token usage](https://gist.github.com/dholdaway/8009f089d3407e14f3d753f2a70eb63e)
- [Token Checkup - Free diagnostic for token consumption patterns](https://yurukusa.github.io/cc-safe-setup/token-checkup.html) - 5-question browser tool that analyzes your Claude Code token usage and suggests optimizations
- [Cache Health Checker - Diagnose cache efficiency from /cost output](https://yurukusa.github.io/cc-safe-setup/cache-health.html) - paste your `/cost` output to check if prompt caching is working correctly
- [Claude Code Best Practices - community](https://rosmur.github.io/claudecode-best-practices/)
- [Vaibhav Sisinty - GrowthSchool](https://growthschool.io) - AI upskilling and prompt engineering best practices
- [Vaibhav Sisinty on X](https://x.com/VaibhavSisinty) - Active discussions on Claude prompt optimization and AI workflows

---

## License

MIT - free to use, modify, and distribute.

---

*Built by [Drona Gangarapu](https://github.com/drona23) - open to PRs, issues, and profile contributions.*
