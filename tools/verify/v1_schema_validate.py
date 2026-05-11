"""V1: JSON-Schema validation of repository config + Phase-3 manifests.

Operates on existing artefacts only. Non-zero exit on any validation failure
or schema-loading error.

Run:
    python -m tools.verify.v1_schema_validate

Outputs:
    tools/verify/reports/v1_schema_validate_<YYYY-MM-DD>.json
"""

from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError:  # pragma: no cover
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "shared" / "config" / "schemas"
REPORT_DIR = REPO_ROOT / "tools" / "verify" / "reports"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _pairs() -> list[tuple[str, Path, Path]]:
    """Return (label, target, schema) tuples for fixed-path validations."""
    sc = SCHEMA_DIR
    return [
        ("unified_taxonomy", REPO_ROOT / "shared/config/unified_taxonomy.json", sc / "unified_taxonomy.schema.json"),
        ("tier_definitions", REPO_ROOT / "shared/config/tier_definitions.json", sc / "tier_definitions.schema.json"),
        ("silo_inclusion", REPO_ROOT / "shared/config/silo_inclusion.json", sc / "silo_inclusion.schema.json"),
        ("extraction_config", REPO_ROOT / "shared/config/extraction_config.json", sc / "extraction_config.schema.json"),
    ]


def _glob_pairs() -> list[tuple[str, Path, Path]]:
    """Per-silo Phase-3 manifests."""
    sc = SCHEMA_DIR
    out: list[tuple[str, Path, Path]] = []
    for p in sorted((REPO_ROOT / "shared/phase3/inclusion").glob("*.json")):
        out.append((f"phase3_inclusion/{p.stem}", p, sc / "phase3_inclusion.schema.json"))
    for p in sorted((REPO_ROOT / "shared/phase3/text_readiness").glob("*.json")):
        out.append((f"phase3_text_readiness/{p.stem}", p, sc / "phase3_text_readiness.schema.json"))
    return out


def _validate_one(label: str, target: Path, schema_path: Path) -> dict:
    if not target.exists():
        return {"label": label, "target": str(target.relative_to(REPO_ROOT)), "status": "missing_target"}
    if not schema_path.exists():
        return {"label": label, "target": str(target.relative_to(REPO_ROOT)), "status": "missing_schema"}
    try:
        instance = _load_json(target)
        schema = _load_json(schema_path)
        jsonschema.validate(instance=instance, schema=schema)
        return {"label": label, "target": str(target.relative_to(REPO_ROOT)), "status": "pass"}
    except jsonschema.ValidationError as e:
        return {
            "label": label,
            "target": str(target.relative_to(REPO_ROOT)),
            "status": "fail",
            "error": e.message,
            "path": list(e.absolute_path),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "label": label,
            "target": str(target.relative_to(REPO_ROOT)),
            "status": "error",
            "error": f"{type(e).__name__}: {e}",
        }


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    for label, target, schema in _pairs() + _glob_pairs():
        results.append(_validate_one(label, target, schema))

    summary = {
        "script": "v1_schema_validate",
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "total": len(results),
        "pass": sum(1 for r in results if r["status"] == "pass"),
        "fail": sum(1 for r in results if r["status"] == "fail"),
        "error": sum(1 for r in results if r["status"] == "error"),
        "missing_target": sum(1 for r in results if r["status"] == "missing_target"),
        "missing_schema": sum(1 for r in results if r["status"] == "missing_schema"),
        "results": results,
    }

    report_path = REPORT_DIR / f"v1_schema_validate_{_dt.date.today().isoformat()}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"V1 schema validation: {summary['pass']}/{summary['total']} pass")
    print(f"  fail={summary['fail']}  error={summary['error']}  "
          f"missing_target={summary['missing_target']}  missing_schema={summary['missing_schema']}")
    print(f"  report: {report_path.relative_to(REPO_ROOT)}")

    for r in results:
        if r["status"] != "pass":
            print(f"  [{r['status']}] {r['label']} :: {r.get('error', '')}")

    return 0 if (summary["fail"] == 0 and summary["error"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
