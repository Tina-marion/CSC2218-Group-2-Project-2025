import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZenBank")

        # Attempt to load your background image
        try:
            self.bg_image = Image.open(r"C:\Users\tinaa\OneDrive\Desktop\BANK\Banking-application\gui\images\background.jpeg")
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading image: {e}")
            self.root.destroy()
            return
        
        # Resize the background image to fit the window size (e.g., 1024x768 or custom size)
        window_width = 1024  # You can set the width you want
        window_height = 768  # You can set the height you want
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

        # -------------- Login Screen --------------
        self.login_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        # Position the login frame on the canvas
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

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.perform_login)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=10)

    def perform_login(self):
        """Authenticate user (dummy credentials) and move to the next screen if successful."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Dummy check: "admin" / "password"
        if username == "admin" and password == "password":
            messagebox.showinfo("Login", "Login successful!")
            self.show_customer_selection_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    # -------------- New Screen: Customer & Product Selection --------------
    def show_customer_selection_screen(self):
        """Destroys the login UI and displays a screen similar to your provided screenshot."""
        self.login_frame.destroy()

        # Create a frame to hold the new content
        self.selection_frame = tk.Frame(self.root, bg="white", bd=2, relief="flat")
        self.canvas.create_window(
            0, 0, anchor="nw", window=self.selection_frame,
            width=self.bg_photo.width(), height=self.bg_photo.height()
        )

        # Title
        title_label = tk.Label(
            self.selection_frame, text="Customer Type & Product", font=("Arial", 16, "bold"), bg="white"
        )
        title_label.pack(pady=15)

        # -------------- Customer Type Buttons --------------
        customer_type_frame = tk.Frame(self.selection_frame, bg="white")
        customer_type_frame.pack(pady=5)

        self.customer_type = tk.StringVar(value="new")

        new_customer_button = tk.Radiobutton(
            customer_type_frame, text="I am a New Customer", variable=self.customer_type,
            value="new", bg="white", font=("Arial", 12)
        )
        new_customer_button.pack(side="left", padx=20)

        existing_customer_button = tk.Radiobutton(
            customer_type_frame, text="I am an Existing Customer", variable=self.customer_type,
            value="existing", bg="white", font=("Arial", 12)
        )
        existing_customer_button.pack(side="left", padx=20)

        # -------------- Preferred Account --------------
        account_frame = tk.Frame(self.selection_frame, bg="white")
        account_frame.pack(pady=10)

        tk.Label(account_frame, text="Preferred Account:", bg="white", font=("Arial", 12, "bold")).pack(anchor="w")

        self.preferred_account = tk.StringVar(value="ordinary")

        cente_ordinary_radio = tk.Radiobutton(
            account_frame, text="Cente Ordinary Savings Account", variable=self.preferred_account,
            value="ordinary", bg="white", font=("Arial", 11)
        )
        cente_ordinary_radio.pack(anchor="w")

        cente_supa_radio = tk.Radiobutton(
            account_frame, text="CenteSupaWoman Account", variable=self.preferred_account,
            value="supawoman", bg="white", font=("Arial", 11)
        )
        cente_supa_radio.pack(anchor="w")

        # -------------- Account Currency --------------
        currency_frame = tk.Frame(self.selection_frame, bg="white")
        currency_frame.pack(pady=10, fill="x")

        tk.Label(currency_frame, text="Account Currency:", bg="white", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, sticky="w")
        self.currency_var = tk.StringVar()
        self.currency_combo = ttk.Combobox(currency_frame, textvariable=self.currency_var, state="readonly")
        self.currency_combo['values'] = ["Select one", "UGX", "USD", "EUR"]
        self.currency_combo.current(0)  # Default to "Select one"
        self.currency_combo.grid(row=0, column=1, padx=10, sticky="w")

        # -------------- Preferred Branch --------------
        branch_frame = tk.Frame(self.selection_frame, bg="white")
        branch_frame.pack(pady=10, fill="x")

        tk.Label(branch_frame, text="Preferred Branch:", bg="white", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, sticky="w")
        self.branch_var = tk.StringVar()
        self.branch_combo = ttk.Combobox(branch_frame, textvariable=self.branch_var, state="readonly")
        self.branch_combo['values'] = ["Select one", "Main Branch", "City Branch", "Rural Branch"]
        self.branch_combo.current(0)
        self.branch_combo.grid(row=0, column=1, padx=10, sticky="w")

        # -------------- Proceed Button --------------
        proceed_button = tk.Button(
            self.selection_frame, text="Proceed", font=("Arial", 14, "bold"),
            fg="white", bg="blue", command=self.on_proceed
        )
        proceed_button.pack(pady=20)

    def on_proceed(self):
        """Handle the 'Proceed' action by gathering selections."""
        chosen_customer_type = self.customer_type.get()
        chosen_account = self.preferred_account.get()
        chosen_currency = self.currency_var.get()
        chosen_branch = self.branch_var.get()

        # Check that the user selected valid combobox values
        if chosen_currency == "Select one":
            messagebox.showwarning("Incomplete Selection", "Please select an account currency.")
            return
        if chosen_branch == "Select one":
            messagebox.showwarning("Incomplete Selection", "Please select a preferred branch.")
            return

        # For now, just show a summary. You could navigate to a new screen or create an account in your Bank class, etc.
        summary = (
            f"Customer Type: {'New' if chosen_customer_type=='new' else 'Existing'}\n"
            f"Preferred Account: {'Cente Ordinary Savings' if chosen_account=='ordinary' else 'CenteSupaWoman'}\n"
            f"Currency: {chosen_currency}\n"
            f"Branch: {chosen_branch}"
        )
        messagebox.showinfo("Selection Summary", summary)

        # Here you could destroy `self.selection_frame` and show another screen, 
        # or proceed with an account creation workflow, etc.
        # self.selection_frame.destroy()
        # self.show_actual_banking_interface()  # <--- Example of next steps

# ---------------------------
# Run the Application
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()
