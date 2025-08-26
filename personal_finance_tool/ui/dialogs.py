# ui/dialogs.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from datetime import datetime
import sqlite3
from ..core.budget import check_budget_alerts
from ..core.database import (
    get_db_connection, 
    get_transactions_for_month, 
    get_all_categories, 
    add_category as db_add_category,
    delete_category as db_delete_category,
    get_category_budgets,
    get_category_spending,
    set_category_budget
)

class AddTransactionTab:
    def __init__(self, app, frame):
        self.app = app
        self.frame = frame
        self.create_widgets()

    def create_widgets(self):
        # Transaction Entry Frame
        entry_frame = tk.LabelFrame(self.frame, text="Add New Transaction", padx=10, pady=10, bg="#f9f9f9")
        entry_frame.pack(padx=20, pady=20, fill="x")

        # Row 0: Date and Type
        tk.Label(entry_frame, text="Date (YYYY-MM-DD):", bg="#f9f9f9").grid(row=0, column=0, sticky="w")
        self.date_entry = tk.Entry(entry_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(entry_frame, text="Type:", bg="#f9f9f9").grid(row=0, column=2, sticky="w")
        self.type_var = tk.StringVar(value="expense")
        tk.Radiobutton(entry_frame, text="Income", variable=self.type_var, value="income", bg="#f9f9f9").grid(row=0, column=3)
        tk.Radiobutton(entry_frame, text="Expense", variable=self.type_var, value="expense", bg="#f9f9f9").grid(row=0, column=4)

        # Row 1: Category + Buttons
        tk.Label(entry_frame, text="Category:", bg="#f9f9f9").grid(row=1, column=0, sticky="w")
        self.category_combo = ttk.Combobox(entry_frame, state="readonly", width=15)
        self.category_combo.grid(row=1, column=1, padx=5, pady=2)
        self.refresh_categories()

        tk.Button(entry_frame, text="Add Custom", command=self.add_category, bg="#4CAF50", fg="white").grid(row=1, column=2, padx=5)
        tk.Button(entry_frame, text="Delete", command=self.delete_category, bg="#f44336", fg="white").grid(row=1, column=3, padx=5)

        # Row 2: Amount
        tk.Label(entry_frame, text="Amount ($):", bg="#f9f9f9").grid(row=2, column=0, sticky="w")
        self.amount_entry = tk.Entry(entry_frame, width=15)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=2)

        # Row 3: Description
        tk.Label(entry_frame, text="Description:", bg="#f9f9f9").grid(row=3, column=0, sticky="w")
        self.desc_entry = tk.Entry(entry_frame, width=50)
        self.desc_entry.grid(row=3, column=1, columnspan=4, padx=5, pady=2)

        # Row 4: Add Transaction Button
        tk.Button(entry_frame, text="➕ Add Transaction", command=self.add_transaction,
                bg="#2196F3", fg="white", font=("bold")).grid(row=4, column=0, columnspan=5, pady=15)

    def refresh_categories(self):
        categories = get_all_categories()
        self.category_combo['values'] = categories
        if categories:
            self.category_combo.current(0)

    def add_category(self):
        new_cat = simpledialog.askstring("Add Category", "Enter new category name:")
        if not new_cat:
            return
        new_cat = new_cat.strip()
        if not new_cat:
            messagebox.showwarning("Invalid", "Category name cannot be empty.")
            return

        if db_add_category(new_cat):
            self.refresh_categories()
            self.app.refresh_categories()
            messagebox.showinfo("Success", f"✅ Category '{new_cat}' added!")
        else:
            messagebox.showwarning("Duplicate", f"Category '{new_cat}' already exists.")

    def delete_category(self):
        categories = get_all_categories()
        if not categories:
            messagebox.showinfo("No Categories", "No categories to delete.")
            return

        cat_to_delete = simpledialog.askstring(
            "Delete Category",
            f"Enter category name to delete:\n{', '.join(categories)}"
        )
        if not cat_to_delete:
            return
        if cat_to_delete not in categories:
            messagebox.showwarning("Not Found", f"Category '{cat_to_delete}' not found.")
            return

        success, message = db_delete_category(cat_to_delete)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_categories()
            self.app.refresh_categories()
        else:
            messagebox.showerror("Cannot Delete", message)

    def add_transaction(self):
        date = self.date_entry.get().strip()
        trans_type = self.type_var.get()
        category = self.category_combo.get()
        amount_str = self.amount_entry.get().strip()
        desc = self.desc_entry.get().strip()

        # Validation
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid positive number.")
            return

        if not category:
            messagebox.showerror("Missing", "Please select a category.")
            return

        # Insert into DB
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO transactions (date, type, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, trans_type, category, amount, desc))
        conn.commit()
        conn.close()

        # Refresh UI
        self.app.refresh_transactions()
        self.app.refresh_budget_summary()
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        check_budget_alerts()  # Check if budget exceeded
        messagebox.showinfo("Success", "✅ Transaction added!")


