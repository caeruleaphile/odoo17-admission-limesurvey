# Admission Hub - Odoo LimeSurvey Integration

This module provides integration between Odoo 17 and LimeSurvey for managing admission forms.

## Features

- LimeSurvey form configuration management
- Support for different form types (student, professional, international)
- Form lifecycle management with opening and closing dates
- Integration with Odoo's chatter for tracking changes
- Modern UI with kanban, tree, and form views

## Installation

1. Clone this repository into your Odoo addons directory:
```bash
git clone https://github.com/YOUR_USERNAME/admission_hub.git
```

2. Update your Odoo configuration to include the addons path.

3. Install the module through Odoo's Apps menu or via command line:
```bash
python3 -m odoo -d YOUR_DATABASE -i admission_hub
```

## Configuration

1. Go to Admissions > LimeSurvey > Referenced Forms
2. Create a new form configuration with:
   - Form name
   - LimeSurvey ID
   - Form type
   - Opening and closing dates
   - Survey URL

## Usage

### Managing Forms
1. Navigate to Admissions > LimeSurvey > Referenced Forms
2. Create or edit form configurations
3. Use the Connect button to establish connection with LimeSurvey
4. Track form status and history through the chatter

### Views
- Kanban view for visual form management
- Tree view for list-based operations
- Detailed form view with all configuration options

## Development

### Module Structure
```
admission_hub/
├── models/
│   └── limesurvey_config.py
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── limesurvey_config_views.xml
│   └── menu_views.xml
├── tests/
│   └── test_limesurvey_config.py
├── __init__.py
└── __manifest__.py
```

### Testing
Run the tests using:
```bash
python3 -m odoo -d YOUR_DATABASE --test-enable --stop-after-init -i admission_hub
```

## License

This module is licensed under the LGPL-3.0 license.

## Support

For support and contributions, please create an issue on the GitHub repository. 