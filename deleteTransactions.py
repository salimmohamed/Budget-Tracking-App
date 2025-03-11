import zmq
import csv
import os
import time
from pathlib import Path

# path to transactions
transactionsFile = "transactions.csv"

def printDebug(message):
    print(f"[DEBUG {time.strftime('%H:%M:%S')}] {message}")

def deleteTransaction(transactionId, confirm=False):
    printDebug(f"Received delete request for ID: '{transactionId}', confirm={confirm}")
    
    if not Path(transactionsFile).exists():
        printDebug(f"CSV file not found: {transactionsFile}")
        return {"success": False, "message": "No transactions file found"}
    
    # read all transactions from the CSV
    allRows = []
    try:
        with open(transactionsFile, 'r') as f:
            reader = csv.reader(f)
            allRows = list(reader)
            printDebug(f"Loaded {len(allRows)} rows from CSV")
    except Exception as e:
        printDebug(f"Error reading CSV: {e}")
        return {"success": False, "message": f"Error reading transactions: {str(e)}"}
    
    # we convert our 001, 002, etc. IDs to 0, 1, etc. for list index
    try:
        idNum = int(transactionId)
        printDebug(f"Converted '{transactionId}' number {idNum}")
        
        # check if we have a valid index
        indexToDelete = idNum - 1
        if indexToDelete < 0 or indexToDelete >= len(allRows):
            printDebug(f"Index {indexToDelete} is out of range (0-{len(allRows)-1})")
            return {"success": False, "message": f"Transaction ID {transactionId} not found (out of range)"}
        
        # get the transaction to delete
        row = allRows[indexToDelete]
        printDebug(f"Found row at index {indexToDelete}: {row}")
        
        if len(row) < 3:
            printDebug(f"Row is missing information: {row}")
            return {"success": False, "message": "Transaction has invalid format"}
        
        # building object
        transaction = {
            "type": row[0],
            "description": row[1],
            "amount": row[2]
        }
        
        # add date if available
        if len(row) >= 4:
            transaction["date"] = row[3]
        
        # if requesting confirmation, return transaction details
        if not confirm:
            printDebug("Returning transaction for confirmation")
            return {
                "success": True,
                "require_confirmation": True,
                "transaction": transaction
            }
        
        # confirmed deletion - remove the row
        printDebug(f"Deleting row {indexToDelete}: {row}")
        deletedRow = allRows.pop(indexToDelete)
        printDebug(f"Deleted row: {deletedRow}")
        
        # update the CSV file
        try:
            with open(transactionsFile, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(allRows)
                printDebug(f"Wrote {len(allRows)} rows back to CSV")
            return {"success": True, "message": f"Transaction {transactionId} deleted successfully"}
        except Exception as e:
            print(f"Error writing CSV: {e}")
            return {"success": False, "message": f"Error saving after deletion: {str(e)}"}
        
    except ValueError:
        printDebug(f"Invalid ID format: {transactionId}")
        return {"success": False, "message": "Invalid transaction ID. Please enter a number."}

def main():
    print("Transaction Delete (C)")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5557")  # 5557 is for microservice C
    
    
    while True:
        try:
            message = socket.recv_json()
            printDebug(f"Received message: {message}")
            
            command = message.get("command")
            
            if command == "delete":
                transactionId = message.get("id")
                confirm = message.get("confirm", False)
                printDebug(f"We are deleting: id={transactionId}, confirm={confirm}")
                
                result = deleteTransaction(transactionId, confirm)
                printDebug(f"Delete result: {result}")
                socket.send_json(result)
            
            elif command == "end":
                printDebug("Received shutdown command")
                socket.send_json({"success": True, "message": "Transaction Delete Microservice shutting down"})
                break
            
            else:
                printDebug(f"Unknown command: {command}")
                socket.send_json({"success": False, "message": "Unknown command"})
        
        except Exception as e:
            printDebug(f"Error processing request: {e}")
            try:
                socket.send_json({"success": False, "message": f"Error: {str(e)}"})
            except:
                pass
    
    printDebug("Transaction Delete (C) shutting down")
    socket.close()
    context.term()

if __name__ == "__main__":
    main()