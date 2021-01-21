import os

import pds.api.utils.templates as templates
from pds.api.storages.memory_storage import SafeMemoryStorage
from pds.api.log import get_logger, debug_enabled
from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.commands.undeploy import undeploy as opera_undeploy


class DeploymentEnvironment:

    def __init__(self):
        self.deployments = {}
        self.logger = get_logger(__name__)

    def setup(self, ssh_keys, env_vars):
        for ssh_key in ssh_keys:
            self.deployments[templates.SSH_KEY_BLUEPRINT] = \
                self._deploy_key(ssh_key[0], ssh_key[1])
        for env_var in env_vars:
            self.deployments[templates.ENV_BLUEPRINT] = \
                self._deploy_env(env_var)

    def cleanup(self):
        errors = []
        for key, deployment in self.deployments.items():
            try:
                path, template = templates.get_service_template(key)
                os.chdir(path)
                self._undeploy(deployment)
            except Exception as ex:
                errors.append(ex)
        return errors

    def _deploy_key(self, key, password):
        self.logger.info("Deploying SSH key to SSH agent")
        key_path, key_template = templates.get_service_template(
            templates.SSH_KEY_BLUEPRINT
            )

        mem_storage = SafeMemoryStorage.create()
        inputs = {"ssh-key": key}
        if password is not None:
            inputs["ssh-key-password"] = password
        os.chdir(key_path)
        opera_deploy(
            key_template, inputs,
            mem_storage,
            verbose_mode=debug_enabled(), num_workers=1,
            delete_existing_state=True
            )

        return mem_storage

    def _deploy_env(self, env_vars):
        env_path, env_template = templates.get_service_template(
            templates.ENV_BLUEPRINT
            )

        mem_storage = SafeMemoryStorage.create()
        inputs = {"env-var-map": env_vars}
        os.chdir(env_path)
        opera_deploy(
            env_template, inputs,
            mem_storage,
            verbose_mode=debug_enabled(), num_workers=1,
            delete_existing_state=True
            )

        return mem_storage

    def _undeploy(self, storage):
        self.logger.info("Removing deployed prerequisite")
        opera_undeploy(
            storage, verbose_mode=debug_enabled(), num_workers=1
            )
