from config import SHOULD_FILL_DATA, LAST_NAME, FIRST_NAME, SECOND_NAME, EMAIL, PHONE
import logging
import time

from selenium import webdriver  # type: ignore
from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
from selenium.webdriver.chrome.service import Service  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def scrape():
    # Налаштування браузера
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        if not open_and_switch_to_form(driver):
            return
        if not select_group(driver):
            return
        if not select_service(driver):
            return
        if not find_and_click_shv_branch(driver):
            driver.quit()
            return
        if not select_date(driver):
            return
        if not select_time(driver):
            return
        if not fill_form(driver):
            return

        logging.info("Всі кроки виконано успішно.")
        # Додаткові дії, якщо потрібно
        time.sleep(5)  # час для спостереження перед закінченням роботи
    except Exception:
        logging.exception("Несподівана помилка в основному процесі")
    finally:
        driver.quit()
        logging.info("Браузер закрито.")


def open_and_switch_to_form(driver):
    """
    Відкриває сторінку та переходить до форми.
    """
    try:
        driver.get("https://cnap.city-adm.lviv.ua/service/preregistration")
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, ".uk-button.uk-button-primary.tm-text-semibold").click()
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(5)
        logging.info("Сторінку відкрито та переключено на вікно форми.")
        return True
    except Exception:
        logging.exception("Помилка при відкритті сторінки та перемиканні вікна форми")
        return False


def select_group(driver):
    """
    Обирає групу послуг "Подати документи".
    """
    try:
        driver.find_element(By.CSS_SELECTOR, "mat-select[formcontrolname='groups']").click()
        time.sleep(1)
        group_option = driver.find_element(
            By.XPATH,
            "//div[@class='cdk-overlay-container']//mat-option//span[contains(text(), 'Подати документи')]"
        )
        group_option.click()
        time.sleep(1)
        logging.info("Обрано групу 'Подати документи'.")
        return True
    except Exception:
        logging.exception("Помилка при виборі групи послуг")
        return False


def select_service(driver):
    """
    Обирає послугу "Паспорт громадянина України".
    """
    try:
        driver.find_element(By.CSS_SELECTOR, "mat-select[formcontrolname='servicesToShow']").click()
        time.sleep(1)
        service_option = driver.find_element(
            By.XPATH,
            "//div[@class='cdk-overlay-container']//mat-option//span[contains(text(), 'Паспорт громадянина України')]"
        )
        service_option.click()
        time.sleep(1)
        logging.info("Обрано послугу 'Паспорт громадянина України'.")
        return True
    except Exception:
        logging.exception("Помилка при виборі послуги")
        return False


def find_and_click_shv_branch(driver):
    """
    Шукає опцію "пр.Ч.Калини, 72 А Терпідрозділ ЦНАП" серед відділень.
    Якщо вона знайдена та активна, виконується клік.
    Якщо знайдена, але не активна, або взагалі не знайдена — це відображається в логах.
    """
    try:
        branch_select = driver.find_element(By.CSS_SELECTOR, "mat-select[formcontrolname='branchess']")
        driver.execute_script("arguments[0].scrollIntoView(true);", branch_select)
        time.sleep(1)
        branch_select.click()
        time.sleep(1)
        branch_options = driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-container mat-option")
        logging.info("Список опцій 'Центр':")
        target_branch_text = "пр.Ч.Калини, 72 А Терпідрозділ ЦНАП"
        target_found = False
        
        for opt in branch_options:
            text = opt.text.strip()
            aria_disabled = opt.get_attribute("aria-disabled") == "true"
            has_disabled_class = "mat-option-disabled" in opt.get_attribute("class").split()
            status = "DISABLED" if aria_disabled or has_disabled_class else "ACTIVE"
            logging.info(f" - {text}: {status}")
            
            # Якщо знайшли потрібну опцію
            if text == target_branch_text:
                target_found = True
                if status == "ACTIVE":
                    opt.click()
                    logging.info(f"Клікнуто цільове відділення: {text}")
                    return True
                else:
                    logging.error(f"Цільове відділення '{text}' знайдено, але воно не активне ({status}).")
                    return False
        
        if not target_found:
            logging.error(f"Цільове відділення '{target_branch_text}' не знайдено серед опцій.")
        return False
    except Exception:
        logging.exception("Помилка при роботі з відділеннями")
        return False



