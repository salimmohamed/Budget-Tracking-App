import datetime
import csv
import zmq

MAX_DESC_LENGTH = 35
MAX_NUM_DIGITS = 10

def receiveInfo(socket):
    isStart, time, isEnd = 0, 0, 0
    
    message = socket.recv()
    
    command, days = message.decode().split(" ")
    if command == "summary":
        isStart = 1
        time = days
    elif command == "end":
        isEnd = 1
        
    return isStart, time, isEnd

def parseCSV(path):
    array = []
    with open(path, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            array.append(row)
    
    return array

def createSummary(array, timeRange):
    string = ''
    totalExpense = 0
    totalIncome = 0
    
    # Determine date range
    endDate = datetime.date.today()
    
    if timeRange == "all":
        string += "-"*(MAX_DESC_LENGTH+MAX_NUM_DIGITS) + "\n"
        string += "All Transaction Info\n"
        string += "-"*(MAX_DESC_LENGTH+MAX_NUM_DIGITS) + "\n"
        
        for line in array:
            if len(line) < 3:  # Skip rows that don't have enough data
                continue
            
            # Get transaction data    
            transType, desc, amount = line[0], line[1], line[2]
            dateStr = line[3] if len(line) >= 4 else "N/A"
            
            sign = '+'
            if transType == "expense":
                sign = '-'
                totalExpense += float(amount)
            else:
                totalIncome += float(amount)
            
            # Add date to display if available
            displayDesc = desc
            if dateStr != "N/A":
                displayDesc = f"{desc} ({dateStr})"
            
            # Ensure description fits within column width
            if len(displayDesc) > MAX_DESC_LENGTH - 2:
                displayDesc = displayDesc[:MAX_DESC_LENGTH-5] + "..."
                
            string += f"{displayDesc.ljust(MAX_DESC_LENGTH)}| {sign}${amount}\n"
            
        string += "-"*(MAX_DESC_LENGTH+MAX_NUM_DIGITS) + "\n"
        string += "Total Income" + " "*(MAX_DESC_LENGTH - 12) + f"| ${totalIncome:.2f}\n"
        string += "Total Expense" + " "*(MAX_DESC_LENGTH - 13) + f"| ${totalExpense:.2f}\n"
        
        string += "Net Income" + " "*(MAX_DESC_LENGTH - 10)
        if totalExpense > totalIncome:
            string += f"| -${totalExpense - totalIncome:.2f}\n"
        elif totalIncome > totalExpense:
            string += f"| +${totalIncome - totalExpense:.2f}\n"
        else:
            string += f"| $0\n"
        
        string += "-"*(MAX_DESC_LENGTH+MAX_NUM_DIGITS) + "\n"
    
    else:
        try:
            # Convert timeRange to integer for date filtering
            daysBack = int(timeRange)
            startDate = endDate - datetime.timedelta(days=daysBack)
        except ValueError:
            # Handle invalid time range
            daysBack = 30  # Default to 30 days
            startDate = endDate - datetime.timedelta(days=daysBack)
        
        string += "-"*(MAX_DESC_LENGTH+MAX_NUM_DIGITS) + "\n"
        string += f"{startDate} -> {endDate} Transaction Info\n"
        string += "-"*(MAX_DESC_LENGTH+MAX_NUM_DIGITS) + "\n"
        
        # Track if we found any transactions in the date range
        transactionsInRange = False
        
        for line in array:
            if len(line) < 3:  # Skip rows that don't have enough data
                continue
                
            transType, desc, amount = line[0], line[1], line[2]
            
            # Check if this transaction has a date
            if len(line) >= 4:
                try:
                    transDate = datetime.datetime.strptime(line[3], "%Y-%m-%d").date()
                    # Only include transactions within date range
                    if transDate < startDate or transDate > endDate:
                        continue
                    dateStr = line[3]
                    transactionsInRange = True
                except ValueError:
                    # If date is invalid, treat as if no date
                    dateStr = "N/A"
            else:
                # No date in the transaction, we can't filter it
                dateStr = "N/A"
            
            sign = '+'
            if transType == "expense":
                sign = '-'
                totalExpense += float(amount)
            else:
                totalIncome += float(amount)
            
            # Add date to display if available
            displayDesc = desc
            if dateStr != "N/A":
                displayDesc = f"{desc} ({dateStr})"
            
            # Ensure description fits within column width
            if len(displayDesc) > MAX_DESC_LENGTH - 2:
                displayDesc = displayDesc[:MAX_DESC_LENGTH-5] + "..."
                
            string += f"{displayDesc.ljust(MAX_DESC_LENGTH)}| {sign}${amount}\n"
            
        if not transactionsInRange:
            string += "No transactions found in this date range.\n"
            
        string += "-"*(MAX_DESC_LENGTH+MAX_NUM_DIGITS) + "\n"
        string += "Total Income" + " "*(MAX_DESC_LENGTH - 12) + f"| ${totalIncome:.2f}\n"
        string += "Total Expense" + " "*(MAX_DESC_LENGTH - 13) + f"| ${totalExpense:.2f}\n"
        
        string += "Net Income" + " "*(MAX_DESC_LENGTH - 10)
        if totalExpense > totalIncome:
            string += f"| -${totalExpense - totalIncome:.2f}\n"
        elif totalIncome > totalExpense:
            string += f"| +${totalIncome - totalExpense:.2f}\n"
        else:
            string += f"| $0\n"
        
        string += "-"*(MAX_DESC_LENGTH+MAX_NUM_DIGITS) + "\n"

    return string

def sendSummary(socket, string):
    socket.send(str.encode(string))
    return

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    
    print("Transaction Summary (A)")
    
    while True:
        isStart, timeRange, isEnd = receiveInfo(socket)
        if isStart:
            filePath = "./transactions.csv"
            try:
                transactionsArray = parseCSV(filePath)
                summaryString = createSummary(transactionsArray, timeRange)
                sendSummary(socket, summaryString)
                print(f"Sent summary for: {timeRange}")
            except Exception as e:
                errorMsg = f"Error generating summary: {str(e)}"
                sendSummary(socket, errorMsg)
                print(errorMsg)
            
        if isEnd:
            socket.send(b"Transaction Summary Microservice shutting down")
            print("Transaction Summary Microservice shutting down")
            break
    
    socket.close()
    context.term()

if __name__ == "__main__":
    main()