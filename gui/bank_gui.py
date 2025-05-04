import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import tkinter.simpledialog
from datetime import datetime
from decimal import Decimal
from domain.models.account import Account, AccountType, AccountStatus
from domain.models.transaction import Transaction, TransactionType, DepositTransaction, WithdrawalTransaction, TransferTransaction
from domain.services.account_service import BankAccountService
from domain.services.logging_service import LoggingService
import csv
import os

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZenBank")
        
        # Initialize the account service with logging
        self.account_service = LoggingService(BankAccountService())
        
        # Store accounts and transactions
        self.accounts = []  # List of Account objects
        self.current_account = None  # Currently selected Account
        
        # Window dimensions
        self.window_width = 600
        self.window_height = 700
        
        # Load and setup background image
        self.setup_background()
        
        # Initialize login screen
        self.setup_login_screen()
    
    def clear_current_frame(self):
        """Destroy all existing frames to prepare for new screen"""
        for attr in ['login_frame', 'account_management_frame', 
                    'operations_frame', 'transaction_frame', 'transfer_frame']:
            if hasattr(self, attr):
                frame = getattr(self, attr)
                if frame.winfo_exists():
                    frame.destroy()
    
    def setup_background(self):
        """Configure the background image for the application"""
        try:
            bg_image = Image.open(r"C:\Users\user\Desktop\Banking\Banking-application\gui\images\background.jpeg")
            bg_image = bg_image.resize((self.window_width, self.window_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            self.canvas = tk.Canvas(
                self.root, 
                width=self.window_width, 
                height=self.window_height
            )
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            
            self.root.geometry(f"{self.window_width}x{self.window_height}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load background image: {e}")
            self.root.destroy()
    
    def setup_login_screen(self):
        """Create the login screen widgets"""
        self.login_frame = tk.Frame(self.root, bg="white", bd=2, relief="groove")
        self.canvas.create_window(
            self.window_width//2, 
            self.window_height//4, 
            anchor="center", 
            window=self.login_frame
        )
        
        tk.Label(
            self.login_frame, 
            text="ZenBank Login", 
            font=("Arial", 14, "bold"), 
            bg="white"
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        
        tk.Label(self.login_frame, text="Username:", bg="white").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.login_frame, text="Password:", bg="white").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.login_button = tk.Button(
            self.login_frame, 
            text="Login", 
            command=self.perform_login,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10
        )
        self.login_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.root.bind('<Return>', lambda event: self.perform_login())
    
    def perform_login(self):
        """Authenticate user and initialize banking session"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "password":
            messagebox.showinfo("Login", "Login successful!")
            self.clear_current_frame()
            self.show_account_management_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")
    
    def show_account_management_screen(self):
        """Show the account type selection screen"""
        self.clear_current_frame()
        
        self.account_management_frame = tk.Frame(
            self.root, 
            bg="white", 
            bd=2, 
            relief="flat"
        )
        self.canvas.create_window(
            0, 0, 
            anchor="nw", 
            window=self.account_management_frame,
            width=self.window_width, 
            height=self.window_height
        )
        
        tk.Label(
            self.account_management_frame,
            text="Account Management",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        ).pack(pady=(20, 15))
        
        account_type_frame = tk.Frame(self.account_management_frame, bg="white")
        account_type_frame.pack(pady=10)
        
        tk.Label(
            account_type_frame,
            text="Select Account Type",
            bg="white",
            font=("Arial", 12, "bold")
        ).pack()
        
        self.account_type = tk.StringVar(value="checking")
        
        tk.Radiobutton(
            account_type_frame,
            text="Checking Account",
            variable=self.account_type,
            value="checking",
            bg="white",
            font=("Arial", 11)
        ).pack(anchor="w", pady=5)
        
        tk.Radiobutton(
            account_type_frame,
            text="Savings Account",
            variable=self.account_type,
            value="savings",
            bg="white",
            font=("Arial", 11)
        ).pack(anchor="w", pady=5)
        
        button_frame = tk.Frame(self.account_management_frame, bg="white")
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Create Account",
            command=self.create_account,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15
        ).pack(pady=5)
        
        self.accounts = list(self.account_service._accounts.values())
        
        if self.accounts:
            tk.Button(
                button_frame,
                text="Existing Accounts",
                command=self.show_account_selection,
                bg="#2196F3",
                fg="white",
                font=("Arial", 12, "bold"),
                width=15
            ).pack(pady=5)
    
    def create_account(self):
        """Creates a new account using domain services"""
        account_type = self.account_type.get()
        
        try:
            account = self.account_service.create_account(
                account_type=account_type,
                initial_balance=0.0,
                owner_id="user1"
            )
            
            self.current_account = account
            self.accounts = list(self.account_service._accounts.values())
            
            messagebox.showinfo(
                "Success",
                f"{account_type.capitalize()} account created!\n"
                f"Account #: {account.account_id}"
            )
            
            if messagebox.askyesno("Initial Deposit", "Make initial deposit now?"):
                self.show_transaction_screen(default_type="deposit")
            else:
                self.show_account_operations_screen()
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_account_selection(self):
        """Show dialog to select from existing accounts"""
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Account")
        selection_window.geometry("400x300")
        
        tk.Label(
            selection_window,
            text="Choose an account:",
            font=("Arial", 12)
        ).pack(pady=10)
        
        account_listbox = tk.Listbox(
            selection_window,
            height=6,
            font=("Arial", 11),
            selectmode=tk.SINGLE
        )
        
        for account in self.accounts:
            account_listbox.insert(
                tk.END,
                f"{account._account_type.value.capitalize()} - {account.account_id} (${account.balance:.2f})"
            )
        
        account_listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        def on_select():
            selected = account_listbox.curselection()
            if selected:
                account_id = list(self.account_service._accounts.keys())[selected[0]]
                self.current_account = self.account_service.get_account(account_id)
                selection_window.destroy()
                self.show_account_operations_screen()
        
        tk.Button(
            selection_window,
            text="Select",
            command=on_select,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11),
            width=10
        ).pack(pady=10)
    
    def show_account_operations_screen(self):
        """Show the main banking operations screen"""
        self.clear_current_frame()
        
        self.operations_frame = tk.Frame(
            self.root,
            bg="white",
            bd=2,
            relief="flat"
        )
        self.canvas.create_window(
            0, 0,
            anchor="nw",
            window=self.operations_frame,
            width=self.window_width,
            height=self.window_height
        )
        
        account_info = (
            f"Account Type: {self.current_account._account_type.value}\n"
            f"Account Number: {self.current_account.account_id}\n"
            f"Balance: ${self.current_account.balance:.2f}\n"
            f"Status: {self.current_account.status.value}"
        )
        
        tk.Label(
            self.operations_frame,
            text=account_info,
            font=("Arial", 12),
            bg="white",
            justify=tk.LEFT
        ).pack(pady=20)
        
        button_frame = tk.Frame(self.operations_frame, bg="white")
        button_frame.pack(pady=10)
        
        operations = [
            ("Deposit", "#4CAF50", lambda: self.show_transaction_screen("deposit")),
            ("Withdraw", "#FF9800", lambda: self.show_transaction_screen("withdrawal")),
            ("Transfer", "#9C27B0", lambda: self.show_transfer_screen()),
            ("View Transactions", "#2196F3", self.view_transaction_history),
            ("Back", "#9E9E9E", self.show_account_management_screen)
        ]
        
        for text, color, command in operations:
            tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 12),
                width=20
            ).pack(pady=5, fill=tk.X)
    
    def show_transfer_screen(self):
        """Show transfer between accounts screen"""
        self.clear_current_frame()
        
        self.transfer_frame = tk.Frame(
            self.root,
            bg="white",
            bd=2,
            relief="flat"
        )
        self.canvas.create_window(
            0, 0,
            anchor="nw",
            window=self.transfer_frame,
            width=self.window_width,
            height=self.window_height
        )
        
        tk.Label(
            self.transfer_frame,
            text=f"Transfer from: {self.current_account.account_id}",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(pady=10)
        
        tk.Label(
            self.transfer_frame,
            text=f"Current Balance: ${self.current_account.balance:.2f}",
            font=("Arial", 12),
            bg="white"
        ).pack(pady=5)
        
        dest_frame = tk.Frame(self.transfer_frame, bg="white")
        dest_frame.pack(pady=10)
        
        tk.Label(
            dest_frame,
            text="Destination Account ID:",
            bg="white",
            font=("Arial", 11)
        ).grid(row=0, column=0, padx=5, sticky="e")
        
        self.dest_account_entry = tk.Entry(
            dest_frame,
            font=("Arial", 11),
            width=20
        )
        self.dest_account_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        amount_frame = tk.Frame(self.transfer_frame, bg="white")
        amount_frame.pack(pady=10)
        
        tk.Label(
            amount_frame,
            text="Amount:",
            bg="white",
            font=("Arial", 11)
        ).grid(row=0, column=0, padx=5, sticky="e")
        
        self.transfer_amount_entry = tk.Entry(
            amount_frame,
            font=("Arial", 11),
            width=15
        )
        self.transfer_amount_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        button_frame = tk.Frame(self.transfer_frame, bg="white")
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Transfer Funds",
            command=self.process_transfer,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 12),
            width=20
        ).pack(pady=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.show_account_operations_screen,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 12),
            width=20
        ).pack(pady=5)
    
    def save_transaction_to_csv(self, transaction):
        """Save transaction details to a CSV file"""
        csv_file = "transactions.csv"
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow([
                    "Transaction ID", "Account ID", "Type", 
                    "Amount", "Date", "Related Account", "Balance After"
                ])
            
            related_account = ""
            if isinstance(transaction, TransferTransaction):
                related_account = transaction.destination_account_id
            
            writer.writerow([
                transaction.transaction_id,
                transaction.account_id,
                transaction.transaction_type.value,
                transaction.amount,
                transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                related_account,
                self.current_account.balance
            ])
    
    def process_transfer(self):
        """Process a transfer between accounts"""
        try:
            amount_str = self.transfer_amount_entry.get()
            dest_account_id = self.dest_account_entry.get()
            
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except:
                raise ValueError("Please enter a valid positive amount")
            
            dest_account = self.account_service.get_account(dest_account_id)
            if not dest_account:
                raise ValueError("Destination account not found")
            
            success = self.account_service.transfer(
                source_account_id=self.current_account.account_id,
                target_account_id=dest_account_id,
                amount=float(amount)
            )
            
            if success:
                self.current_account = self.account_service.get_account(self.current_account.account_id)
                
                transaction = TransferTransaction(
                    amount=float(amount),
                    source_account_id=self.current_account.account_id,
                    destination_account_id=dest_account_id
                )
                self.save_transaction_to_csv(transaction)
                
                messagebox.showinfo(
                    "Success",
                    f"Transfer of ${amount:.2f} completed\n"
                    f"New Balance: ${self.current_account.balance:.2f}"
                )
                self.show_account_operations_screen()
            else:
                messagebox.showerror(
                    "Failed",
                    "Transfer failed. Check account IDs and balance."
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Transfer failed: {str(e)}")
    
    def show_transaction_screen(self, default_type="deposit"):
        """Show transaction entry screen"""
        self.clear_current_frame()
        
        self.transaction_frame = tk.Frame(
            self.root,
            bg="white",
            bd=2,
            relief="flat"
        )
        self.canvas.create_window(
            0, 0,
            anchor="nw",
            window=self.transaction_frame,
            width=self.window_width,
            height=self.window_height
        )
        
        tk.Label(
            self.transaction_frame,
            text=f"Account: {self.current_account.account_id}",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(pady=10)
        
        tk.Label(
            self.transaction_frame,
            text=f"Current Balance: ${self.current_account.balance:.2f}",
            font=("Arial", 12),
            bg="white"
        ).pack(pady=5)
        
        type_frame = tk.Frame(self.transaction_frame, bg="white")
        type_frame.pack(pady=10)
        
        tk.Label(
            type_frame,
            text="Transaction Type:",
            bg="white",
            font=("Arial", 11)
        ).grid(row=0, column=0, padx=5, sticky="w")
        
        self.trans_type = tk.StringVar(value=default_type)
        
        tk.Radiobutton(
            type_frame,
            text="Deposit",
            variable=self.trans_type,
            value="deposit",
            bg="white",
            font=("Arial", 11)
        ).grid(row=0, column=1, padx=5, sticky="w")
        
        tk.Radiobutton(
            type_frame,
            text="Withdrawal",
            variable=self.trans_type,
            value="withdrawal",
            bg="white",
            font=("Arial", 11)
        ).grid(row=0, column=2, padx=5, sticky="w")
        
        amount_frame = tk.Frame(self.transaction_frame, bg="white")
        amount_frame.pack(pady=10)
        
        tk.Label(
            amount_frame,
            text="Amount:",
            bg="white",
            font=("Arial", 11)
        ).grid(row=0, column=0, padx=5, sticky="e")
        
        self.amount_entry = tk.Entry(
            amount_frame,
            font=("Arial", 11),
            width=15
        )
        self.amount_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        button_frame = tk.Frame(self.transaction_frame, bg="white")
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Submit Transaction",
            command=self.process_transaction,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            width=20
        ).pack(pady=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.show_account_operations_screen,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 12),
            width=20
        ).pack(pady=5)
    
    def process_transaction(self):
        """Process the transaction from the form"""
        try:
            amount_str = self.amount_entry.get()
            trans_type = self.trans_type.get()
            
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except:
                raise ValueError("Please enter a valid positive amount")
            
            if trans_type == "deposit":
                transaction = DepositTransaction(
                    amount=float(amount),
                    account_id=self.current_account.account_id
                )
            else:  # withdrawal
                transaction = WithdrawalTransaction(
                    amount=float(amount),
                    account_id=self.current_account.account_id
                )
            
            success = self.account_service.execute_transaction(transaction)
            
            if success:
                self.current_account = self.account_service.get_account(self.current_account.account_id)
                self.save_transaction_to_csv(transaction)
                
                messagebox.showinfo(
                    "Success",
                    f"{trans_type.title()} of ${amount:.2f} completed\n"
                    f"New Balance: ${self.current_account.balance:.2f}"
                )
                self.show_account_operations_screen()
            else:
                messagebox.showerror(
                    "Failed",
                    f"{trans_type.title()} failed. Insufficient funds or minimum balance violation"
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Transaction failed: {str(e)}")
    
    def view_transaction_history(self):
        """Display transaction history from CSV file"""
        try:
            history_window = tk.Toplevel(self.root)
            history_window.title("Transaction History")
            history_window.geometry("800x600")
            
            frame = tk.Frame(history_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tree = ttk.Treeview(frame, columns=("Date", "Type", "Amount", "Related Account", "Balance"), show="headings")
            vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            tree.grid(column=0, row=0, sticky='nsew')
            vsb.grid(column=1, row=0, sticky='ns')
            hsb.grid(column=0, row=1, sticky='ew')
            
            tree.heading("Date", text="Date")
            tree.heading("Type", text="Type")
            tree.heading("Amount", text="Amount")
            tree.heading("Related Account", text="Related Account")
            tree.heading("Balance", text="Balance After")
            
            tree.column("Date", width=150)
            tree.column("Type", width=100)
            tree.column("Amount", width=100)
            tree.column("Related Account", width=150)
            tree.column("Balance", width=100)
            
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            
            try:
                with open("transactions.csv", mode='r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['Account ID'] == self.current_account.account_id:
                            tree.insert("", "end", values=(
                                row['Date'],
                                row['Type'],
                                f"${float(row['Amount']):.2f}",
                                row['Related Account'] if row['Related Account'] else "-",
                                f"${float(row['Balance After']):.2f}"
                            ))
            except FileNotFoundError:
                tk.Label(
                    history_window,
                    text="No transaction history found",
                    font=("Arial", 12)
                ).pack(pady=20)
            
            close_button = tk.Button(
                history_window,
                text="Close",
                command=history_window.destroy,
                bg="#9E9E9E",
                fg="white",
                font=("Arial", 12),
                width=15
            )
            close_button.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display transactions: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()