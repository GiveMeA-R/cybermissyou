from datetime import datetime
from scanmap import start_scan
from usergen import generate_user_list
from chat import start_chat
from exportDocx import generate_docx_from_log

def generate_report(log_filename, successful_logins, discovered_services):
    docx_filename = log_filename.replace('_results.txt', '_report.docx')
    generate_docx_from_log(log_filename, docx_filename, successful_logins, discovered_services)

ACTIONS = {
    "1": start_scan,
    "2": generate_user_list,
    "3": start_chat,
    "4": generate_report,
    "5": lambda: print("Thank you for using our program. Goodbye!") or exit(),
}

def get_greeting(hour):
    if 6 <= hour < 12:
        return "Good morning!"
    elif 12 <= hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

def main():
    print(get_greeting(datetime.now().hour))
    log_filename = None
    successful_logins = None

    while True:
        print("What would you like to do?")
        print("1. Perform network scan")
        print("2. Generate user list")
        print("3. Chat with AI")
        print("4. Generate docx report") 
        print("5. Exit")
        choice = input("Enter your choice: ")

        action = ACTIONS.get(choice)
        if action:
            if choice == "1":
                log_filename, successful_logins, discovered_services = action()
            elif choice == "4":
                if log_filename is None or successful_logins is None:
                    print("You need to perform a network scan before generating a report.")
                else:
                    generate_report(log_filename, successful_logins, discovered_services)
            else:
                action()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
