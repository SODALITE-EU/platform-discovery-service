import pds.api.utils.templates as templates
from pds.api.openapi.models.platform_type import PlatformType


class TestUtils:

    def test_templates(self, flask_app):
        with flask_app.app.app_context():
            bp_name = templates.get_service_template(PlatformType.AWS)
            assert bp_name[1] == "aws_info.yaml"
            bp_name = templates.get_service_template(PlatformType.SLURM)
            assert bp_name[1] == "wm_info.yaml"
