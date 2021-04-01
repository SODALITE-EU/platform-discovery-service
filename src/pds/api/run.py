import connexion
import os
import subprocess
import re
import atexit

from pds.api.openapi import encoder
from pds.api.log import get_logger


logger = get_logger(__name__)


def _killAgent():
    logger.info("killing previously started ssh-agent")
    subprocess.run(["ssh-agent", "-k"])
    del os.environ["SSH_AUTH_SOCK"]
    del os.environ["SSH_AGENT_PID"]


def _setupAgent():
    process = subprocess.run(["ssh-agent", "-s"],
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
    OUTPUT_PATTERN = re.compile("SSH_AUTH_SOCK=(?P<socket>[^;]+).*SSH_AGENT_PID=(?P<pid>\d+)", re.MULTILINE | re.DOTALL )
    match = OUTPUT_PATTERN.search(process.stdout)
    if match is None:
        raise Exception("Could not parse ssh-agent output. It was: {}".format(process.stdout))
    agentData = match.groupdict()
    logger.info("ssh agent data: {}".format(agentData))
    logger.info("exporting ssh agent environment variables")
    os.environ["SSH_AUTH_SOCK"] = agentData["socket"]
    os.environ["SSH_AGENT_PID"] = agentData["pid"]
    atexit.register(_killAgent)


def get_app():
    app = connexion.App(__name__, specification_dir="./openapi/openapi/",
                        server="flask",
                        options=dict(
                            serve_spec=True,
                            swagger_ui=True)
                        )

    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        "openapi.yaml",
        arguments={"title": "Platform Discovery Service API"},
        pythonic_params=True
        )
    app.app.config.update({
        "OIDC_INTROSPECTION_ENDPOINT": os.getenv("OIDC_INTROSPECTION_ENDPOINT", ""),
        "OIDC_CLIENT_ID": os.getenv("OIDC_CLIENT_ID",
                                    "sodalite-ide"),
        "OIDC_CLIENT_SECRET": os.getenv("OIDC_CLIENT_SECRET",
                                        "a8337e6d-ffbf-45ac-9fef-a8d3bd5c45cb"),
        "OIDC_OPENID_REALM": "SODALITE",
        "OIDC_SCOPES": ["openid", "email", "profile"],
        "STORAGE_KEY": os.getenv("PDS_STORAGE_KEY",
                                 "InfxydkOHQ16o5K-qAG04oap593MPK20rpOA8mQh5ao="),
        "BLUEPRINT_PATH": os.getenv("PDS_BLUEPRINT_PATH",
                                    "/root/projects/platform-discovery-service/blueprints"),
        "VAULT_LOGIN_URI": os.getenv("SECRET_VAULT_LOGIN_URI",
                                     "http://localhost:8200/v1/auth/jwt/login"),
        "VAULT_SECRET_URI": os.getenv("SECRET_VAULT_URI",
                                      "http://localhost:8200/v1/"),
        "AUTH_API_KEY": os.getenv("AUTH_API_KEY", ""),
        "SEMANTIC_REASONER_UPDATE_URI": os.getenv("SEMANTIC_REASONER_UPDATE_URI", 
                                                  "http://localhost:8080/reasoner-api/v0.6/saveTOSCA"),   
        "SUBSCRIBER_TIMEOUT": os.getenv("SUBSCRIBER_TIMEOUT", "5"),                                    
    })
    if app.app.config["OIDC_INTROSPECTION_ENDPOINT"] == "":
        logger.warn("Security alert. OIDC_INTROSPECTION_ENDPOINT in not configured.")
    else:
        logger.info("OIDC_INTROSPECTION_ENDPOINT {}".format(app.app.config["OIDC_INTROSPECTION_ENDPOINT"]))
    logger.info("VAULT_LOGIN_URI {}".format(app.app.config["VAULT_LOGIN_URI"]))
    logger.info("VAULT_SECRET_URI {}".format(app.app.config["VAULT_SECRET_URI"]))
    logger.info("SEMANTIC_REASONER_UPDATE_URI {}".format(app.app.config["SEMANTIC_REASONER_UPDATE_URI"]))

    return app


if __name__ == "__main__":
    _setupAgent()
    get_app().run(port=8081, debug=True)
