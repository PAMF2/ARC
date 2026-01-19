# BaaS API Documentation

Complete OpenAPI/Swagger documentation for the Bank as a Service API.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_docs.txt
```

Required packages:
- `flask>=3.0.0` - Web framework
- `pydantic>=2.0.0` - Data validation
- `PyYAML>=6.0.1` - YAML parser for OpenAPI spec

### 2. Run Backend with Swagger UI

```bash
python baas_backend_with_docs.py
```

The server will start on `http://localhost:5001` with:
- **API Server**: http://localhost:5001
- **Swagger UI Documentation**: http://localhost:5001/api/docs
- **OpenAPI Spec (YAML)**: http://localhost:5001/api/openapi.yaml
- **OpenAPI Spec (JSON)**: http://localhost:5001/api/openapi.json

### 3. Access Interactive Documentation

Open your browser and navigate to:

```
http://localhost:5001/api/docs
```

You'll see a fully interactive Swagger UI interface where you can:
- View all API endpoints
- See request/response schemas
- Try out API calls directly from the browser
- View example requests and responses
- Download the OpenAPI specification

## Files Overview

| File | Description |
|------|-------------|
| `openapi.yaml` | Complete OpenAPI 3.0 specification |
| `swagger_ui.py` | Flask blueprint for Swagger UI integration |
| `baas_backend_with_docs.py` | Backend with integrated documentation |
| `baas_backend.py` | Original backend (no docs) |
| `requirements_docs.txt` | Python dependencies |

## OpenAPI Specification

The `openapi.yaml` file includes:

### Complete API Coverage
- ✅ All 9 endpoints documented
- ✅ Request/response schemas
- ✅ Error responses (400, 404, 500)
- ✅ Examples for every endpoint
- ✅ Enum validations
- ✅ Pattern validations (regex)
- ✅ Data types and formats

### Documented Endpoints

#### Health
- `GET /api/health` - Health check

#### Accounts
- `GET /api/accounts` - List all accounts
- `POST /api/accounts` - Create new account
- `GET /api/accounts/{account_id}` - Get account details

#### Transactions
- `GET /api/transactions` - List transactions (with optional filtering)
- `POST /api/transactions` - Create transaction

#### Analytics
- `GET /api/analytics` - Get banking analytics

#### Banking AI
- `POST /api/banking-ai/validate` - AI transaction validation
- `POST /api/banking-ai/advice` - AI financial advice

### Data Models

Complete schemas for:
- `Account` - Full account object
- `AccountSummary` - Account summary view
- `Transaction` - Transaction object
- `TransactionRequest` - Transaction creation request
- `Analytics` - Analytics response
- `ValidationResult` - AI validation result
- `ErrorResponse` - Error response format

### Features

#### Request Validation
- Pattern matching (e.g., `^ACC\d{3}$` for account IDs)
- Enum validation for transaction types and statuses
- Required/optional field specifications
- Min/max value constraints

#### Response Examples
Multiple examples per endpoint:
- Success cases
- Error cases
- Edge cases
- Different scenarios

#### Interactive Testing
- Try API calls directly from Swagger UI
- Pre-filled example values
- Real-time response viewing
- cURL command generation

## Usage Examples

### Testing with Swagger UI

1. **Navigate to endpoint**: Click on any endpoint to expand it
2. **Try it out**: Click the "Try it out" button
3. **Fill parameters**: Modify the example JSON or use as-is
4. **Execute**: Click "Execute" to make the API call
5. **View response**: See the actual response, status code, and headers

### Creating an Account

```json
POST /api/accounts
{
  "owner": "Alice Johnson",
  "account_type": "Checking",
  "initial_balance": 1000.00
}
```

Response:
```json
{
  "success": true,
  "account": {
    "account_id": "ACC003",
    "owner": "Alice Johnson",
    "account_type": "Checking",
    "balance": 1000.00,
    "created_at": "2026-01-19T10:30:00",
    "status": "Active",
    "transactions_count": 0
  }
}
```

### Creating a Transaction

```json
POST /api/transactions
{
  "account_id": "ACC001",
  "transaction_type": "Debit",
  "amount": 100.00,
  "description": "Restaurant payment"
}
```

### AI Transaction Validation

```json
POST /api/banking-ai/validate
{
  "account_id": "ACC001",
  "amount": 100.00,
  "transaction_type": "Debit"
}
```

