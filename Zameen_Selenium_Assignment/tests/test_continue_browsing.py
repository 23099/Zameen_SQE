
import pytest
import time
from urllib.parse import urlparse, urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

from test_login_inquiry import (
    driver,
    open_login_form,
    login,
    TEST_EMAIL,
    TEST_PASSWORD,
)


BASE_URL = "https://www.zameen.com/"
LISTING_URL = "https://www.zameen.com/Homes/Lahore-1-1.html"


# =========================================================
# COMMON HELPERS
# =========================================================

def wait_for_page(driver, timeout=25):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )


def wait_for_results(driver):
    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href, '/Property/')]")
        )
    )


def login_user(driver):
    open_login_form(driver)
    login(driver, TEST_EMAIL, TEST_PASSWORD)

    time.sleep(3)
    wait_for_page(driver)

    login_fields = driver.find_elements(By.NAME, "email")

    if any(field.is_displayed() for field in login_fields):
        raise AssertionError(
            "Login was not successful. Login form is still visible."
        )


def open_results_page(driver):
    driver.get(LISTING_URL)
    wait_for_page(driver)
    wait_for_results(driver)
    time.sleep(3)


def get_property_links(driver):
    """Return unique direct Zameen property detail URLs only."""

    links = driver.find_elements(
        By.XPATH,
        "//a[contains(@href, '/Property/')]"
    )

    urls = []

    for link in links:
        try:
            href = link.get_attribute("href")

            if not href:
                continue

            # Convert relative URLs to absolute URLs
            full_url = urljoin(driver.current_url, href)
            parsed = urlparse(full_url)

            # Exclude Facebook, WhatsApp, Twitter and other share URLs
            if (
                parsed.hostname
                and parsed.hostname.lower() in {
                    "zameen.com",
                    "www.zameen.com"
                }
                and parsed.path.startswith("/Property/")
                and full_url not in urls
            ):
                urls.append(full_url)

        except StaleElementReferenceException:
            continue

    if len(urls) < 2:
        raise AssertionError(
            f"Expected at least 2 direct property URLs, found {len(urls)}: {urls}"
        )

    print("\nDirect property URLs found:")
    for url in urls[:5]:
        print(url)

    return urls


def get_page_text(driver):
    return driver.find_element(
        By.TAG_NAME, "body"
    ).text.lower()


# =========================================================
# FAVOURITE HEART HELPERS
# =========================================================

def find_property_card(driver, property_url):

    target_path = urlparse(property_url).path.rstrip("/")

    links = driver.find_elements(
        By.XPATH,
        "//a[contains(@href, '/Property/')]"
    )

    target = None

    for link in links:
        try:
            href = link.get_attribute("href")

            if not href:
                continue

            full_url = urljoin(driver.current_url, href)
            parsed = urlparse(full_url)

            if (
                parsed.hostname
                and parsed.hostname.lower() in {
                    "zameen.com",
                    "www.zameen.com"
                }
                and parsed.path.rstrip("/") == target_path
            ):
                target = link
                break

        except StaleElementReferenceException:
            continue

    if target is None:
        raise AssertionError(
            f"Property link not found in listing card: {property_url}"
        )

    current = target

    for _ in range(1, 15):
        try:
            current = current.find_element(By.XPATH, "..")

            tag = current.tag_name.lower()
            html = (
                current.get_attribute("innerHTML") or ""
            ).lower()

            if tag in ["article", "li"]:
                return current

            if "<img" in html and (
                "button" in html or "role=" in html
            ):
                return current

        except StaleElementReferenceException:
            break

    raise AssertionError(
        "Could not identify the property listing card."
    )


def find_heart_button(driver, property_url):

    card = find_property_card(driver, property_url)

    elements = card.find_elements(
        By.XPATH,
        ".//button | .//*[@role='button'] | .//a"
    )

    for element in elements:
        try:
            if not element.is_displayed():
                continue

            aria = (
                element.get_attribute("aria-label") or ""
            ).lower()

            title = (
                element.get_attribute("title") or ""
            ).lower()

            html = (
                element.get_attribute("outerHTML") or ""
            ).lower()

            combined = aria + " " + title + " " + html

            if any(word in combined for word in [
                "heart",
                "favorite",
                "favourite",
                "wishlist",
                "shortlist",
                "save"
            ]):
                return element

        except StaleElementReferenceException:
            continue

    # Try identifying the heart through SVG attributes
    svgs = card.find_elements(
        By.XPATH,
        ".//*[name()='svg']"
    )

    for svg in svgs:
        try:
            if not svg.is_displayed():
                continue

            svg_html = (
                svg.get_attribute("outerHTML") or ""
            ).lower()

            if any(word in svg_html for word in [
                "heart",
                "favorite",
                "favourite"
            ]):
                parent = svg.find_element(
                    By.XPATH,
                    "./ancestor::*[self::button or @role='button' or self::a][1]"
                )

                if parent.is_displayed():
                    return parent

        except Exception:
            continue

    raise AssertionError(
        "Heart button not identified inside the property card. "
        "The website's actual heart HTML selector may be different."
    )


def click_favourite(driver, property_url):

    button = find_heart_button(driver, property_url)

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        button
    )

    time.sleep(1)

    try:
        button.click()
    except ElementClickInterceptedException:
        driver.execute_script(
            "arguments[0].click();",
            button
        )

    time.sleep(2)


# =========================================================
# FAVOURITES PAGE HELPERS
# =========================================================

def open_favourites(driver):

    driver.get("https://www.zameen.com/favorite-properties.html")

    WebDriverWait(driver, 25).until(
        lambda d: "favorite-properties" in d.current_url.lower()
    )

    WebDriverWait(driver, 25).until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    return driver

