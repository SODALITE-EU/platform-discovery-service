import os
import pwd
import re
import subprocess
import atexit
import tempfile
from pathlib import Path
from cryptography.hazmat.primitives import serialization

from pds.api.log import get_logger
from pds.api.utils.vault_client import get_secret, list_secrets
from pds.api.utils.settings import Settings

logger = get_logger(__name__)


def setup_agent():
    process = subprocess.run(["/usr/bin/ssh-agent", "-s"],
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
    OUTPUT_PATTERN = re.compile("SSH_AUTH_SOCK=(?P<socket>[^;]+).*SSH_AGENT_PID=(?P<pid>\d+)", re.MULTILINE | re.DOTALL )
    match = OUTPUT_PATTERN.search(process.stdout)
    if match is None:
        raise ValueError("Could not parse ssh-agent output. It was: {}".format(process.stdout))
    agent_data = match.groupdict()
    logger.debug("ssh agent data: {}".format(agent_data))
    logger.debug("exporting ssh agent environment variables")
    os.environ["SSH_AUTH_SOCK"] = agent_data["socket"]
    os.environ["SSH_AGENT_PID"] = agent_data["pid"]
    atexit.register(kill_agent)


def kill_agent():
    logger.debug("killing previously started ssh-agent")
    subprocess.run(["/usr/bin/ssh-agent", "-k"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        del os.environ["SSH_AUTH_SOCK"]
        del os.environ["SSH_AGENT_PID"]
    except KeyError:
        pass


def add_key(key: str):
    process = subprocess.run(['/usr/bin/ssh-add', '-'], input=key, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode != 0:
        logger.warn("Failed to add SSH key.")


def setup_user(username: str, access_token: str, ssh_keys: list):
    if not validate_username(username):
        raise ValueError("Username {} contains illegal characters".format(username))

    try:
        user = pwd.getpwnam(username)
    except KeyError:
        user = create_user(username)

    tmp = (Path(user.pw_dir) / "tmp")
    tempfile.tempdir = str(tmp)

    os.environ["ANSIBLE_LOCAL_TEMP"] = str(tmp)
    os.environ["HOME"] = user.pw_dir
    os.environ["USERNAME"] = username
    os.environ["USER"] = username
    os.environ["LOGNAME"] = username

    os.setgid(user.pw_gid)
    os.setuid(user.pw_uid)
    try:
        os.mkdir(tmp)
    except FileExistsError:
        pass

    if access_token:
        try:
            user_keys = get_user_keys(username, access_token)
            ssh_keys.extend(user_keys)
        except Exception as e:
            logger.warn("An error occurred obtaining SSH key from Vault: " + str(e))
    if ssh_keys:
        try:
            setup_user_keys(ssh_keys)
        except Exception as e:
            logger.warn("An error occurred adding SSH key: " + str(e))


def create_user(username: str):
    subprocess.run(["/usr/sbin/adduser", "--system", username], stdout=subprocess.DEVNULL)
    user = pwd.getpwnam(username)
    return user


def cleanup_user():
    kill_agent()


def get_user_keys(username: str, access_token: str):
    keys = []
    secrets = list_secrets(Settings.SSH_KEY_PATH_TEMPLATE.format(username=username), username, access_token)
    for secret in secrets:
        ssh_key = get_secret(Settings.SSH_KEY_PATH_TEMPLATE.format(username=username) + f"/{secret}", username, access_token)
        keys.append(ssh_key.get(Settings.SSH_KEY_SECRET_NAME))
    return keys


def setup_user_keys(ssh_keys: list):
    setup_agent()
    for key in ssh_keys:
        if key:
            if vaildate_key(key):
                add_key(key)
            else:
                logger.warn("Provided key value is not a valid SSH key.")


def setup_user_dir(location: Path, user_id: int, group_id: int):
    os.chown(location, user_id, group_id)
    os.chmod(location, 0o700)
    for root, dirs, files in os.walk(location):
        for ndir in dirs:
            os.chown(os.path.join(root, ndir), user_id, group_id)
            os.chmod(os.path.join(root, ndir), 0o700)
        for nfile in files:
            os.chown(os.path.join(root, nfile), user_id, group_id)
            os.chmod(os.path.join(root, nfile), 0o700)


def vaildate_key(key: str):
    try:
        serialization.load_ssh_private_key(str.encode(key), password=None)
        return True
    except ValueError:
        pass

    try:
        serialization.load_pem_private_key(str.encode(key), password=None)
        return True
    except ValueError:
        pass

    return False


def validate_username(username: str):
    if re.match(r"^[a-zA-Z0-9_-]*$", username):
        return True
    return False
