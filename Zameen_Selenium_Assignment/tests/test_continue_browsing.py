
# import pytest
# import time
# from urllib.parse import urlparse, urljoin

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import (
#     TimeoutException,
#     StaleElementReferenceException,
#     ElementClickInterceptedException,
# )

# from test_login_inquiry import (
#     driver,
#     open_login_form,
#     login,
#     TEST_EMAIL,
#     TEST_PASSWORD,
# )


# BASE_URL = "https://www.zameen.com/"
# LISTING_URL = "https://www.zameen.com/Homes/Lahore-1-1.html"


# # =========================================================
# # COMMON HELPERS
# # =========================================================

# def wait_for_page(driver, timeout=25):
#     WebDriverWait(driver, timeout).until(
#         lambda d: d.execute_script(
#             "return document.readyState"
#         ) == "complete"
#     )


# def wait_for_results(driver):
#     WebDriverWait(driver, 25).until(
#         EC.presence_of_element_located(
#             (By.XPATH, "//a[contains(@href, '/Property/')]")
#         )
#     )


# def login_user(driver):
#     open_login_form(driver)
#     login(driver, TEST_EMAIL, TEST_PASSWORD)

#     time.sleep(3)
#     wait_for_page(driver)

#     login_fields = driver.find_elements(By.NAME, "email")

#     if any(field.is_displayed() for field in login_fields):
#         raise AssertionError(
#             "Login was not successful. Login form is still visible."
#         )


# def open_results_page(driver):
#     driver.get(LISTING_URL)
#     wait_for_page(driver)
#     wait_for_results(driver)
#     time.sleep(3)


# def get_property_links(driver):
#     """Return unique direct Zameen property detail URLs only."""

#     links = driver.find_elements(
#         By.XPATH,
#         "//a[contains(@href, '/Property/')]"
#     )

#     urls = []

#     for link in links:
#         try:
#             href = link.get_attribute("href")

#             if not href:
#                 continue

#             # Convert relative URLs to absolute URLs
#             full_url = urljoin(driver.current_url, href)
#             parsed = urlparse(full_url)

#             # Exclude Facebook, WhatsApp, Twitter and other share URLs
#             if (
#                 parsed.hostname
#                 and parsed.hostname.lower() in {
#                     "zameen.com",
#                     "www.zameen.com"
#                 }
#                 and parsed.path.startswith("/Property/")
#                 and full_url not in urls
#             ):
#                 urls.append(full_url)

#         except StaleElementReferenceException:
#             continue

#     if len(urls) < 2:
#         raise AssertionError(
#             f"Expected at least 2 direct property URLs, found {len(urls)}: {urls}"
#         )

#     print("\nDirect property URLs found:")
#     for url in urls[:5]:
#         print(url)

#     return urls


# def get_page_text(driver):
#     return driver.find_element(
#         By.TAG_NAME, "body"
#     ).text.lower()


# # =========================================================
# # FAVOURITE HEART HELPERS
# # =========================================================

# def find_property_card(driver, property_url):

#     target_path = urlparse(property_url).path.rstrip("/")

#     links = driver.find_elements(
#         By.XPATH,
#         "//a[contains(@href, '/Property/')]"
#     )

#     target = None

#     for link in links:
#         try:
#             href = link.get_attribute("href")

#             if not href:
#                 continue

#             full_url = urljoin(driver.current_url, href)
#             parsed = urlparse(full_url)

#             if (
#                 parsed.hostname
#                 and parsed.hostname.lower() in {
#                     "zameen.com",
#                     "www.zameen.com"
#                 }
#                 and parsed.path.rstrip("/") == target_path
#             ):
#                 target = link
#                 break

#         except StaleElementReferenceException:
#             continue

#     if target is None:
#         raise AssertionError(
#             f"Property link not found in listing card: {property_url}"
#         )

#     current = target

#     for _ in range(1, 15):
#         try:
#             current = current.find_element(By.XPATH, "..")

#             tag = current.tag_name.lower()
#             html = (
#                 current.get_attribute("innerHTML") or ""
#             ).lower()

#             if tag in ["article", "li"]:
#                 return current

#             if "<img" in html and (
#                 "button" in html or "role=" in html
#             ):
#                 return current

#         except StaleElementReferenceException:
#             break

#     raise AssertionError(
#         "Could not identify the property listing card."
#     )


# def find_heart_button(driver, property_url):

#     card = find_property_card(driver, property_url)

#     elements = card.find_elements(
#         By.XPATH,
#         ".//button | .//*[@role='button'] | .//a"
#     )

#     for element in elements:
#         try:
#             if not element.is_displayed():
#                 continue

#             aria = (
#                 element.get_attribute("aria-label") or ""
#             ).lower()

#             title = (
#                 element.get_attribute("title") or ""
#             ).lower()

#             html = (
#                 element.get_attribute("outerHTML") or ""
#             ).lower()

#             combined = aria + " " + title + " " + html

#             if any(word in combined for word in [
#                 "heart",
#                 "favorite",
#                 "favourite",
#                 "wishlist",
#                 "shortlist",
#                 "save"
#             ]):
#                 return element

#         except StaleElementReferenceException:
#             continue

#     # Try identifying the heart through SVG attributes
#     svgs = card.find_elements(
#         By.XPATH,
#         ".//*[name()='svg']"
#     )

#     for svg in svgs:
#         try:
#             if not svg.is_displayed():
#                 continue

#             svg_html = (
#                 svg.get_attribute("outerHTML") or ""
#             ).lower()

#             if any(word in svg_html for word in [
#                 "heart",
#                 "favorite",
#                 "favourite"
#             ]):
#                 parent = svg.find_element(
#                     By.XPATH,
#                     "./ancestor::*[self::button or @role='button' or self::a][1]"
#                 )

#                 if parent.is_displayed():
#                     return parent

#         except Exception:
#             continue

#     raise AssertionError(
#         "Heart button not identified inside the property card. "
#         "The website's actual heart HTML selector may be different."
#     )


# def click_favourite(driver, property_url):

#     button = find_heart_button(driver, property_url)

#     driver.execute_script(
#         "arguments[0].scrollIntoView({block:'center'});",
#         button
#     )

#     time.sleep(1)

#     try:
#         button.click()
#     except ElementClickInterceptedException:
#         driver.execute_script(
#             "arguments[0].click();",
#             button
#         )

#     time.sleep(2)


# # =========================================================
# # FAVOURITES PAGE HELPERS
# # =========================================================

# def open_favourites(driver):

#     driver.get("https://www.zameen.com/favorite-properties.html")

#     WebDriverWait(driver, 25).until(
#         lambda d: "favorite-properties" in d.current_url.lower()
#     )

#     WebDriverWait(driver, 25).until(
#         lambda d: d.execute_script(
#             "return document.readyState"
#         ) == "complete"
#     )

#     return driver

# def get_favourite_property_paths(driver):
#     """Get actual property links displayed on the Favourites page."""

#     links = driver.find_elements(
#         By.XPATH,
#         "//a[contains(@href, '/Property/')]"
#     )

#     paths = set()

#     for link in links:
#         try:
#             href = link.get_attribute("href")

#             if href:
#                 parsed = urlparse(urljoin(driver.current_url, href))

#                 if (
#                     parsed.hostname
#                     and parsed.hostname.lower() in {
#                         "zameen.com", "www.zameen.com"
#                     }
#                     and parsed.path.startswith("/Property/")
#                 ):
#                     paths.add(parsed.path.rstrip("/").lower())

#         except StaleElementReferenceException:
#             continue

#     return paths

# # =========================================================
# # PRICE FILTER HELPERS
# # =========================================================


# def set_price_filter(driver, minimum, maximum):

#     wait = WebDriverWait(driver, 20)

#     # Find the visible PRICE (PKR) label
#     price_label = wait.until(
#         EC.visibility_of_element_located((
#             By.XPATH,
#             "//*[normalize-space()='PRICE (PKR)' "
#             "or normalize-space()='Price (PKR)']"
#         ))
#     )

#     # Move upward until a container with two visible inputs is found
#     price_container = None
#     current = price_label

#     for _ in range(8):
#         try:
#             current = current.find_element(By.XPATH, "..")

#             inputs = current.find_elements(By.TAG_NAME, "input")

#             visible_inputs = [
#                 field for field in inputs
#                 if field.is_displayed() and field.is_enabled()
#             ]

#             if len(visible_inputs) >= 2:
#                 price_container = current
#                 break

#         except StaleElementReferenceException:
#             continue

#     if price_container is None:
#         raise AssertionError(
#             "Could not locate both inputs inside PRICE (PKR) section."
#         )

#     price_inputs = [
#         field for field in price_container.find_elements(
#             By.TAG_NAME, "input"
#         )
#         if field.is_displayed() and field.is_enabled()
#     ][:2]

#     # Enter minimum and maximum values
#     for field, value in zip(
#         price_inputs, [minimum, maximum]
#     ):
#         field.click()
#         field.send_keys(Keys.CONTROL, "a")
#         field.send_keys(str(value))
#         field.send_keys(Keys.TAB)

#     time.sleep(2)

#     # Click the Find button
#     find_button = wait.until(
#         EC.element_to_be_clickable((
#             By.XPATH,
#             "//button[contains(translate(normalize-space(.),"
#             "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
#             "'find')]"
#             " | //a[contains(translate(normalize-space(.),"
#             "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
#             "'find')]"
#         ))
#     )

#     driver.execute_script(
#         "arguments[0].click();", find_button
#     )

#     time.sleep(5)
#     wait_for_page(driver)

# # =========================================================
# # TC09: CONTINUE BROWSING - VALID
# # =========================================================

# def test_TC09_continue_browsing_valid(driver):

#     login_user(driver)

#     # Check existing favourites first
#     open_favourites(driver)
#     existing_favourites = get_favourite_property_paths(driver)

#     # Open Lahore Homes results
#     open_results_page(driver)

#     property_urls = get_property_links(driver)
#     property_c = property_urls[0]
#     property_d = property_urls[1]

#     path_c = urlparse(property_c).path.rstrip("/").lower()
#     path_d = urlparse(property_d).path.rstrip("/").lower()

#     # Add C only if it is not already a favourite
#     if path_c not in existing_favourites:
#         click_favourite(driver, property_c)

#     # Open C detail page
#     driver.get(property_c)
#     wait_for_page(driver)
#     time.sleep(3)

#     # Browser Back
#     driver.back()
#     wait_for_page(driver)
#     wait_for_results(driver)
#     time.sleep(3)

#     assert "/Homes/Lahore-1-1.html" in driver.current_url, (
#         f"Browser Back did not return to results page: {driver.current_url}"
#     )

#     # Add D only if it is not already a favourite
#     if path_d not in existing_favourites:
#         click_favourite(driver, property_d)

#     # Open Favourites and verify both links
#     open_favourites(driver)
#     final_favourites = get_favourite_property_paths(driver)

#     assert path_c in final_favourites, (
#         f"Property C not found in Favourites: {property_c}"
#     )

#     assert path_d in final_favourites, (
#         f"Property D not found in Favourites: {property_d}"
#     )        


# # =========================================================
# # TC10-A: CLICK SAME HEART TWICE
# # =========================================================

# def test_TC10A_same_property_favourite_toggle(driver):

#     login_user(driver)
#     open_results_page(driver)

#     property_url = get_property_links(driver)[0]

#     # First click: Add favourite
#     click_favourite(driver, property_url)

#     # Second click: Remove favourite
#     click_favourite(driver, property_url)

#     open_favourites(driver)

#     page_text = get_page_text(driver)
#     property_id = (
#         urlparse(property_url).path.rstrip("/").split("/")[-1].lower()
#     )

#     assert property_id not in page_text, (
#         "Property is still present in Favourites after "
#         "clicking its heart twice."
#     )


# # =========================================================
# # TC10-B: INVALID PRICE RANGE
# # =========================================================

# def test_TC10B_invalid_price_range(driver):

#     login_user(driver)

#     # Record favourites before applying filter
#     open_favourites(driver)
#     favourites_before = get_page_text(driver)

#     # Open Lahore Homes results
#     open_results_page(driver)

#     # Apply invalid price range
#     set_price_filter(driver, 90, 80000)

#     # Wait for filtered results to load
#     wait_for_page(driver)

#     results_text = get_page_text(driver).lower()

#     # Check whether website displays a no-results message
#     zero_results = any(message in results_text for message in [
#         "0 properties",
#         "no properties",
#         "no results",
#         "no property found",
#         "no property",
#     ])

#     # Count only unique, direct Zameen property links
#     property_links = get_property_links(driver)
#     unique_property_links = set(property_links)

#     assert zero_results or len(unique_property_links) == 0, (
#         f"Invalid price range did not produce zero results. "
#         f"Found {len(unique_property_links)} property links."
#     )

#     # Check favourites again
#     open_favourites(driver)
#     favourites_after = get_page_text(driver)

#     assert favourites_before == favourites_after, (
#         "Favourites changed after applying the invalid price filter."
#     )


    




import re
import time
from urllib.parse import urlparse, urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

from test_login_inquiry import (
    driver,
    goto,
    open_login_form,
    login,
    TEST_EMAIL,
    TEST_PASSWORD,
)


def go_back(driver):
    """driver.back() that never blocks forever on third-party requests."""
    try:
        driver.back()
    except TimeoutException:
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass


BASE_URL = "https://www.zameen.com/"
LISTING_URL = "https://www.zameen.com/Homes/Lahore-1-1.html"
FAVOURITES_URL = "https://www.zameen.com/favorite-properties.html"

ADDED_TOAST = "added to favourites"
REMOVED_TOAST = "removed from favourites"

ZAMEEN_HOSTS = {"zameen.com", "www.zameen.com"}
HEART_WORDS = ("heart", "favorite", "favourite", "wishlist", "shortlist")

# "0 Properties for Sale ..." but NOT "10 properties" or "1,250 properties"
ZERO_RESULTS = re.compile(r"(?<![\d,.])0\s+propert(?:y|ies)")


# =========================================================
# COMMON HELPERS
# =========================================================

def wait_for_page(driver, timeout=25):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_for_results(driver):
    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href, '/Property/')]")
        )
    )


