# Quick Start Guide - Banking API Documentation

## 30 Second Start

```bash
# 1. Install dependencies
pip install flask pydantic PyYAML

# 2. Start server
python baas_backend_with_docs.py

# 3. Open browser
# http://localhost:5001/api/docs
```

That's it! You now have interactive API documentation.

## What You Get

```
┌─────────────────────────────────────────────────────────────────┐
│                     SWAGGER UI INTERFACE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Bank as a Service (BaaS) API v1.0.0                           │
│                                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                 │
│  📋 Health                                                      │
│     GET /api/health              ✓ Try it out                  │
│                                                                 │
│  👤 Accounts                                                    │
│     GET /api/accounts            ✓ Try it out                  │
│     POST /api/accounts           ✓ Try it out                  │
│     GET /api/accounts/{id}       ✓ Try it out                  │
│                                                                 │
│  💳 Transactions                                                │
│     GET /api/transactions        ✓ Try it out                  │
│     POST /api/transactions       ✓ Try it out                  │
│                                                                 │
│  📊 Analytics                                                   │
│     GET /api/analytics           ✓ Try it out                  │
│                                                                 │
│  🤖 Banking AI                                                  │
│     POST /api/banking-ai/validate ✓ Try it out                 │
│     POST /api/banking-ai/advice   ✓ Try it out                 │
│                                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                 │
│  🔍 Filter endpoints | 📥 Download OpenAPI spec                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
banking/
│
├── 📄 openapi.yaml                    ← OpenAPI 3.0 Specification
│   └── Complete API documentation
│       ├── 7 endpoints documented
│       ├── 7 data models
│       ├── Request/response examples
│       └── Validation rules
│
├── 🔌 swagger_ui.py                   ← Swagger UI Integration
│   └── Flask blueprint
│       ├── Serves Swagger UI
│       ├── Exposes OpenAPI spec
│       └── Interactive testing
│
├── 🚀 baas_backend_with_docs.py       ← Backend + Documentation
│   └── Complete backend server
│       ├── All API endpoints
│       ├── Swagger UI integrated
│       └── Ready to run
│
├── 📖 API_DOCUMENTATION.md            ← Complete Guide
│   └── Everything you need to know
│       ├── Usage examples
│       ├── Integration options
│       ├── Troubleshooting
│       └── Best practices
│
├── 📋 SWAGGER_SUMMARY.md              ← Quick Reference
│   └── Summary of features
│       ├── What was created
│       ├── Features overview
│       ├── Client SDK generation
│       └── Business value
│
├── ⚡ QUICK_START.md                  ← This File
│   └── Get started in 30 seconds
│
├── 🧪 test_swagger.py                 ← Test Script
│   └── Automated testing
│       ├── Starts server
│       ├── Tests endpoints
│       └── Validation
│
└── 📦 requirements_docs.txt           ← Dependencies
    └── Python packages needed
        ├── flask
        ├── pydantic
        └── PyYAML
```

## Architecture

```
┌──────────────┐         ┌──────────────────┐         ┌─────────────┐
│              │         │                  │         │             │
│   Browser    │◄───────►│  Flask Backend   │◄───────►│  Data Store │
│              │  HTTP   │                  │  JSON   │             │
└──────────────┘         └──────────────────┘         └─────────────┘
       │                          │
       │                          │
       ▼                          ▼
┌──────────────┐         ┌──────────────────┐
│              │         │                  │
│  Swagger UI  │         │  OpenAPI Spec    │
│  (Interactive)│◄───────│  (openapi.yaml)  │
│              │         │                  │
└──────────────┘         └──────────────────┘

Flow:
1. Browser requests /api/docs
2. Flask serves Swagger UI HTML
3. Swagger UI loads OpenAPI spec
4. User interacts with API through UI
5. Backend processes requests
6. Responses displayed in Swagger UI
```

## URLs

| URL | Purpose | Status |
|-----|---------|--------|
| http://localhost:5001 | API Base | ✓ API endpoints |
| http://localhost:5001/api/docs | Swagger UI | ✓ Interactive docs |
| http://localhost:5001/api/openapi.yaml | OpenAPI YAML | ✓ Spec file |
| http://localhost:5001/api/openapi.json | OpenAPI JSON | ✓ Spec file |
| http://localhost:5001/api/health | Health Check | ✓ API endpoint |

## Usage Examples

### 1. View Documentation
```bash
# Start server
python baas_backend_with_docs.py

# Open browser to:
http://localhost:5001/api/docs
```

