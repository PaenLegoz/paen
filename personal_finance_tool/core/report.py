# core/report.py
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import datetime
from .database import get_db_connection, get_transactions_for_month, get_all_transactions

def show_spending_pie_chart():
    """
    Show a pie chart of current month's spending by category.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    current_month = datetime.now().strftime("%Y-%m")
    
    c.execute('''
        SELECT category, SUM(amount) 
        FROM transactions 
        WHERE type = 'expense' 
        AND strftime('%Y-%m', date) = ? 
        GROUP BY category
        ORDER BY SUM(amount) DESC
    ''', (current_month,))
    
    data = c.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("No Data", "No expenses recorded this month.")
        return

    categories, amounts = zip(*data)

    # Create pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title(f"Monthly Spending by Category ({current_month})", fontsize=14, pad=20)

    # Display in Tkinter window
    top = tk.Toplevel()
    top.title("📊 Spending Report")
    top.geometry("800x600")
    top.minsize(600, 500)

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # Close button
    close_btn = tk.Button(top, text="Close", command=top.destroy, bg="#f44336", fg="white")
    close_btn.pack(pady=10)

    top.transient()
    top.grab_set()


def show_income_vs_expense_chart():
    """
    Show a bar chart comparing income vs expenses for current month.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    current_month = datetime.now().strftime("%Y-%m")
    
    # Get total income
    c.execute('''
        SELECT COALESCE(SUM(amount), 0) 
        FROM transactions 
        WHERE type = 'income' 
        AND strftime('%Y-%m', date) = ?
    ''', (current_month,))
    income = c.fetchone()[0]
    
    # Get total expenses
    c.execute('''
        SELECT COALESCE(SUM(amount), 0) 
        FROM transactions 
        WHERE type = 'expense' 
        AND strftime('%Y-%m', date) = ?
    ''', (current_month,))
    expenses = c.fetchone()[0]
    
    conn.close()

    if income == 0 and expenses == 0:
        messagebox.showinfo("No Data", "No transactions recorded this month.")
        return

    # Create bar chart
    fig, ax = plt.subplots(figsize=(8, 6))
    categories = ['Income', 'Expenses']
    amounts = [income, expenses]
    colors = ['#4CAF50', '#f44336']
    
    bars = ax.bar(categories, amounts, color=colors)
    ax.set_ylabel('Amount ($)')
    ax.set_title(f"Income vs Expenses ({current_month})", fontsize=14, pad=20)
    
    # Add value labels on bars
    for bar, amount in zip(bars, amounts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'${amount:.2f}', ha='center', va='bottom')

    # Display in Tkinter window
    top = tk.Toplevel()
    top.title("💰 Income vs Expenses Report")
    top.geometry("800x600")
    top.minsize(600, 500)

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # Close button
    close_btn = tk.Button(top, text="Close", command=top.destroy, bg="#f44336", fg="white")
    close_btn.pack(pady=10)

    top.transient()
    top.grab_set()


