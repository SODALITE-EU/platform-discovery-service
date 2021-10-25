import connexion

from pds.api.openapi import encoder
from pds.api.log import get_logger


logger = get_logger(__name__)


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
        pythonic_params=True)

    return app


if __name__ == "__main__":
    get_app().run(port=8081, debug=True)
