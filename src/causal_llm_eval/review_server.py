#!/usr/bin/env python3
"""Clinician review server for parsing, graph generation, and model evaluation."""

from __future__ import annotations

import argparse
import json
import math
import os
import threading
from collections import Counter, defaultdict
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .paths import REPO_ROOT, resolve_repo_path


STATIC_DIR = resolve_repo_path("review_app")
DEFAULT_ANALYSIS_ROOT = resolve_repo_path("results", "analysis")
DEFAULT_RAW_ROOT = resolve_repo_path("results", "raw")
DEFAULT_BATTERY_PATH = resolve_repo_path("data", "vignettes", "vignette_battery.json")
DEFAULT_WORLD_MODEL_PATH = resolve_repo_path("results", "world_model", "v2", "world_model_metrics_v2.json")
DEFAULT_ANNOTATIONS_DIR = resolve_repo_path("results", "review_annotations")


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    with open(path) as f:
        return json.load(f)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def json_safe(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    return value


def normalise_status(value: str | None) -> str:
    allowed = {"unreviewed", "accepted", "corrected", "flagged"}
    if value in allowed:
        return value
    return "unreviewed"


@dataclass(frozen=True)
class DatasetConfig:
    name: str
    analysis_dir: Path
    raw_dir: Path


class ReviewRepository:
    def __init__(
        self,
        analysis_root: Path = DEFAULT_ANALYSIS_ROOT,
        raw_root: Path = DEFAULT_RAW_ROOT,
        battery_path: Path = DEFAULT_BATTERY_PATH,
        world_model_path: Path = DEFAULT_WORLD_MODEL_PATH,
        annotations_dir: Path = DEFAULT_ANNOTATIONS_DIR,
    ) -> None:
        self.analysis_root = analysis_root
        self.raw_root = raw_root
        self.battery_path = battery_path
        self.world_model_path = world_model_path
        self.annotations_dir = annotations_dir
        self.annotations_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._bundle_cache: dict[str, dict[str, Any]] = {}

    def discover_datasets(self) -> list[DatasetConfig]:
        datasets = []
        if not self.analysis_root.exists():
            return datasets
        for entry in sorted(self.analysis_root.iterdir()):
            if entry.is_dir() and (entry / "parsed.json").exists():
                datasets.append(DatasetConfig(name=entry.name, analysis_dir=entry, raw_dir=self.raw_root / entry.name))
        return datasets

    def list_datasets(self) -> list[dict[str, Any]]:
        world_scores = load_json(self.world_model_path, {})
        output = []
        for dataset in self.discover_datasets():
            metrics = load_json(dataset.analysis_dir / "metrics.json", {})
            parsed = load_json(dataset.analysis_dir / "parsed.json", [])
            edge_tests = load_json(dataset.analysis_dir / "edge_tests.json", [])
            models = sorted(metrics.keys() or {row.get("model_name") for row in parsed if row.get("model_name")})
            output.append(
                {
                    "name": dataset.name,
                    "models": models,
                    "n_cases": len({row["item_id"] for row in parsed}) if parsed else 0,
                    "n_runs": len(parsed),
                    "n_edges": len(edge_tests),
                    "has_world_model": any(model in world_scores for model in models),
                }
            )
        return output

    def _annotation_path(self, dataset_name: str) -> Path:
        return self.annotations_dir / f"{dataset_name}.json"

    def load_annotations(self, dataset_name: str) -> dict[str, Any]:
        data = load_json(self._annotation_path(dataset_name), {"cases": {}, "edges": {}, "global_notes": ""})
        data.setdefault("cases", {})
        data.setdefault("edges", {})
        data.setdefault("global_notes", "")
        return data

    def save_annotation(self, dataset_name: str, kind: str, target_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            annotations = self.load_annotations(dataset_name)
            if kind not in {"cases", "edges"}:
                raise ValueError(f"Unsupported annotation kind: {kind}")
            annotations[kind][target_id] = payload
            with open(self._annotation_path(dataset_name), "w") as f:
                json.dump(annotations, f, indent=2)
            self._bundle_cache.pop(dataset_name, None)
            return annotations

    def save_global_notes(self, dataset_name: str, notes: str) -> dict[str, Any]:
        with self._lock:
            annotations = self.load_annotations(dataset_name)
            annotations["global_notes"] = notes
            with open(self._annotation_path(dataset_name), "w") as f:
                json.dump(annotations, f, indent=2)
            self._bundle_cache.pop(dataset_name, None)
            return annotations

    def _load_raw_results(self, dataset: DatasetConfig) -> list[dict[str, Any]]:
        if not dataset.raw_dir.exists():
            return []
        files = sorted(dataset.raw_dir.glob("run_*.jsonl"))
        if not files:
            return []
        rows: list[dict[str, Any]] = []
        for file_path in files:
            with open(file_path) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return rows

    def _build_edge_summaries(self, edge_tests: list[dict[str, Any]], kg2_enhanced: dict[str, Any], annotations: dict[str, Any]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for test in edge_tests:
            for edge_id in test.get("edges", []):
                grouped[edge_id].append(test)

        summaries = []
        model_to_edges = kg2_enhanced if isinstance(kg2_enhanced, dict) else {}
        for edge_id, tests in grouped.items():
            models = sorted({test["model"] for test in tests})
            related_items = sorted({test["pert_id"] for test in tests})
            significant_rate = sum(1 for test in tests if test.get("significant")) / max(len(tests), 1)
            mean_jsd = sum(test.get("jsd", 0) for test in tests) / max(len(tests), 1)
            enhanced = {}
            for model in models:
                if model in model_to_edges and edge_id in model_to_edges[model]:
                    enhanced[model] = model_to_edges[model][edge_id]
            status = normalise_status(annotations.get("edges", {}).get(edge_id, {}).get("status"))
            summaries.append(
                {
                    "edge_id": edge_id,
                    "models": models,
                    "related_items": related_items,
                    "n_tests": len(tests),
                    "significant_rate": significant_rate,
                    "mean_jsd": mean_jsd,
                    "tests": tests,
                    "enhanced": enhanced,
                    "annotation": annotations.get("edges", {}).get(edge_id, {}),
                    "review_status": status,
                }
            )
        summaries.sort(key=lambda item: (-item["significant_rate"], -item["mean_jsd"], item["edge_id"]))
        return summaries

    def _build_cases(
        self,
        battery_items: dict[str, Any],
        parsed_runs: list[dict[str, Any]],
        raw_results: list[dict[str, Any]],
        annotations: dict[str, Any],
    ) -> list[dict[str, Any]]:
        parsed_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
        raw_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for row in parsed_runs:
            parsed_by_item[row["item_id"]].append(row)
        for row in raw_results:
            raw_by_item[row["item_id"]].append(row)

        cases = []
        for item_id, item in battery_items.items():
            parsed = sorted(parsed_by_item.get(item_id, []), key=lambda row: (row.get("model_name", ""), row.get("run_idx", 0)))
            raw = sorted(raw_by_item.get(item_id, []), key=lambda row: (row.get("model_name", ""), row.get("run_idx", 0)))
            models = sorted({row.get("model_name") for row in parsed + raw if row.get("model_name")})
            stance_counts: dict[str, Counter[str]] = defaultdict(Counter)
            for row in parsed:
                for stance in row.get("stances", []):
                    stance_counts[stance["treatment"]][stance["stance"]] += 1

            consensus = []
            for treatment, counts in sorted(stance_counts.items()):
                total = sum(counts.values())
                consensus.append(
                    {
                        "treatment": treatment,
                        "counts": dict(counts),
                        "top_stance": counts.most_common(1)[0][0] if counts else None,
                        "top_rate": counts.most_common(1)[0][1] / total if total else 0,
                    }
                )

            annotation = annotations.get("cases", {}).get(item_id, {})
            cases.append(
                {
                    "item_id": item_id,
                    "family": item.get("family"),
                    "type": item.get("type", "baseline"),
                    "label": item.get("label", item_id),
                    "question": item.get("question"),
                    "clinical_text": item.get("clinical_text"),
                    "expected_recommendations": item.get("expected_recommendations", []),
                    "expected_excluded": item.get("expected_excluded", []),
                    "edge_justification": item.get("edge_justification", []),
                    "grey_zone_statement": item.get("grey_zone_statement"),
                    "variables_changed": item.get("variables_changed", []),
                    "parsed_runs": parsed,
                    "raw_runs": raw,
                    "models": models,
                    "consensus": consensus,
                    "annotation": annotation,
                    "review_status": normalise_status(annotation.get("status")),
                }
            )
        cases.sort(key=lambda item: (item["family"] or "", item["item_id"]))
        return cases

    def load_bundle(self, dataset_name: str) -> dict[str, Any]:
        if dataset_name in self._bundle_cache:
            return self._bundle_cache[dataset_name]

        dataset = next((d for d in self.discover_datasets() if d.name == dataset_name), None)
        if dataset is None:
            raise FileNotFoundError(dataset_name)

        battery = load_json(self.battery_path, {"baselines": [], "perturbations": []})
        battery_items = {item["id"]: item for item in battery.get("baselines", [])}
        battery_items.update({item["id"]: item for item in battery.get("perturbations", [])})

        parsed_runs = load_json(dataset.analysis_dir / "parsed.json", [])
        edge_tests = load_json(dataset.analysis_dir / "edge_tests.json", [])
        metrics = load_json(dataset.analysis_dir / "metrics.json", {})
        kg2 = load_json(dataset.analysis_dir / "kg2.json", {})
        kg2_enhanced = load_json(dataset.analysis_dir / "kg2_enhanced.json", {})
        graph_comparison = load_json(dataset.analysis_dir / "graph_comparison.json", {})
        divergences = load_json(dataset.analysis_dir / "divergences.json", [])
        spurious_edges = load_json(dataset.analysis_dir / "spurious_edges.json", {})
        world_model = load_json(self.world_model_path, {})
        raw_results = self._load_raw_results(dataset)
        annotations = self.load_annotations(dataset_name)

        cases = self._build_cases(battery_items, parsed_runs, raw_results, annotations)
        edge_summaries = self._build_edge_summaries(edge_tests, kg2_enhanced, annotations)
        model_names = sorted(metrics.keys() or {row.get("model_name") for row in parsed_runs if row.get("model_name")})

        bundle = {
            "dataset": {
                "name": dataset_name,
                "models": model_names,
                "analysis_dir": display_path(dataset.analysis_dir),
                "raw_dir": display_path(dataset.raw_dir) if dataset.raw_dir.exists() else None,
                "n_cases": len(cases),
                "n_runs": len(parsed_runs),
                "families": sorted({case["family"] for case in cases if case.get("family")}),
            },
            "cases": cases,
            "edges": edge_summaries,
            "metrics": metrics,
            "kg2": kg2,
            "kg2_enhanced": kg2_enhanced,
            "graph_comparison": graph_comparison,
            "divergences": divergences,
            "spurious_edges": spurious_edges,
            "world_model_metrics": {model: world_model.get(model) for model in model_names if model in world_model},
            "annotations": annotations,
        }
        self._bundle_cache[dataset_name] = bundle
        return bundle


class ReviewRequestHandler(BaseHTTPRequestHandler):
    repository: ReviewRepository

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path == "/api/datasets":
            self._write_json({"datasets": self.repository.list_datasets()})
            return
        if path.startswith("/api/datasets/") and path.endswith("/bundle"):
            dataset_name = path.split("/")[3]
            try:
                self._write_json(self.repository.load_bundle(dataset_name))
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "Dataset not found")
            return
        if path.startswith("/api/datasets/") and path.endswith("/annotations"):
            dataset_name = path.split("/")[3]
            self._write_json(self.repository.load_annotations(dataset_name))
            return
        self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path.startswith("/api/datasets/") and path.endswith("/annotations"):
            dataset_name = path.split("/")[3]
            body = self._read_json()
            try:
                if body.get("kind") == "global":
                    annotations = self.repository.save_global_notes(dataset_name, str(body.get("notes", "")))
                else:
                    annotations = self.repository.save_annotation(
                        dataset_name,
                        str(body["kind"]),
                        str(body["id"]),
                        body.get("payload", {}),
                    )
            except (KeyError, ValueError) as exc:
                self.send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._write_json({"ok": True, "annotations": annotations})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _write_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(json_safe(payload), allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, path: str) -> None:
        if path == "/":
            file_path = STATIC_DIR / "index.html"
        else:
            file_path = (STATIC_DIR / path.lstrip("/")).resolve()
            if STATIC_DIR.resolve() not in file_path.parents and file_path != STATIC_DIR.resolve():
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
                return
            if not file_path.exists() or file_path.is_dir():
                file_path = STATIC_DIR / "index.html"

        if not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        content_type = "text/plain; charset=utf-8"
        if file_path.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif file_path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif file_path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"

        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the clinician review app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--analysis-root", default=str(DEFAULT_ANALYSIS_ROOT))
    parser.add_argument("--raw-root", default=str(DEFAULT_RAW_ROOT))
    parser.add_argument("--battery", default=str(DEFAULT_BATTERY_PATH))
    parser.add_argument("--world-model", default=str(DEFAULT_WORLD_MODEL_PATH))
    parser.add_argument("--annotations-dir", default=str(DEFAULT_ANNOTATIONS_DIR))
    return parser


def run_server(args: argparse.Namespace) -> int:
    repository = ReviewRepository(
        analysis_root=Path(args.analysis_root),
        raw_root=Path(args.raw_root),
        battery_path=Path(args.battery),
        world_model_path=Path(args.world_model),
        annotations_dir=Path(args.annotations_dir),
    )
    handler = type("ConfiguredReviewRequestHandler", (ReviewRequestHandler,), {"repository": repository})
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Clinician review app running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    os.environ.setdefault("XDG_CACHE_HOME", "/tmp/causal-llm-cache")
    args = build_parser().parse_args(argv)
    return run_server(args)


if __name__ == "__main__":
    raise SystemExit(main())