def get_favourite_property_paths(driver):
    """Get actual property links displayed on the Favourites page."""

    links = driver.find_elements(
        By.XPATH,
        "//a[contains(@href, '/Property/')]"
    )

    paths = set()

    for link in links:
        try:
            href = link.get_attribute("href")

            if href:
                parsed = urlparse(urljoin(driver.current_url, href))

                if (
                    parsed.hostname
                    and parsed.hostname.lower() in {
                        "zameen.com", "www.zameen.com"
                    }
                    and parsed.path.startswith("/Property/")
                ):
                    paths.add(parsed.path.rstrip("/").lower())

        except StaleElementReferenceException:
            continue

    return paths

# =========================================================
# PRICE FILTER HELPERS
# =========================================================


def set_price_filter(driver, minimum, maximum):

    wait = WebDriverWait(driver, 20)

    # Find the visible PRICE (PKR) label
    price_label = wait.until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[normalize-space()='PRICE (PKR)' "
            "or normalize-space()='Price (PKR)']"
        ))
    )

    # Move upward until a container with two visible inputs is found
    price_container = None
    current = price_label

    for _ in range(8):
        try:
            current = current.find_element(By.XPATH, "..")

            inputs = current.find_elements(By.TAG_NAME, "input")

            visible_inputs = [
                field for field in inputs
                if field.is_displayed() and field.is_enabled()
            ]

            if len(visible_inputs) >= 2:
                price_container = current
                break

        except StaleElementReferenceException:
            continue

    if price_container is None:
        raise AssertionError(
            "Could not locate both inputs inside PRICE (PKR) section."
        )

    price_inputs = [
        field for field in price_container.find_elements(
            By.TAG_NAME, "input"
        )
        if field.is_displayed() and field.is_enabled()
    ][:2]

    # Enter minimum and maximum values
    for field, value in zip(
        price_inputs, [minimum, maximum]
    ):
        field.click()
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(str(value))
        field.send_keys(Keys.TAB)

    time.sleep(2)

    # Click the Find button
    find_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
            "'find')]"
            " | //a[contains(translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
            "'find')]"
        ))
    )

    driver.execute_script(
        "arguments[0].click();", find_button
    )

    time.sleep(5)
    wait_for_page(driver)

# =========================================================
# TC09: CONTINUE BROWSING - VALID
# =========================================================

def test_TC09_continue_browsing_valid(driver):

    login_user(driver)

    # Check existing favourites first
    open_favourites(driver)
    existing_favourites = get_favourite_property_paths(driver)

    # Open Lahore Homes results
    open_results_page(driver)

    property_urls = get_property_links(driver)
    property_c = property_urls[0]
    property_d = property_urls[1]

    path_c = urlparse(property_c).path.rstrip("/").lower()
    path_d = urlparse(property_d).path.rstrip("/").lower()

    # Add C only if it is not already a favourite
    if path_c not in existing_favourites:
        click_favourite(driver, property_c)

    # Open C detail page
    driver.get(property_c)
    wait_for_page(driver)
    time.sleep(3)

    # Browser Back
    driver.back()
    wait_for_page(driver)
    wait_for_results(driver)
    time.sleep(3)

    assert "/Homes/Lahore-1-1.html" in driver.current_url, (
        f"Browser Back did not return to results page: {driver.current_url}"
    )

    # Add D only if it is not already a favourite
    if path_d not in existing_favourites:
        click_favourite(driver, property_d)

    # Open Favourites and verify both links
    open_favourites(driver)
    final_favourites = get_favourite_property_paths(driver)

    assert path_c in final_favourites, (
        f"Property C not found in Favourites: {property_c}"
    )

    assert path_d in final_favourites, (
        f"Property D not found in Favourites: {property_d}"
    )        


# =========================================================
# TC10-A: CLICK SAME HEART TWICE
# =========================================================

def test_TC10A_same_property_favourite_toggle(driver):

    login_user(driver)
    open_results_page(driver)

    property_url = get_property_links(driver)[0]

    # First click: Add favourite
    click_favourite(driver, property_url)

    # Second click: Remove favourite
    click_favourite(driver, property_url)

    open_favourites(driver)

    page_text = get_page_text(driver)
    property_id = (
        urlparse(property_url).path.rstrip("/").split("/")[-1].lower()
    )

    assert property_id not in page_text, (
        "Property is still present in Favourites after "
        "clicking its heart twice."
    )


# =========================================================
# TC10-B: INVALID PRICE RANGE
# =========================================================

def test_TC10B_invalid_price_range(driver):

    login_user(driver)

    # Record favourites before applying filter
    open_favourites(driver)
    favourites_before = get_page_text(driver)

    # Open Lahore Homes results
    open_results_page(driver)

    # Apply invalid price range
    set_price_filter(driver, 90, 80000)

    # Wait for filtered results to load
    wait_for_page(driver)

    results_text = get_page_text(driver).lower()

    # Check whether website displays a no-results message
    zero_results = any(message in results_text for message in [
        "0 properties",
        "no properties",
        "no results",
        "no property found",
        "no property",
    ])

    # Count only unique, direct Zameen property links
    property_links = get_property_links(driver)
    unique_property_links = set(property_links)

    assert zero_results or len(unique_property_links) == 0, (
        f"Invalid price range did not produce zero results. "
        f"Found {len(unique_property_links)} property links."
    )

    # Check favourites again
    open_favourites(driver)
    favourites_after = get_page_text(driver)

    assert favourites_before == favourites_after, (
        "Favourites changed after applying the invalid price filter."
    )