Place the model weights for MeLM in this folder, downloading the data using the following code, and manually downloading the large files from [here](https://huggingface.co/lamm-mit/MeLM/tree/main/MechGPT-13b_v106C).

```python
from huggingface_hub import HfApi, hf_hub_download

def download_subfolder(repo_id, subfolder, local_dir):
    api = HfApi()
    repo_files = api.list_repo_files(repo_id=repo_id)
    subfolder_files = [f for f in repo_files if f.startswith(subfolder)]
    for filename in subfolder_files:
        hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=local_dir)
        print(f"Downloaded {filename} to {local_dir}")

# Example 
repo_id = 'lamm-mit/MeLM'
subfolder = 'MechGPT-13b_v106C'
local_dir = './MechGPT-13b_v106C'  # Local directory to save the files
download_subfolder(repo_id=repo_id, subfolder=subfolder, local_dir=local_dir)
```
Refer to MeLM documentation [here](https://github.com/lamm-mit/MeLM).