def page_text(driver):
    return driver.execute_script("return document.body.innerText;").lower()


def get_page_text(driver):
    return driver.find_element(By.TAG_NAME, "body").text.lower()


def path_key(url):
    """Lower-case path, used to compare properties (ignores domain and query)."""
    return urlparse(url).path.rstrip("/").lower()


def login_user(driver):
    open_login_form(driver)
    login(driver, TEST_EMAIL, TEST_PASSWORD)

    def logged_in(d):
        try:
            fields = d.find_elements(By.NAME, "email")
            return not any(f.is_displayed() for f in fields)
        except StaleElementReferenceException:
            # The modal is being removed/re-rendered after a successful
            # submit; check again on the next poll instead of crashing.
            return False

    try:
        WebDriverWait(driver, 20).until(logged_in)
    except TimeoutException:
        raise AssertionError(
            "Login was not successful. Login form is still visible."
        )

    wait_for_page(driver)
    time.sleep(2)


def open_results_page(driver):
    goto(driver, LISTING_URL)
    wait_for_page(driver)
    wait_for_results(driver)
    time.sleep(3)


# =========================================================
# PROPERTY LINKS
# =========================================================

def _direct_property_urls(driver):
    """Unique zameen.com/Property/... links on the current page (may be empty)."""
    urls, seen = [], set()

    for link in driver.find_elements(
        By.XPATH, "//a[contains(@href, '/Property/')]"
    ):
        try:
            href = link.get_attribute("href")
        except StaleElementReferenceException:
            continue

        if not href:
            continue

        full = urljoin(driver.current_url, href)
        parsed = urlparse(full)

        if (
            parsed.hostname
            and parsed.hostname.lower() in ZAMEEN_HOSTS
            and parsed.path.startswith("/Property/")
        ):
            key = path_key(full)
            if key not in seen:
                seen.add(key)
                urls.append(full)

    return urls


