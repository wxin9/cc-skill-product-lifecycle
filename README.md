[English](README.md) | [中文](README.zh-CN.md)

# Product Lifecycle

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Release](https://img.shields.io/github/v/release/wxin9/cc-skill-product-lifecycle)](https://github.com/wxin9/cc-skill-product-lifecycle/releases)

> **Script-Orchestrated + Interaction-Paused** product lifecycle management — orchestrator auto-executes phase sequences, pauses at interaction points, notifies model to handle, then resumes

## 🎯 Core Value

**Problems Solved**:
- ❌ Model-driven workflow: Model forgets midway, subsequent scripts never run
- ❌ Manual step execution: User must know next command
- ❌ No interaction handling: Model cannot pause for user input
- ❌ No failure recovery: Validation failure blocks entire workflow

**Solution**:
- ✅ **Script-orchestrated engine**: Orchestrator auto-executes phase sequences
- ✅ **Interaction pauses**: Orchestrator pauses at user review/interview nodes, notifies model
- ✅ **Failure recovery**: Validation/DoD failure pauses workflow, model fixes and resumes
- ✅ **State persistence**: Checkpoint records phase-level state, supports resume from breakpoint

## ⭐ What's New

### v2.1.0 — Solution Analyzer + Phase Renumbering

- **Solution Analyzer**: New Phase 1 analyzes requirements, project code, and industry solutions — generates multiple implementation options for user selection
- **Phase 1 added**: Implementation solution analysis before project initialization
- **Phase renumbering**: Phase 1-10 → Phase 1-11 (checkpoint auto-migrates from v2.0)
- **Checkpoint v2.1**: Automatic migration from v2.0 with backup and Phase ID remapping

### v2.0.1 — Checkpoint Tracking Improvements

- **Intent always recorded**: Intent and user_input now update on every run (not just initial)
- **Resume fixed**: `get_phases_by_intent("resume")` returns all phases correctly
- **Auto PRD snapshots**: SnapshotManager integrated into validate command — snapshots created automatically after validation
- **Phase sequence fixes**: Phase 10 depends_on corrected; prd-change now includes Phase 7-8

### v2.0.0 — Orchestrator Architecture

#### 1. Orchestrator Engine
- **Script-orchestrated workflow**: Auto-executes phase sequences based on intent
- **State machine**: Phase-level state transitions with dependency checking
- **No model memory needed**: Orchestrator handles entire workflow, model just responds to notifications

#### 2. Interaction Pauses
- **Automatic pause**: Orchestrator pauses at user review/interview nodes
- **Dual notification**: stdout + `.lifecycle/notification.json`
- **Resume support**: Model fixes issues and calls `resume` to continue

#### 3. Failure Recovery
- **Validation failure**: Orchestrator pauses, model fixes and retries
- **DoD failure**: Orchestrator pauses, model resolves and continues
- **Retry strategy**: Configurable retry count per phase

#### 4. Checkpoint Manager
- **Phase-level state**: Records completed phases, current phase, phase data
- **Auto-migration**: Migrates legacy `steps/` format to `checkpoint.json`
- **Resume from breakpoint**: Load checkpoint and continue from paused phase
- **Memory caching**: In-memory cache with delayed writing — 25x I/O reduction
- **Thread-safe**: RLock-based concurrency control

#### 5. Intent Resolver
- **Regex matching**: Pattern-based intent recognition
- **Priority ranking**: Bug-fix (1) > PRD-change (3) > New-product (9)
- **Compound intent**: Handles multiple intents in sequence

#### 6. Parallel Execution
- **ParallelExecutor**: Topological sort using Kahn's algorithm for dependency graph analysis
- **Parallel groups**: Independent phases execute concurrently (enable via `ORCHESTRATOR_PARALLEL=1`)

#### 7. Conditional Branching
- **ConditionEvaluator**: Safely evaluates condition expressions for dynamic execution paths
- **Supported operators**: Comparison (`==`, `!=`, `<`, `>`, `<=`, `>=`), logical (`and`, `or`, `not`), membership (`in`, `not in`)

#### 8. Rollback Mechanism
- **File snapshots**: Auto-creates snapshots of `Docs/` and `.lifecycle/` before each phase
- **Rollback to any point**: Restore checkpoint state and files to any previous rollback point
- **Rollback CLI**: `./orchestrator rollback --id <rollback-id>`

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/wxin9/cc-skill-product-lifecycle.git

# Install as Claude Code skill
cp -r cc-skill-product-lifecycle ~/.claude/skills/product-lifecycle
```

### Usage (Orchestrator Commands)

After installation, use orchestrator commands:

```bash
# Start new product workflow
./orchestrator run --intent new-product --user-input "I want to build a task manager"

# Orchestrator will:
# 1. Pause at Phase 1 — Analyze solution options
# 2. Execute Phase 2 (auto) — Create doc structure
# 3. Pause at Phase 3 — Notify model: "Waiting for PRD review"
# 4. Model generates PRD draft
# 5. Resume: ./orchestrator resume --from-phase phase-3-draft-prd
# 6. Continue Phase 4-10...
```

**Example Conversation**:

```
You: "I want to build a task manager"
Claude: [Calls ./orchestrator run --intent new-product]
        [Orchestrator pauses at Phase 1]
        [Notification: "Waiting for solution selection"]
        [Claude analyzes and presents solution options]
        [Calls ./orchestrator resume --from-phase phase-1-analyze-solution]
        [Orchestrator pauses at Phase 3]
        [Notification: "Waiting for PRD review"]
        [Claude generates PRD draft]
        [Calls ./orchestrator resume]

You: "Requirements changed, need to add payment"
Claude: [Calls ./orchestrator run --intent prd-change]
        [Orchestrator executes Phase 11 → Phase 3 → Phase 4...]

You: "Found a bug in login flow"
Claude: [Calls ./orchestrator run --intent bug-fix]
        [Orchestrator executes Phase 11 failure handling → pause for fix]
```

## 💡 Core Features

| Feature | Description |
|---------|-------------|
| **AI-Collaborative Drafting** | Claude actively drafts PRD/architecture, you review |
| **Script-Enforced Gates** | `sys.exit(1)` physical blocking, cannot skip steps |
| **Compound Intent Recognition** | "Fixed bug and want to adjust requirements" — recognizes multiple intents, prioritizes and executes |
| **Project Type Auto-Detection** | 5 types (Web/CLI/Mobile/Data/Microservices), test dimensions self-adapt |
| **Auto-Snapshot & Diff** | Auto-snapshot on validation, auto-diff on change |
| **Velocity Tracking** | Estimated vs actual hours + ASCII trend charts |
| **DoD Gate Extension** | lint/coverage/code review, warn or fail |
| **ADR Management** | Architecture Decision Record full lifecycle |
| **Risk Register** | Probability×impact matrix auto-rating |
| **Sprint Review** | Auto-generates review materials on gate pass |
| **Parallel Execution** | Independent phases run concurrently with topological sort |
| **Conditional Branching** | Dynamic execution paths based on project type/conditions |
| **Rollback** | Revert to any previous checkpoint with file snapshot restoration |

## 📖 Workflow

```
Phase 0: Intent Recognition
   ↓
Phase 1: Solution Analysis → Analyze requirements, code & industry solutions
   ↓
Phase 2: Project Init → DoD/Risk/ADR setup
   ↓
Phase 3: AI Draft PRD → You review
   ↓
Phase 4: Validate PRD → Auto-snapshot
   ↓
Phase 5: Architecture Interview
   ↓
Phase 6: AI Draft Architecture → Includes ADR draft
   ↓
Phase 7: Validate Architecture → Auto-snapshot
   ↓
Phase 8: Generate Test Graph + Adaptive Outline
   ↓
Phase 9: Plan Iterations → Velocity estimation
   ↓
Phase 10: Execute Iterations → 4-layer gate validation
   ↓
Phase 11: Handle Changes → Graph traversal cascade update
```

### Change Intent Paths

| Intent | Phase Sequence |
|--------|---------------|
| `new-product` | Phase 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 |
| `prd-change` | Phase 11 → 3 → 4 → 5 → 6 → 7 → 8 → 9 |
| `arch-change` | Phase 11 → 6 → 7 → 8 → 9 |
| `bug-fix` | Phase 11 → pause for fix |
| `new-iteration` | Phase 9 → 10 |
| `resume` | Continue from checkpoint |

## 🛠️ Commands

### Orchestrator Commands

```bash
# Start orchestration
./orchestrator run --intent new-product --user-input "I want to build a product"

# Resume from paused state
./orchestrator resume --from-phase phase-3-draft-prd

# Show status
./orchestrator status

# Cancel workflow
./orchestrator cancel

# Parallel execution (opt-in)
ORCHESTRATOR_PARALLEL=1 ./orchestrator run --intent new-product --user-input "..."
```

## 📊 Generated Project Structure

```
Docs/
├── product/PRD.md          # PRD document
├── tech/ARCH.md            # Architecture document
├── tests/MASTER_OUTLINE.md # Test outline
└── iterations/iter-N/      # Iteration plan + test records + Sprint Review

.lifecycle/
├── checkpoint.json         # Phase-level state (v2.1+)
├── notification.json       # Pause/failure notifications (v2.0+)
├── test_graph.json         # Test Knowledge Graph
├── config.json             # Project configuration
├── dod.json                # DoD rules
├── risk_register.json      # Risk register
├── velocity.json           # Velocity tracking
└── snapshots/              # Document snapshots + rollback points
```

## 🎓 Model Compatibility

- **Recommended**: Claude Sonnet 4+ — Best drafting quality
- **Usable**: Claude Haiku — Can complete full workflow, slightly lower drafting quality
- **Core Mechanism**: Orchestrator handles workflow, model just responds to notifications

## 📚 Documentation

- [CONTRIBUTING.md](docs/CONTRIBUTING.md) — Development guide
- [CODE_OF_CONDUCT.md](docs/CODE_OF_CONDUCT.md) — Contributor covenant
- [SECURITY.md](docs/SECURITY.md) — Security policy
- [CHANGELOG.md](CHANGELOG.md) — Version history

## 📄 License

Apache License 2.0 — see [LICENSE](LICENSE)

## 🏢 Commercial Use

For commercial use, please include attribution in your product documentation:

```
This product uses Product-Lifecycle Skill (https://github.com/wxin9/cc-skill-product-lifecycle)
Copyright 2026 Kaiser (wxin966@gmail.com)
Apache License 2.0
```

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md) | **GitHub**: [wxin9/cc-skill-product-lifecycle](https://github.com/wxin9/cc-skill-product-lifecycle)
