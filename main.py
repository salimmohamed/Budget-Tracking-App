import csv  # https://docs.python.org/3/library/csv.html
import zmq
import json
import datetime

spreadsheet = "transactions.csv" 

def addTransaction(transactionType): 
    desc = input(f"Enter {transactionType} description: ").strip()
    amount = input(f"Enter {transactionType} amount: ").strip()

    # validate amount
    if not desc or not amount.replace(".", "").isdigit():
        print("Invalid input. Please try again.")
        return
    
    # Get date
    # need error handling if no date or invalid date
    useCustomDate = input("Use a custom date? (y/n, default is today): ").strip().lower()
    if useCustomDate == 'y':
        while True:
            dateStr = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                # validate the date
                transDate = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()
                transDate = transDate.strftime("%Y-%m-%d")  # format
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
    else:
        transDate = datetime.date.today().strftime("%Y-%m-%d")
    
    # append transaction with date
    with open(spreadsheet, "a", newline="") as file:
        csv.writer(file).writerow([transactionType, desc, amount, transDate])

    # success message
    print(f"{transactionType} added with date {transDate}!\n")

def viewSummary():
    totalIncome = 0
    totalExpenses = 0

    try:
        with open(spreadsheet, "r") as file:
            for row in csv.reader(file):
                if len(row) < 3:  # skip invalid rows
                    continue
                    
                # calculate total income
                if row[0] == "income":
                    totalIncome += float(row[2])
                
                # calculate total expenses
                elif row[0] == "expense":
                    totalExpenses += float(row[2]) 

    # handle file not found error
    except FileNotFoundError:
        print("No transactions found.")
        return
    
    # display summary
    print(f"Total Income: ${totalIncome:.2f}")
    print(f"Total Expenses: ${totalExpenses:.2f}")
    print(f"Net Income: ${totalIncome - totalExpenses:.2f}")

# integrating microservices
def getTransactionSummary(days):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555") # 5555 is A
    
    req = f"summary {days}"
    socket.send(str.encode(req))
    
    summary = socket.recv()
    return summary.decode()

def editTransaction(transactionId, updatedData):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556") # 5556 is B
    
    message = {
        "command": "edit",
        "id": transactionId,
        "data": updatedData
    }
    socket.send_json(message)
    
    response = socket.recv_json()
    return response

def getEditHistory(transactionId):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556") # 5556 is B
    
    message = {
        "command": "history",
        "id": transactionId
    }
    socket.send_json(message)
    
    response = socket.recv_json()
    return response

def deleteTransaction(transactionId, confirm=False):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557") # 5557 is C
    
    message = {
        "command": "delete",
        "id": transactionId,
        "confirm": confirm
    }
    socket.send_json(message)
    
    response = socket.recv_json()
    return response

def searchByKeyword(keyword):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5558") # 5558 is D
    
    message = {
        "command": "search_keyword",
        "keyword": keyword
    }
    socket.send_json(message)
    
    response = socket.recv_json()
    return response

def filterByAmount(amount):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5558") # 5558 is D
    
    message = {
        "command": "filter_amount",
        "amount": amount
    }
    socket.send_json(message)
    
    response = socket.recv_json()
    return response

def listTransactions():
    try:
        with open(spreadsheet, "r") as file:
            reader = csv.reader(file)
            transactions = list(reader)
            
            if not transactions:
                print("No transactions found.")
                return
            
            print("\n===== Transaction List =====")
            for idx, row in enumerate(transactions):
                if len(row) >= 3:  # validate
                    transId = f"{idx+1:03d}"  # format as 001, 002, etc.
                    
                    # date check
                    dateStr = row[3] if len(row) >= 4 else "N/A"
                    
                    print(f"ID: {transId} | {row[0].capitalize()}: {row[1]} | ${float(row[2]):.2f} | Date: {dateStr}")
    
    except FileNotFoundError:
        print("No transactions found.")

