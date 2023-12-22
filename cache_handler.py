from datetime import datetime as dt, timedelta
from pathlib import Path
import pickle
import os
import time

# Restrict the dashboard to scan only `Data` directory from mounted HSMFS
HSM_PATH = Path(__file__).parents[1] / "HSMFS" / "Data"
RESOURCE_PATH = Path(__file__).parents[0] / "resources"


class HSMDataProcessor:
    def __init__(self, drive_path, resource_path):
        self.drive_path = drive_path
        self.resource_path = resource_path
        if not resource_path.is_dir():
            resource_path.mkdir(parents=True, exist_ok=True)

    def clear_resource_dir(self):
        """Erase previously created HSMFS drive pickle from resource dir."""
        for item in self.resource_path.iterdir():
            if item.is_file():
                item.unlink()

    @staticmethod
    def get_file_size(file_path):
        """Compute size the file"""
        file_size_bytes = os.path.getsize(file_path)
        if file_size_bytes < 1024 ** 2:  # Less than 1 MB
            return None
        elif file_size_bytes < 1024 ** 3:  # Less than 1 GB
            return f"{file_size_bytes / (1024 ** 2):.1f} MB"
        else:
            return f"{file_size_bytes / (1024 ** 3):.1f} GB"

    def save_hsm_data(self, hsm_data):
        """Save extracted rtdc paths from HSMFS as a pickle file in
        resource dir."""
        with open(self.resource_path / "hsm_drive.pkl", "wb") as f:
            pickle.dump(hsm_data, f)

    def process_drive(self):
        t1 = time.time()

        self.clear_resource_dir()
        hsm_data = []

        for dirpath, dirnames, filenames in os.walk(self.drive_path):
            filenames = [f for f in filenames if f.endswith(".rtdc")]
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                file_size = self.get_file_size(fpath)
                if file_size:
                    # Standardize the RTDC file path
                    fpath = fpath.replace("\\", "/").replace("//", "/")
                    # Get the modified date of the RTDC file
                    modified_time = os.path.getmtime(fpath)
                    modified_time = dt.fromtimestamp(
                        modified_time).strftime("%d-%b-%Y %I.%M %p")
                    # Get the path without HSMFS drive name
                    fpath_wo_hsm = fpath.split("HSMFS/")[1]
                    # Split path into string list, add HSMFS: drive identifier
                    file_path_list = ["HSMFS:"] + list(fpath_wo_hsm.split("/"))
                    entry = {
                        "filepath": file_path_list,
                        "dateModified": modified_time,
                        "size": file_size
                    }
                    hsm_data.append(entry)

        # Pickle the hsm data
        self.save_hsm_data(hsm_data)

        disc_time = str(timedelta(seconds=time.time() - t1)).split(".")[0]
        print(f"Disc scanning time: {disc_time}")


if __name__ == "__main__":
    processor = HSMDataProcessor(HSM_PATH, RESOURCE_PATH)
    processor.process_drive()
