import os
import json
import requests
import base64
import random

# Configurations
IDS_FOLDER = 'ids'
POSES_FOLDER = 'poses'
COMFYUI_API_URL = 'http://127.0.0.1:8188/prompt'

# Helper function to list images in a folder
def list_images(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

# Create the JSON payload for the queue call
def create_payload(id_image_path, pose_image_path):
    """
    Generate a payload object for the ComfyUI workflow API using base64 loaders.

    Args:
        id_image_path (str): File path for the ID image.
        pose_image_path (str): File path for the pose image.

    Returns:
        dict: Payload object for the workflow.
    """
    # Convert images to base64
    def encode_image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    id_image_base64 = encode_image_to_base64(id_image_path)
    pose_image_base64 = encode_image_to_base64(pose_image_path)

    payload = {
        "116": {  # Seed node
            "class_type": "Seed",
            "inputs": {
                "seed": random.randint(0, 2**32 - 1)
            }
        },
        "126": {  # Base64 loader for pose image
            "class_type": "easy loadImageBase64",
            "inputs": {
                "image_output": "Hide",
                "save_prefix": "",
                "base64_data": pose_image_base64
            },
            "widgets_values": [pose_image_base64, "Preview", "ComfyUI"]
        },
        "127": {  # Base64 loader for ID image
            "class_type": "easy loadImageBase64",
            "inputs": {
                "image_output": "Hide",
                "save_prefix": "",
                "base64_data": id_image_base64
            },
            "widgets_values": [id_image_base64, "Preview", "ComfyUI"]
        },
        "105": {  # ControlNetLoader
            "class_type": "ControlNetLoader",
            "inputs": {
                "control_net_name": "OpenPoseXL2.safetensors"
            }
        },
        "100": {  # OpenposePreprocessor
            "class_type": "OpenposePreprocessor",
            "inputs": {
                "image": ["126", 0]
            }
        },
        "104": {  # ControlNetApply
            "class_type": "ControlNetApply",
            "inputs": {
                "conditioning": ["6", 0],
                "control_net": ["105", 0],
                "image": ["100", 0],
                "strength": 0.9
            }
        },
        "6": {  # CLIPTextEncode (positive conditioning)
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": "professional photograph, attractive woman in sports attire"
            }
        },
        "7": {  # CLIPTextEncode (negative conditioning)
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": "bad quality, worse quality, awful, blurry, deformed, ugly"
            }
        },
        "5": {  # EmptyLatentImage
            "class_type": "EmptyLatentImage",
            "inputs": {
                "batch_size": 1,
                "width": 720,
                "height": 1280
            }
        },
        "42": {  # KSampler
            "class_type": "KSampler",
            "inputs": {
                "cfg": 2,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["114", 0],
                "negative": ["7", 0],
                "positive": ["104", 0],
                "sampler_name": "dpmpp_sde_gpu",
                "scheduler": "karras",
                "seed": ["116", 3],
                "steps": 35
            }
        },
        "46": {  # VAEDecode
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["42", 0],
                "vae": ["4", 2]
            }
        },
        "47": {  # SaveImage
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "APIPrompting_",
                "images": ["46", 0]
            }
        },
        "4": {  # CheckpointLoaderSimple
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "juggernautXL_juggXIByRundiffusion.safetensors"
            }
        },
        "114": {  # ApplyPulid
            "class_type": "ApplyPulid",
            "inputs": {
                "model": ["4", 0],
                "pulid": ["112", 0],
                "eva_clip": ["113", 0],
                "face_analysis": ["115", 0],
                "image": ["127", 0],
                "start_at": 0,
                "end_at": 1,
                "weight": 1,
                "method": "fidelity"
            }
        },
        "112": {  # PulidModelLoader
            "class_type": "PulidModelLoader",
            "inputs": {
                "pulid_file": "ip-adapter_pulid_sdxl_fp16.safetensors"
            }
        },
        "113": {  # PulidEvaClipLoader
            "class_type": "PulidEvaClipLoader",
            "inputs": {}
        },
        "115": {  # PulidInsightFaceLoader
            "class_type": "PulidInsightFaceLoader",
            "inputs": {
                "provider": "CUDA"
            }
        }
    }
    return payload

# Send payload to the ComfyUI API
def queue_prompt(payload):
    p = {"prompt": payload}
    response = requests.post(COMFYUI_API_URL, json=p)
    if response.status_code != 200:
        print(f"Error queuing workflow: {response.status_code} - {response.text}")
    else:
        print(f"Workflow queued successfully. Response: {response.json()}")

# Main function
if __name__ == '__main__':
    ids_images = list_images(IDS_FOLDER)
    poses_images = list_images(POSES_FOLDER)

    for id_image in ids_images:
        for pose_image in poses_images:
            # Construct payload for the current pair of images
            payload = create_payload(id_image, pose_image)
            queue_prompt(payload)