def migrateTransactions():
    try:
        with open(spreadsheet, "r") as file:
            reader = csv.reader(file)
            transactions = list(reader)
        
        modified = False
        for i, row in enumerate(transactions):
            if len(row) == 3:  # if no date
                # Add today's date
                transactions[i].append(datetime.date.today().strftime("%Y-%m-%d"))
                modified = True
        
        if modified:
            with open(spreadsheet, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(transactions)
            print("Added dates to existing transactions")
    except FileNotFoundError:
        # worst case scenario
        pass

def extendedMenu():
    print("\n===== Transaction Management System =====")
    print("1. Add Income")
    print("2. Add Expense")
    print("3. View Simple Summary")
    print("4. View Detailed Summary (A)")
    print("5. List All Transactions")
    print("6. Edit Transaction (B)")
    print("7. View Edit History (B)")
    print("8. Delete Transaction (C)")
    print("9. Search Transactions (D)")
    print("10. Filter By Amount (D)")
    print("11. Exit")
    return input("Choose: ").strip()

def main():
    print("Starting Transaction Management System...")
    
    # date check
    migrateTransactions()
    
    try:
        while True:
            choice = extendedMenu()
            
            # add income
            if choice == "1":
                addTransaction("income")
            
            # add expense
            elif choice == "2":
                addTransaction("expense")
            
            # view simple summary
            elif choice == "3":
                viewSummary()
            
            # get transaction summary
            elif choice == "4":
                try:
                    days = input("Enter number of days (or 'all' for all transactions): ")
                    summary = getTransactionSummary(days)
                    print("\nTransaction Summary from Microservice A:")
                    print(summary)
                except Exception as e:
                    print(f"Error connecting to Microservice A: {e}")
                    print("Make sure Microservice A is running")
            
            # list all transactions
            elif choice == "5":
                listTransactions()
            
            # edit transaction
            elif choice == "6":
                try:
                    listTransactions()
                    transactionId = input("\nEnter transaction ID: ").strip()
                    field = input("What to edit (type/description/amount/date): ").strip().lower()
                    
                    if field not in ["type", "description", "amount", "date"]:
                        print("Invalid field. Please choose type, description, amount, or date.")
                        continue
                        
                    value = input(f"Enter new {field}: ").strip()
                    
                    if field == "type" and value not in ["income", "expense"]:
                        print("Type must be 'income' or 'expense'")
                        continue
                    
                    if field == "amount" and not value.replace(".", "").isdigit():
                        print("Amount must be a number")
                        continue
                    
                    if field == "date":
                        try:
                            # make sure we have a valid date
                            datetime.datetime.strptime(value, "%Y-%m-%d")
                        except ValueError:
                            print("Invalid date format. Please use YYYY-MM-DD.")
                            continue
                    
                    # get all transactions to find matching ID
                    with open(spreadsheet, "r") as file:
                        transactions = list(csv.reader(file))
                    
                    # find matching ID
                    try:
                        idNum = int(transactionId)
                        if idNum < 1 or idNum > len(transactions):
                            print("Transaction not found")
                            continue
                            
                        # get the row at that index
                        # -1 because IDs start at 1!!!
                        row = transactions[idNum-1]
                        if len(row) < 3:  # make sure valid
                            print("Transaction not found")
                            continue
                            
                        # use index as ID
                        fullId = f"{idNum:03d}"
                    except ValueError:
                        print("Invalid ID format. Please enter a number.")
                        continue
                    
                    result = editTransaction(fullId, {field: value})
                    if result["success"]:
                        print("Transaction updated successfully")
                    else:
                        print(f"Error: {result.get('message', 'Unknown error')}")
                
                except Exception as e:
                    print(f"Error connecting to Microservice B: {e}")
                    print("Make sure Microservice B is running")
            
            # View edit history
            elif choice == "7":
                try:
                    listTransactions()
                    transactionId = input("\nEnter transaction ID: ").strip()
                    
                    # get all transactions to find matching ID
                    with open(spreadsheet, "r") as file:
                        transactions = list(csv.reader(file))
                    
                    # Find transaction with matching ID (now using simple sequential IDs)
                    try:
                        idNum = int(transactionId)
                        if idNum < 1 or idNum > len(transactions):
                            print("Transaction not found")
                            continue
                            
                        # Get the row at that index (-1 because IDs start at 1)
                        row = transactions[idNum-1]
                        if len(row) < 3:  # Make sure it's valid
                            print("Transaction not found")
                            continue
                            
                        # Use index as ID
                        fullId = f"{idNum:03d}"
                    except ValueError:
                        print("Invalid ID format. Please enter a number.")
                        continue
                    
                    history = getEditHistory(fullId)
                    
                    if history["success"] and history["history"]:
                        print("\nEdit History:")
                        for i, edit in enumerate(history["history"], 1):
                            print(f"Edit {i} - {edit['timestamp']}")
                            print(f"  Original: {edit['original']}")
                            print(f"  Changes: {edit['updated']}")
                            print()
                    else:
                        print("\nNo edit history found for this transaction.")
                
                except Exception as e:
                    print(f"Error connecting to Microservice B: {e}")
                    print("Make sure Microservice B is running")
            
            # Delete transaction
            elif choice == "8":
                try:
                    listTransactions()
                    transactionId = input("\nEnter transaction ID: ").strip()
                    
                    try:
                        idNum = int(transactionId)
                        # format as 3-digit ID
                        formattedId = f"{idNum:03d}"
                        
                        # first get confirmation info
                        result = deleteTransaction(formattedId)
                        
                        if not result["success"]:
                            print(f"Error: {result.get('message', 'Unknown error')}")
                            continue
                        
                        if result.get("require_confirmation"):
                            print("\nTransaction to delete:")
                            transaction = result["transaction"]
                            print(f"Type: {transaction['type']}")
                            print(f"Description: {transaction['description']}")
                            print(f"Amount: ${float(transaction['amount']):.2f}")
                            if 'date' in transaction:
                                print(f"Date: {transaction['date']}")
                            
                            confirm = input("Are you sure you want to delete this transaction? (y/n): ")
                            
                            if confirm.lower() == 'y':
                                result = deleteTransaction(formattedId, confirm=True)
                                if result["success"]:
                                    print("Transaction deleted successfully")
                                else:
                                    print(f"Error: {result.get('message', 'Unknown error')}")
                            else:
                                print("Deletion cancelled")
                    except ValueError:
                        print("Invalid ID format. Please enter a number.")
                
                except Exception as e:
                    print(f"Error connecting to Microservice C: {e}")
                    print("Make sure Microservice C is running")
            
            # Search transactions
            elif choice == "9":
                try:
                    keyword = input("Enter keyword to search for: ")
                    results = searchByKeyword(keyword)
                    
                    if results["success"]:
                        print(f"\nFound {results['count']} transactions:")
                        for i, trans in enumerate(results["results"], 1):
                            dateInfo = f" | Date: {trans.get('date', 'N/A')}"
                            print(f"{i}. {trans['description']} - ${float(trans['amount']):.2f} ({trans['type']}){dateInfo}")
                    else:
                        print(f"Error: {results.get('message', 'Unknown error')}")
                
                except Exception as e:
                    print(f"Error connecting to Microservice D: {e}")
                    print("Make sure Microservice D is running")
            
            # Filter by amount
            elif choice == "10":
                try:
                    amount = input("Enter amount to filter by: ")
                    results = filterByAmount(amount)
                    
                    if results["success"]:
                        print(f"\nFound {results['count']} transactions:")
                        for i, trans in enumerate(results["results"], 1):
                            dateInfo = f" | Date: {trans.get('date', 'N/A')}"
                            print(f"{i}. {trans['description']} - ${float(trans['amount']):.2f} ({trans['type']}){dateInfo}")
                    else:
                        print(f"Error: {results.get('message', 'Unknown error')}")
                
                except Exception as e:
                    print(f"Error connecting to Microservice D: {e}")
                    print("Make sure Microservice D is running")
            
            # Exit
            elif choice == "11":
                print("Exiting program...")
                break
            
            else:
                print("Invalid choice. Please try again.")
                
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\nShutting down due to keyboard interrupt...")
    finally:
        print("System shutdown complete.")

if __name__ == "__main__":
    try:
        # Check if pyzmq is installed
        import zmq
        main()
    except ImportError:
        print("ZMQ is required for this application.")
        print("Please install it using: pip install pyzmq")