def get_property_links(driver, minimum=2):
    """Property links; raises if fewer than `minimum` (use for pages that SHOULD have results)."""
    urls = _direct_property_urls(driver)

    if len(urls) < minimum:
        raise AssertionError(
            f"Expected at least {minimum} direct property URLs, "
            f"found {len(urls)}: {urls}"
        )
    return urls


def count_property_links(driver):
    """Number of property links; never raises (safe for zero-result pages)."""
    return len(_direct_property_urls(driver))


# =========================================================
# FAVOURITES PAGE
# =========================================================

def get_favourite_property_paths(driver):
    """Lower-case paths of property links on the current page."""
    return {path_key(u) for u in _direct_property_urls(driver)}


def _wait_until_favourites_settle(driver, timeout=20, min_wait=5):
    """The list is filled by JavaScript AFTER the page loads, so wait until
    two reads in a row give the same answer (and, if empty, wait a bit longer
    in case it is still loading)."""
    start = time.time()
    previous = None

    while time.time() - start < timeout:
        current = get_favourite_property_paths(driver)
        waited = time.time() - start

        if current == previous and (current or waited >= min_wait):
            return current

        previous = current
        time.sleep(1)

    return previous or set()


def open_favourites(driver):
    goto(driver, FAVOURITES_URL)

    WebDriverWait(driver, 25).until(
        lambda d: "favorite-properties" in d.current_url.lower()
    )
    wait_for_page(driver)
    _wait_until_favourites_settle(driver)

    return driver


