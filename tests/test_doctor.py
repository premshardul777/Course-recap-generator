import shutil, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
import doctor  # noqa: E402

AGENT = ROOT / ".opencode" / "agents" / "summary-reviewer.md"


@pytest.fixture
def agent(tmp_path):
    p = tmp_path / "summary-reviewer.md"
    shutil.copy(AGENT, p)
    return p


def test_set_get_and_idempotent(agent):
    before = agent.read_text(encoding="utf-8")
    assert doctor.get_reviewer_model(agent) == "" or "model:" in before
    assert doctor.set_reviewer_model("google/gemini-3.5-flash", agent) is True
    assert doctor.get_reviewer_model(agent) == "google/gemini-3.5-flash"
    assert doctor.set_reviewer_model("google/gemini-3.5-flash", agent) is False
    text = agent.read_text(encoding="utf-8")
    assert text.count("model:") == 1 and text.split("\n")[0] == "---"
    assert "mode: subagent\nmodel: google/gemini-3.5-flash" in text          # inserted right after mode
    assert text.endswith(before.rsplit("---", 1)[1])                          # body untouched


def test_update_and_clear(agent):
    doctor.set_reviewer_model("google/gemini-3.5-flash", agent)
    assert doctor.set_reviewer_model("google/gemini-3.7-flash", agent) is True
    assert doctor.get_reviewer_model(agent) == "google/gemini-3.7-flash"
    assert doctor.set_reviewer_model("", agent) is True
    assert doctor.get_reviewer_model(agent) == ""
    assert doctor.set_reviewer_model("", agent) is False


def test_rejects_bad_model_names(agent):
    for bad in ("gemini", "google/x\nevil: 1", "a b/c"):
        with pytest.raises(ValueError):
            doctor.set_reviewer_model(bad, agent)


def test_crlf_file_still_works(agent):
    agent.write_bytes(agent.read_bytes().replace(b"\n", b"\r\n"))
    assert doctor.set_reviewer_model("google/gemini-3.5-flash", agent) is True
    assert doctor.get_reviewer_model(agent) == "google/gemini-3.5-flash"
