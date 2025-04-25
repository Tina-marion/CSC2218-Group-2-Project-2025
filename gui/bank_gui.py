import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import tkinter.simpledialog
from datetime import datetime
from decimal import Decimal
from domain.models.account import Account, AccountType, AccountStatus
from domain.models.transaction import Transaction, TransactionType, DepositTransaction, WithdrawalTransaction, TransferTransaction
from domain.services.account_service import BankAccountService

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZenBank")
        
        # Initialize the account service
        self.account_service = BankAccountService()
        
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
        
        # Login widgets
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
        
        # Bind Enter key to login
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
        
        # Title
        tk.Label(
            self.account_management_frame,
            text="Account Management",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        ).pack(pady=(20, 15))
        
        # Account Type selection
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
        
        # Action buttons
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
        
        # Get all accounts from the service
        self.accounts = self.account_service._accounts.values()
        
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
            # Create account through the service
            account = self.account_service.create_account(
                account_type=account_type,
                initial_balance=0.0,
                owner_id="user1"  # You might want to get this from login
            )
            
            self.current_account = account
            self.accounts = self.account_service._accounts.values()
            
            messagebox.showinfo(
                "Success",
                f"{account_type.capitalize()} account created!\n"
                f"Account #: {account.account_id}"
            )
            
            # Offer to make initial deposit
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
        
        # Account info header
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
        
        # Operations buttons
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
        
        # Account info
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
        
        # Destination account
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
        
        # Amount entry
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
        
        # Action buttons
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
    
    def process_transfer(self):
        """Process a transfer between accounts"""
        try:
            amount_str = self.transfer_amount_entry.get()
            dest_account_id = self.dest_account_entry.get()
            
            # Validate amount
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except:
                raise ValueError("Please enter a valid positive amount")
            
            # Execute transfer through the service
            success = self.account_service.transfer(
                source_account_id=self.current_account.account_id,
                target_account_id=dest_account_id,
                amount=float(amount)
            )
            
            if success:
                # Refresh current account data
                self.current_account = self.account_service.get_account(self.current_account.account_id)
                
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
        
        # Account info
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
        
        # Transaction type
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
        
        # Amount entry
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
        
        # Action buttons
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
            # Get form values
            amount_str = self.amount_entry.get()
            trans_type = self.trans_type.get()
            
            # Validate amount
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except:
                raise ValueError("Please enter a valid positive amount")
            
            # Create appropriate transaction
            if trans_type == "deposit":
                transaction = DepositTransaction(
                    transaction_id=str(datetime.now().timestamp()),
                    amount=float(amount),
                    account_id=self.current_account.account_id
                )
            else:  # withdrawal
                transaction = WithdrawalTransaction(
                    transaction_id=str(datetime.now().timestamp()),
                    amount=float(amount),
                    account_id=self.current_account.account_id
                )
            
            # Execute transaction through the service
            success = self.account_service.execute_transaction(transaction)
            
            if success:
                # Refresh current account data
                self.current_account = self.account_service.get_account(self.current_account.account_id)
                
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
        """Display transaction history in a detailed view"""
        # Note: Your current domain model doesn't store transaction history
        # This would need to be implemented in your service layer
        messagebox.showinfo("Info", "Transaction history feature would be implemented here")
        return

if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()