# =========================================================
# HEART HELPERS
# =========================================================

def find_property_card(driver, property_url):

    target = path_key(property_url)
    target_link = None

    for link in driver.find_elements(
        By.XPATH, "//a[contains(@href, '/Property/')]"
    ):
        try:
            href = link.get_attribute("href")
            if href and path_key(urljoin(driver.current_url, href)) == target:
                target_link = link
                break
        except StaleElementReferenceException:
            continue

    if target_link is None:
        raise AssertionError(
            f"Property link not found in listing card: {property_url}"
        )

    current = target_link

    for _ in range(14):
        try:
            current = current.find_element(By.XPATH, "..")
            tag = current.tag_name.lower()
            html = (current.get_attribute("innerHTML") or "").lower()

            if tag in ("article", "li"):
                return current

            if "<img" in html and ("button" in html or "role=" in html):
                return current

        except StaleElementReferenceException:
            break

    raise AssertionError("Could not identify the property listing card.")


def _is_listing_link(element):
    return "/Property/" in (element.get_attribute("href") or "")


def _is_small(element):
    size = element.size
    return size["width"] <= 90 and size["height"] <= 90


def find_heart_button(driver, property_url):
    """The heart is a SMALL clickable element inside the card.
    Listing links (which wrap the whole card) are never accepted."""

    card = find_property_card(driver, property_url)
    clickables = card.find_elements(
        By.XPATH, ".//button | .//*[@role='button'] | .//a"
    )

    # Pass 1: clear label (aria-label / title / class)
    for element in clickables:
        try:
            if (
                not element.is_displayed()
                or _is_listing_link(element)
                or not _is_small(element)
            ):
                continue

            label = " ".join([
                element.get_attribute("aria-label") or "",
                element.get_attribute("title") or "",
                element.get_attribute("class") or "",
            ]).lower()

            if any(word in label for word in HEART_WORDS + ("save",)):
                return element

        except StaleElementReferenceException:
            continue

    # Pass 2: small clickable whose inner markup contains a heart icon
    for element in clickables:
        try:
            if (
                not element.is_displayed()
                or _is_listing_link(element)
                or not _is_small(element)
            ):
                continue

            markup = (element.get_attribute("outerHTML") or "").lower()

            if any(word in markup for word in HEART_WORDS):
                return element

        except StaleElementReferenceException:
            continue

    # Pass 3: a heart-shaped SVG
    for svg in card.find_elements(By.XPATH, ".//*[name()='svg']"):
        try:
            if not svg.is_displayed():
                continue

            markup = (svg.get_attribute("outerHTML") or "").lower()

            if any(word in markup for word in HEART_WORDS):
                parents = svg.find_elements(
                    By.XPATH,
                    "./ancestor::*[self::button or @role='button'][1]"
                )
                return parents[0] if parents else svg.find_element(
                    By.XPATH, ".."
                )

        except StaleElementReferenceException:
            continue

    raise AssertionError(
        "Heart button not identified inside the property card. "
        "The website's heart HTML may be different."
    )


