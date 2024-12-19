# comfyuicharcreator

Script for automating consistent character creation using comfyui

## Requirements

* Python (3.11.9 is what I'm using)
* ComfyUI
  * comfyui-tooling-nodes

## Setup

Run the setup.bat script, this should create the necessary venv and install the required pip packages

## Usage

Start comfyui. You shouldn't need to have a browser window open, just make sure the server is running.

```
.\venv\Scripts\activate
python .\generate.py
```

Now check the output path for comfyui for the generated image.

## TODO

1. Copying generated output files
2. Full range of body poses
3. Full range of face poses
4. Generation of LORA using ai_toolkit from output files
