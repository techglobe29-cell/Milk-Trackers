import sqlite3
from datetime import datetime
import streamlit as st

# Setup the database file
conn = sqlite3.connect("milk_tracker.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS milk_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, quantity REAL, price REAL, total REAL
    )
"""
)
conn.commit()

st.title("🍼 Daily Milk Tracker")

# App Form
with st.form("milk_form", clear_on_submit=True):
    date = st.date_input("Select Date", datetime.now())
    qty = st.number_input("Quantity (Liters)", min_value=0.0, step=0.1)
    price = st.number_input("Price per Liter ($)", min_value=0.0, value=1.50)
    submit = st.form_submit_button("Save Entry")

    if submit and qty > 0:
        total = qty * price
        cursor.execute(
            "INSERT INTO milk_records (date, quantity, price, total) VALUES (?, ?, ?, ?)",
            (str(date), qty, price, total),
        )
        conn.commit()
        st.success("Saved successfully!")

# --- MONTHLY REPORT CALCULATION ---
st.markdown("---")
st.header("📊 Monthly Expense Report")

# SQL Query to extract Year-Month, sum quantities, and sum totals
cursor.execute(
    """
    SELECT 
        strftime('%Y-%m', date) as month, 
        SUM(quantity), 
        SUM(total) 
    FROM milk_records 
    GROUP BY month 
    ORDER BY month DESC
"""
)
monthly_data = cursor.fetchall()

if monthly_data:
    # Format data nicely into cards/columns
    for row in monthly_data:
        # Convert '2026-06' format to a cleaner reading style like 'June 2026'
        date_obj = datetime.strptime(row[0], "%Y-%m")
        month_name = date_obj.strftime("%B %Y")

        total_liters = row[1]
        total_spent = row[2]

        # Display summaries inside clean visual boxes
        with st.container():
            st.subheader(f"📅 {month_name}")
            col1, col2 = st.columns(2)
            col1.metric(label="Total Milk Consumed", value=f"{total_liters:.1f} Liters")
            col2.metric(label="Total Bill Amount", value=f"${total_spent:.2f}")
            st.markdown(" ")
else:
    st.info("No data available yet to generate a monthly report.")


# --- ALL HISTORY DATA TABLE ---
st.markdown("---")
st.subheader("📋 Detailed Daily Records")
cursor.execute("SELECT date, quantity, price, total FROM milk_records ORDER BY date DESC")
data = cursor.fetchall()

if data:
    st.table(
        [
            {"Date": r[0], "Qty (L)": r[1], "Price/L": f"${r[2]:.2f}", "Total": f"${r[3]:.2f}"}
            for r in data
        ]
    )