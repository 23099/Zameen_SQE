
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


# ---------------- LOCATORS ----------------

NAME_FIELD = (By.ID, "contactFormName")
EMAIL_FIELD = (By.ID, "contactFormEmail")
PHONE_FIELD = (By.CSS_SELECTOR, "input[autocomplete='tel']")
MESSAGE_FIELD = (By.ID, "contactFormMessage")
SEND_EMAIL_BUTTON = (By.CSS_SELECTOR, "button[aria-label='Send email']")

NAME_ERROR = "Please enter your name"
EMAIL_ERROR = "Please enter your email address"
PHONE_ERROR = "Please enter a valid international phone number"


# ---------------- DRIVER SETUP ----------------

@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.maximize_window()

    yield browser

    browser.quit()


# ---------------- HELPER FUNCTIONS ----------------

def open_property_listing(driver):

    wait = WebDriverWait(driver, 30)

    driver.get("https://www.zameen.com/Homes/Lahore-1-1.html")

    wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//a[contains(@href, '/Property/')]")
        )
    )

    links = driver.find_elements(
        By.XPATH, "//a[contains(@href, '/Property/')]"
    )

    property_url = None

    for link in links:
        try:
            href = link.get_attribute("href")

            if href and "/Property/" in href:
                property_url = href
                break

        except StaleElementReferenceException:
            continue

    assert property_url is not None, "Property listing not found"

    driver.get(property_url)

    wait.until(EC.presence_of_element_located(NAME_FIELD))
    wait.until(EC.presence_of_element_located(EMAIL_FIELD))

    return wait


def get_visible_field(driver, locator):

    def find_field(d):
        try:
            for field in d.find_elements(*locator):
                if field.is_displayed() and field.is_enabled():
                    return field

            return False

        except StaleElementReferenceException:
            return False

    return WebDriverWait(driver, 25).until(find_field)


def enter_text(driver, locator, value):

    field = get_visible_field(driver, locator)

    field.click()
    field.send_keys(Keys.CONTROL, "a")
    field.send_keys(Keys.BACKSPACE)

    if value:
        field.send_keys(value)

    return field.get_attribute("value")


def enter_phone(driver, number):

    phone = get_visible_field(driver, PHONE_FIELD)

    phone.click()
    phone.send_keys(Keys.CONTROL, "a")
    phone.send_keys(Keys.BACKSPACE)

    if number:
        phone.send_keys(number)

    phone.send_keys(Keys.TAB)

    return get_visible_field(
        driver, PHONE_FIELD
    ).get_attribute("value")


def click_send_email(driver):

    button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(SEND_EMAIL_BUTTON)
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        button
    )

    driver.execute_script(
        "arguments[0].click();",
        button
    )


def get_error(driver, expected_message=None):

    locator = (
        By.CSS_SELECTOR,
        "[aria-label='Error message'], "
        "[aria-label='Error message compact']"
    )

    def find_error(d):
        try:
            for element in d.find_elements(*locator):

                if not element.is_displayed():
                    continue

                error_text = element.text.strip()

                if expected_message is None:
                    if error_text:
                        return error_text

                elif expected_message in error_text:
                    return error_text

            return False

        except StaleElementReferenceException:
            return False

    return WebDriverWait(driver, 20).until(find_error)


# ---------------- TC05: VALID GUEST INQUIRY ----------------

def test_TC05_guest_valid_inquiry(driver):

    open_property_listing(driver)

    assert get_visible_field(driver, NAME_FIELD).is_displayed()
    assert get_visible_field(driver, EMAIL_FIELD).is_displayed()
    assert get_visible_field(driver, PHONE_FIELD).is_displayed()
    assert get_visible_field(driver, MESSAGE_FIELD).is_displayed()

    enter_text(driver, NAME_FIELD, "Test Guest")
    enter_text(driver, EMAIL_FIELD, "guesttest@example.com")

    phone_value = enter_phone(driver, "3001234567")

    message = get_visible_field(
        driver, MESSAGE_FIELD
    ).get_attribute("value")

    assert get_visible_field(
        driver, NAME_FIELD
    ).get_attribute("value") == "Test Guest"

    assert get_visible_field(
        driver, EMAIL_FIELD
    ).get_attribute("value") == "guesttest@example.com"

    assert len("".join(
        digit for digit in phone_value if digit.isdigit()
    )) >= 10

    assert message.strip() != ""

    button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(SEND_EMAIL_BUTTON)
    )

    assert button.is_enabled()


# ---------------- TC06-I1: EMPTY NAME ----------------

def test_TC06_I1_guest_empty_name(driver):

    open_property_listing(driver)

    enter_text(driver, NAME_FIELD, "")
    enter_text(driver, EMAIL_FIELD, "guesttest@example.com")
    enter_phone(driver, "3001234567")

    click_send_email(driver)

    error_text = get_error(driver, NAME_ERROR)

    assert NAME_ERROR in error_text


# ---------------- TC06-I2: INVALID EMAIL ----------------

def test_TC06_I2_guest_invalid_email(driver):

    open_property_listing(driver)

    enter_text(driver, NAME_FIELD, "Test Guest")
    enter_text(driver, EMAIL_FIELD, "testuser.com")
    enter_phone(driver, "3001234567")

    click_send_email(driver)

    error_text = get_error(driver, EMAIL_ERROR)

    assert EMAIL_ERROR in error_text


# ---------------- TC06-I3: EMPTY PHONE ----------------

def test_TC06_I3_guest_empty_phone(driver):

    open_property_listing(driver)

    enter_text(driver, NAME_FIELD, "Test Guest")
    enter_text(driver, EMAIL_FIELD, "guesttest@example.com")

    enter_phone(driver, "")

    click_send_email(driver)

    error_text = get_error(driver, PHONE_ERROR)

    assert PHONE_ERROR in error_text


# ---------------- TC06-I4: SHORT PHONE ----------------

def test_TC06_I4_guest_short_phone(driver):

    open_property_listing(driver)

    enter_text(driver, NAME_FIELD, "Test Guest")
    enter_text(driver, EMAIL_FIELD, "guesttest@example.com")

    enter_phone(driver, "3")

    click_send_email(driver)

    error_text = get_error(driver, PHONE_ERROR)

    assert PHONE_ERROR in error_text


# ---------------- TC06-I5: EMPTY MESSAGE ----------------

def test_TC06_I5_guest_empty_message(driver):

    open_property_listing(driver)

    enter_text(driver, NAME_FIELD, "Test Guest")
    enter_text(driver, EMAIL_FIELD, "guesttest@example.com")
    enter_phone(driver, "3001234567")

    enter_text(driver, MESSAGE_FIELD, "")

    click_send_email(driver)

    error_text = get_error(driver)

    assert error_text.strip() != ""