def click_favourite(driver, property_url):
    """Click the heart ONCE. Retries only if the click did not happen
    (the heart is a switch: clicking twice would undo it)."""

    for _ in range(3):
        try:
            button = find_heart_button(driver, property_url)

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", button
            )
            time.sleep(1)

            try:
                button.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", button)

            time.sleep(1)
            return

        except StaleElementReferenceException:
            time.sleep(1)

    raise AssertionError(
        f"Could not click the heart for {property_url} "
        f"(the page kept re-rendering)."
    )


def confirm_toast(driver, text, timeout=8):
    """Check the pop-up message ('Added to Favourites' etc.) really appeared."""
    try:
        WebDriverWait(driver, timeout, poll_frequency=0.2).until(
            lambda d: text in page_text(d)
        )
    except TimeoutException:
        raise AssertionError(
            f"Expected the message '{text}' after clicking the heart, "
            f"but it never appeared."
        )

    # Wait for it to disappear so the next toast is a fresh one
    try:
        WebDriverWait(driver, 10, poll_frequency=0.3).until(
            lambda d: text not in page_text(d)
        )
    except TimeoutException:
        pass


def cleanup_favourites(driver, urls):
    """Un-save only what this test saved, and only if it is really saved.
    (The heart is a switch: clicking an unsaved property would SAVE it.)"""

    if not urls:
        return

    for url in urls:
        try:
            open_favourites(driver)

            if path_key(url) not in get_favourite_property_paths(driver):
                continue

            try:
                click_favourite(driver, url)      # heart on the Favourites page
            except AssertionError:
                open_results_page(driver)         # fall back to the results page
                click_favourite(driver, url)

            time.sleep(2)

        except Exception as error:
            print(f"WARNING: cleanup of {url} failed: {error}")

    try:
        open_favourites(driver)
        still_saved = get_favourite_property_paths(driver)
        left = [u for u in urls if path_key(u) in still_saved]

        if left:
            print("WARNING: still saved - remove by hand:", left)

    except Exception as error:
        print("WARNING: final favourites check failed:", error)


