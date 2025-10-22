from database import get_db_connection, get_db_cursor
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
from matplotlib.ticker import FixedLocator, FuncFormatter, ScalarFormatter, LogLocator
import datetime
import matplotlib.ticker as mticker  # For tick formatting
import os
import matplotlib
matplotlib.use('Agg')

def trw_guy_def():
    # Database configuration is now handled by database.py

    # Connect to MySQL and create a table if it doesn't exist
    def create_connection():
        try:
            conn = get_db_connection()
            return conn
        except psycopg2.Error as err:
            print(f"Database connection error: {err}")
        return None

    # Create the table if it doesn't exist
    def create_table(conn):
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_data (
                date DATE PRIMARY KEY,
                global_liquidity REAL,
                bitcoin_price REAL,
                gold_price REAL
            )
        """)
        conn.commit()

    # Insert data if the table is empty
    def insert_sample_data(conn, global_liquidity, bitcoin_prices, gold_prices, dates):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM price_data")
        result = cursor.fetchone()[0]

        if result == 0:
            for i in range(len(global_liquidity)):
                cursor.execute("""
                    INSERT INTO price_data (date, global_liquidity, bitcoin_price, gold_price)
                    VALUES (%s, %s, %s, %s)
                """, (dates[i].strftime('%Y-%m-%d'), global_liquidity[i], bitcoin_prices[i], gold_prices[i]))
            conn.commit()

    # Fetch data from the database
    def fetch_data(conn):
        cursor = conn.cursor()
        cursor.execute("SELECT date, global_liquidity, bitcoin_price, gold_price FROM price_data ORDER BY date")
        rows = cursor.fetchall()
        dates_db = [row[0] for row in rows]
        global_liquidity_db = np.array([row[1] for row in rows])
        bitcoin_prices_db = np.array([row[2] for row in rows])
        gold_prices_db = np.array([row[3] for row in rows])
        return dates_db, global_liquidity_db, bitcoin_prices_db, gold_prices_db

    # Save plot images in static/plots folder
    def save_plot(fig, filename):
        plots_dir = os.path.join(os.path.dirname(__file__), 'static', 'plots')
        if not os.path.exists(plots_dir):
            os.makedirs(plots_dir)
        fig.savefig(os.path.join(plots_dir, f'{filename}.png'))

    # ----------------------------
    # Step 1: Define Your Data
    # ----------------------------

    conn = create_connection()
    # create_table(conn)
    # insert_sample_data(conn, global_liquidity, bitcoin_prices, gold_prices, dates)

    dates, global_liquidity, bitcoin_prices, gold_prices = fetch_data(conn)
    conn.close()

    gold_prices_2019 = gold_prices[241:]
    bitcoin_prices_2019 = bitcoin_prices[241:]
    global_liquidity_2018 = global_liquidity[192:]
    gold_prices_2018 = gold_prices[192:]
    bitcoin_prices_2018 = bitcoin_prices[192:]


    # Dates array 2
    dates_2018 = dates[192:]

    #################################################################################################
    ########################## 3rd degree polynomial on log-log #####################################
    #################################################################################################

    # Convert data to numpy arrays
    x = np.array(global_liquidity)
    y = np.array(bitcoin_prices)

    # Ensure all values are positive
    x = x[x > 0]
    y = y[y > 0]

    # Log-transform the data
    log_x = np.log10(x)
    log_y = np.log10(y)

    # Fit a 3rd-degree polynomial to the log-transformed data
    coeffs = np.polyfit(log_x, log_y, deg=3)

    # Compute the predicted log_y values
    log_y_pred = np.polyval(coeffs, log_x)

    # Compute R-squared
    SS_res = np.sum((log_y - log_y_pred) ** 2)
    SS_tot = np.sum((log_y - np.mean(log_y)) ** 2)
    R_squared = 1 - (SS_res / SS_tot)

    # Prepare data for plotting the trend line
    log_x_fit = np.linspace(min(log_x), max(log_x), 100)
    log_y_fit = np.polyval(coeffs, log_x_fit)
    x_fit = 10 ** log_x_fit
    y_fit = 10 ** log_y_fit

    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, label='Data Points', alpha=0.7)

    # Plot the trend line
    plt.plot(x_fit, y_fit, color='red', linewidth=2, label=f'3rd-degree fit, $R^2={R_squared:.4f}$')

    # Set logarithmic scale for X and Y axes
    plt.xscale('log')
    plt.yscale('log')

    # Get current axes
    ax = plt.gca()

    # Format axis labels to display normal numbers
    from matplotlib.ticker import ScalarFormatter

    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_formatter(ScalarFormatter())
    ax.yaxis.set_major_formatter(ScalarFormatter())
    # ax.yaxis.set_minor_formatter(ScalarFormatter())
    ax.ticklabel_format(useOffset=False, style='plain', axis='both')

    # Increase number of labels on Y-axis
    from matplotlib.ticker import LogLocator

    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=15))
    subs = np.arange(1.0, 10.0)
    ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=subs, numticks=100))

    # Add labels and title
    plt.xlabel('Global Liquidity ($ Trillions)')
    plt.ylabel('Bitcoin Price ($)')
    plt.title('Global Liquidity vs. Bitcoin with 3rd-degree Polynomial Trend Line')

    # Add grid
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    # Add legend
    plt.legend()

    # Optionally, add R² value as text on the plot
    # plt.text(0.05, 0.95, f'$R^2 = {R_squared:.4f}$', transform=ax.transAxes, fontsize=12, verticalalignment='top')

    # Save the plot
    save_plot(plt, 'global_liquidity_vs_bitcoin')

    #################################################################################################
    ########################## 3rd degree polynomial on log-log Valuation ###########################
    #################################################################################################

    # ----------------------------
    # Step 2: Data Alignment and Filtering
    # ----------------------------

    # Ensure all values are positive for log transformation
    # Create a mask where both x and y are greater than zero
    mask = (x > 0) & (y > 0)

    # Apply the mask to filter the data
    x_filtered = x[mask]
    y_filtered = y[mask]

    # ----------------------------
    # Step 3: Validate Dates Array Length
    # ----------------------------

    # Check if the length of dates matches the filtered data
    if len(dates) != len(x_filtered):
        raise ValueError(
            f"Length of dates array ({len(dates)}) does not match the number of data points after filtering ({len(x_filtered)}). Please ensure they are equal.")

    # ----------------------------
    # Step 4: Log-Transformation for Polynomial Fitting
    # ----------------------------

    # Log-transform the data for polynomial fitting
    log_x = np.log10(x_filtered)
    log_y = np.log10(y_filtered)

    # ----------------------------
    # Step 5: Fit a 3rd-Degree Polynomial
    # ----------------------------

    # Fit a 3rd-degree polynomial to the log-transformed data
    coeffs = np.polyfit(log_x, log_y, deg=3)

    # Compute the predicted log_y values using the polynomial
    log_y_pred = np.polyval(coeffs, log_x)

    # Compute R-squared to assess the fit quality
    SS_res = np.sum((log_y - log_y_pred) ** 2)
    SS_tot = np.sum((log_y - np.mean(log_y)) ** 2)
    R_squared = 1 - (SS_res / SS_tot)

    # print(f"3rd-degree Polynomial Fit: R-squared = {R_squared:.4f}")

    # ----------------------------
    # Step 6: Calculate Residuals and Z-scores
    # ----------------------------

    # Calculate residuals (actual - predicted)
    residuals = log_y - log_y_pred

    # Calculate the standard deviation of residuals
    std_residuals = np.std(residuals)

    # print(f"Standard Deviation of Residuals: {std_residuals:.4f}")

    # Compute Z-scores
    z_scores = residuals / std_residuals

    # ----------------------------
    # Step 7: Plot Z-scores and BTC Prices Against Dates
    # ----------------------------

    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot Z-scores on the primary y-axis
    color_z = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Z-score', color=color_z)
    z_plot, = ax1.plot(dates, z_scores, color=color_z, linewidth=1, label='Z-score')
    ax1.tick_params(axis='y', labelcolor=color_z)

    # Add horizontal lines at Z=0, Z=1, and Z=-1
    ax1.axhline(0, color='black', linewidth=0.8, linestyle='-')
    ax1.axhline(1, color='red', linewidth=0.8, linestyle='--')
    ax1.axhline(-1, color='red', linewidth=0.8, linestyle='--')

    # Highlight points where |Z| > 2
    significant = np.abs(z_scores) > 2
    significant_dates = np.array(dates)[significant]
    significant_z = np.array(z_scores)[significant]
    scatter_z = ax1.scatter(significant_dates, significant_z, color='orange', label='|Z| > 2')

    # Create a secondary y-axis for BTC prices with logarithmic scale
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color_btc = 'tab:green'
    ax2.set_ylabel('Bitcoin Price (USD)', color=color_btc)  # we already handled the x-label with ax1
    btc_plot, = ax2.plot(dates, y_filtered, color=color_btc, linewidth=1, label='BTC Price')
    ax2.tick_params(axis='y', labelcolor=color_btc)

    # Set the secondary y-axis to logarithmic scale
    ax2.set_yscale('log')

    # Combine legends from both axes
    lines = [z_plot, btc_plot, scatter_z]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left')

    # Set the title
    plt.title('Z-score of Deviations from GL vs. BTC (log-log) 3rd-degree Polynomial Trend Line')

    # Format the x-axis to show dates nicely
    fig.autofmt_xdate()

    # Add grid to the primary y-axis
    ax1.grid(True, which="both", ls="--", linewidth=0.5)

    # Optionally, add R² value as text on the plot
    ax1.text(0.05, 0.95, f'$R^2 = {R_squared:.4f}$', transform=ax1.transAxes, fontsize=12, verticalalignment='top')

    # Adjust layout to prevent clipping
    fig.tight_layout()

    # Format Y-axis to display full numbers with commas
    ax2 = plt.gca()
    from matplotlib.ticker import FuncFormatter


    def y_fmt(x, pos):
        return '${:,.0f}'.format(x)


    ax2.yaxis.set_major_formatter(FuncFormatter(y_fmt))

    # Save the plot
    save_plot(fig, 'zscore_btc_prices')

    #################################################################################################
    ########################## Michael Howell's "Better Model" ######################################
    #################################################################################################

    bitcoin_prices = np.array(bitcoin_prices)
    gold_prices = np.array(gold_prices)
    global_liquidity = np.array(global_liquidity)
    bitcoin_prices_2019 = np.array(bitcoin_prices_2019)
    gold_prices_2019 = np.array(gold_prices_2019)

    assert len(bitcoin_prices) == len(gold_prices) == len(global_liquidity), "Data arrays must be of the same length."
    assert len(bitcoin_prices_2019) == len(gold_prices_2019), "Data arrays (2019) must be of the same length."

    # Log-transform the Bitcoin and gold prices
    log_bitcoin_prices_2019 = np.log(bitcoin_prices_2019)
    log_gold_prices_2019 = np.log(gold_prices_2019)

    # Linear Regression on Log-Log Data

    # Reshape data for sklearn
    X_log_gold = log_gold_prices_2019.reshape(-1, 1)
    y_log_bitcoin = log_bitcoin_prices_2019

    # Perform linear regression
    linear_model_log = LinearRegression()
    linear_model_log.fit(X_log_gold, y_log_bitcoin)
    y_pred_log_linear = linear_model_log.predict(X_log_gold)

    # Calculate R-squared
    r2_log_linear = r2_score(y_log_bitcoin, y_pred_log_linear)
    # print(f'Log-Log Linear Regression R^2: {r2_log_linear:.4f}')
    # print(f'Estimated Coefficient (Slope): {linear_model_log.coef_[0]:.4f}')
    # print(f'Estimated Intercept: {linear_model_log.intercept_:.4f}')

    # Log-transform the data
    log_global_liquidity = np.log(global_liquidity)
    log_gold_prices_gl = np.log(gold_prices)

    # Reshape data for sklearn
    X_log_gl = log_global_liquidity.reshape(-1, 1)
    y_log_gold = log_gold_prices_gl

    # Perform linear regression
    linear_model_gl = LinearRegression()
    linear_model_gl.fit(X_log_gl, y_log_gold)
    y_pred_gl = linear_model_gl.predict(X_log_gl)

    # Calculate R-squared
    r2_gl = r2_score(y_log_gold, y_pred_gl)
    loading_factor = linear_model_gl.coef_[0]
    # print(f'Gold vs. Global Liquidity Regression R^2: {r2_gl:.4f}')
    # print(f'Estimated Loading Factor (Slope): {loading_factor:.4f}')

    # Predict log(Gold Price) at GL = 350
    gl_target = 350  # Global Liquidity target in trillions
    log_gl_target = np.log(gl_target)
    log_gold_pred_target = linear_model_gl.predict([[log_gl_target]])
    gold_price_pred_target = np.exp(log_gold_pred_target)[0]
    # print(f'Predicted Gold Price at GL={gl_target}: ${gold_price_pred_target:,.2f}')

    # Predict log(Bitcoin Price) using log(Gold Price)
    log_gold_pred_target = np.log(gold_price_pred_target)
    log_bitcoin_pred_target = linear_model_log.predict([[log_gold_pred_target]])
    bitcoin_price_pred_target = np.exp(log_bitcoin_pred_target)[0]
    # print(f'Predicted Bitcoin Price at GL={gl_target}: ${bitcoin_price_pred_target:,.2f}')


    def predict_bitcoin_price(gl_value):
        # Step 1: Predict Gold Price
        log_gl_value = np.log(gl_value)
        log_gold_pred = linear_model_gl.predict([[log_gl_value]])
        gold_price_pred = np.exp(log_gold_pred)[0]

        # Step 2: Predict Bitcoin Price
        log_gold_pred = np.log(gold_price_pred)
        log_bitcoin_pred = linear_model_log.predict([[log_gold_pred]])
        bitcoin_price_pred = np.exp(log_bitcoin_pred)[0]

        return bitcoin_price_pred, gold_price_pred


    # Define a range of Global Liquidity values
    gl_values = np.linspace(global_liquidity.min(), 350, 100)
    bitcoin_prices_pred = []
    gold_prices_pred = []

    for gl in gl_values:
        bitcoin_pred, gold_pred = predict_bitcoin_price(gl)
        bitcoin_prices_pred.append(bitcoin_pred)
        gold_prices_pred.append(gold_pred)

    # Plot Bitcoin Price vs. Global Liquidity
    plt.figure(figsize=(12, 6))
    plt.plot(gl_values, bitcoin_prices_pred, color='blue', label='Predicted Bitcoin Price')
    plt.xlabel('Global Liquidity ($ Trillions)')
    plt.ylabel('Bitcoin Price ($)')
    plt.title("Michael Howell's 'Better Model'")
    plt.legend()
    plt.grid(True)

    # Format Y-axis to display full numbers with commas
    ax = plt.gca()
    from matplotlib.ticker import FuncFormatter


    def y_fmt(x, pos):
        return '${:,.0f}'.format(x)


    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))

    # Save the plot
    save_plot(plt, 'michael_howell_better_model')

    #################################################################################################
    ################### Michael Howell's "Better Model" with BTC vs. GL #############################
    #################################################################################################

    # Ensure data alignment and positivity
    mask = (bitcoin_prices > 0) & (gold_prices > 0) & (global_liquidity > 0)
    bitcoin_prices_filtered = bitcoin_prices[mask]
    gold_prices_filtered = gold_prices[mask]
    global_liquidity_filtered = global_liquidity[mask]

    # Log-transform the Bitcoin and gold prices for regression
    log_bitcoin_prices_2019 = np.log(bitcoin_prices_2019)
    log_gold_prices_2019 = np.log(gold_prices_2019)

    # Linear Regression on Log-Log Data for Bitcoin vs. Gold Price
    X_log_gold = log_gold_prices_2019.reshape(-1, 1)
    y_log_bitcoin = log_bitcoin_prices_2019
    linear_model_log = LinearRegression()
    linear_model_log.fit(X_log_gold, y_log_bitcoin)

    # Linear Regression on Log-Log Data for Gold Price vs. Global Liquidity
    log_global_liquidity = np.log(global_liquidity)
    log_gold_prices_gl = np.log(gold_prices)
    X_log_gl = log_global_liquidity.reshape(-1, 1)
    y_log_gold = log_gold_prices_gl
    linear_model_gl = LinearRegression()
    linear_model_gl.fit(X_log_gl, y_log_gold)


    # Define the prediction function
    def predict_bitcoin_price(gl_value):
        # Ensure gl_value is a scalar
        gl_value = np.atleast_1d(gl_value).astype(float)[0]
        # Step 1: Predict Gold Price
        log_gl_value = np.log(gl_value)
        log_gold_pred = linear_model_gl.predict([[log_gl_value]])
        gold_price_pred = np.exp(log_gold_pred)[0]
        # Step 2: Predict Bitcoin Price
        log_bitcoin_pred = linear_model_log.predict([[log_gold_pred[0]]])
        bitcoin_price_pred = np.exp(log_bitcoin_pred)[0]
        return bitcoin_price_pred, gold_price_pred


    # Define a range of Global Liquidity values for prediction
    gl_min = global_liquidity_filtered.min()
    gl_max = 350  # As per your requirement
    gl_values = np.logspace(np.log10(gl_min), np.log10(gl_max), 1000)

    # Generate predicted Bitcoin prices
    bitcoin_prices_pred = []
    for gl in gl_values:
        bitcoin_pred, _ = predict_bitcoin_price(gl)
        bitcoin_prices_pred.append(bitcoin_pred)
    bitcoin_prices_pred = np.array(bitcoin_prices_pred)

    # Plot Bitcoin Price vs. Global Liquidity
    plt.figure(figsize=(12, 6))

    # Plot actual data points
    plt.scatter(global_liquidity_filtered, bitcoin_prices_filtered, alpha=0.7, label='Actual Bitcoin Prices')

    # Plot predicted Bitcoin prices
    plt.plot(gl_values, bitcoin_prices_pred, color='blue', label='Predicted Bitcoin Price')

    # Set logarithmic scale for both axes
    plt.xscale('log')
    plt.yscale('log')

    # Set labels and title
    plt.xlabel('Global Liquidity ($ Trillions)')
    plt.ylabel('Bitcoin Price ($)')
    plt.title('Bitcoin Price vs. Global Liquidity (inc. MH Better Model)')
    plt.legend()

    # Get current axes
    ax = plt.gca()

    # Set major ticks for X-axis at 100, 200, 300, ..., up to 1000
    x_major_ticks = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    ax.xaxis.set_major_locator(FixedLocator(x_major_ticks))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: '${:,.0f}T'.format(val)))

    # Set minor ticks for X-axis between major ticks
    x_minor_ticks = []
    # Between 100 and 200
    x_minor_ticks.extend(range(110, 200, 10))
    # Between 200 and 300
    x_minor_ticks.extend(range(210, 300, 10))
    # Continue as needed
    for start in range(300, 1000, 100):
        x_minor_ticks.extend(range(start + 10, start + 100, 10))
    ax.xaxis.set_minor_locator(FixedLocator(x_minor_ticks))
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda val, pos: '${:,.0f}T'.format(val)))

    # Set major ticks for Y-axis at 1,000, 10,000, 100,000
    y_major_ticks = [1000, 10000, 100000, 1000000]
    ax.yaxis.set_major_locator(FixedLocator(y_major_ticks))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: '${:,.0f}'.format(val)))

    # Set minor ticks for Y-axis between major ticks
    # y_minor_ticks = []
    # Between 1,000 and 10,000
    # y_minor_ticks.extend(range(2000, 10000, 1000))
    # Between 10,000 and 100,000
    # y_minor_ticks.extend(range(20000, 100000, 10000))
    # Between 10,000 and 100,000
    # y_minor_ticks.extend(range(200000, 1000000, 100000))
    # ax.yaxis.set_minor_locator(FixedLocator(y_minor_ticks))
    # ax.yaxis.set_minor_formatter(FuncFormatter(lambda val, pos: '${:,.0f}'.format(val)))

    # Add gridlines
    ax.grid(which='major', color='gray', linewidth=1.0)
    ax.grid(which='minor', color='lightgray', linestyle='--', linewidth=0.5)

    # Rotate tick labels for better readability
    plt.setp(ax.get_xmajorticklabels(), rotation=0, fontsize=10)
    plt.setp(ax.get_xminorticklabels(), rotation=90, fontsize=8)
    plt.setp(ax.get_yminorticklabels(), fontsize=8)

    plt.tight_layout()

    # Save the plot
    save_plot(plt, 'btc_vs_gl_better_model')

    #################################################################################################
    ################### Michael Howell's "Better Model" Valuation ###################################
    #################################################################################################

    # ----------------------------
    # Step 2: Ensure Data Alignment and Positivity
    # ----------------------------

    # Convert data lists to NumPy arrays
    bitcoin_prices = np.array(bitcoin_prices_2018)
    gold_prices = np.array(gold_prices_2018)
    global_liquidity = np.array(global_liquidity_2018)
    bitcoin_prices_2019 = np.array(bitcoin_prices_2019)
    gold_prices_2019 = np.array(gold_prices_2019)

    # Ensure data alignment and positivity
    mask = (bitcoin_prices > 0) & (gold_prices > 0) & (global_liquidity > 0)
    bitcoin_prices_filtered = bitcoin_prices[mask]
    gold_prices_filtered = gold_prices[mask]
    global_liquidity_filtered = global_liquidity[mask]
    dates_filtered = [date for i, date in enumerate(dates_2018) if mask[i]]  # Adjust dates accordingly

    # Verify that the dates array aligns with the filtered data
    if len(bitcoin_prices_filtered) != len(dates_filtered):
        raise ValueError("Length of filtered bitcoin prices and dates do not match.")

    # print(
    #     f"After filtering - Length of Bitcoin Prices: {len(bitcoin_prices_filtered)}, Length of Dates: {len(dates_filtered)}")

    # ----------------------------
    # Step 3: Log-transform the Data for Regression
    # ----------------------------

    # Log-transform the Bitcoin and Gold prices for regression
    log_bitcoin_prices_2019 = np.log(bitcoin_prices_2019)
    log_gold_prices_2019 = np.log(gold_prices_2019)

    # Log-transform the Global Liquidity and Gold Prices for regression
    log_global_liquidity = np.log(global_liquidity_filtered)
    log_gold_prices_gl = np.log(gold_prices_filtered)

    # ----------------------------
    # Step 4: Perform Linear Regression
    # ----------------------------

    # Linear Regression on Log-Log Data for Gold Price vs. Global Liquidity
    X_log_gl = log_global_liquidity.reshape(-1, 1)
    y_log_gold = log_gold_prices_gl
    linear_model_gl = LinearRegression()
    linear_model_gl.fit(X_log_gl, y_log_gold)

    # Linear Regression on Log-Log Data for Bitcoin Price vs. Gold Price
    X_log_gold = log_gold_prices_2019.reshape(-1, 1)
    y_log_bitcoin = log_bitcoin_prices_2019
    linear_model_log = LinearRegression()
    linear_model_log.fit(X_log_gold, y_log_bitcoin)


    # ----------------------------
    # Step 5: Predict Bitcoin Prices for Actual Data Points
    # ----------------------------

    def predict_bitcoin_price(gl_value):
        """
        Predicts Bitcoin price based on Global Liquidity using the two-step regression model.
        Returns both predicted Bitcoin price and predicted Gold price.
        """
        # Predict log(Gold Price) from log(Global Liquidity)
        log_gl_value = np.log(gl_value)
        log_gold_pred = linear_model_gl.predict([[log_gl_value]])[0]

        # Predict log(Bitcoin Price) from log(Gold Price)
        log_bitcoin_pred = linear_model_log.predict([[log_gold_pred]])[0]

        # Convert back to original scale
        gold_price_pred = np.exp(log_gold_pred)
        bitcoin_price_pred = np.exp(log_bitcoin_pred)

        return bitcoin_price_pred, gold_price_pred


    # Generate predicted Bitcoin prices for the actual Global Liquidity data points
    bitcoin_prices_pred = []
    for gl in global_liquidity_filtered:
        btc_pred, _ = predict_bitcoin_price(gl)
        bitcoin_prices_pred.append(btc_pred)
    bitcoin_prices_pred = np.array(bitcoin_prices_pred)

    # ----------------------------
    # Step 6: Calculate Residuals and Z-scores
    # ----------------------------

    # Log-transform actual and predicted Bitcoin prices
    log_bitcoin_actual = np.log(bitcoin_prices_filtered)
    log_bitcoin_pred = np.log(bitcoin_prices_pred)

    # Calculate residuals
    residuals = log_bitcoin_actual - log_bitcoin_pred

    # Calculate standard deviation of residuals
    std_residuals = np.std(residuals)
    # print(f"Standard Deviation of Residuals: {std_residuals:.4f}")

    if std_residuals == 0:
        raise ValueError("Standard deviation of residuals is zero. Z-scores cannot be computed.")

    # Calculate Z-scores
    z_scores = residuals / std_residuals

    # ----------------------------
    # Step 7: Plot Z-scores and BTC Prices Against Dates
    # ----------------------------

    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot Z-scores on the primary y-axis
    color_z = 'tab:green'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Z-score', color=color_z)
    z_plot, = ax1.plot(dates_filtered, z_scores, color=color_z, linewidth=1, label='Z-scores')
    ax1.tick_params(axis='y', labelcolor=color_z)

    # Add horizontal lines at Z=0, Z=1, and Z=-1
    ax1.axhline(0, color='black', linewidth=0.8, linestyle='-')
    ax1.axhline(1, color='red', linewidth=0.8, linestyle='--')
    ax1.axhline(-1, color='red', linewidth=0.8, linestyle='--')

    # Highlight points where |Z| > 2
    significant = np.abs(z_scores) > 2
    significant_dates = np.array(dates_filtered)[significant]
    significant_z = np.array(z_scores)[significant]
    scatter_z = ax1.scatter(significant_dates, significant_z, color='orange', label='|Z| > 2')

    # Create a secondary y-axis for BTC prices with logarithmic scale
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color_btc = 'tab:blue'
    ax2.set_ylabel('Bitcoin Price (USD)', color=color_btc)  # we already handled the x-label with ax1
    btc_plot, = ax2.plot(dates_filtered, bitcoin_prices_filtered, color=color_btc, linewidth=1, label='BTC Price')
    ax2.tick_params(axis='y', labelcolor=color_btc)

    # Set the secondary y-axis to logarithmic scale
    ax2.set_yscale('log')

    # Combine legends from both axes
    lines = [z_plot, btc_plot, scatter_z]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left')

    # Set the title
    plt.title("Michael Howell's 'Better Model' Valuation")

    # Format the x-axis to show dates nicely
    fig.autofmt_xdate()

    # Add grid to the primary y-axis
    ax1.grid(True, which="both", ls="--", linewidth=0.5)

    # Optionally, add R² value as text on the plot
    # Calculate R-squared for the two-step regression model
    # First, predict log_bitcoin_pred for all data points
    # Since we have the residuals and std_residuals, we can compute R-squared
    SS_res = np.sum(residuals ** 2)
    SS_tot = np.sum((log_bitcoin_actual - np.mean(log_bitcoin_actual)) ** 2)
    R_squared = 1 - (SS_res / SS_tot)

    ax1.text(0.05, 0.95, f'$R^2 = {R_squared:.4f}$', transform=ax1.transAxes, fontsize=12, verticalalignment='top')

    # Adjust layout to prevent clipping
    fig.tight_layout()

    # Format Y-axis to display full numbers with commas
    ax = plt.gca()
    from matplotlib.ticker import FuncFormatter


    def y_fmt(x, pos):
        return '${:,.0f}'.format(x)


    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))

    # Save the plot
    save_plot(fig, 'zscore_btc_prices_valuation')

