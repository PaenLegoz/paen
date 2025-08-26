# core/database.py
import sqlite3

def init_db():
    """
    Initialize the database and create tables if they don't exist.
    Also populate default categories if none exist.
    """
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Create transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,          -- 'income' or 'expense'
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    ''')

    # Create budgets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            limit_amount REAL NOT NULL DEFAULT 0
        )
    ''')

    # Insert default categories if table is empty
    c.execute("SELECT COUNT(*) FROM budgets")
    if c.fetchone()[0] == 0:
        default_categories = [
            'Rent',
            'Groceries', 
            'Utilities',
            'Entertainment',
            'Transport',
            'Dining',
            'Shopping',
            'Healthcare',
            'Insurance',
            'Salary',
            'Other'
        ]
        
        for category in default_categories:
            c.execute(
                "INSERT INTO budgets (category, limit_amount) VALUES (?, ?)",
                (category, 0.0)
            )

    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully")

def get_db_connection():
    """
    Get a database connection.
    Returns: sqlite3.Connection object
    """
    return sqlite3.connect('finance.db')

# Initialize database when module is imported
if __name__ != "__main__":
    init_db()