def show_monthly_trend_chart():
    """
    Show a line chart of monthly spending trends over the last 6 months.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get last 6 months of expense data
    c.execute('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount) 
        FROM transactions 
        WHERE type = 'expense' 
        AND date >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    ''')
    
    data = c.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("No Data", "No expense data available for trend analysis.")
        return

    months, amounts = zip(*data)
    
    # Create line chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(months, amounts, marker='o', linewidth=2, markersize=8, color='#2196F3')
    ax.set_ylabel('Total Expenses ($)')
    ax.set_xlabel('Month')
    ax.set_title("Monthly Spending Trend (Last 6 Months)", fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    
    # Add value labels on points
    for i, (month, amount) in enumerate(zip(months, amounts)):
        ax.annotate(f'${amount:.0f}', (month, amount), 
                   textcoords="offset points", xytext=(0,10), ha='center')

    # Display in Tkinter window
    top = tk.Toplevel()
    top.title("📈 Monthly Spending Trend")
    top.geometry("900x600")
    top.minsize(800, 500)

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # Close button
    close_btn = tk.Button(top, text="Close", command=top.destroy, bg="#f44336", fg="white")
    close_btn.pack(pady=10)

    top.transient()
    top.grab_set()


def show_category_breakdown_report():
    """
    Show a detailed breakdown report in a new window.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    current_month = datetime.now().strftime("%Y-%m")
    
    # Get income by category
    c.execute('''
        SELECT category, SUM(amount) 
        FROM transactions 
        WHERE type = 'income' 
        AND strftime('%Y-%m', date) = ? 
        GROUP BY category
        ORDER BY SUM(amount) DESC
    ''', (current_month,))
    income_data = c.fetchall()
    
    # Get expenses by category
    c.execute('''
        SELECT category, SUM(amount) 
        FROM transactions 
        WHERE type = 'expense' 
        AND strftime('%Y-%m', date) = ? 
        GROUP BY category
        ORDER BY SUM(amount) DESC
    ''', (current_month,))
    expense_data = c.fetchall()
    
    conn.close()

    if not income_data and not expense_data:
        messagebox.showinfo("No Data", "No transactions recorded this month.")
        return

    # Create report window
    top = tk.Toplevel()
    top.title("📋 Detailed Category Breakdown")
    top.geometry("800x600")
    top.minsize(600, 500)

    # Title
    title_label = tk.Label(top, text=f"Category Breakdown Report - {current_month}", 
                          font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)

    # Create notebook for tabs
    from tkinter import ttk
    notebook = ttk.Notebook(top)
    notebook.pack(fill="both", expand=True, padx=10, pady=5)

    # Income Tab
    income_frame = tk.Frame(notebook)
    notebook.add(income_frame, text="💰 Income")

    if income_data:
        income_text = tk.Text(income_frame, wrap=tk.WORD, font=("Courier", 10))
        income_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        total_income = sum(amount for _, amount in income_data)
        income_text.insert(tk.END, f"{'Category':<20} {'Amount ($)':<15}\n")
        income_text.insert(tk.END, "-" * 35 + "\n")
        
        for category, amount in income_data:
            income_text.insert(tk.END, f"{category:<20} ${amount:<14.2f}\n")
        
        income_text.insert(tk.END, "-" * 35 + "\n")
        income_text.insert(tk.END, f"{'TOTAL INCOME':<20} ${total_income:<14.2f}\n")
        income_text.config(state=tk.DISABLED)
    else:
        no_income_label = tk.Label(income_frame, text="No income recorded this month.", 
                                  font=("Helvetica", 12))
        no_income_label.pack(pady=50)

    # Expenses Tab
    expense_frame = tk.Frame(notebook)
    notebook.add(expense_frame, text="💸 Expenses")

    if expense_data:
        expense_text = tk.Text(expense_frame, wrap=tk.WORD, font=("Courier", 10))
        expense_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        total_expenses = sum(amount for _, amount in expense_data)
        expense_text.insert(tk.END, f"{'Category':<20} {'Amount ($)':<15}\n")
        expense_text.insert(tk.END, "-" * 35 + "\n")
        
        for category, amount in expense_data:
            expense_text.insert(tk.END, f"{category:<20} ${amount:<14.2f}\n")
        
        expense_text.insert(tk.END, "-" * 35 + "\n")
        expense_text.insert(tk.END, f"{'TOTAL EXPENSES':<20} ${total_expenses:<14.2f}\n")
        expense_text.config(state=tk.DISABLED)
    else:
        no_expense_label = tk.Label(expense_frame, text="No expenses recorded this month.", 
                                   font=("Helvetica", 12))
        no_expense_label.pack(pady=50)

    # Summary Tab
    summary_frame = tk.Frame(notebook)
    notebook.add(summary_frame, text="📊 Summary")

    summary_text = tk.Text(summary_frame, wrap=tk.WORD, font=("Courier", 10))
    summary_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    total_income = sum(amount for _, amount in income_data)
    total_expenses = sum(amount for _, amount in expense_data)
    net = total_income - total_expenses
    
    summary_text.insert(tk.END, "MONTHLY SUMMARY\n")
    summary_text.insert(tk.END, "=" * 30 + "\n\n")
    summary_text.insert(tk.END, f"Total Income:    ${total_income:.2f}\n")
    summary_text.insert(tk.END, f"Total Expenses:  ${total_expenses:.2f}\n")
    summary_text.insert(tk.END, f"Net Savings:     ${net:.2f}\n\n")
    
    if net >= 0:
        summary_text.insert(tk.END, "✅ You saved money this month!\n", "green")
    else:
        summary_text.insert(tk.END, "⚠️ You spent more than you earned.\n", "red")
    
    summary_text.tag_config("green", foreground="green")
    summary_text.tag_config("red", foreground="red")
    summary_text.config(state=tk.DISABLED)

    # Close button
    close_btn = tk.Button(top, text="Close", command=top.destroy, bg="#f44336", fg="white")
    close_btn.pack(pady=10)

    top.transient()
    top.grab_set()


