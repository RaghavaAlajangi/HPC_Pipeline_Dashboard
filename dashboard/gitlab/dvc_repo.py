from collections import defaultdict

import yaml

from .base import BaseAPI


class DVCRepoAPI(BaseAPI):
    """HPC Pipeline Data repository API inherited from BaseAPI"""

    def get_model_metadata(self):
        """Read model checkpoint files from repo and fetch metadata"""
        repo_folder_path = "model_registry/segmentation"
        folder_content = self.repo_listdir(repo_folder_path)
        model_meta = defaultdict(dict)

        for file in folder_content:
            if ".dvc" in file["name"]:
                str_data = self.read_repo_file(file["path"])
                # Convert file content string into dictionary
                dict_data = yaml.safe_load(str_data)
                if not dict_data["meta"]["archive"]:
                    path = dict_data["outs"][0]["path"]
                    model_meta[path] = {
                        "device": dict_data["meta"]["device"],
                        "type": dict_data["meta"]["type"],
                    }

        return model_meta
