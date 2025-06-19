import sqlite3
import os

# Define the default db name
DB_FILENAME = 'test.db'

# Store the colors for the colored console output
GREEN = '\033[92m'
RED = '\033[31m'
RESET = '\033[0m'

# Define a custom error
class QueryError(Exception):
    """Exception raised for the query() caller."""
    def __init__(self):
        self.message = f"{RED}Unable to perform a query.{RESET}"
        super().__init__(self.message)

def create_database(filename: str) -> bool:
    """Creates the SQLite database and the necessary tables if they don't exist.
    
    Args:
        filename (str): the filename of the db it'll create.

    Returns:
        (bool): the success status
    """
    # Check if the database file already exists
    if os.path.exists(filename):
        # Print out the success message
        print(f"{GREEN}Database file '{filename}' already exists.{RESET}")

    # Initialize the connection
    conn = None
    try:
        # Connect to the db. Creates the file if it doesn't exist.
        conn = sqlite3.connect(filename)
        # Create a cursor object to execute SQL commands
        db = conn.cursor()

        print(f"{GREEN}    Database '{filename}' connected/created successfully.{RESET}")

        # Users table
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'worker' CHECK(role IN ('worker', 'admin'))
                );
        """)
        print(f"{GREEN}        Table 'users' checked/created.{RESET}")

        # Tasks table
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL CHECK(task_type IN ('classification', 'ranking', 'code', 'free')),
                content TEXT NOT NULL,
                gold_standart_answer TEXT,
                creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                deadline DATETIME
            );
        """)
        print(f"{GREEN}        Table 'tasks' checked/created.{RESET}")

        # Submissions table
        db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                submitted_answer TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            );
        """)
        print(f"{GREEN}        Table 'submissions' checked/created.{RESET}")

        # Metrics cache table
        db.execute("""
            CREATE TABLE IF NOT EXISTS metrics_cache (
                metric_name TEXT PRIMARY KEY,
                value TEXT,
                last_calculated_timestamp DATETIME
            );
        """)
        print(f"{GREEN}        Table 'metrics_cache' checked/created.{RESET}")

        # Add indexes for faster lookups
        db.execute("CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions (user_id);")
        db.execute("CREATE INDEX IF NOT EXISTS idx_submissions_task ON submissions (task_id);")
        print(f"{GREEN}    Indexes checked/created.{RESET}")

        # Save the database file
        conn.commit()
        print(f"{GREEN}    Database schema created/verified successfully.{RESET}")

        # Return
        return True

    except sqlite3.Error as e:
        print(f"{RED}SQLite error: {e}{RESET}")
        # Rollback changes if something went wrong
        if conn:
            conn.rollback()
        # Return
        return False

    finally:
        # Close the connection
        if conn:
            conn.close()
            print(f"{GREEN}Database connection closed.{RESET}")

def db_connect(filename: str, use_row_factory=True):
    """Connects to the database.

    Args:
        filename (str): The filename of the database to connect to.

    Returns:
        connection: A database connection.
    """
    # Initialize the connection
    connection = None
    try:
        connection = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)

        if use_row_factory:
            connection.row_factory = sqlite3.Row

        print(f"{GREEN}    Database '{filename}' connected successfully.{RESET}")
    except sqlite3.Error as e:
        print(f"{RED}SQLite error: {e}{RESET}")
        return None

    # return
    return connection

def query(connection, query: str, *args):
    """Executes the query on the db.

    Args:
        connection: The db connection, to execute on.
        query (str): The query to execute.
        *args: Other arguments (mostly for ? placeholders).
    """
    try:
        # Ececute a query
        result = connection.execute(query, args)
        # Success output in console
        print(f"{GREEN}{query}{RESET}")
        # Return the result to the caller
        return result.fetchall()
    except sqlite3.Error as e:
        # Output the error
        print(f"{RED}SQLite error: {e}{RESET}")
        raise QueryError

if __name__ == '__main__':
    # Create test db
    create_database(DB_FILENAME)
