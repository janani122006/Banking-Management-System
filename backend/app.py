from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',      # default empty in XAMPP
    'database': 'banking_db'
}

def get_connection():
    """Create and return database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database with required tables"""
    try:
        # First connect without specifying database
        config = DB_CONFIG.copy()
        config.pop('database', None)
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS banking_db")
        cursor.execute("USE banking_db")
        
        # Create accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                acc_no INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                balance DECIMAL(15, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                trans_id INT AUTO_INCREMENT PRIMARY KEY,
                acc_no INT NOT NULL,
                type VARCHAR(20),
                amount DECIMAL(15, 2),
                date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (acc_no) REFERENCES accounts(acc_no) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database initialized successfully!")
        return True
        
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        return False

# Initialize database on startup
init_database()

# ========== API ENDPOINTS ==========

@app.route('/')
def index():
    """Home endpoint"""
    return jsonify({
        'message': 'Banking System API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health (GET)',
            'create_account': '/api/create_account (POST)',
            'deposit': '/api/deposit (POST)',
            'withdraw': '/api/withdraw (POST)',
            'balance': '/api/balance/<acc_no> (GET)',
            'transactions': '/api/transactions/<acc_no> (GET)',
            'init_db': '/api/init_db (POST)'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_connection()
        if conn:
            conn.close()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/init_db', methods=['POST', 'GET'])
def initialize_database_endpoint():
    """Initialize database endpoint"""
    try:
        success = init_database()
        if success:
            return jsonify({
                'success': True,
                'message': 'Database initialized successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to initialize database'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/create_account', methods=['POST', 'OPTIONS'])
def create_account():
    """Create a new bank account"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.json
        logger.info(f"Create account request data: {data}")
        
        name = data.get('name', '').strip()
        balance = float(data.get('balance', 0))
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        if balance < 10:
            return jsonify({
                'success': False,
                'error': 'Minimum initial deposit is $10'
            }), 400
        
        conn = get_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Insert new account
        sql = "INSERT INTO accounts (name, balance) VALUES (%s, %s)"
        cursor.execute(sql, (name, balance))
        conn.commit()
        
        # Get the auto-generated account number
        account_no = cursor.lastrowid
        
        # Log initial deposit as a transaction
        if balance > 0:
            cursor.execute("""
                INSERT INTO transactions (acc_no, type, amount) 
                VALUES (%s, %s, %s)
            """, (account_no, "Initial Deposit", balance))
            conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info(f"Account created: #{account_no} for {name} with ${balance}")
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'account_number': account_no,
            'name': name,
            'balance': balance
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid balance amount'
        }), 400
    except Exception as e:
        logger.error(f"Create account error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/deposit', methods=['POST', 'OPTIONS'])
def deposit():
    """Deposit money into an account"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.json
        logger.info(f"Deposit request data: {data}")
        
        acc_no = int(data.get('acc_no', 0))
        amount = float(data.get('amount', 0))
        
        if acc_no <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid account number'
            }), 400
        
        if amount <= 0:
            return jsonify({
                'success': False,
                'error': 'Amount must be positive'
            }), 400
        
        conn = get_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Check if account exists
        cursor.execute("SELECT name, balance FROM accounts WHERE acc_no=%s", (acc_no,))
        account = cursor.fetchone()
        
        if not account:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        # Update balance
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no = %s",
                      (amount, acc_no))
        
        # Add transaction record
        cursor.execute("INSERT INTO transactions (acc_no, type, amount) VALUES (%s, %s, %s)",
                      (acc_no, "Deposit", amount))
        
        conn.commit()
        
        # Get updated balance
        cursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc_no,))
        new_balance = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(f"Deposited ${amount} to account #{acc_no}. New balance: ${new_balance}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully deposited ${amount:.2f}',
            'account_number': acc_no,
            'amount': amount,
            'new_balance': new_balance
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid input data'
        }), 400
    except Exception as e:
        logger.error(f"Deposit error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/withdraw', methods=['POST', 'OPTIONS'])
def withdraw():
    """Withdraw money from an account"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.json
        logger.info(f"Withdraw request data: {data}")
        
        acc_no = int(data.get('acc_no', 0))
        amount = float(data.get('amount', 0))
        
        if acc_no <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid account number'
            }), 400
        
        if amount <= 0:
            return jsonify({
                'success': False,
                'error': 'Amount must be positive'
            }), 400
        
        conn = get_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Check if account exists and get balance
        cursor.execute("SELECT name, balance FROM accounts WHERE acc_no=%s", (acc_no,))
        account = cursor.fetchone()
        
        if not account:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        current_balance = account[1]
        
        # Check sufficient balance
        if current_balance < amount:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Insufficient balance',
                'current_balance': current_balance,
                'requested_amount': amount
            }), 400
        
        # Update balance
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no = %s",
                      (amount, acc_no))
        
        # Add transaction record
        cursor.execute("INSERT INTO transactions (acc_no, type, amount) VALUES (%s, %s, %s)",
                      (acc_no, "Withdrawal", amount))
        
        conn.commit()
        
        # Get updated balance
        cursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc_no,))
        new_balance = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(f"Withdrew ${amount} from account #{acc_no}. New balance: ${new_balance}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully withdrew ${amount:.2f}',
            'account_number': acc_no,
            'amount': amount,
            'new_balance': new_balance
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid input data'
        }), 400
    except Exception as e:
        logger.error(f"Withdraw error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/balance/<int:acc_no>', methods=['GET'])
def get_balance(acc_no):
    """Get account balance"""
    try:
        if acc_no <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid account number'
            }), 400
        
        conn = get_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT name, balance, created_at FROM accounts WHERE acc_no=%s", (acc_no,))
        account = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not account:
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        return jsonify({
            'success': True,
            'account_number': acc_no,
            'name': account[0],
            'balance': float(account[1]),
            'created_at': str(account[2])
        })
        
    except Exception as e:
        logger.error(f"Balance check error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/transactions/<int:acc_no>', methods=['GET'])
def get_transactions(acc_no):
    """Get transaction history"""
    try:
        if acc_no <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid account number'
            }), 400
        
        conn = get_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # First check if account exists
        cursor.execute("SELECT name FROM accounts WHERE acc_no=%s", (acc_no,))
        account = cursor.fetchone()
        
        if not account:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        # Get transactions (last 20)
        cursor.execute("""
            SELECT type, amount, date_time 
            FROM transactions 
            WHERE acc_no=%s 
            ORDER BY date_time DESC
            LIMIT 20
        """, (acc_no,))
        
        transactions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format transactions
        formatted_transactions = []
        for trans in transactions:
            formatted_transactions.append({
                'type': trans[0],
                'amount': float(trans[1]),
                'date_time': str(trans[2])
            })
        
        return jsonify({
            'success': True,
            'account_number': acc_no,
            'name': account[0],
            'transactions': formatted_transactions,
            'count': len(formatted_transactions)
        })
        
    except Exception as e:
        logger.error(f"Transactions error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Banking System API")
    print("=" * 50)
    print("Server running on: http://localhost:5000")
    print("API Documentation: http://localhost:5000/")
    print("Health Check: http://localhost:5000/api/health")
    print("=" * 50)
    
    app.run(debug=True, port=5000, host='0.0.0.0')