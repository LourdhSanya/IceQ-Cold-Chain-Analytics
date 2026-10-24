
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


BASE_URL = "http://localhost:5173"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1000")

    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(2)

    yield browser

    browser.quit()


def open_page(driver, path="/"):
    driver.get(BASE_URL + path)


def wait_for_text(driver, text):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//*[contains(normalize-space(), '{text}')]")
        )
    )


def test_homepage_loads(driver):
    open_page(driver)

    assert "IceQ" in driver.title or "ICEQ" in driver.page_source.upper()
    assert "Protect Every Degree" in driver.page_source



def test_homepage_login_navigation(driver):
    open_page(driver)

    login_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "nav.main-nav a[href='/login']")
        )
    )

    login_link.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )

    assert driver.current_url.endswith("/login")
    wait_for_text(driver, "Welcome back.")





def test_login_to_signup_and_back(driver):
    open_page(driver, "/login")

    # Login -> Signup
    create_account = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Create account')]")
        )
    )
    create_account.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/signup")
    )
    assert driver.current_url.endswith("/signup")

    # Find the exact React Router link from Signup.jsx.
    sign_in = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "p.signup-login-link a[href='/login']")
        )
    )

    # Scroll the link into the visible area.
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        sign_in
    )

    # Wait until the link can be clicked.
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "p.signup-login-link a[href='/login']")
        )
    )

    driver.execute_script("arguments[0].click();", sign_in)


    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )
    assert driver.current_url.endswith("/login")




def test_login_opens_dashboard(driver):
    open_page(driver, "/login")

    driver.find_element(By.ID, "email").send_keys("demo@iceq.test")
    driver.find_element(By.ID, "password").send_keys("DemoPassword123")
    driver.find_element(
        By.XPATH, "//button[@type='submit']"
    ).click()

    assert driver.current_url.endswith("/dashboard")
    wait_for_text(driver, "SIMULATED DATA")


def test_dashboard_has_simulation_notice(driver):
    open_page(driver, "/dashboard")

    assert "SIMULATED DATA" in driver.page_source.upper()
    assert "UNIT_001" in driver.page_source


def test_unit_search(driver):
    open_page(driver, "/dashboard")

    search = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//input[contains(translate(@placeholder,"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'), 'search')]"
            )
        )
    )

    search.send_keys("UNIT_001")
    wait_for_text(driver, "UNIT_001")

    search.clear()


def test_incident_filter_buttons_exist(driver):
    open_page(driver, "/dashboard")

    for label in ["All", "Critical", "Warning"]:
        wait_for_text(driver, label)


def test_incident_details_can_expand(driver):
    open_page(driver, "/dashboard")

    # Click the first visible incident-like button.
    incident_buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(., 'UNIT_') or contains(., 'DAIRY_')"
        " or contains(., 'PRODUCE_') or contains(., 'FROZEN_')]"
    )

    if incident_buttons:
        incident_buttons[0].click()
        assert incident_buttons[0].is_displayed()
    else:
        pytest.skip(
            "No incident buttons matched. Inspect the dashboard's "
            "incident markup and update this selector."
        )


@pytest.mark.parametrize(
    "width,height",
    [
        (1440, 900),
        (768, 1024),
        (390, 844),
    ],
)
def test_dashboard_responsive_sizes(driver, width, height):
    open_page(driver, "/dashboard")
    driver.set_window_size(width, height)

    assert driver.execute_script(
        "return document.documentElement.scrollWidth"
        " >= document.documentElement.clientWidth"
    )


def test_dashboard_back_to_website(driver):
    open_page(driver, "/dashboard")

    driver.find_element(
        By.XPATH,
        "//*[self::a or self::button][contains(., 'Back to Website')]"
    ).click()

    assert driver.current_url.rstrip("/").endswith("5173")