# =========================================================
# PRICE FILTER
# =========================================================

def set_price_filter(driver, minimum, maximum):
    """Open the Price (PKR) popover and apply a min/max price range.

    On the listings page the price box is a dropdown: the inputs do not
    exist until the [aria-haspopup] button is clicked. There is no 'Find'
    button - pressing Enter in the max input applies the filter.
    """

    wait = WebDriverWait(driver, 20)

    price_filter = wait.until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "#large-search-form div[aria-label='Price filter']"
        ))
    )

    price_button = price_filter.find_element(
        By.CSS_SELECTOR, "div[role='button'][aria-haspopup='true']"
    )
    driver.execute_script("arguments[0].click();", price_button)

    min_input = wait.until(
        EC.visibility_of_element_located((By.ID, "activeNumericInput"))
    )
    max_input = wait.until(
        EC.visibility_of_element_located((By.ID, "inactiveNumericInput"))
    )

    for field, value in ((min_input, minimum), (max_input, maximum)):
        field.click()
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(str(value))
        time.sleep(0.5)

    max_input.send_keys(Keys.ENTER)

    try:
        WebDriverWait(driver, 20).until(
            lambda d: "price_min=" in d.current_url.lower()
            and "price_max=" in d.current_url.lower()
        )
    except TimeoutException:
        pass

    time.sleep(3)
    wait_for_page(driver)


