from collections import defaultdict
import yaml

from .base import BaseAPI


class DVCRepoAPI(BaseAPI):
    def __init__(self, gitlab_url, access_token, project_num):
        super().__init__(gitlab_url, access_token, project_num)

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
                    device = dict_data["meta"]["device"]
                    ftype = dict_data["meta"]["type"]
                    path = dict_data["outs"][0]["path"]
                    model_meta[device][ftype] = path

        # Extract device and type lists from model_meta
        device_list = list(model_meta.keys())
        type_list = list(
            {ty for types in model_meta.values() for ty in types.keys()})

        result = (device_list, type_list, model_meta)

        return result
