import sqlite3
import os

# Get the parent directory of the current script's directory
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define the path to the database file in the parent directory
db_file = os.path.join(parent_directory, 'test_database.db')

# Connect to the SQLite database file in the parent directory
connection = sqlite3.connect(db_file)
cursor = connection.cursor()

# Create the trade_blotter table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS trade_blotter (
        Trade_ID INTEGER PRIMARY KEY,
        Requested_By TEXT NOT NULL,
        Instrument_Type TEXT,
        Symbol_Ticker TEXT,
        Order_Type TEXT,
        Buy_Sell_Indicator TEXT,
        Quantity INTEGER,
        Price REAL,
        Requested_Urgency TEXT,
        Account_Number TEXT,
        Portfolio_ID TEXT,
        Trader_ID TEXT
    )
''')

# Hard-coded data for trade_blotter table
trade_blotter_data = [
    (1, 'User_1', 'Stock', 'AAPL', 'Market', 'Buy', 100, 150.00, 'Immediate', 'ACC_1234', 'PF_1', 'TR_1'),
    (2, 'User_2', 'Bond', 'US10Y', 'Limit', 'Sell', 200, 98.50, 'EOD', 'ACC_5678', 'PF_2', 'TR_2'),
    (3, 'User_3', 'Option', 'TSLA', 'Stop', 'Buy', 50, 210.25, 'Next Open', 'ACC_9101', 'PF_1', 'TR_3'),
    (4, 'User_1', 'Stock', 'GOOGL', 'Limit', 'Sell', 150, 2725.75, 'Immediate', 'ACC_1121', 'PF_2', 'TR_1'),
    (5, 'User_2', 'Bond', 'US30Y', 'Market', 'Buy', 300, 100.00, 'Next Close', 'ACC_3141', 'PF_3', 'TR_2'),
    (6, 'User_3', 'Stock', 'AMZN', 'Limit', 'Buy', 75, 3300.55, 'Immediate', 'ACC_5161', 'PF_1', 'TR_3'),
    (7, 'User_1', 'Option', 'NFLX', 'Stop', 'Sell', 40, 575.20, 'EOD', 'ACC_7181', 'PF_2', 'TR_1'),
    (8, 'User_2', 'Stock', 'MSFT', 'Market', 'Buy', 500, 305.60, 'Next Open', 'ACC_9202', 'PF_3', 'TR_2'),
    (9, 'User_3', 'Bond', 'US5Y', 'Limit', 'Sell', 250, 102.35, 'Next Close', 'ACC_1234', 'PF_1', 'TR_3'),
    (10, 'User_1', 'Stock', 'FB', 'Stop', 'Buy', 125, 355.80, 'Immediate', 'ACC_5678', 'PF_2', 'TR_1')
]

# Insert hard-coded data into trade_blotter table
cursor.executemany('''
    INSERT INTO trade_blotter (
        Trade_ID, Requested_By, Instrument_Type, Symbol_Ticker, Order_Type, 
        Buy_Sell_Indicator, Quantity, Price, Requested_Urgency, 
        Account_Number, Portfolio_ID, Trader_ID
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', trade_blotter_data)

# Commit changes to save data in the trade_blotter table
connection.commit()

# Create the traders table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS traders (
        Trader_ID TEXT PRIMARY KEY,
        Trader_Name TEXT,
        Trader_Email TEXT
    )
''')

# Hard-coded data for traders table
traders_data = [
    ('TR_1', 'Alice Johnson', 'alice.johnson@example.com'),
    ('TR_2', 'Bob Smith', 'bob.smith@example.com'),
    ('TR_3', 'Charlie Brown', 'charlie.brown@example.com')
]

# Insert hard-coded data into traders table
cursor.executemany('''
    INSERT OR IGNORE INTO traders (Trader_ID, Trader_Name, Trader_Email)
    VALUES (?, ?, ?)
''', traders_data)

# Commit changes to save data in the traders table
connection.commit()

# Query and print the data from both tables to verify
print("Trade Blotter Data:")
cursor.execute('SELECT * FROM trade_blotter')
for row in cursor.fetchall():
    print(row)

print("\nTraders Data:")
cursor.execute('SELECT * FROM traders')
for row in cursor.fetchall():
    print(row)

# Close the connection when done
connection.close()
