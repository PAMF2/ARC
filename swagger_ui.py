"""
Swagger UI Integration for BaaS API
Adds /api/docs endpoint with interactive API documentation
"""

from flask import Blueprint, send_from_directory, jsonify
import os
import yaml

swagger_bp = Blueprint('swagger', __name__)

# Get the directory where this file is located
SWAGGER_DIR = os.path.dirname(os.path.abspath(__file__))
OPENAPI_FILE = os.path.join(SWAGGER_DIR, 'openapi.yaml')

@swagger_bp.route('/api/docs')
def swagger_ui():
    """Serve Swagger UI HTML"""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BaaS API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css">
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin: 0;
            padding: 0;
        }
        .topbar {
            display: none;
        }
        .swagger-ui .info {
            margin: 20px 0;
        }
        .swagger-ui .info .title {
            font-size: 36px;
            color: #3b4151;
        }
        .swagger-ui .scheme-container {
            background: #1f8efa;
            box-shadow: 0 1px 2px 0 rgba(0,0,0,0.15);
            padding: 10px 0;
            margin: 0 0 20px;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/api/openapi.yaml",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                tryItOutEnabled: true,
                displayRequestDuration: true,
                filter: true,
                syntaxHighlight: {
                    activate: true,
                    theme: "monokai"
                },
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                displayOperationId: false,
                docExpansion: "list"
            });

            window.ui = ui;
        };
    </script>
</body>
</html>
    """
    return html

@swagger_bp.route('/api/openapi.yaml')
def openapi_spec():
    """Serve OpenAPI specification file"""
    try:
        with open(OPENAPI_FILE, 'r') as f:
            spec = yaml.safe_load(f)
        return jsonify(spec)
    except FileNotFoundError:
        return jsonify({
            "error": "OpenAPI specification file not found",
            "path": OPENAPI_FILE
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Failed to load OpenAPI specification: {str(e)}"
        }), 500

@swagger_bp.route('/api/openapi.json')
def openapi_spec_json():
    """Serve OpenAPI specification as JSON (alternative endpoint)"""
    try:
        with open(OPENAPI_FILE, 'r') as f:
            spec = yaml.safe_load(f)
        return jsonify(spec)
    except FileNotFoundError:
        return jsonify({
            "error": "OpenAPI specification file not found"
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Failed to load OpenAPI specification: {str(e)}"
        }), 500

def register_swagger_ui(app):
    """
    Register Swagger UI blueprint with Flask app

    Usage:
        from swagger_ui import register_swagger_ui
        register_swagger_ui(app)

    Then access documentation at: http://localhost:5001/api/docs
    """
    app.register_blueprint(swagger_bp)
    print("\n" + "="*70)
    print("SWAGGER UI DOCUMENTATION")
    print("="*70)
    print("API Documentation available at: http://localhost:5001/api/docs")
    print("OpenAPI Spec (YAML): http://localhost:5001/api/openapi.yaml")
    print("OpenAPI Spec (JSON): http://localhost:5001/api/openapi.json")
    print("="*70 + "\n")
