import csv  # https://docs.python.org/3/library/csv.html

spreadsheet = "transactions.csv"  # file to store transactions

# add transaction function
def addTransaction(transactionType): 
    desc = input(f"Enter {transactionType} description: ").strip()
    amount = input(f"Enter {transactionType} amount: ").strip()

    # validate amount
    if not desc or not amount.replace(".", "").isdigit():
        print("Invalid input. Please try again.")
        return
    
    # append transaction
    with open(spreadsheet, "a", newline="") as file:
        csv.writer(file).writerow([transactionType, desc, amount])

    # success message
    print(f"{transactionType} added!\n")

# view summary function
def viewSummary():
    totalIncome = 0
    totalExpenses = 0

    try:
        with open(spreadsheet, "r") as file:
            for row in csv.reader(file):
                
                # calculate total income and expenses
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

# main function
def main():
    while True:
        choice = input("1. Add Income  2. Add Expense  3. View Summary  4. Exit\nChoose: ").strip()
        if choice == "1":
            addTransaction("income")

        elif choice == "2":
            addTransaction("expense")

        elif choice == "3":
            viewSummary()

        elif choice == "4":
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please try again.")

main()