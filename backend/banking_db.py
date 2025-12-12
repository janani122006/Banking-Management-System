import mysql.connector
from mysql.connector import Error

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
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database with required tables"""
    try:
        # First connect without specifying database to create it
        config = DB_CONFIG.copy()
        config.pop('database', None)  # Remove database from config
        
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
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_acc_no ON transactions(acc_no)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date_time)")
        
        conn.commit()
        print("Database initialized successfully!")
        
        cursor.close()
        conn.close()
        
        return True
    except Error as e:
        print(f"Error initializing database: {e}")
        return False

def create_account(name, balance):
    """Create a new bank account"""
    try:
        conn = get_connection()
        if not conn:
            return None
        
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
        
        return account_no
        
    except Error as e:
        print(f"Error creating account: {e}")
        return None

def deposit(acc_no, amount):
    """Deposit money into an account"""
    try:
        conn = get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check if account exists
        cursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc_no,))
        result = cursor.fetchone()
        
        if not result:
            print("Account not found!")
            cursor.close()
            conn.close()
            return False
        
        # Update balance
        cursor.execute("""
            UPDATE accounts 
            SET balance = balance + %s 
            WHERE acc_no = %s
        """, (amount, acc_no))
        
        # Add transaction record
        cursor.execute("""
            INSERT INTO transactions (acc_no, type, amount) 
            VALUES (%s, %s, %s)
        """, (acc_no, "Deposit", amount))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True
        
    except Error as e:
        print(f"Error depositing money: {e}")
        return False

def withdraw(acc_no, amount):
    """Withdraw money from an account"""
    try:
        conn = get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check if account exists and get current balance
        cursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc_no,))
        result = cursor.fetchone()
        
        if not result:
            print("Account not found!")
            cursor.close()
            conn.close()
            return False
        
        current_balance = result[0]
        
        # Check if sufficient balance
        if current_balance < amount:
            print("Insufficient balance!")
            cursor.close()
            conn.close()
            return False
        
        # Update balance
        cursor.execute("""
            UPDATE accounts 
            SET balance = balance - %s 
            WHERE acc_no = %s
        """, (amount, acc_no))
        
        # Add transaction record
        cursor.execute("""
            INSERT INTO transactions (acc_no, type, amount) 
            VALUES (%s, %s, %s)
        """, (acc_no, "Withdrawal", amount))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True
        
    except Error as e:
        print(f"Error withdrawing money: {e}")
        return False

def view_balance(acc_no):
    """Get account balance and details"""
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT acc_no, name, balance, created_at 
            FROM accounts 
            WHERE acc_no=%s
        """, (acc_no,))
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return {
                'acc_no': result[0],
                'name': result[1],
                'balance': float(result[2]),
                'created_at': result[3]
            }
        else:
            return None
        
    except Error as e:
        print(f"Error viewing balance: {e}")
        return None

def transaction_history(acc_no, limit=20):
    """Get transaction history for an account"""
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        # First check if account exists
        cursor.execute("SELECT name FROM accounts WHERE acc_no=%s", (acc_no,))
        account = cursor.fetchone()
        
        if not account:
            cursor.close()
            conn.close()
            return None
        
        # Get transactions
        cursor.execute("""
            SELECT trans_id, type, amount, date_time 
            FROM transactions 
            WHERE acc_no=%s 
            ORDER BY date_time DESC 
            LIMIT %s
        """, (acc_no, limit))
        
        transactions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format transactions
        formatted_transactions = []
        for trans in transactions:
            formatted_transactions.append({
                'trans_id': trans[0],
                'type': trans[1],
                'amount': float(trans[2]),
                'date_time': trans[3]
            })
        
        return {
            'acc_no': acc_no,
            'name': account[0],
            'transactions': formatted_transactions,
            'count': len(formatted_transactions)
        }
        
    except Error as e:
        print(f"Error getting transaction history: {e}")
        return None

