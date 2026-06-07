import sqlite3
from datetime import datetime
import streamlit as st

# Set page configuration to make it look like a clean mobile web app
st.set_page_config(page_title="Milk Tracker", page_icon="🍼", layout="centered")

# Custom CSS styling to make metrics and buttons pop out beautifully
st.markdown(
    """
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

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

# --- SIDEBAR MENU FOR DATA ENTRY ---
st.sidebar.header("📥 Log New Entry")

# Creating the sidebar form explicitly
milk_form = st.sidebar.form(key="milk_entry_form", clear_on_submit=True)
date = milk_form.date_input("Select Date", datetime.now())
qty = milk_form.number_input("Quantity (Liters)", min_value=0.0, step=0.1)

# Settled default value to 85.0 here
price = milk_form.number_input("Price per Liter (₹)", min_value=0.0, value=85.0)
submit = milk_form.form_submit_button("💾 Save Record")

if submit and qty > 0:
    total = qty * price
    cursor.execute(
        "INSERT INTO milk_records (date, quantity, price, total) VALUES (?, ?, ?, ?)",
        (str(date), qty, price, total),
    )
    conn.commit()
    st.sidebar.success("✅ Entry saved successfully!")

# --- MAIN APP SCREEN ---
st.title("🍼 Daily Milk Tracker")
st.caption("Track your daily milk consumption & monthly Indian Rupee expenses.")

# --- SECTION 1: MONTHLY REPORT ---
st.header("📊 Monthly Expense Report")

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
    for row in monthly_data:
        # Convert '2026-06' format to a cleaner reading style like 'June 2026'
        date_obj = datetime.strptime(row[0], "%Y-%m")
        month_name = date_obj.strftime("%B %Y")

        total_liters = row[1]
        total_spent = row[2]

        # Display monthly summaries inside clean visual containers
        with st.container():
            st.subheader(f"📅 {month_name}")
            col1, col2 = st.columns(2)
            col1.metric(label="Total Milk Consumed", value=f"{total_liters:.1f} L")
            col2.metric(label="Total Bill Expense", value=f"₹{total_spent:,.2f}")
            st.markdown(" ")
else:
    st.info("No data available yet. Use the left sidebar panel to log your first entry!")


# --- SECTION 2: ALL HISTORY DATA TABLE ---
st.markdown("---")
st.subheader("📋 Detailed Daily Records")
cursor.execute("SELECT date, quantity, price, total FROM milk_records ORDER BY date DESC")
data = cursor.fetchall()

if data:
    # Creating a nicely formatted history table with Indian Rupee formatting
    st.table(
        [
            {
                "Date": r[0],
                "Qty (Liters)": f"{r[1]:.1f} L",
                "Price per Liter": f"₹{r[2]:.2f}",
                "Total Paid": f"₹{r[3]:.2f}",
            }
            for r in data
        ]
    )
