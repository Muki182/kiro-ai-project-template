# kiro-ai-project-template

> A Kiro project template for AI research engineering — structured spec layout, layered hook configuration, and context management strategy for long-running AI system projects.

[简体中文](./README.md) | English

---

## Motivation

AI system development involves long iteration cycles, complex inter-module dependencies, and frequent requirement changes. Most AI coding tools struggle with two core problems in this context:

1. **Context drift**: After many conversation turns, the implementation gradually diverges from the original design intent
2. **Missing acceptance criteria**: Generated code has no explicit binding to requirements, making automated consistency verification impossible

Kiro's spec-driven development model solves both by structurally binding requirements, implementation, and validation. This template codifies that approach into a reusable project scaffold.

---

## Use Cases

- AI model training / inference system design and implementation
- Multi-module AI pipeline engineering
- Research engineering projects that require long-term iterative maintenance
- Team-collaborative AI application development

---

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml              # CI: ruff + mypy + pytest
├── .kiro/
│   ├── steering/
│   │   └── project.md          # Project-level global context (architecture constraints, tech stack, naming conventions)
│   ├── specs/
│   │   ├── 01-architecture.md  # Architecture design spec (requirements + task breakdown)
│   │   ├── 02-implementation.md # Implementation phase spec
│   │   └── examples/           # Worked examples (MNIST classifier)
│   └── hooks/
│       ├── doc-sync.yml        # Auto-sync docs after code changes
│       ├── spec-validate.yml   # Validate implementation against spec after changes
│       └── test-trigger.yml    # Trigger test coverage review on interface changes
├── src/                        # Source skeleton (data / models / training / inference / utils)
├── tests/                      # Tests, mirroring the src/ layout
├── config/                     # YAML configuration files
├── scripts/                    # One-off scripts
├── docs/
│   └── workflow-guide.md       # Workflow usage guide
├── pyproject.toml              # ruff / mypy / pytest configuration
└── README.md
```

---

## Quick Start

### 1. Create your project from this template

Click **Use this template** → **Create a new repository**

### 2. Open with Kiro

```bash
git clone https://github.com/your-username/your-project
# Open in Kiro Desktop or VS Code with the Kiro extension
```

### 3. Customize the steering file

Edit `.kiro/steering/project.md` with your project's architecture constraints, tech stack, and naming conventions. This is the global context that Kiro Agent references across all tasks.

### 4. Write your first spec

Use `.kiro/specs/01-architecture.md` as a format reference. Core elements:
- **Requirements list**: Numbered, verifiable functional requirements
- **Task breakdown**: Implementation task checklist mapped to requirements
- **Acceptance criteria**: Completion standard for each requirement

### 5. Activate hooks

Hooks load automatically when the project opens. Enable or adjust trigger conditions in `.kiro/hooks/` as needed.

---

## Spec Design Principles

The spec structure in this template follows these principles:

| Principle | Description |
|-----------|-------------|
| **Atomicity** | Each requirement is independently verifiable, with no implicit dependencies on other requirements |
| **Traceability** | Every implementation task must map to at least one requirement number |
| **Layered decomposition** | Large modules are split into multiple spec files along functional boundaries to avoid single-file context overload |
| **Explicit state** | Task completion is tracked via checkboxes, not conversation history |

---

## Hook Strategy

### `doc-sync.yml`
**Trigger**: Any `.py` file change under `src/`
**Behavior**: Prompts the Agent to check whether the docstrings of the affected modules and the corresponding docs under `docs/` need to be synced.

### `spec-validate.yml`
**Trigger**: Changes to core module files
**Behavior**: Checks the implementation against the requirement list in the corresponding spec file, confirming each acceptance criterion and emitting a diff report.

### `test-trigger.yml`
**Trigger**: Changes to interface definition files (`*_interface.py` / `*.proto`)
**Behavior**: Prompts the Agent to review existing test coverage and suggest missing boundary tests.

---

## Comparison with Other Tools

| Dimension | Traditional AI coding assistant | Kiro (this template) |
|-----------|---------------------------------|----------------------|
| Requirement persistence | Relies on conversation history; lost when the session ends | Specs stored persistently, valid across sessions |
| Implementation consistency | No explicit validation mechanism | Hooks trigger consistency checks automatically |
| Context management | Global injection; large projects exceed limits | Steering + layered specs, loaded on demand |
| Task status | No structured tracking | Checkbox task list with visible status |
| Team collaboration | Personal conversations, hard to share | Specs tracked in version control |

---

## Contributing

Contributions via Issues or PRs are welcome, especially:
- Specialized spec templates for specific AI frameworks (PyTorch / JAX / vLLM, etc.)
- More fine-grained hook configuration examples
- Real-world project use cases

---

## License

MIT
