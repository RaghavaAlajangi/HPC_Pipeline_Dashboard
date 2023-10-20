from datetime import datetime as dt, timedelta
from pathlib import Path
import pickle
import os
import time

HSM_PATH = Path(__file__).parents[1] / "HSMFS" / "Data"
RESOURCE_PATH = Path(__file__).parents[0] / "resources"

HSM_PATH = Path(__file__).parents[0] / "HSMFS" / "Data"

print(HSM_PATH)

class HSMDataProcessor:
    def __init__(self, drive_path, chunk_size, resource_path):
        self.drive_path = drive_path
        self.chunk_size = chunk_size
        self.resource_path = resource_path
        self.chunk_dir_path = resource_path / "hsm_chunk_dir"
        self.chunk_idx_file_path = resource_path / "hsm_chunk_index.pkl"
        if not self.chunk_dir_path.exists():
            self.chunk_dir_path.mkdir(parents=True, exist_ok=True)
        self.chunk_data = []
        self.chunk_index = {}

    def clear_chunk_directory(self):
        """Erase chunk data and index files from resource dir."""
        if self.chunk_idx_file_path.exists():
            self.chunk_idx_file_path.unlink()
        for item in self.chunk_dir_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()

    def save_chunk_data(self, chunk_data, chunk_id):
        """Save the chunk data as a pickle file in hsm_chunk_dir."""
        chunk_path = self.chunk_dir_path / f"chunk_num_{chunk_id}.pkl"
        with open(chunk_path, "wb") as f:
            pickle.dump(chunk_data, f)

    def update_and_save_chunk_index(self, chunk_data, chunk_id):
        """Update the chunk index and save it."""
        for entry in chunk_data:
            for keyword in entry["filepath"]:
                if keyword not in self.chunk_index:
                    self.chunk_index[keyword] = set()
                self.chunk_index[keyword].add(chunk_id)

        with open(str(self.chunk_idx_file_path), "wb") as f:
            pickle.dump(self.chunk_index, f)

    def process_drive(self):
        t1 = time.time()

        self.clear_chunk_directory()
        chunk_data = []
        chunk_counter = 0

        for dirpath, dirnames, filenames in os.walk(self.drive_path):
            filenames = [f for f in filenames if f.endswith(".rtdc")]
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                # Standardize the RTDC file path
                fpath = fpath.replace("\\", "/").replace("//", "/")
                # Get the modified date of the RTDC file
                modified_time = os.path.getmtime(fpath)
                modified_time = dt.fromtimestamp(
                    modified_time).strftime(
                    "%d-%b-%Y %I.%M %p")
                # Get the relative path without HSMFS drive name
                fpath_wo_hsmfs = fpath.split("HSMFS/")[1]
                # Split path string into list and add HSMFS identifier
                file_path_list = ["HSMFS:"] + list(fpath_wo_hsmfs.split("/"))
                entry = {
                    "filepath": file_path_list,
                    "dateModified": modified_time,
                }
                chunk_data.append(entry)

                # Pickle the chunk data when it reaches the chunk size
                if len(chunk_data) >= self.chunk_size:
                    chunk_counter += 1
                    self.save_chunk_data(chunk_data, chunk_counter)
                    # Update and save the final chunk index
                    self.update_and_save_chunk_index(chunk_data, chunk_counter)
                    chunk_data = []

        # Pickle any remaining data if it's not a full chunk
        if chunk_data:
            chunk_counter += 1
            self.save_chunk_data(chunk_data, chunk_counter)
            # Update and save the final chunk index
            self.update_and_save_chunk_index(chunk_data, chunk_counter)

        # Save the chunk index file
        with open(str(self.chunk_idx_file_path), "wb") as f:
            pickle.dump(self.chunk_index, f)

        disc_time = str(timedelta(seconds=time.time() - t1)).split(".")[0]
        print(f"Disc scanning time: {disc_time}")


if __name__ == "__main__":
    CHUNK_SIZE = 2000000
    processor = HSMDataProcessor(HSM_PATH, CHUNK_SIZE, RESOURCE_PATH)
    processor.process_drive()