def select_date(driver):
    """
    Відкриває календар та клікає по першій доступній даті.
    """
    try:
        date_toggle = driver.find_element(By.CSS_SELECTOR, "mat-datepicker-toggle button")
        driver.execute_script("arguments[0].scrollIntoView(true);", date_toggle)
        time.sleep(1)
        date_toggle.click()
        time.sleep(1)
        date_cells = driver.find_elements(By.CSS_SELECTOR, "div.cdk-overlay-container td.mat-calendar-body-cell")
        logging.info("Список доступних дат:")
        first_available_date = None
        for cell in date_cells:
            date_text = cell.find_element(By.CLASS_NAME, "mat-calendar-body-cell-content").text.strip()
            classes = cell.get_attribute("class").split()
            is_disabled = "mat-calendar-body-disabled" in classes
            status = "DISABLED" if is_disabled else "ACTIVE"
            logging.info(f" - {date_text}: {status}")
            if not is_disabled and first_available_date is None:
                first_available_date = cell
        if first_available_date:
            first_available_date.click()
            selected_date = first_available_date.find_element(By.CLASS_NAME, "mat-calendar-body-cell-content").text.strip()
            logging.info(f"Вибрано першу доступну дату: {selected_date}")
            return True
        else:
            logging.error("Не знайдено доступних дат")
            return False
    except Exception:
        logging.exception("Помилка при виборі дати")
        return False


def select_time(driver):
    """
    Обирає перший активний варіант часу.
    """
    try:
        time.sleep(1)
        timeAvailable_select = driver.find_element(By.CSS_SELECTOR, "mat-select[formcontrolname='timeAvailable']")
        time.sleep(1)
        timeAvailable_select.click()
        time.sleep(1)
        time_options = driver.find_elements(By.CSS_SELECTOR, "div.mat-select-panel mat-option")
        available_times = []
        logging.info("Список доступних часів:")
        for opt in time_options:
            text_elem = opt.find_element(By.CSS_SELECTOR, "span.mat-option-text")
            text = text_elem.text.strip()
            disabled = opt.get_attribute("aria-disabled") == "true" or "mat-option-disabled" in opt.get_attribute("class").split()
            logging.info(f" - {text}: {'DISABLED' if disabled else 'ACTIVE'}")
            if not disabled:
                available_times.append((text, opt))
        if available_times:
            first_text, first_el = available_times[0]
            driver.execute_script("arguments[0].scrollIntoView(true);", first_el)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", first_el)
            logging.info(f"Вибрано перший активний час: {first_text}")
            return True
        else:
            logging.error("Не знайдено активних варіантів часу")
            return False
    except Exception:
        logging.exception("Помилка при виборі часу")
        return False


def fill_form(driver):
    """
    Автоматично заповнює форму (якщо SHOULD_FILL_DATA = True).
    """
    try:
        if not SHOULD_FILL_DATA:
            logging.info("Режим перевірки форми (SHOULD_FILL_DATA=False), заповнення пропущено.")
            return True

        # Заповнення Прізвища
        last_name_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='lastName']")
        last_name_input.clear()
        for ch in LAST_NAME:
            last_name_input.send_keys(ch)
            time.sleep(0.1)
        time.sleep(1)
        logging.info("Заповнено поле Прізвище.")

        # Заповнення Імені
        first_name_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='firstName']")
        first_name_input.clear()
        for ch in FIRST_NAME:
            first_name_input.send_keys(ch)
            time.sleep(0.1)
        time.sleep(1)
        logging.info("Заповнено поле Ім'я.")

        # Заповнення По-батькові
        second_name_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='secondName']")
        second_name_input.clear()
        for ch in SECOND_NAME:
            second_name_input.send_keys(ch)
            time.sleep(0.1)
        time.sleep(1)
        logging.info("Заповнено поле По-батькові.")

        # Заповнення Email
        email_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='email']")
        email_input.clear()
        for ch in EMAIL:
            email_input.send_keys(ch)
            time.sleep(0.1)
        time.sleep(1)
        logging.info("Заповнено поле Email.")

        # Заповнення Телефону
        phone_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='phone']")
        phone_input.clear()
        for ch in PHONE:
            phone_input.send_keys(ch)
            time.sleep(0.1)
        time.sleep(1)
        logging.info("Заповнено поле Телефон.")

        # Відмітка чекбоксів
        for checkbox_id in ("mat-checkbox-1-input", "mat-checkbox-2-input"):
            checkbox_element = driver.find_element(By.ID, checkbox_id)
            driver.execute_script("arguments[0].click();", checkbox_element)
            time.sleep(1)
            logging.info(f"Клікнуто чекбокс {checkbox_id}.")

        return True
    except Exception:
        logging.exception("Помилка при заповненні форми")
        return False