from selenium import webdriver  # type: ignore
from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
from selenium.webdriver.chrome.service import Service  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
import time

# Чи потрібно вводити дані в форму (True — вводити, False — лише перевіряти відділення)
SHOULD_FILL_DATA = True

# Параметри для автозаповнення
LAST_NAME = "Трач"
FIRST_NAME = "Владислав"
SECOND_NAME = "Ігорович"
EMAIL = "vlad09121978@gmail.com"
PHONE = "673480565"

# Налаштування браузера
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Відкриваємо сторінку і переходимо в форму
driver.get("https://cnap.city-adm.lviv.ua/service/preregistration")
time.sleep(2)
driver.find_element(By.CSS_SELECTOR, ".uk-button.uk-button-primary.tm-text-semibold").click()
time.sleep(1)
driver.switch_to.window(driver.window_handles[-1])
time.sleep(5)

# Обираємо «Група послуг»
driver.find_element(By.CSS_SELECTOR, "mat-select[formcontrolname='groups']").click()
time.sleep(1)
driver.find_element(
    By.XPATH,
    "//div[@class='cdk-overlay-container']//mat-option//span[contains(text(), 'Подати документи')]"
).click()
time.sleep(1)

# Обираємо «Послуга»
driver.find_element(By.CSS_SELECTOR, "mat-select[formcontrolname='servicesToShow']").click()
time.sleep(1)
driver.find_element(
    By.XPATH,
    "//div[@class='cdk-overlay-container']//mat-option//span[contains(text(), 'Паспорт громадянина України')]"
).click()
time.sleep(1)

# Обираємо «Центр»
branch_select = driver.find_element(
    By.CSS_SELECTOR,
    "mat-select[formcontrolname='branchess']"
)
driver.execute_script("arguments[0].scrollIntoView(true);", branch_select)
time.sleep(1)
branch_select.click()

# Отримуємо всі відділення та виводимо їх статус
time.sleep(1)
branch_options = driver.find_elements(
    By.CSS_SELECTOR,
    "div.cdk-overlay-container mat-option"
)
print("Список опцій «Центр»:")
first_active = None
for opt in branch_options:
    text = opt.text.strip()
    aria_disabled = opt.get_attribute("aria-disabled") == "true"
    has_disabled_class = "mat-option-disabled" in opt.get_attribute("class").split()
    status = "DISABLED" if aria_disabled or has_disabled_class else "ACTIVE"
    print(f" - {text}: {status}")
    if status == "ACTIVE" and first_active is None:
        first_active = opt

# Клікаємо перше активне відділення
if first_active:
    first_active.click()
    print(f"Клікнуто перше активне відділення: {first_active.text.strip()}")
else:
    print("Не знайдено активних відділень")

# Працюємо з полем дати
# Клікаємо по іконці календаря замість input
date_toggle = driver.find_element(
    By.CSS_SELECTOR,
    "mat-datepicker-toggle button"
)
driver.execute_script("arguments[0].scrollIntoView(true);", date_toggle)
time.sleep(1)
date_toggle.click()

# Чекаємо появи календаря та збираємо всі дати
# Збираємо усі клітини дат у календарі
# Використовуємо td.mat-calendar-body-cell в overlay-контейнері
time.sleep(1)
date_cells = driver.find_elements(
    By.CSS_SELECTOR,
    "div.cdk-overlay-container td.mat-calendar-body-cell"
)
print("Список доступних дат:")
first_available_date = None
for cell in date_cells:
    # Текст дати в div всередині td
    date_text = cell.find_element(By.CLASS_NAME, "mat-calendar-body-cell-content").text.strip()
    classes = cell.get_attribute("class").split()
    # Заблоковані дати мають клас mat-calendar-body-disabled
    is_disabled = "mat-calendar-body-disabled" in classes
    status = "DISABLED" if is_disabled else "ACTIVE"
    print(f" - {date_text}: {status}")
    if not is_disabled and first_available_date is None:
        first_available_date = cell

# Клік по першій доступній даті
if first_available_date:
    first_available_date.click()
    print(f"Вибрано першу доступну дату: {first_available_date.find_element(By.CLASS_NAME, 'mat-calendar-body-cell-content').text.strip()}")
else:
    print("Не знайдено доступних дат")




# Обираємо Доступний час
time.sleep(1)
timeAvailable_select = driver.find_element(
    By.CSS_SELECTOR,
    "mat-select[formcontrolname='timeAvailable']"
)

time.sleep(1)
timeAvailable_select.click()

time.sleep(1)

# 2. Збираємо всі опції часу
time_options = driver.find_elements(
    By.CSS_SELECTOR,
    "div.mat-select-panel mat-option"
)

# 3. Парсимо їхній текст і статус
available_times = []
for opt in time_options:
    text = opt.find_element(By.CSS_SELECTOR, "span.mat-option-text").text.strip()
    disabled = opt.get_attribute("aria-disabled") == "true" or "mat-option-disabled" in opt.get_attribute("class").split()
    print(f" - {text}: {'DISABLED' if disabled else 'ACTIVE'}")
    if not disabled:
        available_times.append((text, opt))

print("Всі активні часи:", [t for t, _ in available_times])

# 4. Клік по першому активному варіанту часу
if available_times:
    first_text, first_el = available_times[0]
    # прокрутимо до нього (щоби бути впевненими, що в зоні видимості)
    driver.execute_script("arguments[0].scrollIntoView(true);", first_el)
    time.sleep(0.2)  # щоб браузер “підтягнувся”
    driver.execute_script("arguments[0].click();", first_el)
    print(f"Вибрано перший активний час: {first_text}")
else:
    print("Не знайдено активних варіантів часу")

# Якщо потрібно вводити дані — заповнюємо форму повністю
if SHOULD_FILL_DATA:
    # Заповнення Прізвища
    last_name_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='lastName']")
    last_name_input.clear()
    for ch in LAST_NAME:
        last_name_input.send_keys(ch)
        time.sleep(0.1)
    time.sleep(1)

    # Заповнення Імені
    first_name_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='firstName']")
    first_name_input.clear()
    for ch in FIRST_NAME:
        first_name_input.send_keys(ch)
        time.sleep(0.1)
    time.sleep(1)

    # Заповнення По-батькові
    second_name_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='secondName']")
    second_name_input.clear()
    for ch in SECOND_NAME:
        second_name_input.send_keys(ch)
        time.sleep(0.1)
    time.sleep(1)

    # Заповнення Email
    email_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='email']")
    email_input.clear()
    for ch in EMAIL:
        email_input.send_keys(ch)
        time.sleep(0.1)
    time.sleep(1)

    # Заповнення Телефону
    phone_input = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='phone']")
    phone_input.clear()
    for ch in PHONE:
        phone_input.send_keys(ch)
        time.sleep(0.1)
    time.sleep(1)

    # Відмічаємо чекбокси
    for checkbox_id in ("mat-checkbox-1-input", "mat-checkbox-2-input"):
        checkbox_element = driver.find_element(By.ID, checkbox_id)
        driver.execute_script("arguments[0].click();", checkbox_element)
        time.sleep(1)
