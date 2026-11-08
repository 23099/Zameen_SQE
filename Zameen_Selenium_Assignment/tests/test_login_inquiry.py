import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)


# =========================================
# TEST DATA
# =========================================

TEST_EMAIL = "manaalranaa123@gmail.com"
TEST_PASSWORD = "Zameennn2#"

WRONG_PASSWORD = "WrongPassword123"
INVALID_EMAIL = "nobody123@example.com"


# =========================================
# INQUIRY FIELD LOCATORS
# =========================================

NAME_FIELD = (By.ID, "contactFormName")
EMAIL_FIELD = (By.ID, "contactFormEmail")
PHONE_FIELD = (By.CSS_SELECTOR, "input[autocomplete='tel']")
MESSAGE_FIELD = (By.ID, "contactFormMessage")

BUYER_RADIO = (
    By.CSS_SELECTOR,
    "input[name='userType'][value='Buyer/Tenant']"
)

SEND_BUTTON = (
    By.CSS_SELECTOR,
    "button[aria-label='Send email']"
)


# =========================================
# DRIVER FIXTURE
# =========================================

# Zameen pages embed a lot of ad/tracker scripts that can stall page
# loads for minutes. Blocking them makes navigation fast and stable;
# the site's own content and functionality are not affected.
BLOCKED_URLS = [
    "*doubleclick.net/*",
    "*googlesyndication.com/*",
    "*googleadservices.com/*",
    "*googletagmanager.com/*",
    "*google-analytics.com/*",
    "*googletagservices.com/*",
    "*criteo.com/*",
    "*criteo.net/*",
    "*adnxs.com/*",
    "*taboola.com/*",
    "*outbrain.com/*",
    "*scorecardresearch.com/*",
    "*quantserve.com/*",
]

PAGE_LOAD_TIMEOUT = 60


@pytest.fixture
def driver():

    browser = webdriver.Chrome()
    # Ad-heavy Zameen pages can take longer than the 120s default for
    # ChromeDriver to answer; give the HTTP client more room.
    browser.command_executor.client_config.timeout = 300

    try:
        browser.execute_cdp_cmd("Network.enable", {})
        browser.execute_cdp_cmd("Network.setBlockedURLs", {"urls": BLOCKED_URLS})
    except Exception:
        pass

    browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    browser.maximize_window()

    yield browser

    browser.quit()


def goto(driver, url):
    """driver.get() that never blocks forever on third-party requests."""
    try:
        driver.get(url)
    except TimeoutException:
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass


# =========================================
# COMMON WAIT
# =========================================

def wait_for(driver, locator, timeout=20):

    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


# =========================================
# OPEN LOGIN FORM
# =========================================

def open_login_form(driver):

    goto(driver, "https://www.zameen.com/")

    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[normalize-space()='Login']")
        )
    )

    login_button.click()

    wait_for(driver, (By.NAME, "email"))


# =========================================
# LOGIN
# =========================================

def login(driver, email, password):

    email_field = wait_for(driver, (By.NAME, "email"))
    password_field = wait_for(driver, (By.ID, "password"))

    email_field.clear()
    email_field.send_keys(email)

    password_field.clear()
    password_field.send_keys(password)

    login_button = driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    )

    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(
            By.CSS_SELECTOR,
            "button[type='submit']"
        ).is_enabled()
    )

    login_button.click()


# =========================================
# LOGIN ERROR
# =========================================

def get_login_error(driver):

    expected_text = (
        "* The email address and password do not match"
    )

    return WebDriverWait(driver, 15).until(
        lambda d: expected_text
        if expected_text.lower() in
        d.find_element(By.TAG_NAME, "body").text.lower()
        else False
    )


# =========================================
# OPEN PROPERTY LISTING
# =========================================

