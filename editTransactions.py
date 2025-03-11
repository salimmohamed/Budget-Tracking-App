import zmq
import json
import csv
import datetime
from pathlib import Path

# path to transactions
transactionsFile = "transactions.csv"
historyFile = "edit_history.json"

def loadTransactions():
    transactions = []
    if Path(transactionsFile).exists():
        with open(transactionsFile, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            for idx, row in enumerate(rows):
                if len(row) >= 3:  # At minimum: Type, Description, Amount
                    transaction = {
                        "id": f"{idx+1:03d}",
                        "type": row[0],
                        "description": row[1],
                        "amount": row[2],
                        "index": idx 
                    }
                    
                    # add date if available
                    if len(row) >= 4:
                        transaction["date"] = row[3]
                    
                    transactions.append(transaction)
    return transactions

def saveTransactions(transactions):
    if not transactions:
        return False
    
    # read existing file
    existingTransactions = []
    try:
        with open(transactionsFile, 'r') as f:
            reader = csv.reader(f)
            existingTransactions = list(reader)
    except FileNotFoundError:
        pass
    
    # opdate transactions in the list
    for transaction in transactions:
        idx = transaction.get("index", -1)
        if idx >= 0 and idx < len(existingTransactions):
            row = [
                transaction["type"], 
                transaction["description"], 
                transaction["amount"]
            ]
            
            if "date" in transaction:
                row.append(transaction["date"])
            elif len(existingTransactions[idx]) >= 4:
                row.append(existingTransactions[idx][3])
            else:
                # add today's date if no date exists
                row.append(datetime.date.today().strftime("%Y-%m-%d"))
                
            # update the row at the specified index
            existingTransactions[idx] = row
    
    # write back to file
    with open(transactionsFile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(existingTransactions)
    
    return True

def loadHistory():
    history = {}
    if Path(historyFile).exists():
        with open(historyFile, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = {}
    return history

def saveHistory(history):
    with open(historyFile, 'w') as f:
        json.dump(history, f, indent=2)

def editTransaction(transactionId, updatedData):
    transactions = loadTransactions()
    
    # find the transaction to edit
    found = False
    original = None
    for i, trans in enumerate(transactions):
        if trans.get('id') == transactionId:
            original = dict(trans)  # make a copy of original just in case
            found = True
            # update transaction with new data
            for key, value in updatedData.items():
                if key in trans and key != 'id': # why does it keep changing
                    trans[key] = value
            transactions[i] = trans
            break
    
    if not found:
        return {"success": False, "message": "Transaction not found"}
    
    # save changes
    if saveTransactions(transactions):
        # throw the transaction into the history
        history = loadHistory()
        if transactionId not in history:
            history[transactionId] = []
        
        editRecord = {
            "timestamp": datetime.datetime.now().isoformat(),
            "original": original,
            "updated": updatedData
        }
        history[transactionId].append(editRecord)
        saveHistory(history)
        
        return {"success": True, "message": "Transaction updated successfully!"}
    else:
        return {"success": False, "message": "Failed to save transaction updates."}

def getEditHistory(transactionId):
    """Get the edit history for a transaction"""
    history = loadHistory()
    if transactionId in history:
        return {"success": True, "history": history[transactionId]}
    else:
        return {"success": True, "history": [], "message": "No edit history found"}

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")  # Using port 5556 for this microservice
    
    print("Transaction Edit (B)")
    
    while True:
        try:
            message = socket.recv_json()
            command = message.get("command")
            
            if command == "edit":
                transactionId = message.get("id")
                updatedData = message.get("data")
                print(f"Received edit request for transaction {transactionId}")
                result = editTransaction(transactionId, updatedData)
                socket.send_json(result)
                print(f"Sent response: {result['message']}")
            
            elif command == "history":
                transactionId = message.get("id")
                print(f"Received history request for transaction {transactionId}")
                result = getEditHistory(transactionId)
                socket.send_json(result)
                print(f"Sent history response")
            
            elif command == "end":
                print("Received shutdown command")
                socket.send_json({"success": True, "message": "Transaction Edit Microservice shutting down"})
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
    
    print("Transaction Edit (B) shutting down")
    socket.close()
    context.term()

if __name__ == "__main__":
    main()