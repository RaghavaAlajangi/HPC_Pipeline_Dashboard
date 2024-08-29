import pickle
import tempfile

from pathlib import Path

from cache_handler import DriveFileScanner

from .helper_methods import retrieve_test_drive

data_path = Path(__file__).parents[0] / "data"


def test_drive_scanner():
    """Test drive scanner"""
    test_drive = retrieve_test_drive(data_path / "dummy_mounted_drive.zip")
    temp_path = Path(tempfile.mkdtemp(prefix=test_drive.name)) / "test.pkl"

    hsm_processor = DriveFileScanner(test_drive, temp_path, ".rtdc", "HSMFS")
    hsm_processor.process_drive()

    with open(temp_path, "rb") as file:
        data_dict = pickle.load(file)
        assert "cache_data" in data_dict.keys()
        assert "update_time" in data_dict.keys()
        cache_data = data_dict["cache_data"]
        assert len(cache_data) > 1
        entry = cache_data[0]
        assert "filepath" in entry.keys()
        assert "dateModified" in entry.keys()