# =========================================================
# TC09: CONTINUE BROWSING - VALID
# =========================================================

def test_TC09_continue_browsing_valid(driver):

    login_user(driver)

    open_favourites(driver)
    already_saved = get_favourite_property_paths(driver)

    open_results_page(driver)
    candidates = [
        u for u in get_property_links(driver)
        if path_key(u) not in already_saved
    ]
    assert candidates, "No unsaved property available for Property C"
    property_c = candidates[0]

    added = []

    try:
        # 1. Save property C
        click_favourite(driver, property_c)
        added.append(property_c)
        confirm_toast(driver, ADDED_TOAST)

        # 2. Open C, then browser Back
        goto(driver, property_c)
        wait_for_page(driver)
        time.sleep(2)

        go_back(driver)
        wait_for_page(driver)
        wait_for_results(driver)
        time.sleep(3)

        assert "/Homes/Lahore" in driver.current_url, (
            f"Browser Back did not return to a results page: {driver.current_url}"
        )

        # 3. Pick D from the page we are on NOW (the order may have changed)
        candidates = [
            u for u in get_property_links(driver)
            if path_key(u) not in already_saved
            and path_key(u) != path_key(property_c)
        ]
        assert candidates, "No unsaved property available for Property D"
        property_d = candidates[0]

        click_favourite(driver, property_d)
        added.append(property_d)
        confirm_toast(driver, ADDED_TOAST)

        # 4. Both must be in Favourites
        open_favourites(driver)
        saved_now = get_favourite_property_paths(driver)

        assert path_key(property_c) in saved_now, (
            f"Property C not found in Favourites: {property_c}"
        )
        assert path_key(property_d) in saved_now, (
            f"Property D not found in Favourites: {property_d}"
        )

    finally:
        cleanup_favourites(driver, added)


# =========================================================
# TC10-A: CLICK SAME HEART TWICE
# =========================================================

def test_TC10A_same_property_favourite_toggle(driver):

    login_user(driver)

    open_favourites(driver)
    already_saved = get_favourite_property_paths(driver)

    open_results_page(driver)
    candidates = [
        u for u in get_property_links(driver)
        if path_key(u) not in already_saved
    ]
    assert candidates, "No unsaved property available"
    property_url = candidates[0]

    added = []

    try:
        # First click: save
        click_favourite(driver, property_url)
        added.append(property_url)
        confirm_toast(driver, ADDED_TOAST)

        # Second click: un-save
        click_favourite(driver, property_url)
        confirm_toast(driver, REMOVED_TOAST)
        added.remove(property_url)          # back to unsaved

        open_favourites(driver)
        assert path_key(property_url) not in get_favourite_property_paths(driver), (
            "Property is still present in Favourites after clicking its heart twice."
        )

    finally:
        cleanup_favourites(driver, added)


# =========================================================
# TC10-B: INVALID PRICE RANGE
# =========================================================

def test_TC10B_invalid_price_range(driver):

    login_user(driver)

    open_favourites(driver)
    favourites_before = get_favourite_property_paths(driver)

    open_results_page(driver)
    set_price_filter(driver, 90, 80000)

    try:
        WebDriverWait(driver, 20, poll_frequency=0.5).until(
            lambda d: ZERO_RESULTS.search(page_text(d)) is not None
        )
    except TimeoutException:
        raise AssertionError(
            "Price range 90-80,000 did not show a '0 properties' message."
        )

    open_favourites(driver)
    favourites_after = get_favourite_property_paths(driver)

    assert favourites_before == favourites_after, (
        "Favourites changed after applying the invalid price filter."
    )