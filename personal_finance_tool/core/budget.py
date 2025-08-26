# core/budget.py
import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
from datetime import datetime
from .database import (
    get_category_budgets, 
    get_category_spending, 
    set_category_budget,
    get_all_categories
)

def set_budget(parent):
    """
    Opens a dialog to set a monthly budget for a selected category.
    """
    categories = get_all_categories()
    
    if not categories:
        messagebox.showinfo("No Categories", "No categories available. Please add a category first.")
        return

    # Ask user to select a category
    category = simpledialog.askstring(
        "Set Budget",
        f"Enter the category name to set budget for:\n\n{', '.join(categories)}"
    )
    if not category:
        return  # User canceled

    if category not in categories:
        messagebox.showwarning("Invalid Category", f"Category '{category}' does not exist.")
        return

    # Ask for budget amount
    amount_str = simpledialog.askstring(
        "Budget Amount",
        f"Enter monthly budget amount for '{category}' (in $):"
    )
    if not amount_str:
        return  # User canceled

    try:
        amount = float(amount_str)
        if amount < 0:
            raise ValueError("Budget cannot be negative.")
        
        # Save to database
        set_category_budget(category, amount)
        messagebox.showinfo("Success", f"✅ Budget of ${amount:.2f} set for '{category}'.")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid positive number.")


def check_budget_alerts():
    """
    Checks all categories with budgets.
    If current month's spending > budget, shows a warning popup.
    """
    budgets = get_category_budgets()
    budgets_with_limits = [(cat, limit) for cat, limit in budgets if limit > 0]

    alert_messages = []
    current_month = datetime.now().strftime("%Y-%m")

    for category, limit in budgets_with_limits:
        spent = get_category_spending(category, current_month)
        
        if spent > limit:
            alert_messages.append(f"🚨 {category}: Spent ${spent:.2f} / Budget ${limit:.2f}")

    # Show one consolidated alert if needed
    if alert_messages:
        message = "You have exceeded your budget in the following categories:\n\n" + "\n".join(alert_messages)
        messagebox.showwarning("Budget Exceeded!", message)


def get_budget_summary():
    """
    Get budget summary for current month.
    Returns: list of dicts with category, budget, spent, remaining info
    """
    budgets = get_category_budgets()
    budgets_with_limits = [(cat, limit) for cat, limit in budgets if limit > 0]
    
    summary = []
    current_month = datetime.now().strftime("%Y-%m")
    
    for category, limit in budgets_with_limits:
        spent = get_category_spending(category, current_month)
        remaining = limit - spent
        
        summary.append({
            'category': category,
            'budget': limit,
            'spent': spent,
            'remaining': remaining,
            'percentage': (spent / limit * 100) if limit > 0 else 0
        })
    
    return summary


def is_over_budget(category):
    """
    Check if a specific category is over budget for current month.
    Returns: bool
    """
    budgets = get_category_budgets()
    budget_dict = dict(budgets)
    
    if category not in budget_dict:
        return False
    
    limit = budget_dict[category]
    if limit <= 0:
        return False
    
    current_month = datetime.now().strftime("%Y-%m")
    spent = get_category_spending(category, current_month)
    
    return spent > limit


def get_total_budget_vs_spending():
    """
    Get total budget vs total spending for current month.
    Returns: (total_budget, total_spent, remaining)
    """
    budgets = get_category_budgets()
    budgets_with_limits = [(cat, limit) for cat, limit in budgets if limit > 0]
    
    total_budget = sum(limit for _, limit in budgets_with_limits)
    
    current_month = datetime.now().strftime("%Y-%m")
    total_spent = sum(get_category_spending(cat, current_month) for cat, _ in budgets_with_limits)
    
    remaining = total_budget - total_spent
    
    return total_budget, total_spent, remaining


def get_overspent_categories():
    """
    Get list of categories that are over budget for current month.
    Returns: list of (category, budget, spent, overspent_amount)
    """
    budgets = get_category_budgets()
    budgets_with_limits = [(cat, limit) for cat, limit in budgets if limit > 0]
    
    overspent = []
    current_month = datetime.now().strftime("%Y-%m")
    
    for category, limit in budgets_with_limits:
        spent = get_category_spending(category, current_month)
        if spent > limit:
            overspent.append((category, limit, spent, spent - limit))
    
    return overspent


def reset_all_budgets():
    """
    Reset all budget limits to 0.
    Returns: number of budgets reset
    """
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute("UPDATE budgets SET limit_amount = 0")
    rows_affected = c.rowcount
    conn.commit()
    conn.close()
    return rows_affected


def get_budget_utilization_rate():
    """
    Calculate overall budget utilization rate.
    Returns: float (percentage) or 0 if no budgets set
    """
    total_budget, total_spent, _ = get_total_budget_vs_spending()
    
    if total_budget <= 0:
        return 0
    
    return (total_spent / total_budget) * 100


def get_category_budget_status(category):
    """
    Get detailed budget status for a specific category.
    Returns: dict with budget info or None if category not found
    """
    budgets = get_category_budgets()
    budget_dict = dict(budgets)
    
    if category not in budget_dict:
        return None
    
    limit = budget_dict[category]
    current_month = datetime.now().strftime("%Y-%m")
    spent = get_category_spending(category, current_month)
    remaining = limit - spent
    percentage = (spent / limit * 100) if limit > 0 else 0
    
    return {
        'category': category,
        'budget': limit,
        'spent': spent,
        'remaining': remaining,
        'percentage': percentage,
        'over_budget': spent > limit
    }