from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import time
import os

def extract_data(page):
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return page.evaluate(f"""
        () => {{
            const data = [];
            
            // Select all league blocks
            const leagues = document.querySelectorAll('#__BETTING_APP__ > div.default-layout-container > div > div > div.layout__main > main > div.betting-main.betting-content__main > div > div > div > div.betting-main-dashboard > div > ul > li');

            leagues.forEach((league) => {{
                // Extract league name
                const leagueName = league.querySelector('div.ui-dashboard-champ-name.dashboard-champ__name.ui-dashboard-cell.ui-dashboard-champ-name.dashboard-champ__name')?.innerText.trim() || 'Unknown';

                // Select all betting rows inside the league
                const bettingRows = league.querySelectorAll('ul > li');

                bettingRows.forEach((row) => {{
                    const team1 = row.querySelector('div.dashboard-game-block.dashboard-game__block.ui-dashboard-cell.dashboard-game-block.dashboard-game__block > span:nth-child(1) > a > span > span > span > div:nth-child(1) > div.team-score-name--nowrap.team-score-name > span > span')?.innerText.trim() || 'Unknown';
                    const team2 = row.querySelector('div.dashboard-game-block.dashboard-game__block.ui-dashboard-cell.dashboard-game-block.dashboard-game__block > span:nth-child(1) > a > span > span > span > div:nth-child(2) > div.team-score-name--nowrap.team-score-name > span > span')?.innerText.trim() || 'Unknown';
                    
                    // Extract all the odds (Odd 1, X, and 2)
                    const odd1 = row.querySelector('div.ui-dashboard-markets-cell.dashboard-markets.ui-dashboard-cell.ui-dashboard-markets-cell.dashboard-markets > span > button:nth-child(1) > span')?.innerText.trim() || 'Unknown';
                    const oddX = row.querySelector('div.ui-dashboard-markets-cell.dashboard-markets.ui-dashboard-cell.ui-dashboard-markets-cell.dashboard-markets > span > button:nth-child(2)')?.innerText.trim() || 'Unknown';
                    const odd2 = row.querySelector('div.ui-dashboard-markets-cell.dashboard-markets.ui-dashboard-cell.ui-dashboard-markets-cell.dashboard-markets > span > button:nth-child(3)')?.innerText.trim() || 'Unknown';

                    // Extract game score
                    const gameScore = row.querySelector('div.dashboard-game-block.dashboard-game__block.ui-dashboard-cell.dashboard-game-block.dashboard-game__block > span:nth-child(1) > a > span > span > div > span > span.game-scores__item.game-scores__item--total')?.innerText.trim() || 'Unknown';

                    // Add the data into an array
                    data.push({{
                        "timestamp": "{timestamp}",  // Add timestamp to each record
                        "league_name": leagueName,
                        "team_1": team1,
                        "team_2": team2,
                        "odd_1": odd1,
                        "odd_X": oddX,
                        "odd_2": odd2,
                        "game_score": gameScore  // Add the game score
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

def save_to_csv(data, filename='betting_data.csv'):
    if data:
        print(f"Attempting to save {len(data)} records.")
        
        # Check if file exists and whether it's empty
        file_exists = os.path.exists(filename)
        is_empty = os.stat(filename).st_size == 0 if file_exists else True
        
        keys = data[0].keys() if data else []
        with open(filename, 'a', newline='', encoding='utf-8') as output_file:  # 'a' mode for appending data
            dict_writer = csv.DictWriter(output_file, keys)
            
            # Write the header only if the file is new or empty
            if is_empty:
                dict_writer.writeheader()  
            
            dict_writer.writerows(data)
        
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
