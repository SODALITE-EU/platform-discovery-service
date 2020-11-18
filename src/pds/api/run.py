import connexion
import os

from pds.api.openapi import encoder


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
        'OIDC_INTROSPECTION_ENDPOINT': 'http://localhost:8080/auth/realms/SODALITE/protocol/openid-connect/token/introspect',
        'OIDC_CLIENT_ID': 'sodalite-ide',
        'OIDC_CLIENT_SECRET': 'a8337e6d-ffbf-45ac-9fef-a8d3bd5c45cb',
        'OIDC_OPENID_REALM': 'SODALITE',
        'OIDC_SCOPES': ['openid', 'email', 'profile'],
        'STORAGE_KEY': os.getenv('PDS_STORAGE_KEY', "InfxydkOHQ16o5K-qAG04oap593MPK20rpOA8mQh5ao="),
        'BLUEPRINT_PATH': os.getenv('PDS_BLUEPRINT_PATH', "/root/projects/platform-discovery-service/bluerprints"),
        'VAULT_LOGIN_URI': os.getenv('SECRET_VAULT_LOGIN_URI', "http://localhost:8200/v1/auth/jwt/login"),
        'VAULT_SECRET_URI': os.getenv('SECRET_VAULT_URI', "http://localhost:8200/v1/"),
    })
    return app


if __name__ == "__main__":
    get_app().run(port=8081, debug=True)
