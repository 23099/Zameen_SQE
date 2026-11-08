# test_favourites.py -- TC07 and TC08 (Favourites)
import os
import re
import time
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)

# Re-use the helpers that already work in the other files
from test_login_inquiry import driver, open_login_form, login
from test_continue_browsing import (
    login_user, open_results_page, get_property_links, find_heart_button,
    open_favourites, get_favourite_property_paths, wait_for_page,
)

ADDED_TOAST = "added to favourites"

# TC08B needs a SECOND test account that never saves anything.
# Register it by hand once, then set these two environment variables.
EMPTY_EMAIL = os.getenv("EMPTY_FAV_EMAIL", "")
EMPTY_PASSWORD = os.getenv("EMPTY_FAV_PASSWORD", "")

# Copy the empty-page wording from the manual check, e.g. "no favourites".
# While it is None, TC08B only checks that nothing is saved.
EMPTY_STATE_TEXT = None


# ---------------- helpers ----------------

def page_text(driver):
    return driver.execute_script("return document.body.innerText;").lower()


def path_key(url):
    return urlparse(url).path.rstrip("/").lower()


def click_heart(driver, property_url):
    button = find_heart_button(driver, property_url)
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", button
    )
    time.sleep(0.5)
    try:
        button.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", button)


def wait_for_text(driver, text, timeout=8):
    WebDriverWait(driver, timeout, poll_frequency=0.2).until(
        lambda d: text in page_text(d)
    )


def wait_until_gone(driver, text, timeout=10):
    try:
        WebDriverWait(driver, timeout, poll_frequency=0.3).until(
            lambda d: text not in page_text(d)
        )
    except TimeoutException:
        pass


def favourites_count(driver):
    """Number shown in the avatar menu, e.g. 'Favourites (2)'. None if unreadable."""
    try:
        avatar = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.zh-dropdown-trigger")
            )
        )
        avatar.click()

        def read(d):
            m = re.search(r"favou?rites\s*\((\d+)\)", page_text(d))
            return m.group(1) if m else False   # "0" is truthy, 0 would not be

        count = int(WebDriverWait(driver, 10).until(read))
        try:
            avatar.click()                      # close the menu again
        except Exception:
            pass
        return count
    except TimeoutException:
        return None


def remove_favourites(driver, urls):
    """Un-save properties this test saved, so the next run starts clean."""
    for url in urls:
        for open_page in (open_favourites, open_results_page):
            try:
                open_page(driver)
                click_heart(driver, url)
                time.sleep(2)
                break
            except Exception:
                continue
        else:
            print(f"WARNING: could not un-save {url} - remove it by hand")


# ---------------- TC07: favourites, valid ----------------

def test_TC07_favourites_valid(driver):

    login_user(driver)

    open_favourites(driver)
    existing = get_favourite_property_paths(driver)
    count_before = favourites_count(driver)

    open_results_page(driver)
    candidates = [
        url for url in get_property_links(driver)
        if path_key(url) not in existing
    ]
    assert len(candidates) >= 2, "Need two properties that are not saved yet"
    prop_a, prop_b = candidates[0], candidates[1]

    saved = []
    try:
        click_heart(driver, prop_a)
        saved.append(prop_a)
        wait_for_text(driver, ADDED_TOAST)
        wait_until_gone(driver, ADDED_TOAST)

        click_heart(driver, prop_b)
        saved.append(prop_b)
        wait_for_text(driver, ADDED_TOAST)

        open_favourites(driver)
        in_list = get_favourite_property_paths(driver)

        assert path_key(prop_a) in in_list, f"A missing from Favourites: {prop_a}"
        assert path_key(prop_b) in in_list, f"B missing from Favourites: {prop_b}"

        count_after = favourites_count(driver)
        if count_before is not None and count_after is not None:
            assert count_after == count_before + 2, (
                f"Favourites count went {count_before} -> {count_after}, expected +2"
            )
    finally:
        try:
            remove_favourites(driver, saved)
        except Exception as error:
            print("cleanup problem:", error)


# ---------------- TC08A: logged out, heart ----------------

def heart_icon_class(driver, property_url):
    """CSS class of the heart's <svg>; it changes when the heart is saved."""
    button = find_heart_button(driver, property_url)
    return button.find_element(By.TAG_NAME, "svg").get_attribute("class")


def test_TC08A_logged_out_heart_asks_for_login(driver):

    open_results_page(driver)
    property_url = get_property_links(driver)[0]

    class_before = heart_icon_class(driver, property_url)

    click_heart(driver, property_url)

    # The login pop-up opens
    WebDriverWait(driver, 15).until(
        lambda d: any(
            e.is_displayed() for e in d.find_elements(By.NAME, "email")
        )
    )
    assert "forgot password" in page_text(driver), "Login pop-up not shown"

    # Zameen shows an optimistic 'Added to Favourites' toast even for
    # guests, so the toast text cannot be used here. The real indicator
    # is the heart icon: it must NOT switch to its saved state.
    time.sleep(1)
    class_after = heart_icon_class(driver, property_url)

    assert class_after == class_before, (
        "Heart switched to the saved state although the user is logged out"
    )


# ---------------- TC08B: logged in, nothing saved ----------------

def test_TC08B_empty_favourites_state(driver):

    assert EMPTY_EMAIL and EMPTY_PASSWORD, (
        "Set EMPTY_FAV_EMAIL and EMPTY_FAV_PASSWORD for the 'never saves anything' account"
    )

    open_login_form(driver)
    login(driver, EMPTY_EMAIL, EMPTY_PASSWORD)
    time.sleep(3)
    wait_for_page(driver)

    open_favourites(driver)
    time.sleep(2)

    count = favourites_count(driver)
    if count is None:                       # fall back to counting listings
        count = len(get_favourite_property_paths(driver))

    assert count == 0, f"Expected an empty Favourites list, found {count}"

    if EMPTY_STATE_TEXT:
        assert EMPTY_STATE_TEXT.lower() in page_text(driver)

    # Run once with -s and copy this text into your report
    print("\nEMPTY STATE PAGE TEXT:", page_text(driver)[:400])