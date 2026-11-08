
import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# --------------------------------
# TEST DATA
# --------------------------------

TEST_NAME = "Test User"

# Use a NEW email that has never been registered
TEST_EMAIL = ""

# Already registered email
REGISTERED_EMAIL = ""

TEST_PASSWORD = "Test@12345"
TEST_PHONE = "+923001234567"


# --------------------------------
# BROWSER SETUP
# --------------------------------

@pytest.fixture
def driver():

    browser = webdriver.Chrome()
    browser.maximize_window()

    yield browser

    browser.quit()


# --------------------------------
# OPEN REGISTRATION FORM
# --------------------------------

def open_registration_form(driver):

    driver.get("https://www.zameen.com/")

    wait = WebDriverWait(driver, 15)

    # Click Login
    login_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[normalize-space()='Login']"
        ))
    )

    login_button.click()

    # Click Sign Up
    signup_button = wait.until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "button[aria-label='Sign up button']"
        ))
    )

    signup_button.click()

    # Wait for registration form
    wait.until(
        EC.visibility_of_element_located((
            By.NAME, "name"
        ))
    )


# --------------------------------
# FILL REGISTRATION FORM
# --------------------------------

def fill_registration_form(
    driver,
    name,
    email,
    password,
    confirm_password,
    phone,
    terms
):

    wait = WebDriverWait(driver, 15)

    # Name
    name_field = wait.until(
        EC.visibility_of_element_located((
            By.NAME, "name"
        ))
    )

    name_field.clear()
    name_field.send_keys(name)

    # Email
    email_field = driver.find_element(
        By.NAME, "email"
    )

    email_field.clear()
    email_field.send_keys(email)

    # Password
    password_field = driver.find_element(
        By.ID, "password"
    )

    password_field.clear()
    password_field.send_keys(password)

    # Confirm Password
    confirm_field = driver.find_element(
        By.NAME, "repeatPassword"
    )

    confirm_field.clear()
    confirm_field.send_keys(confirm_password)

    # Phone
    phone_field = driver.find_element(
        By.CSS_SELECTOR,
        "input[type='tel']"
    )

    phone_field.click()
    phone_field.send_keys(Keys.CONTROL, "a")
    phone_field.send_keys(phone)

    # Terms Checkbox
    terms_checkbox = driver.find_element(
        By.ID, "termsAgreed"
    )

    if terms and not terms_checkbox.is_selected():
        terms_checkbox.click()

    elif not terms and terms_checkbox.is_selected():
        terms_checkbox.click()


# --------------------------------
# GET CONTINUE BUTTON
# --------------------------------

def get_continue_button(driver):

    return driver.find_element(
        By.CSS_SELECTOR,
        "button[aria-label='Continue button']"
    )


# --------------------------------
# CAPTURE TEMPORARY MESSAGES
# --------------------------------

def start_message_observer(driver):

    driver.execute_script("""
        window.capturedMessages = [];

        const observer = new MutationObserver((mutations) => {

            mutations.forEach((mutation) => {

                if (mutation.addedNodes) {

                    mutation.addedNodes.forEach((node) => {

                        if (node.nodeType === Node.ELEMENT_NODE) {

                            const message = node.innerText || node.textContent;

                            if (message && message.trim()) {
                                window.capturedMessages.push(message.trim());
                            }

                        }

                        else if (node.nodeType === Node.TEXT_NODE) {

                            if (node.textContent.trim()) {
                                window.capturedMessages.push(
                                    node.textContent.trim()
                                );
                            }

                        }

                    });

                }

            });

            // Also capture current page text
            const pageText = document.body.innerText;

            if (pageText) {
                window.capturedMessages.push(pageText);
            }

        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true
        });

        window.messageObserver = observer;
    """)


def get_captured_messages(driver):

    return driver.execute_script("""
        return (window.capturedMessages || []).join("\\n");
    """)


# --------------------------------
# TC01: VALID REGISTRATION
# --------------------------------

