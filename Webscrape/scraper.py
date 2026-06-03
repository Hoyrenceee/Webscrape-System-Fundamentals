from playwright.sync_api import sync_playwright
from datetime import datetime
import csv
import os
import re

def scrape_starlink_data():
    CSV_FILENAME = "data_usage.csv"
    STATE_FILE = "starlink_state.json" 

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, 
            channel="chrome", 
            args=['--disable-blink-features=AutomationControlled']
        )
        
        if os.path.exists(STATE_FILE):
            print("Saved session found! Bypassing the login screen...")
            context = browser.new_context(storage_state=STATE_FILE)
            needs_login = False
        else:
            print("No saved session. You must log in manually this one time.")
            context = browser.new_context()
            needs_login = True

        page = context.new_page()

        try:
            # DIRECT NAVIGATION USING TARGET METRIC LINK
            target_url = "https://starlink.com/account/service-line/AST-2293597-46342-54?selectedDevice=ut01000000-00000000-0060d786&page=0&limit=5"
            
            if needs_login:
                page.goto(target_url)
                print("Waiting up to 5 minutes for manual login...")
                # Wait for the data elements of the dashboard to confirm authenticated view
                page.wait_for_selector('rect.MuiBarElement-series-y_0', timeout=300000)
                context.storage_state(path=STATE_FILE)
                print("Session successfully saved for future runs!")
            else:
                page.goto(target_url)
            
            print("Waiting for data usage graph to load...")
            page.wait_for_selector('rect.MuiBarElement-series-y_0', timeout=60000)
            page.wait_for_timeout(2000) 
            
            print("Graph detected! Scraping data layers...")
            extracted_data = []
            
            # FIXED: Added 'Dec' back into your execution roadmap array
            months_to_scrape = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

            for month in months_to_scrape:
                print(f"Loading data for {month}...")
                try:
                    page.get_by_role("button", name=month, exact=True).click(timeout=5000)
                    page.wait_for_timeout(2000) 
                except Exception:
                    print(f"Could not find or click {month}. Skipping to next.")
                    continue

                chart_bars = page.locator('rect.MuiBarElement-series-y_0').all()
                
                if chart_bars:
                    for bar in chart_bars:
                        try:
                            bar.hover(force=True, timeout=1000) 
                            tooltip = page.locator('*[role="tooltip"]')
                            tooltip_text = tooltip.inner_text(timeout=1000)
                            
                            lines = tooltip_text.split('\n')
                            
                            if len(lines) >= 2:
                                raw_date = lines[0].strip()
                                raw_usage = lines[1].strip()
                                
                                try:
                                    parsed_date = datetime.strptime(raw_date, "%b %d")
                                    year = 2025 if parsed_date.month >= 11 else 2026
                                    clean_date = f"{year}-{parsed_date.month:02d}-{parsed_date.day:02d}"
                                except Exception:
                                    clean_date = raw_date

                                match = re.search(r"[\d\.]+", raw_usage)
                                clean_usage = match.group(0) if match else raw_usage
                                data_row = [clean_date, clean_usage]
                            else:
                                data_row = [tooltip_text, ""]
                                
                            if data_row not in extracted_data:
                                extracted_data.append(data_row)
                                
                        except Exception:
                            continue

            if not extracted_data:
                extracted_data.append(["No Data", "Could not read any graph bars."])
                
            with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Data Usage (GB)']) 
                writer.writerows(extracted_data)
                
            return True, "Scraping completed successfully! Clean CSV generated."

        except Exception as e:
            return False, f"An execution boundary error occurred: {str(e)}"
            
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_starlink_data()