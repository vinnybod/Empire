class FlaskConfig:
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = '/doc'
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    OPENAPI_SWAGGER_UI_PATH = '/swagger'
    OPENAPI_SWAGGER_UI_URL = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/'
    OPENAPI_JSON_PATH = "api-spec.json"
    API_SPEC_OPTIONS = {
        'security': [{"ApiKeyAuth": []}],
        'components': {
            "securitySchemes":
                {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "query",
                        "name": "token"
                    }
                }
        }
    }
