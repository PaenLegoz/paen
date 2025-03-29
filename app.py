from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'attachments'
app.config['DATABASE'] = 'data.db'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load data from SQLite database
def load_data():
    if not os.path.exists(app.config['DATABASE']):
        # Create an empty DataFrame and save to SQLite
        df = pd.DataFrame(columns=["DATE", "FROM", "DETAILS", "INCOME", "EXPENSES", "Attachments"])
        df.to_sql("records", pd.io.sql.connect(app.config['DATABASE']), index=False, if_exists="replace")
    return pd.read_sql("SELECT * FROM records", pd.io.sql.connect(app.config['DATABASE']))

# Save data to SQLite database
def save_data(df):
    df.to_sql("records", pd.io.sql.connect(app.config['DATABASE']), index=False, if_exists="replace")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle form submission
        date = request.form.get("date")
        source = request.form.get("from")
        details = request.form.get("details")
        income = float(request.form.get("income", 0))
        expenses = float(request.form.get("expenses", 0))
        attachments = request.files.getlist("attachments")

        # Save attachments
        attachment_paths = []
        for file in attachments:
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                attachment_paths.append(filepath)

        # Add new record to DataFrame
        new_record = {
            "DATE": date,
            "FROM": source,
            "DETAILS": details,
            "INCOME": income,
            "EXPENSES": expenses,
            "Attachments": ",".join(attachment_paths),
        }
        df = load_data()
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        save_data(df)
        flash("Record added successfully!", "success")
        return redirect(url_for("index"))

    # Load data and render the page
    df = load_data()
    return render_template("index.html", records=df.to_dict(orient="records"))

@app.route("/download/<path:filename>")
def download_attachment(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route("/report")
def generate_report():
    df = load_data()
    total_income = df["INCOME"].sum()
    total_expenses = df["EXPENSES"].sum()
    balance = total_income - total_expenses
    return render_template("report.html", total_income=total_income, total_expenses=total_expenses, balance=balance)

if __name__ == "__main__":
    app.run(debug=True)