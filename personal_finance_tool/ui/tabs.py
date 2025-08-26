# ui/tabs.py
import tkinter as tk
from tkinter import ttk
from .dialogs import AddTransactionTab, ViewTransactionsTab, BudgetStatusTab

def create_tabs(app):
    """Create all tabs and return references."""
    notebook = ttk.Notebook(app.root)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    # Tab 1: Add Transaction
    add_frame = tk.Frame(notebook, bg="#f9f9f9")
    notebook.add(add_frame, text="➕ Add Transaction")
    add_tab = AddTransactionTab(app, add_frame)

    # Tab 2: View Transactions
    view_frame = tk.Frame(notebook)
    notebook.add(view_frame, text="📋 View Transactions")
    view_tab = ViewTransactionsTab(app, view_frame)

    # Tab 3: Budget Status
    budget_frame = tk.Frame(notebook, bg="#fff8e1")
    notebook.add(budget_frame, text="📊 Budget Status")
    budget_tab = BudgetStatusTab(app, budget_frame)

    return {
        'tabs': {
            'add': add_tab,
            'view': view_tab,
            'budget': budget_tab
        },
        'notebook': notebook
    }

