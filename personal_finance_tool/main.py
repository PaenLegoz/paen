# main.py
"""
Personal Finance Tracker - Main Entry Point
A comprehensive desktop application for tracking income, expenses, and budgets.
"""

# Standard library imports
import tkinter as tk
from tkinter import messagebox

# Core module imports
from core.database import init_db
from app import FinanceApp

def main():
    """Main application entry point."""
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
        return

    # Create and run the main application
    root = tk.Tk()
    
    # Set up window closing protocol
    def on_closing():
        """Handle application closing with confirmation dialog."""
        if messagebox.askyesno("Quit", "Are you sure you want to exit the finance app?"):
            root.destroy()
            root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Set application properties
    root.title("Personal Finance Tracker")
    root.geometry("800x600")
    root.minsize(600, 400)
    
    # Create and start the application
    try:
        app = FinanceApp(root)
        print("✅ Application started successfully")
        root.mainloop()
    except Exception as e:
        print(f"❌ Application failed to start: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()