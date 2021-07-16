from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from ansible_collections.sodalite.hpc.plugins.module_utils import date_utils


class TestDateUtils:
    @pytest.fixture
    def date1(self):
        date = "1-12:34"
        return date

    @pytest.fixture
    def date2(self):
        date = "12:34"
        return date

    @pytest.fixture
    def date3(self):
        date = "12"
        return date

    @pytest.fixture
    def wrong_date1(self):
        date = "1-12:3d"
        return date

    @pytest.fixture
    def wrong_date2(self):
        date = "1-12:3334"
        return date

    def test_validate(self, date1, date2, date3, wrong_date1, wrong_date2):
        assert date_utils.validate(date1) is True
        assert date_utils.validate(date2) is True
        assert date_utils.validate(date3) is True
        assert date_utils.validate(wrong_date1) is False
        assert date_utils.validate(wrong_date2) is False

    def test_convert_to_torque(self, date1, date2, date3, wrong_date1, wrong_date2):
        assert date_utils.convert_to_torque(date1) == "36:34:00"
        assert date_utils.convert_to_torque(date2) == "00:12:34"
        assert date_utils.convert_to_torque(date3) == "00:12:00"
        assert date_utils.convert_to_torque(wrong_date1) is None
        assert date_utils.convert_to_torque(wrong_date2) is None