def export_report_to_text():
    """
    Export current month's report to a text file.
    Returns: bool (success)
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        current_month = datetime.now().strftime("%Y-%m")
        filename = f"finance_report_{current_month.replace('-', '_')}.txt"
        
        # Get income data
        c.execute('''
            SELECT category, SUM(amount) 
            FROM transactions 
            WHERE type = 'income' 
            AND strftime('%Y-%m', date) = ? 
            GROUP BY category
            ORDER BY SUM(amount) DESC
        ''', (current_month,))
        income_data = c.fetchall()
        
        # Get expense data
        c.execute('''
            SELECT category, SUM(amount) 
            FROM transactions 
            WHERE type = 'expense' 
            AND strftime('%Y-%m', date) = ? 
            GROUP BY category
            ORDER BY SUM(amount) DESC
        ''', (current_month,))
        expense_data = c.fetchall()
        
        conn.close()

        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"PERSONAL FINANCE REPORT - {current_month}\n")
            f.write("=" * 50 + "\n\n")
            
            # Income section
            f.write("INCOME BREAKDOWN:\n")
            f.write("-" * 20 + "\n")
            total_income = sum(amount for _, amount in income_data)
            for category, amount in income_data:
                f.write(f"{category:<20} ${amount:>10.2f}\n")
            f.write("-" * 20 + "\n")
            f.write(f"{'TOTAL INCOME':<20} ${total_income:>10.2f}\n\n")
            
            # Expenses section
            f.write("EXPENSE BREAKDOWN:\n")
            f.write("-" * 20 + "\n")
            total_expenses = sum(amount for _, amount in expense_data)
            for category, amount in expense_data:
                f.write(f"{category:<20} ${amount:>10.2f}\n")
            f.write("-" * 20 + "\n")
            f.write(f"{'TOTAL EXPENSES':<20} ${total_expenses:>10.2f}\n\n")
            
            # Summary
            net = total_income - total_expenses
            f.write("SUMMARY:\n")
            f.write("-" * 10 + "\n")
            f.write(f"Net Savings: ${net:>10.2f}\n")
            if net >= 0:
                f.write("Status: You saved money this month! 🎉\n")
            else:
                f.write("Status: You spent more than you earned. 💰\n")

        messagebox.showinfo("Export Complete", f"Report exported to {filename}")
        return True
        
    except Exception as e:
        messagebox.showerror("Export Failed", f"Failed to export report: {str(e)}")
        return False


def get_monthly_summary_stats():
    """
    Get summary statistics for current month.
    Returns: dict with income, expenses, net, and transaction count
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    current_month = datetime.now().strftime("%Y-%m")
    
    # Get income
    c.execute('''
        SELECT COALESCE(SUM(amount), 0), COUNT(*) 
        FROM transactions 
        WHERE type = 'income' 
        AND strftime('%Y-%m', date) = ?
    ''', (current_month,))
    income_sum, income_count = c.fetchone()
    
    # Get expenses
    c.execute('''
        SELECT COALESCE(SUM(amount), 0), COUNT(*) 
        FROM transactions 
        WHERE type = 'expense' 
        AND strftime('%Y-%m', date) = ?
    ''', (current_month,))
    expense_sum, expense_count = c.fetchone()
    
    conn.close()
    
    return {
        'period': current_month,
        'total_income': income_sum,
        'total_expenses': expense_sum,
        'net_savings': income_sum - expense_sum,
        'income_transactions': income_count,
        'expense_transactions': expense_count,
        'total_transactions': income_count + expense_count
    }