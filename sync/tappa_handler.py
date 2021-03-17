from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import json
import time
from datetime import datetime, timezone, timedelta


def print_status(category, msg):
    print("[%s] %s" % (category, msg), flush=True)

def update_data(driver, username, password, folder="/data/"):
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
    sleep(3)

    print_status("DATA", "Opening table")
    showall_button = driver.find_element_by_css_selector(".btn.btn-tappa.showall")
    showall_button.click()

    # Wait for window to load
    sleep(1)

    def hover_el(el):
        hover = ActionChains(driver).move_to_element(el)
        hover.perform()

    print_status("DATA", "Iterating over result")
    result = []
    rows = driver.find_elements_by_css_selector(".modal-dialog table.tappa-toplist tbody tr:not(.nodelete)")
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
    out_file = "%s/result.json" % folder
    save_data = {
        "timestamp": int(time.time()),
        "players": result
    }
    with open(out_file, "w") as out:
        json.dump(save_data, out, indent=4)
    print_status("SAVE", "File written to %s" % out_file)

    one_hour_ago = (datetime.now(timezone(timedelta(hours=1))) - timedelta(hours=1))
    daily_file = "%s/%s.json" % (folder, one_hour_ago.strftime("%Y%m%d"))
    with open(daily_file, "w") as out:
        json.dump(save_data, out, indent=4)
    print_status("SAVE", "Saved to daily file as well")
