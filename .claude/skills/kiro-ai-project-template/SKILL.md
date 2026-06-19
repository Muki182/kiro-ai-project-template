```markdown
# kiro-ai-project-template Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns and conventions used in the `kiro-ai-project-template` TypeScript repository. You'll learn about file naming, import/export styles, commit patterns, and how to write and organize tests. While no specific workflows were detected, this guide provides best practices and suggested commands to streamline your development process.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `userProfile.ts`, `dataFetcher.ts`

### Imports
- Use **relative imports** for internal modules.
  - Example:
    ```typescript
    import { fetchData } from './dataFetcher';
    ```

### Exports
- Use **named exports** for all modules.
  - Example:
    ```typescript
    // In userProfile.ts
    export function getUserProfile(id: string) { ... }
    ```

### Commit Patterns
- Commit messages are **freeform** (no enforced prefix).
- Average commit message length: **80 characters**.
- Example:
  ```
  Add initial implementation of user authentication and session management
  ```

## Workflows

### Adding a New Module
**Trigger:** When you need to add a new feature or utility.
**Command:** `/add-module`

1. Create a new file using camelCase naming (e.g., `newFeature.ts`).
2. Use relative imports to bring in dependencies.
3. Export your functions or types using named exports.
4. Write corresponding tests in a `*.test.ts` file.

### Writing Tests
**Trigger:** When you add or update functionality.
**Command:** `/write-test`

1. Create a test file with the same base name as the module, ending with `.test.ts` (e.g., `userProfile.test.ts`).
2. Use your preferred testing framework (not specified in this repo).
3. Structure tests to cover all exported functions.

## Testing Patterns

- Test files follow the `*.test.*` pattern (e.g., `dataFetcher.test.ts`).
- Place test files alongside the modules they test or in a dedicated `tests` directory.
- No specific testing framework detected; choose one that fits your needs (e.g., Jest, Mocha).
- Example test file:
  ```typescript
  // userProfile.test.ts
  import { getUserProfile } from './userProfile';

  describe('getUserProfile', () => {
    it('returns correct user data', () => {
      // Test implementation
    });
  });
  ```

## Commands
| Command       | Purpose                                    |
|---------------|--------------------------------------------|
| /add-module   | Scaffold a new module with conventions     |
| /write-test   | Create a test file for a module            |
```
