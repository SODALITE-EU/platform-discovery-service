from os import path

from pds.api.openapi.models.platform_type import PlatformType
from .settings import Settings

SSH_KEY_BLUEPRINT = "ssh_key"


def get_service_template(blueprint_type: str):
    blueprint_folder = Settings.BLUEPRINT_PATH
    if blueprint_type == PlatformType.SLURM:
        return (path.abspath(path.join(blueprint_folder, "slurm")),
                "slurm_wm_info.yaml")
    if blueprint_type == PlatformType.AWS:
        return (path.abspath(path.join(blueprint_folder, "aws")),
                "aws_info.yaml")
    if blueprint_type == PlatformType.TORQUE:
        return (path.abspath(path.join(blueprint_folder, "torque")),
                "torque_wm_info.yaml")
    if blueprint_type == PlatformType.OPENSTACK:
        return (path.abspath(path.join(blueprint_folder, "openstack")),
                "openstack_info.yaml")
    if blueprint_type == PlatformType.KUBERNETES:
        return (path.abspath(path.join(blueprint_folder, "kubernetes")),
                "kubernetes_info.yaml")
    if blueprint_type == SSH_KEY_BLUEPRINT:
        return (path.abspath(path.join(blueprint_folder, "auth")),
                "ssh_key.yaml")
