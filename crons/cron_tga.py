import requests
import datetime
import time
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection, get_db_cursor


# Function to send email notification
def send_email_notification(record):
    sender_email = "charismoutafidis@gmail.com"
    receiver_email = "charismoutafidis@gmail.com"
    cc_emails = ["kleung963@gmail.com", "pkoszycki444@gmail.com", "tszyeungcheung2007@gmail.com", "tonyteglas@yahoo.com"]
    cc_emails = ["kleung963@gmail.com"]
    subject = "New Record Saved to Database"

    # Create the email content
    message = MIMEText(f"A new record was saved to the database:\n\n{record}")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Bcc"] = ", ".join(cc_emails)
    message["Subject"] = subject

    recipients = [receiver_email] + cc_emails

    # SMTP server configuration for Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    smtp_user = "charismoutafidis@gmail.com"
    smtp_password = "nykh sgvi nmon gbyx"  # Use the App Password

    # Send the email
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, recipients, message.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


# Create table if it does not exist
def create_table():
    conn = get_db_connection()
    cursor = get_db_cursor(conn, dict_cursor=False)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS liquidity (
            record_date DATE,
            account_type VARCHAR(255),
            close_today_bal VARCHAR(255),
            open_today_bal VARCHAR(255),
            open_month_bal VARCHAR(255),
            open_fiscal_year_bal VARCHAR(255),
            table_nbr VARCHAR(255),
            table_nm VARCHAR(255),
            sub_table_name VARCHAR(255),
            src_line_nbr INTEGER,
            record_fiscal_year INTEGER,
            record_fiscal_quarter INTEGER,
            record_calendar_year INTEGER,
            record_calendar_quarter INTEGER,
            record_calendar_month INTEGER,
            record_calendar_day INTEGER,
            record_index VARCHAR(255)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


# Save record to database and send email
def save_record(record, index):
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn, dict_cursor=False)
        cursor.execute('''
            INSERT INTO liquidity (
                record_date, account_type, close_today_bal, open_today_bal, open_month_bal, open_fiscal_year_bal, 
                table_nbr, table_nm, sub_table_name, src_line_nbr, record_fiscal_year, record_fiscal_quarter, 
                record_calendar_year, record_calendar_quarter, record_calendar_month, record_calendar_day, record_index
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            record['record_date'], record['account_type'], record.get('close_today_bal'), record['open_today_bal'],
            record['open_month_bal'], record['open_fiscal_year_bal'], record['table_nbr'], record['table_nm'],
            record['sub_table_name'], record['src_line_nbr'], record['record_fiscal_year'],
            record['record_fiscal_quarter'],
            record['record_calendar_year'], record['record_calendar_quarter'], record['record_calendar_month'],
            record['record_calendar_day'], index
        ))
        conn.commit()
        cursor.close()
        conn.close()

        # Send email after saving the record
        send_email_notification(record)

    except Exception as e:
        print(f"Error saving record to database: {e}")
        raise


# Function to get the most recent date from the database
def get_most_recent_date():
    conn = get_db_connection()
    cursor = get_db_cursor(conn, dict_cursor=False)
    cursor.execute('SELECT MAX(record_date) FROM liquidity')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0]


# Define the base URL and endpoint
BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance"


# Function to fetch and process data for a specific date
def process_date(current_date):
    attempts = 0
    max_attempts = 5
    date_str = current_date.strftime('%Y-%m-%d')

    while attempts < max_attempts:
        print(current_date)
        try:
            # Make the API request
            response = requests.get(BASE_URL, params={'filter': f'record_date:eq:{date_str}'})

            # Check if the response is successful
            if response.status_code == 200:
                data = response.json().get('data', [])

                # Iterate over the records and find the one with the "Treasury General Account (TGA) Closing Balance"
                for record in data:
                    if record.get('account_type') == 'Treasury General Account (TGA) Closing Balance':
                        save_record(record, "TGA1")
                    #if record.get('account_type') == 'Treasury General Account (TGA) Opening Balance':
                        #save_record(record, "TGA2")
                break
            else:
                print(f"Failed to fetch data for date {date_str}: {response.status_code}")
        except Exception as e:
            print(f"Error processing date {date_str}: {e}")

        attempts += 1
        time.sleep(300)  # Pause for 5 minutes before retrying

    if attempts == max_attempts:
        print(f"Failed to process data for date {date_str} after {max_attempts} attempts")


# Create table if not exists
create_table()

# Get the most recent date from the database
most_recent_date = get_most_recent_date()

# Define the start date as the next day after the most recent date
if most_recent_date:
    start_date = most_recent_date + datetime.timedelta(days=1)
else:
    start_date = datetime.date(2022, 1, 1)

# Define the end date as today
end_date = datetime.date.today()

# Iterate over each day in the date range
current_date = start_date
while current_date <= end_date:
    process_date(current_date)
    time.sleep(2)
    # Move to the next day
    current_date += datetime.timedelta(days=1)
