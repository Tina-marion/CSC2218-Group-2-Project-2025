import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import tkinter.simpledialog

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZenBank")

         # Load and set the icon for all screens
        try:
            self.icon_image = Image.open("C:/Users/tinaa/OneDrive/Desktop/BANK/Banking-application/gui/images/bank icon.jpg")
            self.icon_image = self.icon_image.resize((50, 50), Image.Resampling.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(self.icon_image)
            self.root.iconphoto(True, self.icon_photo)  # Set the icon for the root window
        except Exception as e:
            messagebox.showerror("Icon Error", f"Error loading icon: {e}")
            self.root.destroy()
            return

        # Attempt to load your background image
        try:
            self.bg_image = Image.open(r"C:\Users\tinaa\OneDrive\Desktop\BANK\Banking-application\gui\images\background.jpeg")
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading image: {e}")
            self.root.destroy()
            return
        
        # Resize the background image to fit the window size
        window_width = 500
        window_height = 660
        self.bg_image = self.bg_image.resize((window_width, window_height), Image.Resampling.LANCZOS)

        # Convert the image to a Tkinter-compatible object
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a Canvas that covers the window
        self.canvas = tk.Canvas(root, width=self.bg_photo.width(), height=self.bg_photo.height())
        self.canvas.pack(fill="both", expand=True)

        # Place the image onto the canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        # Resize the window to match the background image dimensions
        root.geometry(f"{self.bg_photo.width()}x{self.bg_photo.height()}")
        
        self.account_types = []  # To hold created account types
        self.current_account = None

        # Start with the login screen
        self.show_login_screen()

    def show_login_screen(self):
        """Displays the login screen."""
        self.login_frame = tk.Frame(self.root, bg="white", bd=2, relief="groove")
        self.canvas.create_window(150, 50, anchor="nw", window=self.login_frame)

        # Widgets in the login frame
        tk.Label(self.login_frame, text="Welcome to ZenBank", font=("Arial", 14, "bold"), bg="white").grid(
            row=0, column=0, columnspan=2, padx=10, pady=10
        )
        tk.Label(self.login_frame, text="Username:", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.login_frame, text="Password:", bg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        self.login_button = tk.Button(
            self.login_frame, 
            text="Login", 
            command=self.perform_login,
            bg="#4CAF50",  # Green color
            fg="white",
            font=("Arial", 10, "bold"),
            width=10
        )
        self.login_button.grid(row=3, column=0, columnspan=2, pady=10)

    def perform_login(self):
        """Authenticate user (dummy credentials) and move to the next screen if successful."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Dummy check: "admin" / "password"
        if username == "admin" and password == "password":
            messagebox.showinfo("Login", "Login successful!")
            self.show_account_management_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")
    
    def show_account_management_screen(self):
        """Destroys the login UI and displays the account management screen."""
        self.login_frame.destroy()

        # Create a frame for account management
        self.account_management_frame = tk.Frame(self.root, bg="white", bd=2, relief="flat")
        self.canvas.create_window(0, 0, anchor="nw", window=self.account_management_frame, 
                                  width=self.bg_photo.width(), height=self.bg_photo.height())

        # Title
        title_label = tk.Label(
            self.account_management_frame, 
            text="Account Management", 
            font=("Arial", 14, "bold"), 
            bg="white", 
            fg="black"
        )
        title_label.pack(pady=(20, 15))

        # Go back button (Back arrow)
        back_button = tk.Button(self.account_management_frame, text="← Back", command=self.show_login_screen, 
                                bg="#FF6347", fg="white", font=("Arial", 10, "bold"))
        back_button.pack(pady=10, anchor="w")

        # Parent frame for account type options
        account_type_frame = tk.Frame(self.account_management_frame, bg="white")
        account_type_frame.pack(pady=10)

        tk.Label(account_type_frame, text="Select Account Type", bg="white", font=("Arial", 12, "bold")).pack()

        self.account_type = tk.StringVar(value="checking")

        # Container for Checking Account
        checking_container = tk.Frame(account_type_frame, bg="white", bd=1, relief="groove", padx=10, pady=5)
        checking_container.pack(pady=5, fill="x")
        checking_radio = tk.Radiobutton(checking_container, text="Checking Account", variable=self.account_type,
                                        value="checking", bg="white", font=("Arial", 11))
        checking_radio.pack(anchor="w")

        # Container for Savings Account
        savings_container = tk.Frame(account_type_frame, bg="white", bd=1, relief="groove", padx=10, pady=5)
        savings_container.pack(pady=5, fill="x")
        savings_radio = tk.Radiobutton(savings_container, text="Savings Account", variable=self.account_type,
                                       value="savings", bg="white", font=("Arial", 11))
        savings_radio.pack(anchor="w")

        # Proceed Button
        proceed_button = tk.Button(self.account_management_frame, text="Create Account", 
                                   command=self.create_account, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        proceed_button.pack(pady=20)

    def create_account(self):
        """Creates a new account based on the selected account type."""
        account_type = self.account_type.get()
        
        if account_type == "checking":
            new_account = BankAccount("Checking", 0)
        elif account_type == "savings":
            new_account = BankAccount("Savings", 0)
        else:
            messagebox.showerror("Error", "Invalid account type selected.")
            return

        self.account_types.append(new_account)
        self.current_account = new_account

        messagebox.showinfo("Account Created", f"{account_type.capitalize()} account created successfully!")

        # Show deposit option
        self.show_deposit_withdraw_screen()

    def show_deposit_withdraw_screen(self):
        """Displays deposit/withdraw options after creating an account."""
        self.account_management_frame.destroy()

        self.deposit_withdraw_frame = tk.Frame(self.root, bg="white", bd=2, relief="flat")
        self.canvas.create_window(0, 0, anchor="nw", window=self.deposit_withdraw_frame,
                                  width=self.bg_photo.width(), height=self.bg_photo.height())

        # Go back button (Back arrow)
        back_button = tk.Button(self.deposit_withdraw_frame, text="← Back", command=self.show_account_management_screen, 
                                bg="#FF6347", fg="white", font=("Arial", 10, "bold"))
        back_button.pack(pady=10, anchor="w")

        # Account info label
        account_info_label = tk.Label(self.deposit_withdraw_frame, text=f"Account Type: {self.current_account.account_type}\nBalance: {self.current_account.balance}",
                                      font=("Arial", 12), bg="white")
        account_info_label.pack(pady=20)

        # Deposit option
        deposit_button = tk.Button(self.deposit_withdraw_frame, text="Deposit", command=self.deposit_funds,
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        deposit_button.pack(pady=5)

        # Withdraw option
        withdraw_button = tk.Button(self.deposit_withdraw_frame, text="Withdraw", command=self.withdraw_funds,
                                    bg="#FF6347", fg="white", font=("Arial", 12, "bold"))
        withdraw_button.pack(pady=5)

        # View Transaction History
        transaction_button = tk.Button(self.deposit_withdraw_frame, text="View Transactions", 
                                       command=self.view_transaction_history, bg="#1E90FF", fg="white", font=("Arial", 12, "bold"))
        transaction_button.pack(pady=20)

    def deposit_funds(self):
        """Prompts the user to deposit funds."""
        amount = self.prompt_for_amount("Deposit Amount")
        if amount:
            self.current_account.deposit(amount)
            messagebox.showinfo("Deposit Successful", f"Deposited {amount} successfully.")
            self.show_deposit_withdraw_screen()

    def withdraw_funds(self):
        """Prompts the user to withdraw funds."""
        amount = self.prompt_for_amount("Withdraw Amount")
        if amount:
            if self.current_account.withdraw(amount):
                messagebox.showinfo("Withdrawal Successful", f"Withdrew {amount} successfully.")
            else:
                messagebox.showerror("Insufficient Funds", "Not enough balance to withdraw this amount.")
            self.show_deposit_withdraw_screen()

    def prompt_for_amount(self, action):
        """Prompts the user for an amount for deposit/withdrawal."""
        amount = tk.simpledialog.askfloat("Amount", f"Enter the amount to {action}:")
        if amount is not None and amount > 0:
            return amount
        else:
            messagebox.showerror("Invalid Amount", "Please enter a valid amount.")
            return None

    def view_transaction_history(self):
       """Displays the transaction history in a scrollable list."""
       if not self.current_account.transactions:
        messagebox.showinfo("No Transactions", "No transactions made yet.")
       else:
           history_window = tk.Toplevel(self.root)
           history_window.title("Transaction History")

        # Create a scrollable listbox
           history_listbox = tk.Listbox(history_window, width=50, height=10)
           history_listbox.pack(padx=10, pady=10)

        # Populate the listbox with transactions
           for transaction in self.current_account.transactions:
            history_listbox.insert(tk.END, transaction)

        # Add a scrollbar to the listbox
           scrollbar = tk.Scrollbar(history_window, orient="vertical", command=history_listbox.yview)
           scrollbar.pack(side="right", fill="y")
           history_listbox.config(yscrollcommand=scrollbar.set)


class BankAccount:
    """Represents a simple bank account."""
    def __init__(self, account_type, initial_balance=0):
        self.account_type = account_type
        self.balance = initial_balance
        self.transactions = []

    def deposit(self, amount):
        self.balance += amount
        self.transactions.append(f"Deposited {amount}, Balance: {self.balance}")

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            self.transactions.append(f"Withdrew {amount}, Balance: {self.balance}")
            return True
        return False


# ---------------------------
# Run the Application
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()
