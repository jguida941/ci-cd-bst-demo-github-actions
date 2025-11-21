#!/usr/bin/env python3
"""
Utility to translate pip-audit's JSON output into SARIF for GitHub code scanning.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


@dataclass
class SeverityInfo:
    label: Optional[str]
    score: Optional[float]

    @property
    def sarif_level(self) -> str:
        label = (self.label or "").lower()
        if label in {"critical", "high"}:
            return "error"
        if label in {"medium", "moderate"}:
            return "warning"
        if label in {"low"}:
            return "note"
        if self.score is not None:
            if self.score >= 7.0:
                return "error"
            if self.score >= 4.0:
                return "warning"
            return "note"
        return "warning"

    @property
    def sarif_label(self) -> Optional[str]:
        if self.label:
            return self.label.lower()
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to pip-audit JSON output.")
    parser.add_argument("output", help="Destination SARIF file.")
    parser.add_argument(
        "--source",
        default="environment",
        help="Label or file path representing the scanned dependency source.",
    )
    return parser.parse_args()


def load_dependencies(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []
    deps = payload.get("dependencies")
    if isinstance(deps, list):
        return deps
    return []


def normalize_label(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    label = raw.strip().lower()
    mapping = {
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "moderate": "medium",
        "low": "low",
    }
    return mapping.get(label, label or None)


def severity_from_entries(entries: Iterable[Dict[str, Any]]) -> SeverityInfo:
    best_score: Optional[float] = None
    best_label: Optional[str] = None
    for entry in entries or []:
        score_val = entry.get("score")
        if score_val is not None:
            try:
                numeric = float(score_val)
            except (TypeError, ValueError):
                numeric = None
            if numeric is not None and (best_score is None or numeric > best_score):
                best_score = numeric
        label = entry.get("value") or entry.get("severity")
        normalized = normalize_label(label)
        if normalized and best_label is None:
            best_label = normalized
    if best_label is None and best_score is not None:
        if best_score >= 9.0:
            best_label = "critical"
        elif best_score >= 7.0:
            best_label = "high"
        elif best_score >= 4.0:
            best_label = "medium"
        else:
            best_label = "low"
    return SeverityInfo(label=best_label, score=best_score)


def find_requirement_line(source: Path, package_name: str) -> int:
    if not source.is_file():
        return 1
    try:
        for idx, raw_line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            lower = line.lower()
            pkg_lower = package_name.lower()
            if lower.startswith(f"{pkg_lower}==") or lower == pkg_lower or lower.startswith(
                f"{pkg_lower}>"
            ):
                return idx
    except OSError:
        return 1
    return 1


def ensure_rule(
    vuln: Dict[str, Any],
    rules: List[Dict[str, Any]],
    rules_index: Dict[str, int],
) -> Tuple[str, int]:
    vuln_id = vuln.get("id")
    aliases = vuln.get("aliases") or []
    rule_id = vuln_id or (aliases[0] if aliases else None) or "UNKNOWN"
    if rule_id not in rules_index:
        description = vuln.get("description") or "Vulnerability detected by pip-audit."
        help_uri = None
        links = vuln.get("links")
        if isinstance(links, list) and links:
            help_uri = links[0]
        properties = {
            "tags": ["security", "pip-audit"],
            "aliases": aliases,
            "fixVersions": vuln.get("fix_versions") or [],
        }
        severity_info = severity_from_entries(vuln.get("severity") or [])
        if severity_info.sarif_label:
            properties["problem.severity"] = severity_info.sarif_label
        if severity_info.score is not None:
            properties["security-severity"] = f"{severity_info.score:.1f}"
        rule = {
            "id": rule_id,
            "name": vuln_id or rule_id,
            "shortDescription": {"text": rule_id},
            "fullDescription": {"text": description},
            "helpUri": help_uri,
            "properties": properties,
        }
        rules_index[rule_id] = len(rules)
        rules.append(rule)
    return rule_id, rules_index[rule_id]


def build_sarif(
    dependencies: List[Dict[str, Any]],
    source_label: str,
) -> Dict[str, Any]:
    source_path = Path(source_label)
    artifact_uri = source_label
    if source_path.is_file():
        artifact_uri = source_path.as_posix()

    runs: List[Dict[str, Any]] = []
    tool_driver = {
        "name": "pip-audit",
        "informationUri": "https://github.com/pypa/pip-audit",
        "rules": [],
    }
    rules_index: Dict[str, int] = {}
    results: List[Dict[str, Any]] = []

    for dep in dependencies:
        vulns = dep.get("vulns") or []
        if not vulns:
            continue
        package = dep.get("name") or "unknown"
        version = dep.get("version") or "unpinned"
        for vuln in vulns:
            rule_id, rule_index = ensure_rule(vuln, tool_driver["rules"], rules_index)
            severity_info = severity_from_entries(vuln.get("severity") or [])
            fixes = vuln.get("fix_versions") or []
            fix_text = ", ".join(fixes) if fixes else "No known fix."
            description = vuln.get("description") or rule_id
            line = find_requirement_line(source_path, package) if source_path.is_file() else 1

            result = {
                "ruleId": rule_id,
                "ruleIndex": rule_index,
                "level": severity_info.sarif_level,
                "message": {
                    "text": f"{package} {version} is affected by {rule_id}: {description} Fix: {fix_text}"
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": artifact_uri},
                            "region": {"startLine": line},
                        }
                    }
                ],
                "partialFingerprints": {
                    "package": f"{package}@{version}",
                    "vulnerability": rule_id,
                },
            }
            results.append(result)

    run = {
        "tool": {"driver": tool_driver},
        "results": results,
        "artifacts": [
            {
                "location": {"uri": artifact_uri},
                "description": {"text": f"Dependencies from {source_label}"},
            }
        ],
    }
    runs.append(run)
    return {"version": "2.1.0", "$schema": SARIF_SCHEMA, "runs": runs}


def main() -> None:
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)
    dependencies = load_dependencies(in_path)
    sarif = build_sarif(dependencies, args.source)
    out_path.write_text(json.dumps(sarif, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
