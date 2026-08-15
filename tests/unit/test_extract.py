import json

from src.ingestion import extract


def test_extract_json_reads_file(tmp_path, monkeypatch):
    monkeypatch.setattr(extract, "DATA_DIR", tmp_path)
    (tmp_path / "sample.json").write_text(
        json.dumps({"category": "avantages", "full_text": "Contenu accentué : é à ç"}),
        encoding="utf-8",
    )

    data = extract.extract_json("sample.json")

    assert data == {"category": "avantages", "full_text": "Contenu accentué : é à ç"}


def test_extract_json_reads_list(tmp_path, monkeypatch):
    monkeypatch.setattr(extract, "DATA_DIR", tmp_path)
    (tmp_path / "sample_list.json").write_text(
        json.dumps([{"concours_num": "1"}, {"concours_num": "2"}]),
        encoding="utf-8",
    )

    data = extract.extract_json("sample_list.json")

    assert data == [{"concours_num": "1"}, {"concours_num": "2"}]
