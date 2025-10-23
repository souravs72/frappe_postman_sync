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

## Usage

### Bench Commands (Recommended)

```bash
# Generate APIs for a single DocType and sync to Postman
bench --site your-site execute frappe_postman_sync.generate_doctype_apis --args '["User"]'

# Generate APIs for an entire module and sync to Postman
bench --site your-site execute frappe_postman_sync.generate_module_apis --args '["QuickNotes"]'
```

### Wrapper Script (Simple Format)

```bash
# Make executable (one-time setup)
chmod +x postman-sync

# Generate APIs for DocType
./postman-sync --site your-site --doctype "User"

# Generate APIs for module
./postman-sync --site your-site --module "QuickNotes"
```

## Generated Endpoints

For each DocType:

- `GET /api/resource/{DocType}` - List records
- `GET /api/resource/{DocType}/{name}` - Get specific record
- `POST /api/resource/{DocType}` - Create record
- `PUT /api/resource/{DocType}/{name}` - Update record
- `DELETE /api/resource/{DocType}/{name}` - Delete record
- Plus any `@frappe.whitelist()` methods found automatically

## API Authentication

```http
Authorization: token your_api_key_here
```

## Configuration

Required Postman credentials:

- **API Key**: [Get from Postman](https://web.postman.co/settings/me/api-keys)
- **Workspace ID**: From workspace URL
- **Collection ID**: From collection URL

## License

MIT
