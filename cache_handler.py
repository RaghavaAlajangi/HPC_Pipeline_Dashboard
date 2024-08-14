from datetime import datetime as dt, timedelta
from pathlib import Path
import pickle
import os
import time


class DriveFileScanner:
    def __init__(self, drive_path, result_path, file_suffix, identifier):
        self.drive_path = drive_path
        self.result_path = result_path
        self.file_suffix = file_suffix
        self.identifier = identifier
        if not result_path.parent.is_dir():
            result_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_size(file_path):
        """Compute size of the file."""
        file_size_bytes = os.path.getsize(file_path)
        if file_size_bytes < 1024 ** 2:  # Less than 1 MB
            return None
        elif file_size_bytes < 1024 ** 3:  # Less than 1 GB
            return f"{file_size_bytes / (1024 ** 2):.1f} MB"
        else:
            return f"{file_size_bytes / (1024 ** 3):.1f} GB"

    def save_data(self, data):
        """Save extracted paths as a pickle file in resources dir."""
        with open(self.result_path, "wb") as f:
            pickle.dump(data, f)

    def process_drive(self):
        t1 = time.time()

        data = []

        for dirpath, dirnames, filenames in os.walk(self.drive_path):
            filenames = [f for f in filenames if f.endswith(self.file_suffix)]
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                file_size = self.get_file_size(fpath)
                if file_size:
                    # Standardize the file path
                    fpath = fpath.replace("\\", "/").replace("//", "/")
                    # Get the modified date of the file
                    modified_time = os.path.getmtime(fpath)
                    modified_time = dt.fromtimestamp(modified_time).strftime(
                        "%d-%b-%Y %I.%M %p")

                    # Save files in "HSMFS:/Data/path/to/the/rtdc/file"
                    fpath = str(fpath).strip()
                    # Get the path starts from 'Data' (eg: Data/path/to/file)
                    data_dir_idx = fpath.index("Data/")
                    fpath = fpath[data_dir_idx:]
                    # Split the path into a list (eg: [Data, path, to, file])
                    fpath_split_list = list(fpath.split("/"))
                    # Add identifier to split list
                    # (eg: [HSMFS:, Data, path, to, file])
                    fpath_list = [f"{self.identifier}:"] + fpath_split_list

                    entry = {
                        "filepath": fpath_list,
                        "dateModified": modified_time,
                        "size": file_size
                    }
                    data.append(entry)

        # Save the processed data to a pickle file
        self.save_data(data)

        disc_time = str(timedelta(seconds=time.time() - t1)).split(".")[0]
        print(f"Disc scanning time: {disc_time}")


if __name__ == "__main__":
    # Restrict the dashboard to scan only `Data` directory from mounted HSMFS
    HSM_PATH = Path(__file__).parents[1] / "HSMFS" / "Data"
    RESOURCE_PATH = Path(__file__).parents[0] / "resources" / "hsm_drive.pkl"
    hsm_processor = DriveFileScanner(HSM_PATH, RESOURCE_PATH, ".rtdc", "HSMFS")
    hsm_processor.process_drive()