def open_property_listing(driver):

    goto(
        driver,
        "https://www.zameen.com/Homes/Lahore-1-1.html"
    )

    wait = WebDriverWait(driver, 30)

    wait.until(
        lambda d: len(
            d.find_elements(
                By.XPATH,
                "//a[contains(@href, '/Property/') "
                "and not(contains(@href, 'Houses_Property'))]"
            )
        ) > 0
    )

    property_links = driver.find_elements(
        By.XPATH,
        "//a[contains(@href, '/Property/') "
        "and not(contains(@href, 'Houses_Property'))]"
    )

    property_url = None

    for link in property_links:

        try:
            href = link.get_attribute("href")

            if href and "/Property/" in href:
                property_url = href
                break

        except StaleElementReferenceException:
            continue

    if not property_url:
        raise Exception("No actual property listing found!")

    goto(driver, property_url)

    wait.until(
        EC.presence_of_element_located(NAME_FIELD)
    )

    print("Property page opened:", driver.current_url)
    print("Inquiry form found!")


# =========================================
# GET VISIBLE FIELD VALUE
# =========================================

def get_field_value(driver, locator):

    wait = WebDriverWait(driver, 20)

    def read_value(d):

        try:

            for field in d.find_elements(*locator):

                if field.is_displayed():
                    return {
                        "value": field.get_attribute("value")
                    }

            return False

        except StaleElementReferenceException:
            return False

    result = wait.until(read_value)

    return result["value"]


# =========================================
# GET VISIBLE PHONE FIELD
# =========================================

def get_visible_phone_field(driver):

    def find_phone(d):

        try:

            for field in d.find_elements(*PHONE_FIELD):

                if field.is_displayed() and field.is_enabled():
                    return field

            return False

        except StaleElementReferenceException:
            return False

    return WebDriverWait(driver, 25).until(find_phone)


# =========================================
# GET ALL PREFILLED INQUIRY VALUES
# =========================================

def get_inquiry_values(driver):

    wait = WebDriverWait(driver, 30)

    def read_fields(d):

        try:

            values = d.execute_script("""
                function getVisibleValue(selector) {

                    const elements =
                        document.querySelectorAll(selector);

                    for (const element of elements) {

                        if (element.getClientRects().length > 0) {
                            return element.value;
                        }
                    }

                    return null;
                }

                return {
                    name: getVisibleValue('#contactFormName'),
                    email: getVisibleValue('#contactFormEmail'),
                    phone: getVisibleValue(
                        'input[autocomplete="tel"]'
                    ),
                    message: getVisibleValue(
                        '#contactFormMessage'
                    )
                };
            """)

            if values and all(
                value is not None
                for value in values.values()
            ):
                return values

            return False

        except StaleElementReferenceException:
            return False

    fields = wait.until(read_fields)

    return (
        fields["name"],
        fields["email"],
        fields["phone"],
        fields["message"]
    )


# =========================================
# CLEAR AND ENTER NORMAL FIELDS
# =========================================

def clear_and_enter(driver, locator, value):

    wait = WebDriverWait(driver, 20)

    def update_field(d):

        try:

            field = next(
                (
                    element
                    for element in d.find_elements(*locator)
                    if element.is_displayed()
                    and element.is_enabled()
                ),
                None
            )

            if field is None:
                return False

            field.click()
            field.send_keys(Keys.CONTROL, "a")
            field.send_keys(Keys.BACKSPACE)

            if value:
                field.send_keys(value)

            field.send_keys(Keys.TAB)

            return (
                field.get_attribute("value") == value
            )

        except StaleElementReferenceException:
            return False

    wait.until(update_field)


# =========================================
# CLEAR PHONE FIELD
# =========================================

def clear_phone_field(driver):

    phone = get_visible_phone_field(driver)

    phone.click()
    phone.send_keys(Keys.CONTROL, "a")
    phone.send_keys(Keys.BACKSPACE)
    phone.send_keys(Keys.TAB)

    return get_field_value(driver, PHONE_FIELD)


# =========================================
# ENTER SHORT PHONE
# =========================================

def enter_short_phone(driver):

    phone = get_visible_phone_field(driver)

    phone.click()
    phone.send_keys(Keys.CONTROL, "a")
    phone.send_keys(Keys.BACKSPACE)
    phone.send_keys("+923")
    phone.send_keys(Keys.TAB)

    return get_field_value(driver, PHONE_FIELD)


# =========================================
# CHECK ERROR MESSAGE
# =========================================

def check_error_message(driver, expected_text):

    return WebDriverWait(driver, 15).until(
        lambda d: expected_text
        if expected_text.lower() in
        d.execute_script(
            "return document.body.innerText;"
        ).lower()
        else False
    )


