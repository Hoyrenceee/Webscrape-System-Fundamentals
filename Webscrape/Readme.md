Starlink Daily Data Usage Scraper (Lab Work 1)
This application is a web scraper built with Python, Playwright, and Streamlit. It automates the extraction of seven months of daily data usage from the Starlink user dashboard and exports the data into a formatted .csv file via a web interface.

Technology Stack
Frontend: Streamlit
Backend: Playwright (Browser Automation), Pandas (Data Processing), Regex (Data Cleaning)

Language: Python

Execution Instructions

Install dependencies:
python -m pip install -r requirements.txt

Install automated browser binaries:
python -m playwright install

Launch the application:
python -m streamlit run app.py

Usage:

Click the "Start Webscraping" button in the interface.

Initial Run: A browser window will open. Manually log in using the provided credentials. The script will automatically save your session cookies.

Subsequent Runs: The script will load the saved session to bypass the login screen, navigate directly to the data graph, sequentially extract the data from November through June, and close the browser.