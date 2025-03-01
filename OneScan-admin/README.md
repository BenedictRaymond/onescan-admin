# Dynamic Form Builder

A web application that allows organizations to create custom forms with various field types. Built with Flask and modern web technologies.

## Features

- User authentication for organizations
- Dynamic form creation with drag-and-drop interface
- Support for multiple field types:
  - Text input
  - Email input
  - Number input
  - Phone input
  - Date input
  - Dropdown select
- Form preview functionality
- Responsive design

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Update the secret key in `app.py`:
```python
app.config['SECRET_KEY'] = 'your-secure-secret-key'
```

2. Update the Font Awesome kit URL in `templates/create_form.html` with your kit URL:
```html
<script src="https://kit.fontawesome.com/your-font-awesome-kit.js"></script>
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Register your organization with basic information
2. Log in to access the dashboard
3. Click "Create New Form" to start building a custom form
4. Add fields by clicking on the field types
5. Configure each field's properties
6. Save the form
7. View and manage your forms from the dashboard

## Project Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── templates/         # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── create_form.html
└── database.db        # SQLite database (created automatically)
```

## Security Considerations

- Passwords are hashed using Werkzeug's security functions
- Forms are associated with their creating organization
- User sessions are managed securely
- CSRF protection is enabled by default

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 