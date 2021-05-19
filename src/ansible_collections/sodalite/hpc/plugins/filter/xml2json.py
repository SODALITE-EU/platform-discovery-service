from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import xmltodict
import json


class FilterModule(object):

    def filters(self):
        return {
            'xml2json': self.xml2json,
        }

    def xml2json(self, value):
        return json.dumps(xmltodict.parse(value))
