"""Export the VOLT deployment's validated capability set for the React app.

Reads a `volt_deploy` folder (the FastAPI/Next.js VOLT package) and writes:

  data/volt-catalog.json     agents (with system prompts), multi-phase workflows,
                             consulting services catalog, workflow intake questions,
                             layer colours and the skill index
  data/volt-skills.json.gz   full SKILL.md text per skill (+ resource file list),
                             served to agents on demand through the load_skill tool

Usage:
    python -I scripts/export_volt_catalog.py "C:\\Users\\<you>\\...\\volt_deploy"

VOLT's own loaders (agents.AGENT_REGISTRY, WORKFLOWS, CONSULTING_SERVICES,
WORKFLOW_INTAKE, discover_all_skills) are imported directly so the export sees
exactly what the VOLT runtime sees.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "data"
RESOURCE_SUFFIXES = {".md", ".txt", ".json", ".csv", ".yaml", ".yml", ".py", ".sql"}
MAX_SKILL_CHARS = 120_000


def main(volt_home: Path) -> None:
    if not (volt_home / "agents.py").exists():
        sys.exit(f"{volt_home} is not a volt_deploy folder (agents.py missing)")
    sys.path.insert(0, str(volt_home))
    import agents as volt  # noqa: E402  (VOLT's registry module)

    package = {}
    pkg_file = volt_home / ".volt-package.json"
    if pkg_file.exists():
        raw = json.loads(pkg_file.read_text(encoding="utf-8"))
        package = {k: raw.get(k) for k in ("commit", "ref", "built_utc", "version")}

    agents = []
    for aid, a in volt.AGENT_REGISTRY.items():
        agents.append({
            "id": aid,
            "name": a.get("name", aid),
            "layer": a.get("layer", ""),
            "icon": a.get("icon", ""),
            "color": a.get("color", ""),
            "description": a.get("description", ""),
            "keywords": list(a.get("keywords") or []),
            "skills": list(a.get("skills") or []),
            "systemPrompt": a.get("system_prompt", ""),
        })

    workflows = []
    for wid, w in volt.WORKFLOWS.items():
        workflows.append({
            "id": wid,
            "name": w.get("name", wid),
            "icon": w.get("icon", ""),
            "description": w.get("description", ""),
            "agents": list(w.get("agents") or []),
            "phases": [{"name": p.get("name", ""), "agents": list(p.get("agents") or [])} for p in w.get("phases") or []],
        })

    services = []
    for practice, pdata in volt.CONSULTING_SERVICES.items():
        for sub, sdata in (pdata.get("sub_practices") or {}).items():
            for s in sdata.get("services") or []:
                services.append({
                    "code": s.get("code", ""),
                    "name": s.get("name", ""),
                    "practice": practice,
                    "subPractice": sub,
                    "description": s.get("description", ""),
                    "agents": list(s.get("agents") or []),
                    "workflows": list(s.get("workflows") or []),
                    "skills": list(s.get("skills") or []),
                    "coverage": s.get("coverage", ""),
                })

    skill_index, skill_bodies = [], {}
    for sid, meta in sorted(volt.discover_all_skills().items()):
        skill_dir = Path(meta["path"]).parent
        body = Path(meta["path"]).read_text(encoding="utf-8-sig")
        resources = sorted(
            str(p.relative_to(skill_dir)).replace("\\", "/")
            for p in skill_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in RESOURCE_SUFFIXES and p.name != "SKILL.md"
        )
        skill_index.append({
            "id": sid,
            "name": meta.get("name", sid),
            "description": meta.get("description", ""),
            "category": meta.get("category", "General"),
            "industry": meta.get("industry", ""),
            "resources": resources,
        })
        skill_bodies[sid] = {
            "body": body[:MAX_SKILL_CHARS],
            "truncated": len(body) > MAX_SKILL_CHARS,
            "resources": {
                r: (skill_dir / r).read_text(encoding="utf-8", errors="replace")[:40_000]
                for r in resources
                if r.endswith(".md")
            },
        }

    catalog = {
        "source": {"name": "volt_deploy", **package},
        "agents": agents,
        "workflows": workflows,
        "services": services,
        "intake": volt.WORKFLOW_INTAKE,
        "layerColors": getattr(volt, "LAYER_COLORS", {}),
        "skills": skill_index,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "volt-catalog.json").write_text(json.dumps(catalog, indent=1, ensure_ascii=False), encoding="utf-8")
    with gzip.open(OUT_DIR / "volt-skills.json.gz", "wt", encoding="utf-8") as fh:
        json.dump(skill_bodies, fh, ensure_ascii=False)

    print(
        f"Exported {len(agents)} agents, {len(workflows)} workflows, {len(services)} services, "
        f"{len(skill_index)} skills from {volt_home} -> {OUT_DIR}"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]).resolve())
