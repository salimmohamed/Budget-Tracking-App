import zmq
import csv
from pathlib import Path

# Path to transaction data
transactionsFile = "transactions.csv"

def loadTransactions():
    """Load transactions from CSV file"""
    transactions = []
    if Path(transactionsFile).exists():
        with open(transactionsFile, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            for idx, row in enumerate(rows):
                if len(row) >= 3:  # Format: Type, Description, Amount, [Date]
                    transaction = {
                        "id": f"{idx+1:03d}",  # we are using a simple sequential ID (001, 002, etc.)
                        "type": row[0],
                        "description": row[1],
                        "amount": row[2]
                    }
                    
                    # add date if available
                    if len(row) >= 4:
                        transaction["date"] = row[3]
                        
                    transactions.append(transaction)
    return transactions

def searchByKeyword(keyword):
    """Search transactions by keyword in description"""
    transactions = loadTransactions()
    if not keyword:
        return {"success": False, "message": "No keyword provided"}
    
    keyword = keyword.lower()
    results = [t for t in transactions if keyword in t.get('description', '').lower()]
    
    return {
        "success": True,
        "count": len(results),
        "results": results
    }

def filterByAmount(amount):
    """Filter transactions by exact amount"""
    transactions = loadTransactions()
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return {"success": False, "message": "Invalid amount provided"}
    
    results = []
    for t in transactions:
        try:
            if float(t.get('amount', 0)) == amount:
                results.append(t)
        except (ValueError, TypeError):
            # skip if weird amount
            continue
    
    return {
        "success": True,
        "count": len(results),
        "results": results
    }

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5558")  # Using port 5558 for this microservice
    
    print("Transaction Search (D)")
    
    while True:
        try:
            message = socket.recv_json()
            command = message.get("command")
            
            if command == "search_keyword":
                keyword = message.get("keyword")
                print(f"Received search request for keyword: {keyword}")
                result = searchByKeyword(keyword)
                socket.send_json(result)
                print(f"Sent search results: {result['count']} transactions found!")
            
            elif command == "filter_amount":
                amount = message.get("amount")
                print(f"Received filter request for amount: {amount}")
                result = filterByAmount(amount)
                socket.send_json(result)
                print(f"Sent filter results: {result['count']} transactions found!")
            
            elif command == "end":
                print("Received shutdown command")
                socket.send_json({"success": True, "message": "Transaction Search Microservice shutting down"})
                break
            
            else:
                print(f"Received unknown command: {command}")
                socket.send_json({"success": False, "message": "Unknown command"})
        
        except Exception as e:
            print(f"Error processing request: {e}")
            try:
                socket.send_json({"success": False, "message": f"Error: {str(e)}"})
            except:
                pass
    
    print("Transaction Search (D) shutting down")
    socket.close()
    context.term()

if __name__ == "__main__":
    main()