def get_all_accounts():
    """Get all accounts (for admin purposes)"""
    try:
        conn = get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT acc_no, name, balance, created_at 
            FROM accounts 
            ORDER BY created_at DESC
        """)
        
        accounts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return accounts
        
    except Error as e:
        print(f"Error getting all accounts: {e}")
        return []

def transfer(from_acc, to_acc, amount):
    """Transfer money between accounts"""
    try:
        conn = get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check if both accounts exist
        cursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (from_acc,))
        from_account = cursor.fetchone()
        
        cursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (to_acc,))
        to_account = cursor.fetchone()
        
        if not from_account or not to_account:
            print("One or both accounts not found!")
            cursor.close()
            conn.close()
            return False
        
        # Check if sufficient balance in source account
        if from_account[0] < amount:
            print("Insufficient balance for transfer!")
            cursor.close()
            conn.close()
            return False
        
        # Start transaction
        cursor.execute("START TRANSACTION")
        
        try:
            # Deduct from source account
            cursor.execute("""
                UPDATE accounts 
                SET balance = balance - %s 
                WHERE acc_no = %s
            """, (amount, from_acc))
            
            # Add to destination account
            cursor.execute("""
                UPDATE accounts 
                SET balance = balance + %s 
                WHERE acc_no = %s
            """, (amount, to_acc))
            
            # Record both transactions
            cursor.execute("""
                INSERT INTO transactions (acc_no, type, amount) 
                VALUES (%s, %s, %s)
            """, (from_acc, "Transfer Out", amount))
            
            cursor.execute("""
                INSERT INTO transactions (acc_no, type, amount) 
                VALUES (%s, %s, %s)
            """, (to_acc, "Transfer In", amount))
            
            conn.commit()
            print("Transfer successful!")
            
        except Error as e:
            conn.rollback()
            print(f"Transfer failed: {e}")
            cursor.close()
            conn.close()
            return False
        
        cursor.close()
        conn.close()
        
        return True
        
    except Error as e:
        print(f"Error transferring money: {e}")
        return False

def search_accounts_by_name(name):
    """Search accounts by name"""
    try:
        conn = get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        
        search_pattern = f"%{name}%"
        cursor.execute("""
            SELECT acc_no, name, balance, created_at 
            FROM accounts 
            WHERE name LIKE %s 
            ORDER BY name
        """, (search_pattern,))
        
        accounts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return accounts
        
    except Error as e:
        print(f"Error searching accounts: {e}")
        return []

def get_account_summary():
    """Get banking system summary statistics"""
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        # Get total accounts
        cursor.execute("SELECT COUNT(*) FROM accounts")
        total_accounts = cursor.fetchone()[0]
        
        # Get total balance
        cursor.execute("SELECT SUM(balance) FROM accounts")
        total_balance = cursor.fetchone()[0] or 0
        
        # Get total transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0]
        
        # Get recent accounts (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM accounts 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        recent_accounts = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'total_accounts': total_accounts,
            'total_balance': float(total_balance),
            'total_transactions': total_transactions,
            'recent_accounts': recent_accounts
        }
        
    except Error as e:
        print(f"Error getting account summary: {e}")
        return None

# CLI Interface (Original main function)
def main():
    """Command-line interface for the banking system"""
    # Initialize database
    print("Initializing database...")
    init_database()
    
    while True:
        print("\n" + "="*40)
        print("       BANKING SYSTEM")
        print("="*40)
        print("1. Create Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. View Balance")
        print("5. Transaction History")
        print("6. Transfer Money")
        print("7. View All Accounts")
        print("8. Search Accounts")
        print("9. System Summary")
        print("10. Exit")
        print("="*40)

        try:
            choice = input("\nEnter your choice (1-10): ").strip()
            
            if choice == '1':
                name = input("Enter Name: ").strip()
                if not name:
                    print("Name cannot be empty!")
                    continue
                    
                try:
                    bal = float(input("Enter Initial Balance: "))
                    if bal < 0:
                        print("Balance cannot be negative!")
                        continue
                        
                    account_no = create_account(name, bal)
                    if account_no:
                        print(f"\n✓ Account Created Successfully!")
                        print(f"  Account Number: {account_no}")
                        print(f"  Account Holder: {name}")
                        print(f"  Initial Balance: ${bal:.2f}")
                    else:
                        print("\n✗ Failed to create account!")
                        
                except ValueError:
                    print("Invalid balance amount!")
                    
            elif choice == '2':
                try:
                    acc = int(input("Enter Account Number: "))
                    amt = float(input("Enter Deposit Amount: "))
                    
                    if amt <= 0:
                        print("Amount must be positive!")
                        continue
                        
                    if deposit(acc, amt):
                        print(f"\n✓ ${amt:.2f} Deposited Successfully!")
                    else:
                        print("\n✗ Deposit failed!")
                        
                except ValueError:
                    print("Invalid input!")
                    
            elif choice == '3':
                try:
                    acc = int(input("Enter Account Number: "))
                    amt = float(input("Enter Withdraw Amount: "))
                    
                    if amt <= 0:
                        print("Amount must be positive!")
                        continue
                        
                    if withdraw(acc, amt):
                        print(f"\n✓ ${amt:.2f} Withdrawn Successfully!")
                    else:
                        print("\n✗ Withdrawal failed!")
                        
                except ValueError:
                    print("Invalid input!")
                    
            elif choice == '4':
                try:
                    acc = int(input("Enter Account Number: "))
                    account_info = view_balance(acc)
                    
                    if account_info:
                        print("\n" + "="*40)
                        print("      ACCOUNT INFORMATION")
                        print("="*40)
                        print(f"Account Number: {account_info['acc_no']}")
                        print(f"Account Holder: {account_info['name']}")
                        print(f"Current Balance: ${account_info['balance']:.2f}")
                        print(f"Account Created: {account_info['created_at']}")
                        print("="*40)
                    else:
                        print("\n✗ Account not found!")
                        
                except ValueError:
                    print("Invalid account number!")
                    
            elif choice == '5':
                try:
                    acc = int(input("Enter Account Number: "))
                    history = transaction_history(acc)
                    
                    if history:
                        print(f"\nTransaction History for Account #{acc}")
                        print(f"Account Holder: {history['name']}")
                        print("="*60)
                        print(f"{'Type':<15} {'Amount':<15} {'Date/Time':<25}")
                        print("="*60)
                        
                        for trans in history['transactions']:
                            trans_type = trans['type']
                            amount = f"${trans['amount']:.2f}"
                            date_time = str(trans['date_time'])
                            print(f"{trans_type:<15} {amount:<15} {date_time:<25}")
                            
                        print("="*60)
                        print(f"Total Transactions: {history['count']}")
                    else:
                        print("\n✗ Account not found or no transactions!")
                        
                except ValueError:
                    print("Invalid account number!")
                    
            elif choice == '6':
                try:
                    from_acc = int(input("Enter From Account Number: "))
                    to_acc = int(input("Enter To Account Number: "))
                    amount = float(input("Enter Transfer Amount: "))
                    
                    if amount <= 0:
                        print("Amount must be positive!")
                        continue
                        
                    if transfer(from_acc, to_acc, amount):
                        print(f"\n✓ ${amount:.2f} Transferred Successfully!")
                        print(f"  From Account: {from_acc}")
                        print(f"  To Account: {to_acc}")
                    else:
                        print("\n✗ Transfer failed!")
                        
                except ValueError:
                    print("Invalid input!")
                    
            elif choice == '7':
                accounts = get_all_accounts()
                
                if accounts:
                    print("\n" + "="*70)
                    print("                         ALL ACCOUNTS")
                    print("="*70)
                    print(f"{'Acc No':<10} {'Name':<25} {'Balance':<15} {'Created At':<20}")
                    print("="*70)
                    
                    for acc in accounts:
                        acc_no = acc['acc_no']
                        name = acc['name'][:24]  # Truncate if too long
                        balance = f"${acc['balance']:.2f}"
                        created_at = str(acc['created_at'])[:19]
                        print(f"{acc_no:<10} {name:<25} {balance:<15} {created_at:<20}")
                        
                    print("="*70)
                    print(f"Total Accounts: {len(accounts)}")
                else:
                    print("\nNo accounts found!")
                    
            elif choice == '8':
                name = input("Enter name to search: ").strip()
                if not name:
                    print("Please enter a name to search!")
                    continue
                    
                accounts = search_accounts_by_name(name)
                
                if accounts:
                    print(f"\nSearch Results for '{name}':")
                    print("="*60)
                    print(f"{'Acc No':<10} {'Name':<25} {'Balance':<15}")
                    print("="*60)
                    
                    for acc in accounts:
                        acc_no = acc['acc_no']
                        name = acc['name'][:24]
                        balance = f"${acc['balance']:.2f}"
                        print(f"{acc_no:<10} {name:<25} {balance:<15}")
                        
                    print("="*60)
                    print(f"Found {len(accounts)} account(s)")
                else:
                    print(f"\nNo accounts found for '{name}'")
                    
            elif choice == '9':
                summary = get_account_summary()
                
                if summary:
                    print("\n" + "="*40)
                    print("      SYSTEM SUMMARY")
                    print("="*40)
                    print(f"Total Accounts: {summary['total_accounts']}")
                    print(f"Total Balance: ${summary['total_balance']:.2f}")
                    print(f"Total Transactions: {summary['total_transactions']}")
                    print(f"Accounts Created (Last 7 days): {summary['recent_accounts']}")
                    print("="*40)
                else:
                    print("\nUnable to get system summary!")
                    
            elif choice == '10':
                print("\nThank you for using the Banking System!")
                print("Goodbye!")
                break
                
            else:
                print("\nInvalid choice! Please enter a number between 1-10.")
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()