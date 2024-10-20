import csv
import os
from datetime import datetime
import time
from playwright.sync_api import sync_playwright

def extract_data(page):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return page.evaluate(f"""
        () => {{
            const data = [];
            const leagues = document.querySelectorAll('#__BETTING_APP__ > div.default-layout-container > div > div > div.layout__main > main > div.betting-main.betting-content__main > div > div > div > div.betting-main-dashboard > div > ul > li');
            
            leagues.forEach((league) => {{
                const leagueName = league.querySelector('div.ui-dashboard-champ-name.dashboard-champ__name.ui-dashboard-cell.ui-dashboard-champ-name.dashboard-champ__name')?.innerText.trim() || 'Unknown';
                const bettingRows = league.querySelectorAll('ul > li');

                bettingRows.forEach((row) => {{
                    const team1 = row.querySelector('div.dashboard-game-block.dashboard-game__block.ui-dashboard-cell.dashboard-game-block.dashboard-game__block > span:nth-child(1) > a > span > span > span > div:nth-child(1) > div.team-score-name--nowrap.team-score-name > span > span')?.innerText.trim() || 'Unknown';
                    const team2 = row.querySelector('div.dashboard-game-block.dashboard-game__block.ui-dashboard-cell.dashboard-game-block.dashboard-game__block > span:nth-child(1) > a > span > span > span > div:nth-child(2) > div.team-score-name--nowrap.team-score-name > span > span')?.innerText.trim() || 'Unknown';
                    const odd1 = row.querySelector('div.ui-dashboard-markets-cell.dashboard-markets.ui-dashboard-cell.ui-dashboard-markets-cell.dashboard-markets > span > button:nth-child(1) > span')?.innerText.trim() || 'Unknown';
                    const oddX = row.querySelector('div.ui-dashboard-markets-cell.dashboard-markets.ui-dashboard-cell.ui-dashboard-markets-cell.dashboard-markets > span > button:nth-child(2)')?.innerText.trim() || 'Unknown';
                    const odd2 = row.querySelector('div.ui-dashboard-markets-cell.dashboard-markets.ui-dashboard-cell.ui-dashboard-markets-cell.dashboard-markets > span > button:nth-child(3)')?.innerText.trim() || 'Unknown';
                    const gameScore = row.querySelector('div.dashboard-game-block.dashboard-game__block.ui-dashboard-cell.dashboard-game-block.dashboard-game__block > span:nth-child(1) > a > span > span > div > span > span.game-scores__item.game-scores__item--total')?.innerText.trim() || 'Unknown';

                    data.push({{
                        "timestamp": "{timestamp}",
                        "league_name": leagueName,
                        "team_1": team1,
                        "team_2": team2,
                        "odd_1": odd1,
                        "odd_X": oddX,
                        "odd_2": odd2,
                        "game_score": gameScore
                    }});
                }}); 
            }});

            return data;
        }}
    """)

def intercept_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://fun88if.top/en/live", wait_until="networkidle")
        raw_data = extract_data(page)
        browser.close()
        return raw_data

def read_existing_data(filename):
    """Reads the existing data from the CSV if it exists."""
    existing_data = []
    if os.path.exists(filename):
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            dict_reader = csv.DictReader(file)
            existing_data = list(dict_reader)
    return existing_data

def save_to_csv(data, filename='betting_data.csv'):
    if data:
        print(f"Attempting to save {len(data)} records.")
        
        # Read existing data
        existing_data = read_existing_data(filename)

        # Combine existing data with the new data
        combined_data = existing_data + data

        # Sort combined data by 'league_name'
        sorted_data = sorted(combined_data, key=lambda x: x['league_name'])

        # Write the sorted data back to the CSV file (overwrite mode)
        keys = sorted_data[0].keys() if sorted_data else []
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(sorted_data)

        print(f"Data successfully saved to {filename}.")
    else:
        print("No data collected to save.")

if __name__ == "__main__":
    try:
        while True:
            print(f"Scraping data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            data = intercept_data()
            save_to_csv(data)
            
            # Sleep for a fixed 30 seconds before the next scrape
            time_to_sleep = 30
            print(f"Sleeping for {time_to_sleep} seconds.")
            time.sleep(time_to_sleep)
            
    except KeyboardInterrupt:
        print("Scraping interrupted by user.")