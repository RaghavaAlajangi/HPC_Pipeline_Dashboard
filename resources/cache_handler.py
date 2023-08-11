from datetime import datetime as dt, timedelta
from pathlib import Path
import pickle
import os
import time

HSM_PATH = Path(__file__).parents[1] / "HSMFS"
RESOURCE_PATH = Path(__file__).parents[1] / "resources"


class HSMDataProcessor:
    def __init__(self, drive_path, chunk_size, resource_path):
        self.drive_path = drive_path
        self.chunk_size = chunk_size
        self.resource_path = resource_path
        self.chunk_dir_path = resource_path / "hsm_chunk_dir"
        self.chunk_idx_file_path = resource_path / "hsm_chunk_index.pkl"
        if not self.chunk_dir_path.exists():
            self.chunk_dir_path.mkdir(parents=True, exist_ok=True)
        self.data = []
        self.chunk_data = []
        self.chunk_index = {}

    def clear_chunk_directory(self):
        self.chunk_idx_file_path.unlink()
        for item in self.chunk_dir_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()

    def update_chunk_index(self, chunk_data, chunk_id):
        for entry in chunk_data:
            for keyword in entry["filepath"]:
                if keyword not in self.chunk_index:
                    self.chunk_index[keyword] = set()
                self.chunk_index[keyword].add(chunk_id)

    def save_chunk_to_pickle(self, chunk_data, chunk_id):
        chunk_path = self.chunk_dir_path / f"chunk_num_{chunk_id}.pkl"
        with open(chunk_path, "wb") as f:
            pickle.dump(chunk_data, f)

    def process_hsmdrive(self):
        t1 = time.time()

        self.clear_chunk_directory()
        chunk_data = []
        chunk_counter = 0

        for dirpath, dirnames, filenames in os.walk(self.drive_path):
            filenames = [f for f in filenames if f.endswith('.rtdc')]
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                fpath = fpath.replace("\\", "/").replace("//", "/")

                modified_time = os.path.getmtime(fpath)
                modified_time = dt.fromtimestamp(
                    modified_time).strftime(
                    "%d-%b-%Y %I.%M %p")

                entry = {
                    "filepath": fpath.split("/"),
                    "dateModified": modified_time
                }
                self.data.append(entry)

                chunk_data.append(entry)

                # Pickle the chunk data when it reaches the chunk size
                if len(chunk_data) >= self.chunk_size:
                    chunk_counter += 1
                    self.save_chunk_to_pickle(chunk_data, chunk_counter)
                    # Update chunk index for filtering
                    self.update_chunk_index(chunk_data, chunk_counter)
                    chunk_data = []

        # Pickle any remaining data if it's not a full chunk
        if chunk_data:
            self.save_chunk_to_pickle(chunk_data, chunk_counter)
            # Update chunk index for filtering
            self.update_chunk_index(chunk_data, chunk_counter)

        # Save the chunk index file
        with open(str(self.chunk_idx_file_path), "wb") as f:
            pickle.dump(self.chunk_index, f)

        disc_time = str(timedelta(seconds=time.time() - t1)).split('.')[0]
        print(f"Disc scanning time: {disc_time}")


if __name__ == "__main__":
    CHUNK_SIZE = 200
    processor = HSMDataProcessor(HSM_PATH, CHUNK_SIZE, RESOURCE_PATH)
    processor.process_hsmdrive()