# =========================================
# TC03: VALID LOGGED-IN INQUIRY
# =========================================

def test_TC03_valid_logged_in_inquiry(driver):

    open_login_form(driver)
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    open_property_listing(driver)

    name, email, phone, message = get_inquiry_values(driver)

    assert name.strip() != "", "Name field is empty"
    assert email.strip() != "", "Email field is empty"
    assert phone.strip() != "", "Phone field is empty"
    assert message.strip() != "", "Message field is empty"

    buyer_selected = driver.execute_script("""
        const radios = document.querySelectorAll(
            'input[name="userType"][value="Buyer/Tenant"]'
        );

        return Array.from(radios).some(radio => radio.checked);
    """)

    assert buyer_selected, "Buyer/Tenant is not selected"

    send_enabled = driver.execute_script("""
        const button = document.querySelector(
            'button[aria-label="Send email"]'
        );

        return button && !button.disabled;
    """)

    assert send_enabled, "Send Email button is disabled"

    print("TC03 Passed: Inquiry form is prefilled.")


# =========================================
# TC04 L1: WRONG PASSWORD
# =========================================

def test_TC04_L1_wrong_password(driver):

    open_login_form(driver)

    login(driver, TEST_EMAIL, WRONG_PASSWORD)

    error = get_login_error(driver)

    assert error == (
        "* The email address and password do not match"
    )


# =========================================
# TC04 L2: UNREGISTERED EMAIL
# =========================================

def test_TC04_L2_unregistered_email(driver):

    open_login_form(driver)

    login(driver, INVALID_EMAIL, TEST_PASSWORD)

    error = get_login_error(driver)

    assert error == (
        "* The email address and password do not match"
    )


# =========================================
# TC04 I1: EMPTY NAME
# =========================================

def test_TC04_I1_empty_name(driver):

    open_login_form(driver)
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    open_property_listing(driver)

    clear_and_enter(driver, NAME_FIELD, "")

    name_value = get_field_value(driver, NAME_FIELD)

    print("Name after clearing:", repr(name_value))

    assert name_value == "", (
        f"Name field should be empty. Actual value: {name_value}"
    )


# =========================================
# TC04 I2: INVALID EMAIL
# =========================================

def test_TC04_I2_invalid_email(driver):

    open_login_form(driver)
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    open_property_listing(driver)

    clear_and_enter(driver, EMAIL_FIELD, "testuser.com")

    check_error_message(
        driver,
        "Your email address must be in the format of name@domain.com."
    )


# =========================================
# TC04 I3: EMPTY PHONE
# =========================================

def test_TC04_I3_empty_phone(driver):

    open_login_form(driver)
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    open_property_listing(driver)

    phone_value = clear_phone_field(driver)

    print("Phone after clearing:", repr(phone_value))

    # Some phone inputs retain the country-code prefix.
    # Check that no subscriber digits remain after +92.
    digits = "".join(
        character
        for character in phone_value
        if character.isdigit()
    )

    remaining_digits = (
        digits[2:]
        if digits.startswith("92")
        else digits
    )

    assert remaining_digits == "", (
        f"Phone number should be empty. Actual value: {phone_value}"
    )


# =========================================
# TC04 I4: SHORT PHONE
# =========================================

def test_TC04_I4_short_phone(driver):

    open_login_form(driver)
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    open_property_listing(driver)

    phone_value = enter_short_phone(driver)

    print("Short phone value:", repr(phone_value))

    digits = "".join(
        character
        for character in phone_value
        if character.isdigit()
    )

    # +923 may be displayed as +92-3 by the phone formatter.
    assert digits.startswith("923"), (
        f"Short phone value was not entered correctly: {phone_value}"
    )

    assert len(digits) <= 3, (
        f"Phone number is not short: {phone_value}"
    )


# =========================================
# TC04 I5: EMPTY MESSAGE
# =========================================

def test_TC04_I5_empty_message(driver):

    open_login_form(driver)
    login(driver, TEST_EMAIL, TEST_PASSWORD)
    open_property_listing(driver)

    clear_and_enter(driver, MESSAGE_FIELD, "")

    message_value = get_field_value(driver, MESSAGE_FIELD)

    assert message_value == "", (
        f"Message was not cleared. Actual value: {message_value}"
    )