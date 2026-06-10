"""extraction_log.json が schemas/extraction_log.schema.json に適合することを検証する。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from revenue_kun.cli import run
from revenue_kun.sample_pdf import generate_sample_pdf

ASSUMPTIONS = "assumptions.sample.yaml"
DUMMY_CSV = "data/dummy_rent_roll.csv"
SCHEMA_PATH = "schemas/extraction_log.schema.json"


@pytest.fixture(scope="module")
def validator() -> Draft7Validator:
    schema = json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)  # スキーマ自体の妥当性
    return Draft7Validator(schema)


def _run_and_load(out: Path, **kw) -> dict:
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(out), **kw)
    assert rc == 0
    return json.loads((out / "extraction_log.json").read_text(encoding="utf-8"))


def test_csv_log_matches_schema(validator, tmp_path):
    log = _run_and_load(tmp_path / "csv")
    errors = sorted(validator.iter_errors(log), key=lambda e: e.path)
    assert not errors, [e.message for e in errors]
    assert log["rent_roll_pdf"] is None


def test_pdf_log_matches_schema(validator, tmp_path):
    pdf = generate_sample_pdf(tmp_path / "simple.pdf", pattern="simple")
    log = _run_and_load(tmp_path / "pdf", rent_roll_pdf=str(pdf))
    errors = sorted(validator.iter_errors(log), key=lambda e: e.path)
    assert not errors, [e.message for e in errors]
    assert log["rent_roll_pdf"] == pdf.name


def test_schema_rejects_missing_required_key(validator):
    """スキーマが必須キー欠落を検出することを確認（スキーマの実効性）。"""
    bad = {"input_files": {"assumptions": "a", "rent_roll": "b"}}
    assert list(validator.iter_errors(bad)), "必須キー欠落が検出されていない"
