# Budget Tracker Application

A comprehensive personal finance tracking system built with Python that helps users manage their income and expenses through a microservices architecture.

## Features

- **Transaction Management**
  - Add income and expense transactions with descriptions, amounts, and dates
  - View transactions with formatted IDs (001, 002, etc.)
  - Edit existing transactions (type, description, amount, date)
  - Delete transactions with confirmation
  - Track edit history for accountability

- **Financial Analysis**
  - View basic income/expense summaries
  - Generate detailed reports for specific date ranges
  - Calculate net income automatically

- **Search & Filter Capabilities**
  - Search transactions by keyword
  - Filter transactions by exact amount

## System Architecture

The application uses a microservices architecture with ZeroMQ for inter-process communication:

1. **Main Service** (`main.py`)
   - Provides the user interface
   - Coordinates all microservices
   - Handles basic transaction management

2. **Transaction Summary** (`transactionSummary.py` - Service A)
   - Generates financial summaries and reports
   - Supports filtering by date ranges

3. **Transaction Editor** (`editTransactions.py` - Service B)
   - Handles updating transaction data
   - Maintains edit history in JSON format

4. **Transaction Deletion** (`deleteTransactions.py` - Service C)
   - Manages the removal of transactions
   - Provides confirmation before deletion

5. **Transaction Search** (`searchTransactions.py` - Service D)
   - Implements search functionality
   - Supports filtering by amount

## Data Storage

- Transactions are stored in CSV format (`transactions.csv`)
- Edit history is maintained in JSON format (`edit_history.json`)
- Each transaction includes:
  - Type (income/expense)
  - Description
  - Amount
  - Date (optional, defaults to today)

## Setup and Installation

### Prerequisites

- Python 3.6+
- PyZMQ library

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/budget-tracker.git
cd budget-tracker
```

2. Install required packages:
```
pip install pyzmq
```

### Running the Application

1. Start the microservices in separate terminal windows:

```
python transactionSummary.py
python editTransactions.py
python deleteTransactions.py
python searchTransactions.py
```

2. Start the main application:

```
python main.py
```

## Usage Guide

### Adding Transactions

1. Select options 1 (Add Income) or 2 (Add Expense)
2. Enter a description and amount
3. Choose whether to use today's date or a custom date

### Viewing Information

- **Option 3**: View a simple income/expense summary
- **Option 4**: Generate a detailed transaction report for a specific date range
- **Option 5**: List all transactions with their IDs

### Editing Transactions

1. Select option 6 (Edit Transaction)
2. Choose a transaction by ID
3. Select what to edit (type/description/amount/date)
4. Enter the new value

### Viewing Edit History

1. Select option 7 (View Edit History)
2. Enter the transaction ID
3. View the complete edit history with timestamps

### Deleting Transactions

1. Select option 8 (Delete Transaction)
2. Enter the transaction ID
3. Confirm deletion

### Searching Transactions

- **Option 9**: Search by keyword in the description
- **Option 10**: Filter by exact amount

## File Structure

- `main.py` - Main application interface
- `transactionSummary.py` - Service A for financial reports
- `editTransactions.py` - Service B for editing transactions
- `deleteTransactions.py` - Service C for deleting transactions
- `searchTransactions.py` - Service D for search functionality
- `transactions.csv` - Data storage (gitignored)
- `edit_history.json` - Transaction modification history

## Development Notes

- The application uses ZeroMQ (port 5555-5558) for inter-service communication
- Transaction IDs are zero-padded sequential numbers (001, 002, etc.)
- The edit history tracks all changes with timestamps

## Credits
- ChatGPT for helping generate this ReadMe!
