import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import tkinter.simpledialog
from datetime import datetime
from decimal import Decimal
from domain.models.account import Account, AccountStatus
from domain.models.transaction import Transaction, TransactionType
from domain.models.services import AccountService

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
    def perform_login(self):
        """Authenticate user and initialize banking session"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        # In a real app, this would verify against a user service
        if username == "admin" and password == "password":
            messagebox.showinfo("Login", "Login successful!")
            self.login_frame.destroy()
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
            bd=2, 
            relief="flat"
        )
        title_label.pack(pady=(20, 15))

        # Go back button (Back arrow)
        back_button = tk.Button(self.account_management_frame, text="← Back", command=self.show_login_screen, 
                                bg="#FF6347", fg="white", font=("Arial", 10, "bold"))
        back_button.pack(pady=10, anchor="w")

        # Parent frame for account type options
        account_type_frame = tk.Frame(self.account_management_frame, bg="white")
        account_type_frame.pack(pady=10)
        
        tk.Label(
            account_type_frame,
            text="Select Account Type",
            bg="white",
            font=("Arial", 12, "bold")
        ).pack()
        
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
        """Creates a new account using domain services"""
        account_type = self.account_type.get()
        
        try:
            # Use AccountService to create account
            account, transaction = AccountService.create_account(
                account_type=account_type,
                initial_balance=Decimal('0.00')
            )
            
            self.accounts.append(account)
            self.current_account = account
            
            messagebox.showinfo(
                "Account Created",
                f"{account_type.capitalize()} account created successfully!\n"
                f"Account Number: {account.account_id}"
            )
            
            self.show_account_operations_screen()
            
        except ValueError as e:
            messagebox.showerror("Account Creation Error", str(e))
    
    def show_account_selection(self):
        """Show dialog to select from existing accounts"""
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Account")
        
        tk.Label(
            selection_window,
            text="Choose an account:",
            font=("Arial", 12)
        ).pack(pady=10)
        
        account_listbox = tk.Listbox(
            selection_window,
            height=5,
            font=("Arial", 11),
            selectmode=tk.SINGLE
        )
        
        for account in self.accounts:
            account_listbox.insert(
                tk.END,
                f"{account.account_type.title()} - {account.account_id}"
            )
        
        account_listbox.pack(pady=5, padx=10)
        
        def on_select():
            selected = account_listbox.curselection()
            if selected:
                self.current_account = self.accounts[selected[0]]
                selection_window.destroy()
                self.show_account_operations_screen()
        
        tk.Button(
            selection_window,
            text="Select",
            command=on_select,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=10)
    
    def show_account_operations_screen(self):
        """Show the main banking operations screen"""
        if hasattr(self, 'account_management_frame'):
            self.account_management_frame.destroy()
        
        if hasattr(self, 'operations_frame'):
            self.operations_frame.destroy()
        
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
            f"Account Type: {self.current_account.account_type}\n"
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
            ("Deposit", "#4CAF50", self.deposit_funds),
            ("Withdraw", "#FF9800", self.withdraw_funds),
            ("Transactions", "#2196F3", self.view_transaction_history),
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
                width=15
            ).pack(pady=5, fill=tk.X)
    
    def deposit_funds(self):
        """Handle deposit operation"""
        amount = self.prompt_for_amount("Deposit Amount")
        if amount is not None:
            try:
                amount = Decimal(str(amount))
                tx = Transaction(
                    transaction_id=f"TX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    transaction_type=TransactionType.DEPOSIT,
                    amount=float(amount),
                    account_id=self.current_account.account_id,
                    description="Manual Deposit"
                )
                
                success = AccountService.execute_transaction(self.current_account, tx)
                
                if success:
                    messagebox.showinfo("Success", f"Deposited ${amount:.2f} successfully")
                    self.show_account_operations_screen()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
    
    def withdraw_funds(self):
        """Handle withdrawal operation"""
        amount = self.prompt_for_amount("Withdraw Amount")
        if amount is not None:
            try:
                amount = Decimal(str(amount))
                tx = Transaction(
                    transaction_id=f"TX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    transaction_type=TransactionType.WITHDRAWAL,
                    amount=float(amount),
                    account_id=self.current_account.account_id,
                    description="Manual Withdrawal"
                )
                
                success = AccountService.execute_transaction(self.current_account, tx)
                
                if success:
                    messagebox.showinfo("Success", f"Withdrew ${amount:.2f} successfully")
                else:
                    messagebox.showerror("Failed", "Withdrawal failed - insufficient funds")
                
                self.show_account_operations_screen()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
    
    def view_transaction_history(self):
        """Display transaction history"""
        if not hasattr(self.current_account, 'transaction_history'):
            messagebox.showinfo("No Transactions", "No transactions recorded yet")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("Transaction History")
        history_window.geometry("500x400")
        
        text_frame = tk.Frame(history_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_text = tk.Text(
            text_frame,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        history_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=history_text.yview)
        
        history_text.insert(tk.END, "Transaction History\n\n")
        history_text.insert(tk.END, f"Account: {self.current_account.account_id}\n")
        history_text.insert(tk.END, f"Type: {self.current_account.account_type}\n\n")
        
        for tx in getattr(self.current_account, 'transaction_history', []):
            history_text.insert(
                tk.END,
                f"{tx.timestamp.strftime('%Y-%m-%d %H:%M')} - "
                f"{tx.transaction_type.value.title()} ${tx.amount:.2f}\n"
                f"Description: {tx.description}\n\n"
            )
        
        history_text.config(state=tk.DISABLED)
    
    def prompt_for_amount(self, title):
        """Show dialog to get transaction amount"""
        while True:
            amount = tk.simpledialog.askfloat(title, "Enter amount:")
            if amount is None:  # User cancelled
                return None
            try:
                if amount <= 0:
                    messagebox.showerror("Invalid Amount", "Amount must be positive")
                    continue
                return amount
            except (ValueError, TypeError):
                messagebox.showerror("Invalid Amount", "Please enter a valid number")
                continue

if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()