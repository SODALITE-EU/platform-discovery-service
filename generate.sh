#!/bin/sh

set -e
set -u

[ -f openapi-generator-cli-4.3.0.jar ] || wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/4.3.0/openapi-generator-cli-4.3.0.jar
rm -rf gen/
rm -rf src/pds/api/controllers/openapi/
java -jar openapi-generator-cli-4.3.0.jar generate \
    --input-spec openapi-spec.yaml \
    --api-package api \
    --invoker-package invoker \
    --model-package models \
    --generator-name python-flask \
    --strict-spec true \
    --output gen/ \
    --config openapi-python-config.yaml
cp -r gen/pds/api/openapi/ src/pds/api/
rm -rf src/pds/api/openapi/test/
rm -rf src/pds/api/openapi/CONTROLLER_PACKAGE_MATCH_ANCHOR/
rm src/pds/api/openapi/__main__.py
sed -i -E -e 's/(.*?) .*?CONTROLLER_PACKAGE_MATCH_ANCHOR.*$/\1 pds.api.controllers.default/g' src/pds/api/openapi/openapi/openapi.yaml