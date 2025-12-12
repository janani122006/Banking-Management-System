
# 🏦 Banking Management System

A full-stack banking management system with a modern web interface and secure backend API. Manage bank accounts, process transactions, and track financial activities seamlessly.

![Banking System](https://img.shields.io/badge/Banking-System-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![Flask](https://img.shields.io/badge/Flask-API-lightgrey)

## ✨ Features

### 🎯 Core Banking Operations
- **Account Management**: Create new bank accounts with customer details
- **Deposit/Withdrawal**: Process financial transactions securely
- **Balance Inquiry**: Real-time account balance checking
- **Transaction History**: Detailed transaction logs with timestamps
- **Account Search**: Find accounts by name or account number

### 🛡️ Security Features
- Secure MySQL database with proper constraints
- Transaction logging for audit trails
- Input validation and error handling
- CORS protection for API security
- Session management ready

### 💻 User Interface
- Modern, responsive design with dark/light modes
- Real-time notifications and alerts
- Interactive transaction history viewer
- Mobile-friendly interface
- Loading states and progress indicators

### 🔧 Technical Features
- RESTful API with proper HTTP methods
- Database auto-initialization
- Comprehensive error handling
- Health monitoring endpoints
- Detailed logging system

## 📋 Prerequisites

### Required Software
1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **MySQL Server** (via XAMPP/WAMP/MAMP) - [XAMPP Download](https://www.apachefriends.org/)
3. **Web Browser** (Chrome, Firefox, Edge)

### Recommended Tools
- **Git** for version control
- **VS Code** or any code editor
- **Postman** for API testing

## 🚀 Quick Start

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd banking-system
```

### Step 2: Project Structure Setup
```
banking-system/
├── backend/           # Flask API Server
│   ├── app.py         # Main Flask application
│   ├── banking_db.py  # Database operations
│   └── requirements.txt
├── frontend/          # Web Interface
│   ├── index.html     # Main HTML file
│   ├── style.css      # Styling
│   └── script.js      # Frontend logic
└── README.md          # This file
```

### Step 3: Database Setup

#### For XAMPP (Windows):
1. Open XAMPP Control Panel
2. Click **Start** next to MySQL
3. Default credentials: `root` with **empty password**
4. MySQL runs on port **3306**

#### For WAMP (Windows):
1. Start WAMP Server
2. Click system tray icon → **Start All Services**
3. MySQL runs on port **3306**

#### For Linux/Mac:
```bash
sudo systemctl start mysql
# or with Homebrew:
brew services start mysql
```

### Step 4: Backend Setup
```bash
# Navigate to backend folder
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python app.py
```

### Step 5: Frontend Setup
```bash
# Open new terminal
cd frontend

# Start HTTP server
python -m http.server 8000
```

### Step 6: Access the Application
1. **Backend API**: `http://localhost:5000`
2. **Frontend Interface**: `http://localhost:8000`
3. **API Documentation**: `http://localhost:5000/`

## 📊 Database Schema

### Accounts Table
```sql
CREATE TABLE accounts (
    acc_no INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    trans_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_no INT NOT NULL,
    type VARCHAR(20),      -- Deposit, Withdrawal, Transfer
    amount DECIMAL(15, 2),
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no) ON DELETE CASCADE
);
```

## 🔌 API Endpoints

### Health & Status
- `GET /api/health` - Check API and database status
- `GET /` - API documentation and available endpoints

### Account Operations
- `POST /api/create_account` - Create new bank account
- `POST /api/deposit` - Deposit money into account
- `POST /api/withdraw` - Withdraw money from account
- `GET /api/balance/<acc_no>` - Get account balance
- `GET /api/transactions/<acc_no>` - Get transaction history
- `GET /api/all_accounts` - List all accounts

### Administrative
- `POST /api/init_db` - Initialize database tables
- `GET /api/summary` - System statistics

## 💡 Usage Guide

### Creating an Account
1. Open `http://localhost:8000` in browser
2. Click "Create Account" in left menu
3. Enter customer name and initial deposit (minimum $10)
4. Click "Create Account"
5. Note your account number from success message

### Making a Deposit
1. Select "Deposit Money" from menu
2. Enter account number and amount
3. Click "Deposit Funds"
4. Verify success notification

### Checking Balance
1. Select "View Balance" from menu
2. Enter account number
3. Click "Check Balance"
4. View account details and current balance

### Viewing Transactions
1. Select "Transaction History" from menu
2. Enter account number
3. Click "View History"
4. Browse all transactions with dates and amounts

## 🧪 Testing the API

### Using curl
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Create test account
curl -X POST http://localhost:5000/api/create_account \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","balance":100}'

# Check balance
curl http://localhost:5000/api/balance/1
```

### Using Python
```python
import requests

# Test connection
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Create account
data = {"name": "John Doe", "balance": 500.00}
response = requests.post('http://localhost:5000/api/create_account', json=data)
print(response.json())
```

## 🔧 Configuration

### Database Configuration
Edit `backend/app.py` to modify database settings:
```python
DB_CONFIG = {
    'host': 'localhost',      # MySQL host
    'user': 'root',           # MySQL username
    'password': '',           # MySQL password
    'database': 'banking_db'  # Database name
}
```

### API Configuration
- **Port**: Default 5000 (change in `app.py`)
- **Debug Mode**: Enabled by default
- **CORS**: Enabled for localhost domains

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. MySQL Connection Failed
**Error**: `Can't connect to MySQL server on 'localhost'`
**Solution**:
- Ensure MySQL service is running
- Check XAMPP/WAMP control panel
- Verify port 3306 is available

#### 2. Python Module Not Found
**Error**: `ModuleNotFoundError: No module named 'flask'`
**Solution**:
```bash
pip install -r requirements.txt
```

#### 3. Port Already in Use
**Error**: `Address already in use`
**Solution**:
```bash
# Find process using port
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Mac/Linux

# Kill process or change port in app.py
```

#### 4. CORS Errors in Browser
**Error**: `Access blocked by CORS policy`
**Solution**:
- Ensure `CORS(app)` is enabled in app.py
- Clear browser cache (Ctrl+Shift+R)
- Check network tab in DevTools

### Debug Mode
When backend is running in debug mode:
- Automatic reload on code changes
- Detailed error messages
- Debugger PIN for interactive debugging
- Access debugger at `http://localhost:5000/console`



## 📈 Performance

### Database Optimization
- Indexes on frequently queried columns
- Connection pooling for database connections
- Query optimization for large datasets

### API Performance
- Response compression
- Caching for static data
- Pagination for transaction history

## 🧰 Development

### Running in Development Mode
```bash
# Backend with hot reload
cd backend
python app.py  # Debug mode enabled by default

# Frontend with live reload (optional)
cd frontend
# Use VS Code Live Server extension
```

### Code Structure
```
frontend/
├── index.html     # Main application interface
├── style.css      # All styling and animations
└── script.js      # Client-side logic and API calls

backend/
├── app.py         # Flask application and routes
├── banking_db.py  # Database operations and models
└── requirements.txt
```



*This system is designed for educational purposes to demonstrate full-stack web development with Python, Flask, MySQL, and modern frontend technologies.*
