# Setup Guide

## Prerequisites

- Frappe Bench installed
- Postman account with API access

## Installation

```bash
bench --site your-site install-app frappe_postman_sync
bench --site your-site migrate
```

## Configuration

### 1. Get Postman Credentials

- **API Key**: [Generate here](https://web.postman.co/settings/me/api-keys)
- **Workspace ID**: From your workspace URL
- **Collection ID**: From your collection URL

### 2. Configure in Frappe

1. Search "Postman Setting" in Frappe Desk
2. Fill in:
   - Postman API Key
   - Workspace ID  
   - Collection ID
   - Base URL (e.g., `http://localhost:8000`)
   - Enable Auto Sync ✓
3. Click "Test Connection"

## Usage

### Automatic Generation
Create any DocType → APIs auto-generated and synced to Postman.

### Manual Generation
1. Go to **API Generator**
2. Create new record:
   - **Single DocType**: Select specific DocType
   - **Entire Module**: Select "Entire Module" → Choose module
3. Save → APIs generated

### Whitelisted Methods
Any `@frappe.whitelist()` methods are automatically discovered and added to Postman.

```python
@frappe.whitelist()
def calculate_discount(self, discount_percent):
    return self.grand_total * (discount_percent / 100)
```

## Testing

### 1. Create Test DocType
- Customize → DocType → New
- Add fields → Save

### 2. Verify APIs
- Check API Generator for your DocType
- Verify status is "Active"

### 3. Test in Postman
- Open your collection
- Find DocType folder
- Test the generated requests

## API Examples

```http
# Create record
POST /api/resource/YourDocType
Authorization: token your_api_key
Content-Type: application/json

{
    "field1": "value1",
    "field2": "value2"
}

# Get records
GET /api/resource/YourDocType
Authorization: token your_api_key

# Call whitelisted method
POST /api/method/your_app.doctype.your_doctype.your_doctype.calculate_discount
Authorization: token your_api_key
Content-Type: application/json

{
    "args": ["DOC-001", 10]
}
```

## Troubleshooting

- **Connection Failed**: Check API key, workspace ID, collection ID
- **APIs Not Syncing**: Verify auto-sync enabled, check Postman Settings status
- **Endpoints Not Working**: Check site accessibility, API key permissions
- **Check Error Log**: Frappe → Error Log for detailed errors
