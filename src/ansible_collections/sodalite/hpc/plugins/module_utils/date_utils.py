from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import datetime

regex_timespan = r"^((?P<days>\d+)-)?((?P<time1>\d+):)?((?P<time2>\d{2,}):)?((?P<time3>\d{2}))$"


def validate(slurm_time):
    match = re.match(regex_timespan, slurm_time.strip(), re.IGNORECASE)
    if match is None:
        return False
    return True


def convert_to_torque(slurm_time):
    match = re.match(regex_timespan, slurm_time.strip(), re.IGNORECASE)
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    if match is not None:
        if match.group("days") is not None:
            days = int(match.group("days"))
            if match.group("time1") is not None:
                hours = int(match.group("time1"))
                minutes = int(match.group("time3"))
            elif match.group("time3") is not None:
                hours = int(match.group("time3"))
        elif match.group("time1") is not None:
            minutes = int(match.group("time1"))
            seconds = int(match.group("time3"))
        elif match.group("time3") is not None:
            minutes = int(match.group("time3"))
        if match.group("time2") is not None:
            minutes = int(match.group("time2"))
            hours = int(match.group("time1"))
            seconds = int(match.group("time3"))

        hours = hours + days * 24
        return format(hours, '02') + ':' + format(minutes, '02') + ':' + format(seconds, '02')

    return None


def convert_torque_datetime(torque_datetime):
    return datetime.datetime.strptime(torque_datetime, '%a %b %d %H:%M:%S %Y').strftime("%Y-%m-%dT%H:%M:%S")