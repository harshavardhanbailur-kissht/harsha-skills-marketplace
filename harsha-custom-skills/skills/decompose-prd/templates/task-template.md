# Task: T-{epic}.{feature}.{task}: {Action Verb} {Object}

## Metadata
- Epic: E-{epic}: {epic name}
- Feature: F-{epic}.{feature}: {feature name}
- Priority: P{0-3}
- Effort: {XS/S/M/L/XL}
- Execution Layer: {0/1/2/3}
- Critical Path: {Yes/No}
- Domain: {Frontend/Backend/Infrastructure/Data/ML/Security}

## Objective
{Exactly what must be produced — specific, unambiguous, measurable.
The "Zero Questions Test": a competent developer can execute this with zero clarifying questions.}

## Context
{Project context needed to execute:
- Tech stack and versions
- Architectural patterns in use
- Coding conventions and style
- Relevant existing code/files}

## Inputs
| Source | Description | Format |
|--------|-------------|--------|
| PRD | REQ-{id}: {requirement} | Requirement text |
| Task T-{x}.{y}.{z} | {what this provides} | {file format} |
| Existing code | {specific file} | {language} |

## Expected Output
| File Path | Description | Format |
|-----------|-------------|--------|
| {path/to/file.ext} | {what this file contains} | {language/format} |
| {path/to/file.ext} | {what this file contains} | {language/format} |

## Technical Requirements
- Language: {specific language and version}
- Framework: {specific framework}
- Libraries: {specific packages with versions}
- Patterns: {specific design patterns to follow}
- Performance: {specific targets if applicable}

## Boundary Conditions
### DO NOT:
- {specific thing out of scope}
- {specific file not to modify}
- {specific pattern not to use}

### ASSUMPTIONS:
- {what this task can safely assume about other tasks}
- {what infrastructure/services are available}

## Acceptance Criteria
- [ ] Given {precondition}, when {action}, then {result}
- [ ] Given {precondition}, when {action}, then {result}
- [ ] Given {precondition}, when {action}, then {result}

## Verification
- **Syntax**: {how to verify — linting command, type check, ast.parse}
- **Unit Test**: {specific test to run or write}
- **Integration**: {how this connects to adjacent tasks}
- **Manual**: {what to visually/functionally verify}

## Estimated Output Size
~{N} lines / ~{N} tokens