Response:
```json
{
  "success": true,
  "validation": {
    "risk_score": 20,
    "recommendation": "APPROVE",
    "reason": "OK",
    "risk_level": "low"
  }
}
```

## Integration Options

### Option 1: Use Integrated Backend

Run `baas_backend_with_docs.py` for backend + Swagger UI in one process.

```bash
python baas_backend_with_docs.py
```

### Option 2: Add to Existing Backend

Add Swagger UI to the original backend:

```python
from swagger_ui import register_swagger_ui

app = Flask(__name__)
# ... your existing code ...

register_swagger_ui(app)

if __name__ == '__main__':
    app.run()
```

### Option 3: Use OpenAPI Spec Separately

Use `openapi.yaml` with external tools:
- Import into Postman
- Generate client SDKs with OpenAPI Generator
- Use with API Gateway tools
- Integrate with CI/CD documentation pipelines

## OpenAPI Generator

Generate client libraries from the OpenAPI spec:

```bash
# Install OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Generate Python client
openapi-generator-cli generate -i openapi.yaml -g python -o ./client-python

# Generate JavaScript client
openapi-generator-cli generate -i openapi.yaml -g javascript -o ./client-js

# Generate TypeScript client
openapi-generator-cli generate -i openapi.yaml -g typescript-axios -o ./client-ts
```

## Testing with cURL

Swagger UI generates cURL commands automatically. Example:

```bash
# Health check
curl -X GET "http://localhost:5001/api/health"

# Get all accounts
curl -X GET "http://localhost:5001/api/accounts"

# Create account
curl -X POST "http://localhost:5001/api/accounts" \
  -H "Content-Type: application/json" \
  -d '{"owner":"Alice","account_type":"Checking","initial_balance":1000}'

# Get transactions for account
curl -X GET "http://localhost:5001/api/transactions?account_id=ACC001"
```

## API Design Notes

### Response Format
All responses follow this structure:
```json
{
  "success": true|false,
  "data_field": { ... },  // or "error": "message" for failures
}
```

### Error Handling
- `400` - Bad Request (invalid input)
- `404` - Not Found (account/resource doesn't exist)
- `500` - Internal Server Error

### Transaction Types
- `Debit` - Money out
- `Credit` - Money in
- `Transfer` - Between accounts
- `Withdrawal` - Cash withdrawal
- `Deposit` - Cash deposit

### Transaction Statuses
- `Approved` - Transaction successful
- `Pending` - Awaiting processing
- `Blocked` - Rejected (e.g., insufficient funds)

### AI Risk Levels
- **Low** (< $5,000): Risk score 20
- **Medium** ($5,000-$20,000): Risk score 50
- **High** (> $20,000): Risk score 80

## Extending the Documentation

To add new endpoints:

1. **Update `openapi.yaml`**:
   - Add path under `paths:`
   - Define request/response schemas
   - Add examples

2. **No code changes needed**:
   - Swagger UI automatically updates
   - Changes reflect immediately

Example:
```yaml
paths:
  /api/new-endpoint:
    get:
      tags:
        - New Feature
      summary: Description
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
```

## Validation Features

The OpenAPI spec includes:
- Pattern validation (regex)
- Enum validation
- Type validation
- Required field validation
- Min/max value constraints
- Format validation (date, date-time, float)

## Best Practices

1. **Keep spec in sync**: Update `openapi.yaml` when adding endpoints
2. **Use examples**: Provide realistic example data
3. **Document errors**: Include all possible error responses
4. **Version your API**: Use semantic versioning
5. **Test with Swagger UI**: Verify all endpoints work as documented

## Troubleshooting

### Swagger UI not loading
- Check that `swagger_ui.py` is in the same directory
- Verify PyYAML is installed: `pip install PyYAML`
- Check browser console for errors

### OpenAPI spec not found
- Ensure `openapi.yaml` exists in the same directory
- Check file permissions
- Verify YAML syntax: `python -c "import yaml; yaml.safe_load(open('openapi.yaml'))"`

### CORS errors
- Swagger UI is served from same origin (no CORS issues)
- For external clients, add CORS headers to Flask app

## Additional Resources

- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Postman OpenAPI Import](https://learning.postman.com/docs/integrations/available-integrations/working-with-openAPI/)

## Support

For issues or questions:
1. Check Swagger UI at http://localhost:5001/api/docs
2. Review OpenAPI spec for endpoint details
3. Test endpoints with "Try it out" feature
4. Check server logs for errors

---

**Ready to use!** Start the server and visit http://localhost:5001/api/docs