def test_registration_valid(driver):

    open_registration_form(driver)

    fill_registration_form(
        driver,
        name=TEST_NAME,
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        confirm_password=TEST_PASSWORD,
        phone=TEST_PHONE,
        terms=True
    )

    continue_button = get_continue_button(driver)

    assert continue_button.is_enabled(), (
        "Continue button should be enabled for valid data."
    )

    # Start capturing messages BEFORE clicking Continue
    start_message_observer(driver)

    continue_button.click()

    # Wait for temporary success message
    try:

        WebDriverWait(driver, 10).until(
            lambda d: (
                "activation link has been emailed"
                in get_captured_messages(d).lower()
            )
        )

    except Exception:

        driver.save_screenshot("registration_success_debug.png")

        captured_text = get_captured_messages(driver)

        raise AssertionError(
            "Success message was not captured. "
            f"Captured page text: {captured_text}"
        )

    captured_text = get_captured_messages(driver).lower()

    assert "activation link has been emailed" in captured_text

    print("Valid registration successful!")


# --------------------------------
# TC02: INVALID REGISTRATION
# --------------------------------

@pytest.mark.parametrize(
    "scenario, name, email, password, confirm, phone, terms",
    [

        (
            "Empty Name",
            "",
            TEST_EMAIL,
            TEST_PASSWORD,
            TEST_PASSWORD,
            TEST_PHONE,
            True
        ),

        (
            "Invalid Email",
            TEST_NAME,
            "testuser.com",
            TEST_PASSWORD,
            TEST_PASSWORD,
            TEST_PHONE,
            True
        ),

        (
            "Empty Email",
            TEST_NAME,
            "",
            TEST_PASSWORD,
            TEST_PASSWORD,
            TEST_PHONE,
            True
        ),

        (
            "Already Registered Email",
            TEST_NAME,
            REGISTERED_EMAIL,
            TEST_PASSWORD,
            TEST_PASSWORD,
            TEST_PHONE,
            True
        ),

        (
            "Weak Password",
            TEST_NAME,
            TEST_EMAIL,
            "test@1",
            "test@1",
            TEST_PHONE,
            True
        ),

        (
            "Empty Password",
            TEST_NAME,
            TEST_EMAIL,
            "",
            "",
            TEST_PHONE,
            True
        ),

        (
            "Password Mismatch",
            TEST_NAME,
            TEST_EMAIL,
            TEST_PASSWORD,
            "Test@54321",
            TEST_PHONE,
            True
        ),

        (
            "Empty Confirm Password",
            TEST_NAME,
            TEST_EMAIL,
            TEST_PASSWORD,
            "",
            TEST_PHONE,
            True
        ),

        (
            "Short Phone",
            TEST_NAME,
            TEST_EMAIL,
            TEST_PASSWORD,
            TEST_PASSWORD,
            "+9230012345",
            True
        ),

        (
            "Long Phone",
            TEST_NAME,
            TEST_EMAIL,
            TEST_PASSWORD,
            TEST_PASSWORD,
            "+9230012345678",
            True
        ),

        (
            "Empty Phone",
            TEST_NAME,
            TEST_EMAIL,
            TEST_PASSWORD,
            TEST_PASSWORD,
            "",
            True
        ),

        (
            "Terms Not Accepted",
            TEST_NAME,
            TEST_EMAIL,
            TEST_PASSWORD,
            TEST_PASSWORD,
            TEST_PHONE,
            False
        )

    ]
)


def test_registration_invalid(
    driver,
    scenario,
    name,
    email,
    password,
    confirm,
    phone,
    terms
):

    open_registration_form(driver)

    fill_registration_form(
        driver,
        name=name,
        email=email,
        password=password,
        confirm_password=confirm,
        phone=phone,
        terms=terms
    )

    continue_button = get_continue_button(driver)

    # Special case: Already Registered Email
    if scenario == "Already Registered Email":

        assert continue_button.is_enabled(), (
            "Continue should be enabled before submitting this email."
        )

        # Start capturing messages BEFORE clicking
        start_message_observer(driver)

        continue_button.click()

        try:

            WebDriverWait(driver, 10).until(
                lambda d: (
                    "email or password is not correct"
                    in get_captured_messages(d).lower()
                )
            )

        except Exception:

            driver.save_screenshot("registered_email_debug.png")

            captured_text = get_captured_messages(driver)

            raise AssertionError(
                "Expected registered-email error was not captured. "
                f"Captured page text: {captured_text}"
            )

        captured_text = get_captured_messages(driver).lower()

        assert "email or password is not correct" in captured_text

        print("Already registered email rejected successfully!")

    else:

        # All other invalid scenarios
        assert not continue_button.is_enabled(), (
            f"{scenario}: Continue should remain disabled."
        )
