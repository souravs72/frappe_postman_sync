# Frappe Postman Sync

A powerful Frappe app that automatically generates CRUD API endpoints for your doctypes and syncs them with Postman for easy API testing and documentation.

## Features

- 🚀 **Automatic API Generation**: Automatically creates CRUD APIs when you create new doctypes
- 🔄 **Postman Integration**: Syncs generated APIs directly to your Postman collections
- 🔍 **Whitelisted Methods Discovery**: Automatically finds and syncs custom `@frappe.whitelist()` methods
- 📚 **Comprehensive Documentation**: Generates detailed API documentation
- ⚡ **Real-time Sync**: APIs are synced immediately or on a schedule
- 🛠️ **Easy Configuration**: Simple setup with Postman API credentials
- 📊 **Status Monitoring**: Track API generation and sync status
- 🏗️ **Module-based Generation**: Generate APIs for entire modules (all doctypes) at once
- 🎯 **Flexible Generation**: Choose between single doctype or module-wide API generation

## Installation

1. **Install the app**:

   ```bash
   bench --site your-site install-app frappe_postman_sync
   ```

2. **Migrate the database**:
   ```bash
   bench --site your-site migrate
   ```

## Quick Setup

1. **Configure Postman Settings**:

   - Go to Frappe Desk → Search "Postman Settings"
   - Create a new record with your Postman API credentials
   - Enable auto-sync

2. **Generate APIs**:
   - **Automatic**: Create any custom doctype and APIs are automatically generated
   - **Manual**: Use API Generator to create APIs for specific doctypes or entire modules

## API Generation Options

### Single DocType Generation

- Generate APIs for individual doctypes
- Perfect for specific doctype testing
- Automatically triggered when creating new doctypes

### Module-based Generation

- Generate APIs for all doctypes within a module
- Bulk API generation for entire modules
- Ideal for comprehensive module testing
- Access via API Generator → Select "Entire Module"

## Generated API Endpoints

For each doctype, the app generates:

### Standard CRUD Operations

- `GET /api/resource/{DocType}` - List all records
- `GET /api/resource/{DocType}/{name}` - Get specific record
- `POST /api/resource/{DocType}` - Create new record
- `PUT /api/resource/{DocType}/{name}` - Update existing record
- `DELETE /api/resource/{DocType}/{name}` - Delete record
- `GET /api/method/frappe.desk.reportview.get` - Advanced filtering

### Whitelisted Methods

- **Automatic Discovery**: Scans all apps for `@frappe.whitelist()` decorated methods
- **Custom Methods**: Includes custom business logic methods from doctype controllers
- **Hook Methods**: Discovers methods defined in `hooks.py` files
- **Smart Detection**: Automatically finds and includes relevant whitelisted methods for each doctype

**Example Custom Method:**

```python
@frappe.whitelist()
def calculate_discount(self, discount_percent):
    """Calculate discount for the invoice"""
    return self.grand_total * (discount_percent / 100)
```

This method will be automatically discovered and added to Postman as:

```
POST /api/method/your_app.doctype.invoice.invoice.calculate_discount
```

## Components

### DocTypes

1. **Postman Settings**: Configure Postman API credentials and sync settings
2. **API Generator**: Manage and monitor generated APIs for each doctype

### Services

- **Automatic API Generation**: Hooks into doctype creation events
- **Postman Sync Service**: Handles API synchronization with Postman
- **Documentation Generator**: Creates comprehensive API documentation

### API Endpoints

- `/api/method/frappe_postman_sync.api.postman_sync.sync_all_apis_to_postman`
- `/api/method/frappe_postman_sync.api.help.get_setup_instructions`
- `/api/method/frappe_postman_sync.api.help.get_system_status`
- `/api/method/frappe_postman_sync.api.help.scan_and_sync_whitelisted_methods`
- `/api/method/frappe_postman_sync.services.generate_api_for_doctype`
- `/api/method/frappe_postman_sync.whitelist_scanner.get_all_whitelisted_methods`

## Configuration

### Required Postman Credentials

1. **Postman API Key**: Get from [Postman API Keys](https://web.postman.co/settings/me/api-keys)
2. **Workspace ID**: Found in your workspace URL
3. **Collection ID**: Found in your collection URL

### Sync Options

- **Immediate**: Sync APIs as soon as they're generated
- **Hourly**: Sync every hour
- **Daily**: Sync once per day

## Usage Examples

### Creating a New DocType

1. Go to **Customize → DocType**
2. Create a new doctype (e.g., "Product")
3. Add fields as needed
4. Save the doctype
5. Check **API Generator** - your APIs are automatically created!
6. Check **Postman** - your APIs are synced and ready to test!

### Manual API Generation

```python
# Generate APIs for a specific doctype
frappe.call("frappe_postman_sync.services.generate_api_for_doctype", "Your DocType")

# Sync all APIs to Postman
frappe.call("frappe_postman_sync.api.postman_sync.sync_all_apis_to_postman")
```

### Testing APIs in Postman

1. Open your Postman collection
2. Find the folder for your doctype
3. Use the pre-configured requests
4. Set your API key in the environment variables
5. Test your APIs!

## API Authentication

All generated APIs require authentication using your Frappe API key:

```http
Authorization: token your_api_key_here
```

## Troubleshooting

### Common Issues

1. **Postman API Connection Failed**:

   - Verify your API key is correct
   - Check workspace and collection IDs
   - Ensure proper permissions

2. **APIs Not Syncing**:

   - Check if auto-sync is enabled
   - Verify Postman Settings status
   - Try manual sync

3. **API Endpoints Not Working**:
   - Verify site accessibility
   - Check API key permissions
   - Review Error Log for details

### Getting Help

1. Check the **Error Log** in Frappe
2. Review **API Generator** records for failed generations
3. Test individual endpoints in Postman

## Development

### File Structure

```
frappe_postman_sync/
├── frappe_postman_sync/
│   ├── doctype/
│   │   ├── postman_settings/
│   │   └── api_generator/
│   ├── api/
│   │   ├── postman_sync.py
│   │   └── help.py
│   ├── services.py
│   ├── utils.py
│   └── hooks.py
├── SETUP_GUIDE.md
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:

- Create an issue in the repository
- Contact the developer
- Check the Frappe forum

---

**Happy API Testing! 🚀**