class ViewTransactionsTab:
    def __init__(self, app, frame):
        self.app = app
        self.frame = frame
        self.create_widgets()

    def create_widgets(self):
        # Transactions List
        list_frame = tk.LabelFrame(self.frame, text="Transactions This Month", padx=10, pady=10)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("Date", "Type", "Category", "Amount", "Desc"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount ($)")
        self.tree.heading("Desc", text="Description")

        self.tree.column("Date", width=100)
        self.tree.column("Type", width=80)
        self.tree.column("Category", width=120)
        self.tree.column("Amount", width=100)
        self.tree.column("Desc", width=250)

        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        scroll = tk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # Load data
        self.refresh_transactions()

    def refresh_transactions(self):
        # Clear current rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        current_month = datetime.now().strftime("%Y-%m")
        transactions = get_transactions_for_month(current_month)

        for row in transactions:
            self.tree.insert("", "end", values=row)


class BudgetStatusTab:
    def __init__(self, app, frame):
        self.app = app
        self.frame = frame
        self.create_widgets()

    def create_widgets(self):
        # Budget Summary Frame
        self.budget_summary_frame = tk.Frame(self.frame, bg="#fff8e1")
        self.budget_summary_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Placeholder for budget rows
        self.budget_rows_container = tk.Frame(self.budget_summary_frame, bg="#fff8e1")
        self.budget_rows_container.pack(fill="both", expand=True)

        # Load data
        self.refresh_budget_summary()

    def refresh_budget_summary(self):
        """Refresh the budget summary panel with current month's data."""
        # Clear previous rows
        for widget in self.budget_rows_container.winfo_children():
            widget.destroy()

        budgets = get_category_budgets()
        budgets_with_limits = [(cat, limit) for cat, limit in budgets if limit > 0]

        if not budgets_with_limits:
            tk.Label(self.budget_rows_container, text="No budgets set.", bg="#fff8e1", fg="gray", font=("Helvetica", 12)).pack(pady=20)
            return

        # Header row
        header = tk.Frame(self.budget_rows_container, bg="#fff8e1")
        header.pack(fill="x", pady=5)
        tk.Label(header, text="Category", width=15, anchor="w", font=("Helvetica", 9, "bold"), bg="#fff8e1").pack(side="left")
        tk.Label(header, text="Budget", width=10, anchor="center", font=("Helvetica", 9, "bold"), bg="#fff8e1").pack(side="left")
        tk.Label(header, text="Spent", width=10, anchor="center", font=("Helvetica", 9, "bold"), bg="#fff8e1").pack(side="left")
        tk.Label(header, text="Remaining", width=12, anchor="center", font=("Helvetica", 9, "bold"), bg="#fff8e1").pack(side="left")
        tk.Label(header, text="Progress", width=20, anchor="center", font=("Helvetica", 9, "bold"), bg="#fff8e1").pack(side="left")

        # Add each category row
        current_month = datetime.now().strftime("%Y-%m")
        for category, limit in budgets_with_limits:
            spent = get_category_spending(category, current_month)
            remaining = limit - spent

            # Create clickable row
            row = tk.Frame(self.budget_rows_container, bg="#fff8e1", pady=3, relief="solid", bd=1)
            row.pack(fill="x", padx=2, pady=1)
            
            # Make the entire row clickable
            row.bind("<Button-1>", lambda e, cat=category: self.on_category_click(cat))
            
            # Category label (clickable)
            cat_label = tk.Label(row, text=category, width=15, anchor="w", bg="#fff8e1", cursor="hand2")
            cat_label.pack(side="left")
            cat_label.bind("<Button-1>", lambda e, cat=category: self.on_category_click(cat))

            # Budget amount
            budget_label = tk.Label(row, text=f"${limit:.2f}", width=10, anchor="center", bg="#fff8e1")
            budget_label.pack(side="left")

            # Spent amount
            spent_label = tk.Label(row, text=f"${spent:.2f}", width=10, anchor="center", bg="#fff8e1")
            spent_label.pack(side="left")

            # Remaining amount (color-coded)
            remaining_label = tk.Label(row, text=f"${remaining:.2f}", width=12, anchor="center", bg="#fff8e1",
                                     fg="red" if remaining < 0 else "green")
            remaining_label.pack(side="left")

            # Progress bar
            bar_frame = tk.Frame(row, width=100, height=15, bg="lightgray")
            bar_frame.pack(side="left", padx=5)
            bar_frame.pack_propagate(False)

            if limit > 0:
                pct = min(100, max(0, (spent / limit) * 100))
                color = "green" if pct <= 100 else "red"
                bar = tk.Frame(bar_frame, bg=color, width=pct, height=15)
                bar.pack(side="left", fill="y")
                bar.pack_propagate(False)

                # Show % label
                pct_label = tk.Label(bar_frame, text=f"{pct:.0f}%", font=("Helvetica", 7), bg="white")
                pct_label.pack(side="right")

    def on_category_click(self, category):
        """Handle click on category row - switch to Add Transaction tab and pre-select category."""
        # Switch to Add Transaction tab (index 0)
        self.app.notebook.select(0)
        
        # Pre-select the category in the dropdown
        add_tab = self.app.tabs['add']
        add_tab.category_combo.set(category)
        
        # Focus on amount field for quick entry
        add_tab.amount_entry.focus_set()

    def view_budgets(self):
        """Show a popup window with all category budgets and current spending."""
        budgets = get_category_budgets()
        
        if not budgets:
            messagebox.showinfo("Budgets", "No categories found.")
            return

        # Build message header
        header = f"{'Category':<15} {'Budget':<10} {'Spent':<10} {'Remaining':<12}\n"
        header += "-" * 50 + "\n"

        lines = [header]
        current_month = datetime.now().strftime("%Y-%m")

        for category, limit in budgets:
            spent = get_category_spending(category, current_month)
            remaining = limit - spent

            # Format line
            line = f"{category:<15} ${limit:<9.2f} ${spent:<9.2f} "
            if remaining >= 0:
                line += f"${remaining:<11.2f}"
            else:
                line += f"⚠️ ${remaining:.2f}"
            lines.append(line)

        # Show in a popup
        top = tk.Toplevel(self.app.root)
        top.title("📊 Monthly Budget Overview")
        top.geometry("600x400")
        top.transient(self.app.root)
        top.grab_set()

        # Title
        tk.Label(top, text="Monthly Budget Status", font=("Helvetica", 14, "bold")).pack(pady=10)

        # Text box with scroll
        text_widget = scrolledtext.ScrolledText(top, wrap=tk.WORD, height=20, width=70, font=("Courier", 10))
        text_widget.pack(padx=20, pady=5, fill="both", expand=True)
        text_widget.insert(tk.END, "\n".join(lines))
        text_widget.config(state=tk.DISABLED)  # Read-only

        # Close button
        tk.Button(top, text="Close", command=top.destroy, bg="#f44336", fg="white").pack(pady=5)