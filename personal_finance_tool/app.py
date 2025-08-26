# app.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from ui.tabs import create_tabs
from core.budget import set_budget, check_budget_alerts
# from core.report import show_spending_pie_chart  # Removed due to unknown symbol

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.create_widgets()
        self.refresh_transactions()
        self.refresh_budget_summary()

    def create_widgets(self):
        """Create the main UI with tabs."""
        # Title
        title = tk.Label(self.root, text="Personal Finance Tracker", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
        title.pack(pady=10)

        # Month label
        current_month = datetime.now().strftime("%B %Y")
        month_label = tk.Label(self.root, text=f"Viewing data for: {current_month}", font=("Helvetica", 10), fg="gray", bg="#f0f0f0")
        month_label.pack(pady=2)

        # Create tabs
        self.tabs_data = create_tabs(self)
        self.tabs = self.tabs_data['tabs']
        self.notebook = self.tabs_data['notebook']  # Store notebook reference

        # Buttons Frame (outside tabs)
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Set Budget", command=self.set_budget, bg="#FF9800", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="View Report", command=lambda: messagebox.showinfo("Report", "Report feature not implemented."), bg="#9C27B0", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh All", command=self.refresh_all, bg="#607D8B", fg="white", width=15).pack(side="left", padx=5)

    # ==================== Delegates to tabs ====================
    def refresh_transactions(self):
        self.tabs['view'].refresh_transactions()

    def refresh_budget_summary(self):
        self.tabs['budget'].refresh_budget_summary()

    def refresh_categories(self):
        self.tabs['add'].refresh_categories()

    # ==================== Category Management ====================
    def add_category(self):
        self.tabs['add'].add_category()

    def delete_category(self):
        self.tabs['add'].delete_category()

    # ==================== Transaction Management ====================
    def add_transaction(self):
        self.tabs['add'].add_transaction()

    # ==================== Budget Management ====================
    def set_budget(self):
        set_budget(self.root)

    def view_budgets(self):
        self.tabs['budget'].view_budgets()

    # ==================== Refresh Methods ====================
    def refresh_all(self):
        self.refresh_transactions()
        self.refresh_categories()
        self.refresh_budget_summary()