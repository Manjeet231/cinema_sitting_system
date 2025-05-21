# Cinema Seating System

This is a prototype seating system for a cinema theatre that provides an interactive interface for seat selection and an intelligent algorithm for optimal seat allocation.

## File Structure

```
cinema_seating_system/
├── src/                      # Source code directory
│   ├── static/               # Static assets
│   │   ├── css/              # CSS stylesheets
│   │   │   └── styles.css    # Main stylesheet
│   │   ├── js/               # JavaScript files
│   │   │   └── seating.js    # Seating algorithm and UI interactions
│   │   └── index.html        # Main HTML page
│   ├── models/               # Data models
│   │   ├── seating.py        # Seating model and business logic
│   │   └── user.py           # User model
│   ├── routes/               # API routes
│   │   ├── seating.py        # Seating-related endpoints
│   │   ├── improved_seating.py # Enhanced seating algorithm
│   │   └── user.py           # User-related endpoints
│   ├── data/                 # Data storage
│   │   └── seating.json      # Seating configuration
│   ├── __init__.py           # Package initialization
│   └── main.py               # Application entry point
├── tests/                    # Test directory
│   ├── test_seating_algorithm.py      # Tests for basic algorithm
│   ├── test_improved_algorithm.py     # Tests for enhanced algorithm
│   ├── test_seating_algorithm_js.py   # Tests for JavaScript algorithm
│   └── run_tests.py          # Test runner
└── requirements.txt          # Python dependencies
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- VS Code or any code editor

### Installation

1. **Clone or extract the project files to your local machine**

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask server**:
   ```bash
   cd src
   python main.py
   ```

2. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

### Running Tests

```bash
python -m tests.run_tests
```

## Deployment Instructions

### Local Deployment

The application runs on Flask's development server by default. For a more robust local deployment, you can use Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### Cloud Deployment

To deploy to a cloud platform:

1. **Ensure your `requirements.txt` is up to date**:
   ```bash
   pip freeze > requirements.txt
   ```

2. **For platforms like Heroku**:
   - Create a `Procfile` with:
     ```
     web: gunicorn src.main:app
     ```
   - Follow the platform's deployment instructions

3. **For platforms like AWS, Azure, or GCP**:
   - Follow their specific Flask deployment guides
   - Ensure you set the correct environment variables

## VS Code Configuration

For optimal development in VS Code:

1. **Install recommended extensions**:
   - Python
   - Pylance
   - Flask-Snippets
   - HTML CSS Support
   - JavaScript (ES6) code snippets

2. **Configure Python interpreter**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment

3. **Set up debugging**:
   - Create a `.vscode/launch.json` file with:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: Flask",
         "type": "python",
         "request": "launch",
         "module": "flask",
         "env": {
           "FLASK_APP": "src/main.py",
           "FLASK_ENV": "development"
         },
         "args": [
           "run",
           "--no-debugger",
           "--no-reload"
         ],
         "jinja": true
       }
     ]
   }
   ```

## Features

- Interactive seating map with color-coded availability
- Automatic seat allocation for groups
- VIP, accessible, and normal seating zones
- Admin mode for overriding seating rules
- Prevention of single-seat gaps
- Center and middle row seat prioritization

## Algorithm Overview

The seating algorithm prioritizes:
1. Keeping groups together in the same row
2. Allocating seats in middle rows for optimal viewing
3. Centering groups in each row when possible
4. Preventing single-seat gaps between bookings
5. Respecting seat type preferences (VIP, Accessible, Normal)

## License

This project is provided for educational purposes only.
