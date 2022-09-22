from selenium.webdriver.common.action_chains import ActionChains
from time import sleep, time
import json
import os
from datetime import datetime, timezone, timedelta
import sqlite3

DATA_FOLDER = os.environ.get("DATA_FOLDER", "/data/")
DB_FILE = os.environ.get("DB_FILE", "/data/data.db")

def print_status(category, msg):
    print("[%s] %s" % (category, msg), flush=True)

def update_data(driver, username, password):
    driver.get("https://tappa.se")
    assert("Tappa.se" in driver.title)

    # Open login prompt
    driver.find_element_by_css_selector(".login.dropdown-content-handling > a").click()

    # Wait for elements to load
    print_status("LOGIN", "Wait for login elements to load...")
    sleep(1)

    # Expand login form
    print_status("LOGIN", "Getting input fields field")
    input_fields = driver.find_elements_by_css_selector(".login.dropdown-content-handling form input.form-control")
    print_status("LOGIN", "Found %d input fields" % len(input_fields))
    username_field = input_fields[0]
    pw_field = input_fields[1]
    print_status("LOGIN", "Getting submit button")
    submit_button = driver.find_element_by_css_selector(".login.dropdown-content-handling form button")

    username_field.clear()
    username_field.send_keys(username)
    pw_field.clear()
    pw_field.send_keys(password)
    submit_button.click()

    # Wait for all to load
    print_status("LOGIN", "Waiting for login...")
    sleep(2)
    
    print_status("DATA", "Going to tab Topplistor")  # 5th tab, since first is invis
    tab_link = driver.find_element_by_css_selector(".tappa-nav-tabs li:nth-child(5) a")
    tab_link.click()

    sleep(5)
    
    print_status("DATA", "Opening table")
    showall_buttons = driver.find_elements_by_css_selector(".btn.btn-tappa.showall")
    if len(showall_buttons) != 4:
        print("Unexpected number of 'showall' buttons ({} but expected 4)".format(len(showall_buttons)))
    showall_buttons[3].click()
    
    sleep(2)
    
    org_results = []
    rows = driver.find_elements_by_css_selector(".modal.fade.in .modal-dialog table.tappa-toplist tbody tr:not(.nodelete)")
    for row in rows:
        cells = row.find_elements_by_css_selector("td")
        org_results.append({
            "name": cells[1].text,
            "steps": int(cells[2].text),
            "distance": float(cells[3].text)
        })
        print_status("DATA", "Added organisation %s" % cells[1].text)
    
    close_button = driver.find_element_by_css_selector(".modal.fade.in .modal-header button")
    close_button.click()
    
    sleep(4)

    print_status("DATA", "Going to tab Avdelning")  # 6th tab, since first is invis
    tab_link = driver.find_element_by_css_selector(".tappa-nav-tabs li:nth-child(6) a")
    tab_link.click()

    sleep(5)

    print_status("DATA", "Opening table")
    showall_buttons = driver.find_elements_by_css_selector(".btn.btn-tappa.showall")
    if len(showall_buttons) != 6:
        print("Unexpected number of 'showall' buttons ({} but expected 6)".format(len(showall_buttons)))
    showall_buttons[4].click()

    # Wait for window to load
    sleep(2)

    def hover_el(el):
        hover = ActionChains(driver).move_to_element(el)
        hover.perform()

    print_status("DATA", "Iterating over result")
    result = []
    rows = driver.find_elements_by_css_selector(".modal.fade.in .modal-dialog table.tappa-toplist tbody tr:not(.nodelete)")
    for row in rows:
        # Load team tooltip
        hover_el(row)
        sleep(1)

        # Try to get team
        try:
            tooltip_id = row.get_attribute("aria-describedby")
            tooltip = driver.find_element_by_id(tooltip_id)
            team = tooltip.find_element_by_css_selector(".popover-content div p").text
        except:
            team = None

        # Summarize data
        cells = row.find_elements_by_css_selector("td")
        result.append({
            "name": cells[1].text,
            "steps": int(cells[2].text),
            "distance": float(cells[3].text),
            "team": team
        })
        print_status("DATA", "Added player %s" % cells[1].text)

    print_status("SAVE", "Writing data to file")
    save_data = {
        "timestamp": int(time()),
        "players": result,
        "organistaions": org_results
    }

    store_data(save_data)

def store_data(data):
    store_data_to_file(data)
    store_data_to_db(data)

def store_data_to_file(data):
    out_file = "%s/result.json" % DATA_FOLDER
    with open(out_file, "w") as out:
        json.dump(data, out, indent=4)
    print_status("SAVE", "File written to %s" % out_file)

    one_hour_ago = (datetime.now(timezone(timedelta(hours=1))) - timedelta(hours=1))
    daily_file = "%s/%s.json" % (DATA_FOLDER, one_hour_ago.strftime("%Y%m%d"))
    with open(daily_file, "w") as out:
        json.dump(data, out, indent=4)
    print_status("SAVE", "Saved to daily file as well")

def store_data_to_db(data):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            team TEXT
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            steps INTEGER,
            distance INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS org (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orgstats (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            org_id INTEGER,
            steps INTEGER,
            distance INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    name_to_user_id = {}
    users = conn.execute("SELECT id, name FROM user")
    for user_id, name in users:
        name_to_user_id[name] = user_id
        
    org_name_to_id = {}
    orgs = conn.execute("SELECT id, name FROM org")
    for org_id, name in orgs:
        org_name_to_id[name] = org_id

    for player in data["players"]:
        name = player["name"]
        if name not in name_to_user_id:
            print("Creating user with name {} in DB".format(name))
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user (name, team) VALUES (?, ?)", (name, player["team"]))
            name_to_user_id[name] = cursor.lastrowid

        user_id = name_to_user_id[name]
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stats (user_id, steps, distance) VALUES (?, ?, ?)", (user_id, player["steps"], int(player["distance"]*1000)))
        
    for org in data["organistaions"]:
        name = org["name"]
        if name not in org_name_to_id:
            print("Creating org with name {} in DB".format(name))
            cursor = conn.cursor()
            cursor.execute("INSERT INTO org (name) VALUES (?)", (name,))
            org_name_to_id[name] = cursor.lastrowid
        org_id = org_name_to_id[name]
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orgstats (org_id, steps, distance) VALUES (?, ?, ?)", (org_id, org["steps"], int(1000*org["distance"])))
    conn.commit()
    
    print_status("SAVE", "Saved to database")

# SELECT U.name as name, U.team AS team, MAX(S.steps) as steps, MAX(S.distance) as distance FROM user U LEFT JOIN stats S ON S.user_id = U.id GROUP BY U.id;