### 2. Test an Endpoint
1. Open Swagger UI
2. Click on `POST /api/accounts`
3. Click "Try it out"
4. Modify the JSON:
   ```json
   {
     "owner": "Your Name",
     "account_type": "Checking",
     "initial_balance": 1000.00
   }
   ```
5. Click "Execute"
6. See the response!

### 3. Generate cURL Command
Swagger UI automatically generates cURL commands for you:

```bash
curl -X POST "http://localhost:5001/api/accounts" \
  -H "Content-Type: application/json" \
  -d '{"owner":"Alice","account_type":"Checking","initial_balance":1000}'
```

### 4. Export OpenAPI Spec
```bash
# Download as YAML
curl http://localhost:5001/api/openapi.yaml > my-spec.yaml

# Download as JSON
curl http://localhost:5001/api/openapi.json > my-spec.json
```

### 5. Import to Postman
1. Open Postman
2. Click "Import"
3. Choose "Link"
4. Enter: http://localhost:5001/api/openapi.yaml
5. Done! All endpoints imported

## Features at a Glance

### ✓ Complete Documentation
- All 9 endpoints documented
- Request/response schemas
- Examples for every endpoint
- Error responses included

### ✓ Interactive Testing
- Try endpoints directly in browser
- No Postman needed
- Pre-filled examples
- Real-time responses

### ✓ Validation Rules
- Pattern matching for IDs
- Enum validation for types
- Type checking
- Min/max constraints

### ✓ Multiple Examples
- Success cases
- Error cases
- Edge cases
- Different scenarios

### ✓ Data Models
- 7 schemas documented
- Nested objects
- Array types
- Optional fields

### ✓ Code Generation
- Auto-generates cURL
- Copy-paste ready
- Multiple languages via OpenAPI Generator

## Testing Checklist

```bash
# ✓ Start server
python baas_backend_with_docs.py

# ✓ Test health
curl http://localhost:5001/api/health

# ✓ View docs
open http://localhost:5001/api/docs

# ✓ Get OpenAPI spec
curl http://localhost:5001/api/openapi.yaml

# ✓ Test API endpoint
curl http://localhost:5001/api/accounts

# ✓ Try interactive testing
# Click "Try it out" in Swagger UI
```

## Next Steps

### Integrate into Your Project
```python
from swagger_ui import register_swagger_ui

app = Flask(__name__)
# Your code here...

register_swagger_ui(app)
app.run()
```

### Generate Client SDKs
```bash
npm install @openapitools/openapi-generator-cli -g
openapi-generator-cli generate -i openapi.yaml -g python -o ./client
```

### Share with Team
```bash
# Share the OpenAPI spec
# Team can import into Postman, generate clients, etc.
cp openapi.yaml /shared/location/
```

## Common Commands

```bash
# Install dependencies
pip install flask pydantic PyYAML

# Run backend with docs
python baas_backend_with_docs.py

# Run original backend (no docs)
python baas_backend.py

# Test swagger integration
python test_swagger.py

# Validate OpenAPI spec
python -c "import yaml; yaml.safe_load(open('openapi.yaml'))"

# Generate client (Python)
openapi-generator-cli generate -i openapi.yaml -g python -o ./client
```

## Tips

1. **Use "Try it out"** - Test endpoints without writing code
2. **Check examples** - Pre-filled with realistic data
3. **Copy cURL commands** - Great for sharing with team
4. **Filter by tag** - Use tags to find specific endpoints
5. **Expand schemas** - Click to see full data model details
6. **Download spec** - Export for Postman or other tools

## Troubleshooting

### Server won't start
```bash
# Check if port 5001 is in use
netstat -ano | findstr :5001

# Or use different port
# Edit baas_backend_with_docs.py line:
app.run(port=5002)  # Change to different port
```

### Swagger UI not loading
```bash
# Verify PyYAML installed
pip install PyYAML

# Check files exist
ls openapi.yaml swagger_ui.py

# Check browser console (F12) for errors
```

### OpenAPI spec errors
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('openapi.yaml'))"

# Check encoding
# File should be UTF-8
```

## Support

Need help? Check these files:
1. **QUICK_START.md** (this file) - Getting started
2. **API_DOCUMENTATION.md** - Complete guide
3. **SWAGGER_SUMMARY.md** - Feature summary

Or visit:
- Swagger UI: http://localhost:5001/api/docs
- Health check: http://localhost:5001/api/health

## Success!

You now have:
- ✅ Interactive API documentation
- ✅ Complete OpenAPI specification
- ✅ Try-it-out functionality
- ✅ Automatic code generation
- ✅ Zero-config setup

**Start exploring at: http://localhost:5001/api/docs**

---

Questions? Check the full documentation in `API_DOCUMENTATION.md`
