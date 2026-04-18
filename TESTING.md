# Dex Checkpointing — Testing Guide

This document describes the end-to-end test scenarios for exercising the Dex
checkpoint system (008-interactive-checkpoint + 009-testing-checkpointing)
against this example project.

All scenarios below use the **mock agent backend** (009). It replays a
scripted, deterministic "run" in seconds at zero API cost. Real runs are
validated separately against real Claude.

---

## Prerequisites

1. Dex dev environment running:
   ```bash
   cd /home/lukas/Projects/Github/lukaskellerstein/dex
   ./dev-setup.sh
   ```
   Expect `~/.dex/dev-logs/electron.log` to contain
   `DevTools listening on ws://127.0.0.1:9333/...`.

2. This project reset to the committed main:
   ```bash
   cd /home/lukas/Projects/Github/lukaskellerstein/dex
   ./scripts/reset-example-to.sh clean
   ```
   Afterwards `ls dex-ecommerce` should show `.dex/`, `.gitignore`, `GOAL.md`,
   and `TESTING.md`.

3. The mock agent is selected (verified by committed `.dex/dex-config.json`):
   ```bash
   cat .dex/dex-config.json    # → { "agent": "mock" }
   ```

4. The mock script is present (verified by committed `.dex/mock-config.json`):
   ```bash
   node /home/lukas/Projects/Github/lukaskellerstein/dex/scripts/validate-mock-config.mjs \
        /home/lukas/Projects/Github/lukaskellerstein/dex-ecommerce
   ```
   Expect `✓ all fixture 'from' paths resolve`.

---

## Scenario 1 — Happy path (T033)

**Goal**: A full 3-cycle mock run completes end-to-end in under 60 s,
produces the same checkpoint tags / artifacts a real run would produce.

**Steps**:

1. From the welcome screen, fill:
   - Parent: `/home/lukas/Projects/Github/lukaskellerstein`
   - Name: `dex-ecommerce`
2. Click **Open Existing**.
3. On the loop page, toggle **Automatic Clarification** on.
4. Click **Start Autonomous Loop**.
5. Watch the trace view. Three cycles run (f-001 Authentication → f-002
   Payments → f-003 Final feature). Loop terminates cleanly when the
   manifest shows no pending features.

**Expected observables**:

| Check | Expected |
|---|---|
| Wall-clock start→terminate | < 60 s |
| Stage events per cycle | `gap_analysis → specify → plan → tasks → implement → verify → learnings` |
| Total cycles | 3 full cycles + 1 terminator iteration that breaks immediately |
| External API cost | $0 |

**Post-run assertions** (shell):

```bash
cd /home/lukas/Projects/Github/lukaskellerstein/dex-ecommerce

# Every stage in every cycle got a checkpoint tag
git tag --list 'checkpoint/*' | sort

# Every checkpoint commit has a non-empty diff
git log --all --grep='^\[checkpoint:' --stat | head -100

# Filesystem artifacts
ls .dex/feature-manifest.json .dex/learnings.md
ls specs/*/spec.md specs/*/plan.md specs/*/tasks.md
ls src/mock/*.ts

# Learnings has exactly 3 bulleted lines (one per implement cycle)
cat .dex/learnings.md
```

**Success criteria**: SC-001, SC-004, SC-009 from the 009 spec.

---

## Scenario 2 — Go Back (T044)

**Goal**: Clicking Go Back on a mid-cycle checkpoint creates an attempt
branch whose working tree matches that checkpoint's committed state.

**Steps**:

1. Start from a completed Scenario 1 run.
2. Open the Loop Dashboard → checkpoint timeline.
3. Click Go Back on a cycle-2 stage (e.g., `cycle-2-after-specify`).

**Expected**:

- An `attempt-<timestamp>` branch is created.
- `git status` shows the working tree matches the checkpoint commit.
- The trace view shows the loop is paused/reset at that checkpoint.

**Shell check**:

```bash
git branch --list 'attempt-*'
git log --oneline HEAD | head -5
```

---

## Scenario 3 — Step Mode (T045)

**Goal**: With Step Mode on, the loop pauses after each stage; Continue
advances by exactly one stage.

**Steps**:

1. Reset the project (`./scripts/reset-example-to.sh clean` in the Dex repo).
2. Toggle Step Mode on before starting the loop.
3. Click Start. Observe the loop pauses after the first stage.
4. Click Continue; verify exactly one stage advances.
5. Continue advancing; verify the loop can complete normally.

---

## Scenario 4 — Record Mode (T046)

**Goal**: With Record Mode on, every checkpoint candidate is auto-promoted.

**Steps**:

1. Reset the project.
2. Toggle Record Mode on.
3. Run the loop end-to-end.
4. Verify `capture/*` branches/tags are auto-created per the 008 Record Mode
   contract.

**Shell check**:

```bash
git branch --list 'capture/*'
```

---

## Scenario 5 — Loud drift: missing script entry (T036)

**Goal**: When the mock script is missing an entry, the run halts within
one stage of the missing coordinate with a coordinate-level error.

**Steps**:

1. Reset the project.
2. In `.dex/mock-config.json`, delete `dex_loop.cycles[1].stages.implement`.
3. Start the loop.
4. Observe the loop advances through cycle 1 (f-001), advances into cycle 2
   (f-002) through specify/plan/tasks, and halts at `implement`.

**Expected error** (in `~/.dex/logs/dex-ecommerce/<runId>/run.log`):

```
MockConfigMissingEntryError: no script entry for phase=dex_loop, stage=implement, cycle=2, feature=f-002. Update .dex/mock-config.json.
```

---

## Scenario 6 — Loud drift: missing fixture (T037)

**Goal**: When a referenced fixture file is absent, the run halts with the
resolved path named.

**Steps**:

1. Reset the project.
2. Rename `/home/lukas/Projects/Github/lukaskellerstein/dex/fixtures/mock-run/f2-spec.md`
   to `f2-spec.md.bak`.
3. Start the loop.
4. Observe the loop halts at cycle-2 `specify`.
5. Restore the fixture filename at the end of the test.

**Expected error**:

```
MockFixtureMissingError: fixture file not found at /home/lukas/Projects/Github/lukaskellerstein/dex/fixtures/mock-run/f2-spec.md
```

---

## Scenario 7 — Unknown agent (T035 extended)

**Goal**: Unknown agent name in `dex-config.json` fails at startup with a
message listing the registered names.

**Steps**:

1. Edit `.dex/dex-config.json` to `{ "agent": "codex" }`.
2. Start the loop.
3. Observe startup fails immediately.

**Expected**:

```
UnknownAgentError: Unknown agent: 'codex'. Registered: claude, mock
```

Restore `dex-config.json` afterwards.

---

## Switching back to real Claude

```bash
echo '{ "agent": "claude" }' > .dex/dex-config.json
./scripts/reset-example-to.sh clean   # optional
```

Or delete the file — absent dex-config.json defaults to `agent: "claude"`.

---

## Diagnostic tools

- `~/.dex/dev-logs/electron.log` — main-process stdout (IPC, orchestrator
  events). Truncated on every dev-setup.sh restart.
- `~/.dex/logs/dex-ecommerce/<runId>/run.log` — per-run orchestrator log.
- `~/.dex/logs/dex-ecommerce/<runId>/phase-<N>_*/agent.log` — per-stage
  mock events.
- `scripts/validate-mock-config.mjs` (in the Dex repo) — validates
  `.dex/dex-config.json` + `.dex/mock-config.json` without running the
  orchestrator.
- DEBUG badge in the UI breadcrumb — click to copy RunID + PhaseTraceID.
