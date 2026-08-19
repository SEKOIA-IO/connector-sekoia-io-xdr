from scripts.sync_requirements_txt import sync_requirements_txt


def test_sync_requirements_txt_check_fails_when_different(monkeypatch, tmp_path):
    file_path = tmp_path / "requirements.txt"
    file_path.write_text("current\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.sync_requirements_txt._build_expected_requirements",
        lambda: "expected\n",
    )

    assert sync_requirements_txt(file_path, check_only=True) == 1


def test_sync_requirements_txt_check_passes_when_equal(monkeypatch, tmp_path):
    file_path = tmp_path / "requirements.txt"
    file_path.write_text("expected\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.sync_requirements_txt._build_expected_requirements",
        lambda: "expected\n",
    )

    assert sync_requirements_txt(file_path, check_only=True) == 0


def test_sync_requirements_txt_writes_when_different(monkeypatch, tmp_path):
    file_path = tmp_path / "requirements.txt"
    file_path.write_text("old\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.sync_requirements_txt._build_expected_requirements",
        lambda: "new\n",
    )

    assert sync_requirements_txt(file_path, check_only=False) == 0
    assert file_path.read_text(encoding="utf-8") == "new\n"


def test_sync_requirements_txt_keeps_file_when_equal(monkeypatch, tmp_path):
    file_path = tmp_path / "requirements.txt"
    file_path.write_text("same\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.sync_requirements_txt._build_expected_requirements",
        lambda: "same\n",
    )

    assert sync_requirements_txt(file_path, check_only=False) == 0
    assert file_path.read_text(encoding="utf-8") == "same\n"


def test_sync_requirements_txt_creates_file_when_missing(monkeypatch, tmp_path):
    file_path = tmp_path / "requirements.txt"

    monkeypatch.setattr(
        "scripts.sync_requirements_txt._build_expected_requirements",
        lambda: "created\n",
    )

    assert sync_requirements_txt(file_path, check_only=False) == 0
    assert file_path.read_text(encoding="utf-8") == "created\n"
