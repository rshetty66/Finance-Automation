# Incident Response Plan — {INCIDENT_ID}

**Project:** {PROJECT_NAME}
**Date reported:** {DATE_REPORTED}
**Reported by:** {REPORTED_BY}
**Severity:** {SEVERITY}  <!-- Critical | High | Medium | Low -->
**Incident type:** {INCIDENT_TYPE}  <!-- Technical | Operational | Business -->
**Status:** Active

---

## 1. Incident Description

**What happened:** {INCIDENT_DESCRIPTION}

**When detected:** {DATE_DETECTED}

**Where detected:** {LOCATION}  <!-- system / process / team / external -->

---

## 2. Impact Assessment

| Category | Details |
|----------|---------|
| Affected systems | {AFFECTED_SYSTEMS} |
| Affected processes | {AFFECTED_PROCESSES} |
| Affected users / stakeholders | {AFFECTED_USERS} |
| Business impact | {IMPACT_DESCRIPTION} |
| Project blocked? | {YES / NO} |

**Severity justification:** {SEVERITY_RATIONALE}

---

## 3. Response Team

| Role | Name | Contact | Responsibility |
|------|------|---------|----------------|
| Incident Lead | {NAME} | {CONTACT} | Overall coordination, decisions |
| Technical Lead | {NAME} | {CONTACT} | Technical investigation and fix |
| Business Owner | {NAME} | {CONTACT} | Business impact decisions |
| PM | {PM_NAME} | {CONTACT} | Communication, escalation, log |

> Add or remove rows based on team composition.

---

## 4. Initial Root Cause Analysis

**Probable cause:** {PROBABLE_CAUSE}

**Contributing factors:**
- {FACTOR_1}
- {FACTOR_2}

**Known risk?** {YES — see risk-register.md, risk #{RISK_ID} / NO}

---

## 5. Response Action Plan

| # | Action | Owner | Deadline | Status |
|---|--------|-------|----------|--------|
| 1 | {ACTION_1} | {OWNER} | {DEADLINE} | Pending |
| 2 | {ACTION_2} | {OWNER} | {DEADLINE} | Pending |
| 3 | {ACTION_3} | {OWNER} | {DEADLINE} | Pending |

> Add rows for additional actions. Update Status as actions progress: Pending → In Progress → Done.

---

## 6. Resolution Timeline

| Event | Target date/time | Actual |
|-------|-----------------|--------|
| Incident detected | {DATETIME} | {DATETIME} |
| Response initiated | {DATETIME} | — |
| Root cause identified | {DATETIME} | — |
| Resolution implemented | {DATETIME} | — |
| Incident closed | {DATETIME} | — |

---

## 7. Escalation Path

| Level | Condition | Contact | Communication method |
|-------|-----------|---------|---------------------|
| L1 — Team | Incident open > 2h without progress | {TECH_LEAD} | Direct message / call |
| L2 — PM | Business impact confirmed | {PM_NAME} | Call |
| L3 — Sponsor | Critical severity or unresolved > 4h | {SPONSOR} | Call |

> Adjust thresholds and contacts based on project escalation policy.

---

## 8. Communication Plan

| Stakeholder | Message | When | Sender | Method |
|-------------|---------|------|--------|--------|
| {STAKEHOLDER_1} | Incident confirmed, assessment in progress | Immediately | PM | {METHOD} |
| {STAKEHOLDER_2} | Response plan and resolution timeline | Within 1h | PM | {METHOD} |
| {STAKEHOLDER_3} | Resolution confirmed, incident closed | On closure | PM | {METHOD} |

> Use send-email skill for external stakeholder notifications (autonomy level per comm-plan.md).

---

## 9. Post-Incident Tasks

| # | Task | Owner | Deadline |
|---|------|-------|----------|
| 1 | Complete final root cause analysis | {OWNER} | {DEADLINE} |
| 2 | Update risk register with lessons learned | PM | Within 3 business days |
| 3 | Review and implement preventive measures | {OWNER} | Within 5 business days |
| 4 | Post-mortem meeting (if Critical or High) | PM | Within 5 business days |

---

**Approved by:** {PM_NAME}
**Last updated:** {DATE}

---

## Change Log

| Date | Update |
|------|--------|
| {DATE} | Document created |
