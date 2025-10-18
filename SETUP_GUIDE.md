# Frappe Postman Sync - Setup Guide

This guide will help you set up the Frappe Postman Sync app to automatically generate CRUD APIs for your doctypes and sync them with Postman.

## Prerequisites

1. **Frappe Bench** installed and running
2. **Postman** installed on your laptop
3. **Postman Account** with API access

## Installation

1. **Install the app** (if not already installed):

   ```bash
   bench --site your-site install-app frappe_postman_sync
   ```

2. **Migrate the database**:
   ```bash
   bench --site your-site migrate
   ```

## API Generation Methods

The app supports two methods for generating APIs:

### 1. Automatic Generation (Single DocType)

- APIs are automatically generated when you create new doctypes
- Perfect for individual doctype testing
- No manual intervention required

### 2. Manual Generation (Single DocType or Module)

- Use the API Generator for precise control
- Generate APIs for specific doctypes
- Generate APIs for entire modules (all doctypes in a module)

## Configuration

### Step 1: Get Your Postman API Key

1. Go to [Postman API Keys](https://web.postman.co/settings/me/api-keys)
2. Click "Generate API Key"
3. Give it a name (e.g., "Frappe Integration")
4. Copy the generated API key

### Step 2: Create a Postman Collection

1. Go to [Postman Collections](https://web.postman.co/collections)
2. Click "Create Collection"
3. Name it "Frappe CRUD APIs" (or any name you prefer)
4. Note down the Collection ID from the URL

### Step 3: Get Workspace ID

1. Go to [Postman Workspaces](https://web.postman.co/workspaces)
2. Click on your workspace
3. Copy the Workspace ID from the URL

### Step 4: Configure Postman Settings in Frappe

1. **Navigate to Postman Settings**:

   - Go to Frappe Desk
   - Search for "Postman Settings"
   - Create a new record

2. **Fill in the configuration**:

   - **Title**: Give it a descriptive name
   - **Postman API Key**: Paste your API key from Step 1
   - **Workspace ID**: Paste your workspace ID from Step 3
   - **Collection ID**: Paste your collection ID from Step 2
   - **Base URL**: Your Frappe site URL (e.g., http://localhost:8000)
   - **Enable Auto Sync**: Check this box
   - **Sync Frequency**: Choose "Immediate" for instant sync

3. **Test Connection**:
   - Click "Test Connection" button
   - Verify that the status shows "Active"

## How It Works

### Automatic API Generation

1. **When you create a new DocType**:

   - The app automatically detects the new DocType
   - Creates an API Generator record for it
   - Generates CRUD API endpoints
   - Scans for whitelisted methods
   - Syncs the APIs to your Postman collection

2. **Generated API Endpoints**:
   - `GET /api/resource/{DocType}` - List all records
   - `GET /api/resource/{DocType}/{name}` - Get specific record
   - `POST /api/resource/{DocType}` - Create new record
   - `PUT /api/resource/{DocType}/{name}` - Update existing record
   - `DELETE /api/resource/{DocType}/{name}` - Delete record
   - `GET /api/method/frappe.desk.reportview.get` - Advanced filtering

### Whitelisted Methods Discovery

1. **Automatic Scanning**:

   - Scans all installed apps for `@frappe.whitelist()` decorated methods
   - Discovers custom methods in doctype controllers
   - Finds methods defined in `hooks.py` files
   - Automatically includes relevant methods for each doctype

2. **Custom Method Examples**:

   ```python
   @frappe.whitelist()
   def calculate_total(self):
       # This method will be automatically discovered and added to Postman
       return self.amount * self.quantity

   @frappe.whitelist()
   def send_notification(self, message):
       # Custom methods with parameters are also supported
       frappe.msgprint(message)
   ```

### Manual Operations

1. **Regenerate APIs**: Use the "Regenerate APIs" button in API Generator
2. **Test Endpoints**: Use the "Test Endpoints" button to verify APIs work
3. **Sync to Postman**: Use the "Sync to Postman" button in Postman Settings
4. **Scan Whitelisted Methods**: Use the "Scan Whitelisted Methods" button to discover and sync custom methods
5. **System Status**: Use the "System Status" button to view comprehensive system information

## Module-based API Generation

Generate APIs for entire modules (all doctypes within a module) using the API Generator:

### Step 1: Access API Generator

1. Go to **API Generator** list
2. Click **New** to create a new API Generator record

### Step 2: Configure Module Generation

1. **Generation Type**: Select "Entire Module"
2. **Module Name**: Select the module you want to generate APIs for
3. **Auto Generate**: Check this to automatically generate APIs
4. **Save** the record

### Step 3: Generated APIs

The system will:

- Find all custom doctypes in the selected module
- Generate CRUD APIs for each doctype
- Store all endpoints in a structured JSON format
- Display the count of generated APIs in the description

### Example Module Generation

```json
{
  "Customer": [
    {
      "method": "GET",
      "path": "/api/resource/Customer",
      "description": "Get list of Customer records"
    }
    // ... more endpoints
  ],
  "Sales Order": [
    {
      "method": "GET",
      "path": "/api/resource/Sales Order",
      "description": "Get list of Sales Order records"
    }
    // ... more endpoints
  ]
  // ... more doctypes
}
```

### Benefits of Module Generation

- **Bulk Generation**: Create APIs for multiple doctypes at once
- **Module Testing**: Test entire modules comprehensively
- **Time Saving**: Avoid manual generation for each doctype
- **Consistency**: Ensure all doctypes in a module have APIs

## Testing the Integration

### Step 1: Create a Test DocType

1. Go to **Customize > DocType**
2. Click "New"
3. Create a simple DocType (e.g., "Test Item")
4. Add a few fields (e.g., "Item Name", "Price")
5. Save the DocType

### Step 2: Verify API Generation

1. Go to **API Generator** list
2. Look for your new DocType
3. Check that the status is "Active"
4. Review the generated API endpoints

### Step 3: Check Postman Collection

1. Open Postman
2. Go to your collection
3. You should see new folders/requests for your DocType
4. Test the APIs using the generated requests

### Step 4: Test Whitelisted Methods (Optional)

1. **Add a Custom Method to Your DocType**:

   ```python
   @frappe.whitelist()
   def calculate_discount(self, discount_percent):
       return self.amount * (discount_percent / 100)
   ```

2. **Scan for Whitelisted Methods**:

   - Go to Postman Settings
   - Click "Scan Whitelisted Methods" button
   - Check that your custom method appears in the collection

3. **Test the Custom Method**:
   - Find the custom method in your Postman collection
   - Test it with appropriate parameters

## Whitelisted Methods Discovery

The app automatically discovers whitelisted methods in several ways:

### 1. Automatic Scanning

- Scans all installed apps for `@frappe.whitelist()` decorated methods
- Discovers custom methods in doctype controllers
- Finds methods defined in `hooks.py` files
- Automatically includes relevant methods for each doctype

### 2. Manual Discovery

- Use the "Scan Whitelisted Methods" button in Postman Settings
- This will discover and sync all custom methods across your installation

### 3. Method Examples

```python
# Basic method
@frappe.whitelist()
def get_customer_balance(self):
    return frappe.db.get_value("Customer", self.customer, "credit_limit")

# Method with parameters
@frappe.whitelist()
def calculate_tax(self, tax_rate):
    return self.grand_total * (tax_rate / 100)

# Complex method
@frappe.whitelist()
def send_payment_reminder(self, reminder_type="email"):
    if reminder_type == "email":
        frappe.sendmail(
            recipients=[self.customer_email],
            subject="Payment Reminder",
            message=f"Please pay invoice {self.name}"
        )
    return {"status": "sent", "type": reminder_type}
```

## API Usage Examples

### Authentication

All API requests require authentication using your Frappe API key:

```http
Authorization: token your_api_key_here
```

### Example API Calls

**Create a record:**

```http
POST /api/resource/Test Item
Content-Type: application/json
Authorization: token your_api_key_here

{
    "item_name": "Sample Item",
    "price": 100
}
```

**Get all records:**

```http
GET /api/resource/Test Item
Authorization: token your_api_key_here
```

**Update a record:**

```http
PUT /api/resource/Test Item/ITEM-0001
Content-Type: application/json
Authorization: token your_api_key_here

{
    "item_name": "Updated Item Name",
    "price": 150
}
```

**Call a whitelisted method:**

```http
POST /api/method/your_app.doctype.test_item.test_item.calculate_discount
Content-Type: application/json
Authorization: token your_api_key_here

{
    "args": ["ITEM-0001", 10]
}
```

## Troubleshooting

### Common Issues

1. **"Failed to connect to Postman API"**:

   - Verify your API key is correct
   - Check that your Workspace ID is correct
   - Ensure you have proper permissions

2. **"Invalid collection ID"**:

   - Verify your Collection ID is correct
   - Make sure you have write access to the collection

3. **APIs not syncing**:

   - Check if "Enable Auto Sync" is checked
   - Verify Postman Settings status is "Active"
   - Try manual sync using "Sync to Postman" button

4. **API endpoints not working**:
   - Ensure your Frappe site is accessible
   - Check your API key permissions
   - Verify the DocType exists and is accessible

### Getting Help

1. Check the **Error Log** in Frappe for detailed error messages
2. Review the **API Generator** records for any failed generations
3. Test individual API endpoints using Postman

## Advanced Configuration

### Custom API Endpoints

You can extend the generated APIs by modifying the `build_crud_endpoints` method in the API Generator DocType.

### Scheduled Sync

The app supports scheduled sync frequencies:

- **Immediate**: Sync as soon as APIs are generated
- **Hourly**: Sync every hour
- **Daily**: Sync once per day

### Environment Variables

The app automatically creates Postman environment variables:

- `base_url`: Your Frappe site URL
- `api_key`: Your API key (set this manually in Postman)
- `site_name`: Your site name

## Support

For issues or questions:

1. Check the Frappe forum
2. Create an issue in the app repository
3. Contact the app developer

---

**Happy API Testing with Frappe Postman Sync!** 🚀
