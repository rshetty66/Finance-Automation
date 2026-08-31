# Reusable Prompt Template — AI Consulting Workflows

Built on Andrej Karpathy's Spec → Verifier → Environment framework, adapted for finance transformation, ERP/EPM, and consulting deliverable work. Fill in the bracketed fields; delete what you don't need.

Sources: [The Karpathy Method](https://blog.radlak.com/auto-content/2026/06/12/the-karpathy-method-how-to-prompt-claude-10x-faster-using-a-three-layer-framework/), [Karpathy's AI Engineering Playbook](https://www.aibuilderclub.com/blog/karpathy-ai-engineering-playbook), [Karpathy's CLAUDE.md guide](https://drol.dev/blog/andrej-karpathy-claude-md-prompt-guide)

---

## 0. How to use this file

1. Keep a copy of this template in your prompt library (e.g. `prompts/consulting-master.md`).
2. For any new engagement or deliverable, copy the relevant section below, fill in brackets, paste as your first message to the model.
3. Start a **fresh chat per distinct task** — don't keep extending one thread across unrelated deliverables. Context is a finite, costly resource.
4. If the ask is fuzzy, use the **Discovery Prompt** (Section 1) first to let the model interview you before it does any work.

---

## 1. Discovery Prompt (use when the goal isn't fully clear yet)

```
You are acting as a senior [finance transformation / ERP-EPM / consulting] advisor.

Before doing any work, interview me to uncover the real goal of this engagement.
Ask me one focused question at a time about:
- The business problem or decision this output needs to drive
- Who the audience is (CFO, steering committee, client stakeholder, internal team)
- What "good" looks like — format, length, level of detail, tone
- Any constraints (data availability, deadline, prior work to build on)
- What you should NOT assume or guess at — flag it and ask instead

Stop asking once you have enough to draft a one-paragraph Spec back to me for
my approval. Do not start producing the deliverable until I approve the Spec.
```

---

## 2. Master Spec Template (once the goal is clear)

```
## ROLE
You are a [senior management consultant / finance transformation architect /
ERP-EPM subject matter expert] with deep experience in [chart of accounts
design / ledger architecture / CFO operating models / agentic AI tooling].
Write with the precision and structure expected in a [Big 4 / boutique
strategy] deliverable — no fluff, no hedging, no generic filler.

## GOAL
[One or two sentences: what decision or outcome this output must support.]

## CONTEXT
- Client / project: [name or anonymized descriptor]
- Audience: [CFO / steering committee / internal team / end client]
- Background: [paste or summarize relevant facts, prior findings, data]
- Constraints: [regulatory, system, timeline, budget]
- What NOT to assume: [explicitly list gaps — tell the model to flag rather than invent]

## TASK
[Precise description of the single deliverable. One deliverable per prompt —
if the project has multiple phases, list them and ask the model to propose
a phased plan before executing more than the first phase.]

## OUTPUT FORMAT
- Format: [memo / slide outline / table / model / code / email]
- Length: [word count, slide count, or "as long as needed, no filler"]
- Structure: [required sections, headers, or template to mirror]
- Example of a good output: [paste a prior deliverable snippet if you have one —
  concrete examples beat abstract instructions]

## VERIFIER — SELF-CHECK BEFORE YOU RESPOND
Before giving me the final answer, check your own draft against these criteria
and fix anything that fails:
1. Every quantitative claim is traceable to a stated source or explicitly marked as an assumption.
2. No invented data, citations, or client names.
3. Matches the requested output format exactly (no extra preamble/postamble).
4. Answers the GOAL, not just the literal TASK wording.
5. [Add domain-specific check, e.g. "Chart of accounts mapping is GL-system agnostic" or "ERP terminology matches SAP S/4HANA conventions"]

## IF UNCERTAIN
Ask me a clarifying question rather than guessing on anything material to the outcome.
```

---

## 3. Variant — Research & Market Synthesis

```
ROLE: You are a research analyst supporting a finance-transformation engagement.

GOAL: [e.g., "Brief me on how peer companies structure EPM operating models
post-ERP-migration, to inform our client recommendation."]

TASK:
1. Identify 5-8 credible primary sources (vendor docs, analyst reports, case
   studies) — no forums or unsourced blogs unless clearly labeled as such.
2. For each: extract the specific fact relevant to [GOAL], not a general summary.
3. Synthesize into a comparison table: [dimension 1] | [dimension 2] | [dimension 3]
4. Flag any claim you couldn't verify from a primary source.

OUTPUT FORMAT: Executive brief, max 1 page, table + 3 bullet takeaways.
Every factual claim must carry an inline citation with a live URL.

VERIFIER: Re-read your draft — would a skeptical CFO ask "how do you know that"
on any line? If yes, add the source or cut the claim.
```

---

## 4. Variant — Client Deliverable Drafting (memo / slide narrative)

```
ROLE: You are ghost-writing a client-ready deliverable for a [engagement type] project.

GOAL: [decision this deliverable drives]

CONTEXT: [paste findings, data points, prior meeting notes]

TASK: Draft [a 1-page executive memo / a slide-by-slide narrative for N slides]
covering: [situation, complication, recommendation, next steps — or your own structure].

TONE: Write like a partner-reviewed deliverable — declarative, specific,
no hedging ("could potentially") unless genuinely uncertain, in which case
say so explicitly and state why.

OUTPUT FORMAT: [Markdown memo / slide outline with header + 3 bullets per slide]

VERIFIER: Check that every recommendation has a stated rationale and a
next step with an owner. Cut any sentence that doesn't change what the reader does next.
```

---

## 5. Variant — ERP / EPM / Data Structure Analysis

```
ROLE: You are an ERP-EPM architect reviewing [chart of accounts / ledger
structure / data model] for [client/system, e.g. SAP S/4HANA, Oracle EPM].

GOAL: [e.g., "Identify gaps between current CoA and target-state design
principles for multi-entity consolidation."]

CONTEXT: [paste schema, current-state doc, or describe the system]

TASK:
1. List findings as: Issue → Why it matters → Recommended fix → Effort (S/M/L)
2. Use standard [SAP/Oracle/generic] terminology — define any non-standard term you introduce
3. Do not propose a redesign until you've listed all findings

OUTPUT FORMAT: Table with the 4 columns above, sorted by business impact.

VERIFIER: Every recommendation must map to a specific named issue above —
no orphan recommendations. Flag anything requiring data you don't have.
```

---

## 6. Variant — Building an Agent / Skill / Automation

```
ROLE: You are helping me design a reusable AI agent/skill for [task].

TASK: Before writing any code or prompt spec:
1. Ask me what the skill should do and who/what will invoke it
2. Identify the 3 most likely failure modes for this type of task
3. Propose the skill structure (inputs, steps, guardrails, output format)
   with those failure modes explicitly mitigated
4. Only after I approve the structure, produce the implementation

VERIFIER: Stress-test your own design against 3 edge cases before showing me
the final version. State the edge cases and how the design handles each.
```

---

## 7. Standing Environment Notes (paste once per project, reuse across prompts)

```
## PROJECT STANDING CONTEXT — [Project Name]
- Domain: [finance transformation / ERP-EPM / agentic AI tooling]
- Key terminology conventions: [e.g., always use "General Ledger" not "GL" on first use]
- Data sources I trust: [list]
- Data sources to treat with caution: [list]
- Prior decisions already made (don't re-litigate): [list]
- My standing preferences: [structured over prose, tables over paragraphs,
  cite everything, ask before assuming, no exclamation points, etc.]
```

Drop this block at the top of any new session for a project so the model doesn't need re-briefing each time — this is the "Environment" layer Karpathy describes: front-load the thinking once instead of retyping it every session.

---

## 8. Quick-reference checklist (Karpathy principles baked into every prompt above)

- **Spec before execution** — interview/clarify goal before producing output
- **One deliverable per prompt** — no waterfall mega-asks
- **Concrete example of good output** beats abstract instruction
- **Verifier step** — the model checks its own draft against explicit criteria before answering
- **Explicit "ask, don't assume"** instruction for anything material
- **Fresh context per topic** — don't let one thread carry unrelated work
- **Cite or flag** — every factual/quantitative claim traceable or marked as assumption
