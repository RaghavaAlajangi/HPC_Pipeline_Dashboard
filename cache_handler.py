from datetime import datetime as dt, timedelta
from pathlib import Path
import pickle
import os
import time

HSM_PATH = Path(__file__).parents[1] / "HSMFS" / "Data"
RESOURCE_PATH = Path(__file__).parents[0] / "resources"


class HSMDataProcessor:
    def __init__(self, drive_path, resource_path):
        self.drive_path = drive_path
        self.resource_path = resource_path

    def clear_resource_dir(self):
        """Erase previously created HSMFS drive pickle from resource dir."""
        for item in self.resource_path.iterdir():
            if item.is_file():
                item.unlink()

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
                # Standardize the RTDC file path
                fpath = fpath.replace("\\", "/").replace("//", "/")
                # Get the modified date of the RTDC file
                modified_time = os.path.getmtime(fpath)
                modified_time = dt.fromtimestamp(
                    modified_time).strftime("%d-%b-%Y %I.%M %p")
                # Get the path without HSMFS drive name
                fpath_wo_hsm = fpath.split("HSMFS/")[1]
                # Split path string into list and add HSMFS: drive identifier
                file_path_list = ["HSMFS:"] + list(fpath_wo_hsm.split("/"))
                entry = {
                    "filepath": file_path_list,
                    "dateModified": modified_time,
                }
                hsm_data.append(entry)

        # Pickle the hsm data
        self.save_hsm_data(hsm_data)

        disc_time = str(timedelta(seconds=time.time() - t1)).split(".")[0]
        print(f"Disc scanning time: {disc_time}")


if __name__ == "__main__":
    processor = HSMDataProcessor(HSM_PATH, RESOURCE_PATH)
    processor.process_drive()
