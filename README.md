# Frappe Postman Sync

Auto-generates CRUD APIs for DocTypes and syncs them to Postman collections.

## Installation

```bash
bench --site your-site install-app frappe_postman_sync
bench --site your-site migrate
```

## Quick Setup

1. **Configure Postman Settings**:
   - Search "Postman Setting" in Frappe Desk
   - Add your Postman API credentials (API Key, Workspace ID, Collection ID)
   - Enable auto-sync

2. **Generate APIs**:
   - **Automatic**: Create any DocType → APIs auto-generated
   - **Manual**: Use API Generator for specific DocTypes or entire modules

## Generated Endpoints

For each DocType:
- `GET /api/resource/{DocType}` - List records
- `GET /api/resource/{DocType}/{name}` - Get specific record
- `POST /api/resource/{DocType}` - Create record
- `PUT /api/resource/{DocType}/{name}` - Update record
- `DELETE /api/resource/{DocType}/{name}` - Delete record
- `GET /api/method/frappe.desk.reportview.get` - Advanced filtering

Plus any `@frappe.whitelist()` methods found automatically.

## API Authentication

```http
Authorization: token your_api_key_here
```

## Configuration

### Postman Credentials Required:
- **API Key**: [Get from Postman](https://web.postman.co/settings/me/api-keys)
- **Workspace ID**: From workspace URL
- **Collection ID**: From collection URL

## Usage

### Auto Generation
Create a DocType → APIs are automatically generated and synced to Postman.

### Manual Generation
```python
# Generate for specific DocType
frappe.call("frappe_postman_sync.services.generate_api_for_doctype", "Your DocType")

# Sync all to Postman
frappe.call("frappe_postman_sync.api.postman_sync.sync_all_apis_to_postman")
```

### Module Generation
Use API Generator → Select "Entire Module" → Choose module → Generate APIs for all DocTypes in that module.

## Troubleshooting

- **Connection Failed**: Check API key, workspace ID, collection ID
- **APIs Not Syncing**: Verify auto-sync enabled, check Postman Settings status
- **Endpoints Not Working**: Verify site accessibility, check API key permissions

## Development

```
frappe_postman_sync/
├── frappe_postman_sync/
│   ├── doctype/
│   │   ├── postman_setting/     # Single DocType config
│   │   └── api_generator/       # API management
│   ├── api/                     # API endpoints
│   ├── services.py              # Core services
│   ├── utils.py                 # Utilities
│   └── hooks.py                 # Auto-generation hooks
└── SETUP_GUIDE.md
```

## License

MIT
