from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from envcheck import check_files, parse_env


def test_parse_env_comments_export_and_quotes() -> None:
    parsed = parse_env('''# commentaire

export NAME=Alice
QUOTED="hello world"
SINGLE='two words'
UNQUOTED=value # commentaire
INLINE_HASH=value#not-a-comment
''')
    assert parsed == {
        "NAME": "Alice",
        "QUOTED": "hello world",
        "SINGLE": "two words",
        "UNQUOTED": "value",
        "INLINE_HASH": "value#not-a-comment",
    }


def test_parse_env_empty_value_and_duplicate() -> None:
    assert parse_env("A=first\nA=\nINVALID\n") == {"A": ""}


def test_all_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    env = tmp_path / ".env"
    example = tmp_path / ".env.example"
    env.write_text("A=1\nB=2\n", encoding="utf-8")
    example.write_text("A=\nB=\n", encoding="utf-8")
    assert check_files(env, example) == 0
    assert "✅" in capsys.readouterr().out


def test_missing_variable(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    env = tmp_path / ".env"
    example = tmp_path / ".env.example"
    env.write_text("A=1\n", encoding="utf-8")
    example.write_text("A=\nB=\n", encoding="utf-8")
    assert check_files(env, example) == 1
    output = capsys.readouterr().out
    assert "❌" in output and "B" in output


def test_extra_variable_is_warning_but_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    env = tmp_path / ".env"
    example = tmp_path / ".env.example"
    env.write_text("A=1\nEXTRA=x\n", encoding="utf-8")
    example.write_text("A=\n", encoding="utf-8")
    assert check_files(env, example) == 0
    assert "⚠️" in capsys.readouterr().out


def test_strict_empty_value_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    env = tmp_path / ".env"
    example = tmp_path / ".env.example"
    env.write_text("A=   \n", encoding="utf-8")
    example.write_text("A=example\n", encoding="utf-8")
    assert check_files(env, example, strict=True) == 1
    assert "Variable vide : A" in capsys.readouterr().out


def test_missing_file_subprocess_returns_two(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("envcheck.py")),
         "--env", str(tmp_path / "absent.env"), "--example", str(tmp_path / ".env.example")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Fichier introuvable" in result.stderr
