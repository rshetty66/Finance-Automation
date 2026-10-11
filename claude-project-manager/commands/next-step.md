---
description: Determine and suggest the next step based on dependencies
---

# Next Step

Analyze project state and orchestration rules to recommend the immediate next action.

## Process

### 1. Read Project State

Read `project-state.md` to get:
- Current phase
- Status of all 34 artifacts
- Which artifacts are "approved", "in_progress", "not started"

### 2. Read Orchestration Map

Read `references/orchestration-map.md` to understand:
- Artifact dependencies (which artifacts must complete before others can start)
- Skill-to-artifact mapping (which skills produce which artifacts)
- Phase progression rules
- Blocking conditions for phase transitions

### 3. Identify Available Next Steps

For each artifact with status "approved":
- Check if all dependent prerequisites have status "completed"
- If yes, that artifact is "ready to execute"

For each artifact with status "not started":
- Check if all dependencies have status "approved" or "completed"
- If yes, and no other blocker exists, that artifact is "available to start"

### 4. Validate Input Data

For each available artifact:
- Check if required input data exists in `input/` folder
- Verify data completeness (no critical missing fields)
- If data is missing, flag as "blocked pending input"

### 5. Present Recommendations

Display 1-3 recommended next steps in priority order:

```
# Recommended Next Steps

## Priority 1: [Artifact Name] (ID: #X)
**Status**: [Ready to execute / Available to start / Blocked]
**Skill**: [Skill name from orchestration map]
**Dependencies**: [All satisfied / Missing Y, Z]
**Rationale**: [Why this is the next logical step]

**Action**: 
- If ready: "Run skill [skill-name] now"
- If blocked: "Waiting for [artifact] or [input file] — see requirements below"

---

## Priority 2: [Artifact Name] (ID: #Y)
[Same format]

---

## Priority 3: [Artifact Name] (ID: #Z)
[Same format]

---

## Blocking Issues (if any)
- [Issue 1]: Cannot proceed to Phase N without artifact #M
- [Issue 2]: Missing input: [file name] required for artifact #X
```

### 6. Offer Confirmation

If user confirms the recommended step:
- Extract skill name
- Trigger skill with appropriate parameters
- Pass `artifact_id`, `phase`, `project_path` to the skill
- Update project-state.md upon skill completion

If user wants different step:
- Ask which alternative they prefer
- Validate that alternative's dependencies
- Proceed with their choice

If user indicates input data is missing:
- Guide them to `input/` folder
- Explain required file format and fields
- Recommend re-running this command after data is added

## Completion

Log the recommended next step in `logs/log.md`:
```
[TIMESTAMP] | NEXT-STEP | analysis_complete | Recommended: [artifact name] (ID: #X)
```

After skill execution, return to this command to identify subsequent steps.
