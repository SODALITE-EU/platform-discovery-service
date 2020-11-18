import os

from pds.api.openapi.models.platform_type import PlatformType
from flask import current_app


SSH_KEY_BLUEPRINT = "ssh_key"
ENV_BLUEPRINT = "env"


def get_service_template(blueprint_type: str):
    blueprint_folder = current_app.config['BLUEPRINT_PATH']
    if blueprint_type == PlatformType.SLURM:
        return os.path.join(blueprint_folder, "slurm"), "wm_info.yaml"
    if blueprint_type == PlatformType.AWS:
        return os.path.join(blueprint_folder, "aws"), "aws_info.yaml"
    if blueprint_type == SSH_KEY_BLUEPRINT:
        return os.path.join(blueprint_folder, "auth"), "ssh_key.yaml"
    if blueprint_type == ENV_BLUEPRINT:
        return os.path.join(blueprint_folder, "env"), "env_var.yaml"
