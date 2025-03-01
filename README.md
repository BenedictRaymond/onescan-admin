# OneScan Admin Portal

OneScan is a modern QR code-based form management system that allows organizations to create, manage, and collect data through dynamic forms. The system generates QR codes for each form, making it easy for users to access and fill out forms using their mobile devices.

## Features

- **User Authentication**: Secure login and registration system for organizations
- **Dynamic Form Builder**: Create custom forms with various field types
- **QR Code Generation**: Automatic QR code generation for each form
- **Modern UI**: Clean and responsive design using Bootstrap 5
- **Database Integration**: MySQL backend for reliable data storage

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, Bootstrap 5
- **Database**: MySQL
- **Authentication**: Flask-Login
- **Forms**: Dynamic form generation and handling
- **QR Codes**: QR code generation for form access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/onescan-admin.git
cd onescan-admin
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```
FLASK_SECRET_KEY=your_secret_key
FLASK_DEBUG=True

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=form_builder
MYSQL_PORT=3306
```

5. Initialize the database:
```bash
python app.py
```

## Usage

1. Start the development server:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Register your organization and start creating forms

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask framework
- Bootstrap 5
- Font Awesome icons
- QRCode library 