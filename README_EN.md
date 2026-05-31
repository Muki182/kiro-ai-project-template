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
├── .kiro/
│   ├── steering/
│   │   └── project.md          # Project-level global context (architecture constraints, tech stack, naming conventions)
│   ├── specs/
│   │   ├── 01-architecture.md  # Architecture design spec (requirements + task breakdown)
│   │   └── 02-implementation.md # Implementation phase spec
│   └── hooks/
│       ├── doc-sync.yml        # Auto-sync docs after code changes
│       ├── spec-validate.yml   # Validate implementation against spec after changes
│       └── test-trigger.yml    # Trigger test coverage review on interface changes
├── docs/
│   └── workflow-guide.md       # Workflow usage guide
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

## License

MIT
