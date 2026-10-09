from kkbsecu.config import Settings


def test_settings_paths_are_relative_to_data_dir(tmp_path):
    config = Settings(data_dir=tmp_path, image_dir=tmp_path)
    assert config.db_path == tmp_path / 'events.sqlite3'
    assert config.embeddings_path.parent == tmp_path / 'private'
    assert config.save_unknown_crops is False
