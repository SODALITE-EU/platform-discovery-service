# Platform Discovery Service 
Platform Discovery Service (PDS) provides [TOSCA](https://docs.oasis-open.org/tosca/TOSCA/v2.0/TOSCA-v2.0.html) resource descriptions for target platforms. Service method takes data required to access the platform as an input and creates a usable TOSCA service template definition from an obtained infrastructure description. PDS core is [xOpera](https://github.com/xlab-si/xopera-opera), a lightweight orchestrator, used as a module to execute TOSCA discovery blueprints for a predefined set of platforms. For each platform specialized Ansible collections or modules are used to implement specific resource discovery and gather resource description data in JSON format. The gathered data is converted from JSON into TOSCA resource template definitions through the jinja templating. This design improves code reusability as TOSCA discovery blueprints can be used separately with TOSCA orchestrators to create a TOSCA representation of the infrastructure even outside the Platform Discovery Service. 
Platform Discovery Service (PDS) is implemented as a REST API. The interface design is based on the OpenAPI 3.0 specification. [OpenAPI Generator](https://github.com/OpenAPITools/openapi-generator) is used to create stubs for REST API controllers and models. 

## Authorization configuration
By default PDS REST API uses [OAuth 2.0](https://tools.ietf.org/html/rfc6750) for authentication and authorization, namely [Resource Owner Password Credentials Grant flow](https://tools.ietf.org/html/rfc6749#section-4.3). This requires [Keycloak](https://www.keycloak.org/) to be installed and configured. Optionally a Secret Manager [Hashicorp Vault](https://www.vaultproject.io/) can be used for securely storing and handling user secrets. 
### OAuth 2.0 
OAuth 2.0 authentication uses confidential client type and requires certain parameters to be configured. Following environment variables must be set:
- `OIDC_INTROSPECTION_ENDPOINT` Keycloak OAuth 2.0 Introspection endpoint URI
- `OIDC_CLIENT_ID` The client identifier issued to the client, as described in [Client Authentication](https://tools.ietf.org/html/rfc6749#section-2.3)
- `OIDC_CLIENT_SECRET` The client secret.
#### Hashicorp Vault integration
PDS - Vault interaction is configured in a way that PDS acquires a short lived token from Vault and then uses this token to obtain secrets. The following environment variables must be set in order to use Vault as secret storage
- `SECRET_VAULT_LOGIN_URI`
- `SECRET_VAULT_URI`

With Vault configured any input parameter can be substituted with a following pattern:\
`"_get_secret*": "<path to secret in the vault>:<vault role name that grants access to secret>"`\
e.g.\
`"_get_secret_ssh_slurm": "pds/ssh_key_slurm:pds"`
### API key 
OAuth 2.0 authentication be overridden by setting `AUTH_API_KEY` env var. If the var is set then [API key security scheme](https://swagger.io/docs/specification/authentication/api-keys/) is enabled, otherwise API key authorization is disabled.
This key must be added to requests as `-H  "X-API-Key: [key_name]"`
Vault integration is unavailable with API key authorization.
## Running app
With Docker (API key authorization configured):

```shell script
docker build -t pds:latest .
docker run -d -p 8081:8081 \
    -e AUTH_API_KEY=TEST \
    --name pds pds:latest
```

With a local development installation (API key authorization configured):

```shell script
./generate.sh
python3 -m venv .venv
source .venv/bin/activate
pip install wheel
pip install -r requirements.txt
export PDS_BLUEPRINT_PATH="../blueprints"
export AUTH_API_KEY="TEST"
cd src/
python3 -m pds.api.run
```
## Usage
PDS REST API has a single `discover` HTTP POST method. Request body must contain `inputs` section and `platform_type` defined.
Supported platform types:
- `slurm`
- `torque`
- `openstack`
- `aws` 
```shell script
curl -X POST \
  http://localhost:8081/discover \
  -H 'content-type: application/json' \
  -H 'x-api-key: TEST' \
  -d '{
    "inputs" : { <input parameters> },
    "platform_type" : <platform type>
}'
```
Inputs consist of data required for accessing infrastructure targeted for discovery plus the `namespace` parameter used in TOSCA types name generation. Inputs can also contain special parameters described below:

- If SSH key is passed in inputs, it should have dedicated `_ssh_key` parameter name, that would indicate PDS to add it to SSH agent before discovery process begins. If key is password protected an `_ssh_key_password` should also be added.
- During the discovery process all intermediate results are stored in encrypted disc storage, that is implemented using [Fernet](https://cryptography.io/en/latest/fernet.html). Fernet encryption key must be provided and could be set either as `PDS_STORAGE_KEY` env var or passed as `_storage_key` inputs parameter.

Inputs example:
```json
"inputs" : 
{
    "frontend-address": "8.8.8.8",
    "user": "john",
    "_ssh_key": "MIEPDa......",
    "_storage_key": "81HqDtbqAywKSOumSha3BhWNOdQ26slT6K0YaZeZyPs=",
    "namespace": "TestSlurm"    	
}
```  


