# Subagent Prompt Template

Use this template when creating `.parallel/prompts/TASK-{id}.md` files.
Fill in all `{placeholders}` with specific, unambiguous content.
The goal: a subagent receiving this prompt can execute with ZERO clarifying questions.

---

## Template

```markdown
# Subagent Prompt: TASK-{id} — {task_name}

## Your Role
You are a specialist agent working on ONE specific subtask of a larger feature.
You have ONE job. Do it completely and correctly. Another agent is handling the
other parts — focus ONLY on your assigned scope.

## Your Task
{Detailed description of what to build. Be specific:
- NOT "implement the auth module"
- YES "Create a JWT authentication module with login/logout endpoints,
  token generation using python-jose, password hashing with passlib/bcrypt,
  and a dependency injection function get_current_user() that validates
  the Bearer token from the Authorization header."}

## Project Context
- **Tech Stack**: {language, framework, key libraries}
- **Conventions**: {naming, file structure, patterns used in this project}
- **Existing Code**: {relevant existing files/structures the agent should know about}

## Dependencies (Output from Prior Tasks)
{For Layer 0 tasks:}
None — you have no dependencies. Work independently.

{For Layer 1+ tasks:}
The following outputs from prior tasks are provided as context.
Use them exactly as-is. Do NOT modify or reimplement anything from these outputs.

### From TASK-{dep_id}: {dep_name}
\```
{Paste the COMPLETE output from the dependency task here — VERBATIM, never summarized}
\```

## Interface Contract
- **You MUST produce**: {exact files, with paths}
- **You MUST NOT**: {boundary conditions — what's out of scope}
- **You CAN assume**: {what other tasks are handling}
- **Output format**: {code language, structure requirements}

## Technical Requirements
- {Specific library versions, patterns, conventions}
- {API contracts to follow}
- {Data models to use}

## Quality Standards
- Production-ready code (no TODOs, no placeholders, no "implement later")
- All functions: docstrings + type hints
- Error handling for all edge cases
- Imports at top of file, organized

## Output Instructions
Write your complete output. Create the actual files with full implementation.
Do NOT explain your reasoning. Just produce the deliverable.
```

---

## Prompt Quality Checklist

Before sending any prompt to a subagent, verify:

- [ ] Objective is specific and unambiguous (not "build the thing")
- [ ] Output format is explicit (exact file paths, schemas)
- [ ] Boundary conditions state what NOT to do
- [ ] Dependencies are included verbatim (never summarized)
- [ ] Tech stack and conventions are specified
- [ ] A competent developer could execute with ZERO questions

## Tips

1. **Be specific about output** — "Return a Python module with classes User and Session" beats "Write the database models"
2. **Include dependency output verbatim** — Don't summarize; let the agent see the full interface
3. **State boundaries explicitly** — "Do NOT implement the API routes" prevents overlap
4. **Specify error handling** — "Raise ValueError for invalid inputs" beats "handle errors"
5. **Keep prompts focused** — Each prompt = ONE clear deliverable
