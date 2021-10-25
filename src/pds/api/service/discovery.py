import multiprocessing
import os
import pds.api.utils.templates as templates

from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.commands.outputs import outputs as opera_outputs

from pds.api.log import debug_enabled
from pds.api.storages.memory_storage import SafeMemoryStorage
from pds.api.utils.inputs import preprocess_inputs
from pds.api.utils.environment import setup_user, cleanup_user


def discover(inputs, namespace, platform_type, access_token, username):
    with multiprocessing.Pool(1) as pool:
        result = pool.apply(run_discovery, (inputs, namespace, platform_type, access_token, username,))
        return result


def run_discovery(inputs, namespace, platform_type, access_token, username):
    path, template = templates.get_service_template(platform_type)

    try:
        # TODO: Disable verbose mode universally
        refined_inputs, ssh_keys = preprocess_inputs(inputs, access_token, namespace)
        if username:
            setup_user(username, access_token, ssh_keys)

        safe_storage = SafeMemoryStorage.create()
        os.chdir(path)
        opera_deploy(template, refined_inputs, safe_storage,
                     verbose_mode=debug_enabled(),
                     num_workers=1, delete_existing_state=True)
        result = opera_outputs(safe_storage)
        if len(result) != 1 or "value" not in list(result.values())[0]:
            raise KeyError("Error in discovery process output")
        return list(result.values())[0]["value"]
    finally:
        if username:
            cleanup_user()
