import allure
import pytest
import time
import random
import os
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, \
    TimeoutException

# Данные для входа



class YclientsAuth:
    """Класс для авторизации на Yclients"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def login(self, email=LOGIN, password=PASSWORD):
        """Метод авторизации"""
        with allure.step("Открыть главную страницу"):
            self.driver.get("https://www.yclients.com/signin")

        with allure.step(f"Ввести email: {email}"):
            email_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(1.5)

        with allure.step("Ввести пароль"):
            password_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "input[type='password']"))
            )
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1.5)

        with allure.step("Нажать кнопку 'Войти'"):
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "button[type='submit']"))
            )
            submit_button.click()

            self.wait.until(
                lambda d: d.execute_script(
                    "return document.readyState") == "complete"
            )
            time.sleep(3)

    def take_screenshot(self, name):
        """Метод для скриншотов"""
        try:
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
        except Exception:
            pass


class TestYclientsCreateClient:
    """Тест на создание клиента"""

    @pytest.fixture
    def driver(self):
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches",
                                        ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)
        driver.maximize_window()

        yield driver
        driver.quit()

    def safe_click(self, driver, element, wait_time=1):
        """Безопасный клик по элементу с увеличенным ожиданием"""
        try:
            # Скроллим к элементу
            driver.execute_script("arguments[0].scrollIntoView({block: \
                                  'center', behavior: 'smooth'});", element)
            time.sleep(wait_time)

            # Пробуем обычный клик
            element.click()
            time.sleep(0.5)  # Небольшая задержка после клика
            return True
        except Exception:
            try:
                # Пробуем JavaScript клик
                driver.execute_script("arguments[0].click();", element)
                time.sleep(0.5)
                return True
            except Exception as e2:
                print(f"Не удалось кликнуть по элементу: {e2}")
                return False

    def wait_for_element(self, driver, locator, timeout=15):
        """Универсальный метод ожидания элемента"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"element_not_found_{timeout}",
                attachment_type=allure.attachment_type.PNG
            )
            raise

    def wait_for_clickable(self, driver, locator, timeout=15):
        """Универсальный метод ожидания кликабельного элемента"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"element_not_clickable_{timeout}",
                attachment_type=allure.attachment_type.PNG
            )
            raise

    @pytest.mark.ui
    @allure.title("Тест создания нового клиента")
    @allure.description("Авторизация и добавление нового \
                        клиента в клиентскую базу")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.feature("Клиенты")
    @allure.story("Создание клиента")
    def test_create_client(self, driver):
        auth = YclientsAuth(driver)

        unique_id = random.randint(10000, 99999)
        client_name = f"Тестовый_{unique_id}"
        client_phone = f"7999{unique_id}"

        with allure.step("ШАГ 1: Авторизация"):
            auth.login()

        with allure.step("ШАГ 2: Переход в раздел 'Клиенты'"):
            # Ждем загрузки основного интерфейса
            time.sleep(2)

            clients_menu = self.wait_for_clickable(
                driver,
                (By.XPATH, "//span[contains(@class, \
                 'nav-label') and contains(text(), 'Клиенты')]")
            )
            self.safe_click(driver, clients_menu)
            time.sleep(3)  # Увеличил ожидание после клика
            auth.take_screenshot("clients_menu_clicked")

        with allure.step("ШАГ 3: Переход в 'Клиентская база'"):
            client_base = self.wait_for_clickable(
                driver,
                (By.XPATH, "//a[contains(text(), 'Клиентская база')]")
            )
            self.safe_click(driver, client_base)
            time.sleep(3)  # Увеличил ожидание после клика
            auth.take_screenshot("client_base_page")

        with allure.step(f"ШАГ 4: Добавление нового клиента '{client_name}'"):
            # Ждем загрузки страницы клиентской базы
            time.sleep(2)

            add_button = self.wait_for_clickable(
                driver,
                (By.CSS_SELECTOR, "button.btn.btn-primary.add-new-client")
            )
            self.safe_click(driver, add_button)
            time.sleep(2)  # Ожидание открытия формы
            auth.take_screenshot("add_form_opened")

            # Заполняем имя
            name_field = self.wait_for_element(
                driver,
                (By.CSS_SELECTOR, "input[data-locator='input_client_name']")
            )
            name_field.clear()
            time.sleep(0.5)
            name_field.send_keys(client_name)
            time.sleep(1)

            # Заполняем телефон
            phone_field = self.wait_for_element(
                driver,
                (By.CSS_SELECTOR, "input[data-locator='input_client_phone']")
            )
            phone_field.clear()
            time.sleep(0.5)
            phone_field.send_keys(client_phone)
            time.sleep(1)

            # Сохраняем клиента
            save_button = self.wait_for_clickable(
                driver,
                (By.CSS_SELECTOR, "button.btn.btn-w-m.btn-success.add")
            )
            self.safe_click(driver, save_button)
            time.sleep(4)  # Увеличил ожидание после сохранения
            auth.take_screenshot("client_saved")

        with allure.step(f"ШАГ 5: Проверка, что клиент \
                         '{client_name}' создан"):
            # Даем время на сохранение данных
            time.sleep(2)

            # Обновляем страницу
            driver.refresh()
            time.sleep(4)  # Ожидание после обновления

            # Ждем загрузки таблицы
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                ".table tbody"))
            )
            time.sleep(2)

            # Прокручиваем страницу для загрузки всех клиентов
            driver.execute_script("window.scrollTo(0, document.body.\
                                  scrollHeight);")
            time.sleep(3)

            # Ищем созданного клиента
            client_found = False

            # Поиск по имени
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    f"//a[contains(text(), \
                                                        '{client_name}')]"))
                )
                client_found = True
                allure.attach("Клиент найден по имени",
                              name="client_found_by_name",
                              attachment_type=allure.attachment_type.TEXT)
                auth.take_screenshot("client_found_in_list")
            except TimeoutException:
                allure.attach("Клиент не найден по имени, пробуем "
                              "другие способы",
                              name="client_not_found_by_name",
                              attachment_type=allure.attachment_type.TEXT)

            # Если не нашли по имени, ищем по телефону
            if not client_found:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        f"//div\
                                                        [contains(text(), \
                                                        '{client_phone}')]"))
                    )
                    client_found = True
                    allure.attach(f"Клиент найден по телефону: {client_phone}",
                                  name="client_found_by_phone",
                                  attachment_type=allure.attachment_type.TEXT)
                    auth.take_screenshot("client_found_by_phone")
                except TimeoutException:
                    pass

            # Если все еще не нашли, ищем среди всех клиентов
            if not client_found:
                all_clients = driver.find_elements(By.CSS_SELECTOR,
                                                   ".v-table__v-table-body")
                for client in all_clients:
                    if client_name in client.text:
                        client_found = True
                        allure.attach(f"Клиент найден среди всех: \
                                      {client.text}",
                                      name="client_found_in_all",
                                      attachment_type=allure.
                                      attachment_type.TEXT)
                        break

            # Проверяем результат
            assert client_found, f"❌ Клиент '{client_name}' \
                с телефоном '{client_phone}' \
                не найден в списке после создания"

            allure.attach(
                f"✅ Клиент '{client_name}' успешно создан и найден в списке",
                name="test_result",
                attachment_type=allure.attachment_type.TEXT
            )


class TestYclientsFinanceReport:
    """Тест финансового отчета"""

    @pytest.fixture
    def driver(self):
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches",
                                        ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')

        # Настройка для загрузки файлов
        download_dir = r"C:\Downloads"
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)
        driver.maximize_window()
        driver.set_page_load_timeout(60)

        yield driver
        driver.quit()

    def click_with_scroll(self, driver, element):
        """Клик по элементу с прокруткой и обработкой перекрытия"""
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: "
                                  "'center', behavior: 'smooth'});", element)
            time.sleep(0.5)
            element.click()
            return True
        except ElementClickInterceptedException:
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                pass
        except Exception:
            try:
                ActionChains(driver).move_to_element(element).\
                    click().perform()
                return True
            except Exception:
                pass
        return False

    def check_downloaded_file(self, download_dir=r"C:\Downloads",
                              timeout=30):
        """Проверка, что файл скачался"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Ищем файлы .xlsx или .csv
            files = glob.glob(os.path.join(download_dir, "*.xlsx")) + \
                    glob.glob(os.path.join(download_dir, "*.csv")) + \
                    glob.glob(os.path.join(download_dir, "*.xls"))

            if files:
                # Берем самый новый файл
                latest_file = max(files, key=os.path.getctime)
                file_size = os.path.getsize(latest_file)
                if file_size > 0:
                    return latest_file, file_size
            time.sleep(1)
        return None, 0

    def cleanup_downloads(self, download_dir=r"C:\Downloads"):
        """Очистка папки загрузок от временных файлов"""
        try:
            for file in glob.glob(os.path.join(download_dir,
                                               "*.crdownload")):
                os.remove(file)
        except Exception:
            pass

    @pytest.mark.ui
    @allure.title("Тест формирования финансового отчета")
    @allure.description("Авторизация, выбор периода, "
                        "формирование отчета и выгрузка в Excel")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.feature("Финансы")
    @allure.story("Финансовый отчет")
    def test_finance_report(self, driver):
        auth = YclientsAuth(driver)

        start_date = "01.03.2026"
        end_date = "31.03.2026"
        download_dir = r"C:\Downloads"

        # Очищаем старые временные файлы
        self.cleanup_downloads(download_dir)

        with allure.step("ШАГ 1: Авторизация"):
            auth.login()

        with allure.step("ШАГ 2: Переход в раздел 'Финансы'"):
            time.sleep(2)

            finance_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//span[contains(text(), "
                                            "'Финансы')]"))
            )
            self.click_with_scroll(driver, finance_menu)
            time.sleep(2)
            auth.take_screenshot("after_click_finance")

        with allure.step("ШАГ 3: Переход в 'Отчеты'"):
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            reports_link = None
            locators = [
                (By.XPATH, "//a[contains(@href, '/analytics/reports/') "
                 "and contains(text(), 'Отчеты')]"),
                (By.XPATH, "//a[contains(text(), 'Отчеты') \
                 and contains(@href, 'reports')]"),
                (By.LINK_TEXT, "Отчеты")
            ]

            for locator_type, locator_value in locators:
                try:
                    reports_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable
                        ((locator_type, locator_value))
                    )
                    if reports_link:
                        break
                except Exception:
                    continue

            if reports_link:
                if not self.click_with_scroll(driver, reports_link):
                    raise AssertionError("Не удалось \
                                         кликнуть по ссылке 'Отчеты'")
                time.sleep(2)
                auth.take_screenshot("reports_page")
            else:
                raise AssertionError("Не удалось найти ссылку 'Отчеты'")

        with allure.step("ШАГ 4: Переход в 'Финансовый отчет'"):
            finance_report_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "a[data-locator='link_\
                                                report.finances.period']"))
            )
            self.click_with_scroll(driver, finance_report_link)
            time.sleep(3)
            auth.take_screenshot("finance_report_page")

        with allure.step(f"ШАГ 5: Установка периода отчета с \
                         {start_date} по {end_date}"):
            start_date_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "input[name='start_date']"))
            )
            start_date_field.clear()
            start_date_field.send_keys(start_date)
            time.sleep(1)

            end_date_field = driver.find_element(By.CSS_SELECTOR,
                                                 "input[name='end_date']")
            end_date_field.clear()
            end_date_field.send_keys(end_date)
            time.sleep(1)

            auth.take_screenshot("dates_filled")
            allure.attach(
                f"Установлен период: {start_date} - {end_date}",
                name="report_period",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("ШАГ 6: Нажать кнопку 'Показать'"):
            show_button = driver.find_element(By.CSS_SELECTOR,
                                              "input[type='submit']\
                                                [value='Показать']")
            show_button.click()
            time.sleep(5)
            auth.take_screenshot("report_shown")

            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return \
                                           document.readyState") == "complete"
            )
            time.sleep(2)

        with allure.step("ШАГ 7: Проверка, что отчет сформирован"):
            # Проверка 1: Наличие таблицы с данными
            try:
                driver.find_element(By.CSS_SELECTOR,
                                    "table, .report-table, "
                                    ".finance-table")
                allure.attach("Таблица отчета найдена", name="table_found",
                              attachment_type=allure.attachment_type.TEXT)
                auth.take_screenshot("report_table")

                # Проверка 2: Наличие заголовков таблицы
                headers = driver.find_elements(By.CSS_SELECTOR,
                                               "th, .table-header")
                if headers:
                    header_texts = [h.text for h in headers if h.text]
                    allure.attach(
                        f"Заголовки таблицы: {', '.join(header_texts[:10])}",
                        name="table_headers",
                        attachment_type=allure.attachment_type.TEXT
                    )

                # Проверка 3: Наличие строк с данными
                rows = driver.find_elements(By.CSS_SELECTOR, "tr, .table-row")
                allure.attach(
                    f"Найдено строк в таблице: {len(rows)}",
                    name="row_count",
                    attachment_type=allure.attachment_type.TEXT
                )

                # Проверка 4: Проверка соответствия периода в отчете
                try:
                    period_text = driver.find_element(By.XPATH,
                                                      "//*[contains(text(), "
                                                      "'01.03.2026') "
                                                      "and contains(text(), "
                                                      "'31.03.2026')]")
                    if period_text:
                        allure.attach("Период в отчете соответствует \
                                      заданному",
                                      name="period_match",
                                      attachment_type=allure.
                                      attachment_type.TEXT)
                except Exception:
                    allure.attach("Период в отчете не найден",
                                  name="period_not_found",
                                  attachment_type=allure.
                                  attachment_type.TEXT)

            except Exception:
                # Если нет таблицы, проверяем наличие сообщения "Нет данных"
                try:
                    driver.find_element(By.XPATH,
                                        "//*[contains(text(),"
                                        " 'Нет данных')]")
                    allure.attach("Нет данных за выбранный период",
                                  name="no_data",
                                  attachment_type=allure.attachment_type.TEXT)
                except Exception:
                    pass

        with allure.step("ШАГ 8: Выгрузка в Excel"):
            # Ищем кнопку выгрузки
            excel_button = None
            excel_locators = [
                (By.CSS_SELECTOR, "a[data-to-excel='true']"),
                (By.XPATH, "//a[contains(@href, 'period_to_csv')]"),
                (By.XPATH, "//a[contains(text(), 'Выгрузить в Excel')]")
            ]

            for locator_type, locator_value in excel_locators:
                try:
                    excel_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((locator_type,
                                                    locator_value))
                    )
                    if excel_button:
                        break
                except Exception:
                    continue

            if excel_button:
                self.click_with_scroll(driver, excel_button)
                allure.attach("Кнопка 'Выгрузить в Excel' нажата",
                              name="excel_export",
                              attachment_type=allure.attachment_type.TEXT)

                # ШАГ 9: Проверка, что файл скачался
                with allure.step("ШАГ 9: Проверка скачивания файла"):
                    time.sleep(3)
                    downloaded_file, file_size = \
                        self.check_downloaded_file(download_dir, timeout=30)

                    if downloaded_file:
                        allure.attach(
                            f"Файл скачан: {os.path.basename
                                            (downloaded_file)}, \
                                Размер: {file_size} байт",
                            name="file_downloaded",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        auth.take_screenshot("excel_export_clicked")

                        # Проверка, что файл не пустой
                        assert file_size > 0, f"Скачанный файл пустой: \
                            {downloaded_file}"

                        # Проверка расширения файла
                        file_ext = os.path.splitext(downloaded_file)[1].lower()
                        assert file_ext in ['.xlsx', '.csv', '.xls'], \
                            f"Неверный формат файла: {file_ext}"

                        allure.attach(f"✅ Файл успешно скачан: \
                                      {os.path.basename(downloaded_file)}",
                                      name="download_success",
                                      attachment_type=allure.
                                      attachment_type.TEXT)
                    else:
                        allure.attach("❌ Файл не был скачан",
                                      name="download_failed",
                                      attachment_type=allure.
                                      attachment_type.TEXT)
                        raise AssertionError("Файл не был скачан \
                                             после нажатия кнопки "
                                             "'Выгрузить в Excel'")
            else:
                allure.attach("Кнопка выгрузки не найдена",
                              name="excel_button_not_found",
                              attachment_type=allure.attachment_type.TEXT)
                raise AssertionError("Не найдена кнопка выгрузки в Excel")

        with allure.step("ШАГ 10: Финальная проверка URL"):
            current_url = driver.current_url
            allure.attach(current_url, name="current_url",
                          attachment_type=allure.attachment_type.TEXT)
            auth.take_screenshot("final_state")

        allure.attach(
            "✅ Тест успешно завершен: отчет сформирован и выгружен в Excel",
            name="test_result",
            attachment_type=allure.attachment_type.TEXT
        )


class TestYclientsSaleCertificate:
    """Тест продажи сертификата и проверка в разделе Лояльность"""

    @pytest.fixture
    def driver(self):
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches",
                                        ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)
        driver.maximize_window()

        yield driver
        driver.quit()

    def safe_click(self, driver, element, wait_time=0.5):
        """Безопасный клик по элементу с несколькими попытками"""
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: \
                                  'center', behavior: 'smooth'});", element)
            time.sleep(wait_time)
            element.click()
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                try:
                    ActionChains(driver).move_to_element(element).\
                        click().perform()
                    return True
                except Exception:
                    return False

    def safe_send_keys(self, driver, element, text):
        """Безопасный ввод текста"""
        try:
            element.clear()
            element.send_keys(text)
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].value = '';", element)
                driver.execute_script("arguments[0].value = arguments[1];",
                                      element, text)
                return True
            except Exception:
                try:
                    element.click()
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)
                    element.send_keys(text)
                    return True
                except Exception:
                    return False

    def select_from_dropdown(self, driver, text=None, index=0):
        """Выбрать элемент из выпадающего списка"""
        try:
            time.sleep(0.5)
            option_locators = [
                (By.CSS_SELECTOR, ".q-item"),
                (By.CSS_SELECTOR, "[role='option']"),
                (By.XPATH, "//div[contains(@class, 'q-item')]")
            ]

            for locator in option_locators:
                try:
                    if text:
                        option = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH,
                                                        f"//div[contains\
                                                        (@class, 'q-item') \
                                                        and \
                                                        contains(text(), \
                                                        '{text}')]"))
                        )
                        if option:
                            self.safe_click(driver, option)
                            return True
                    else:
                        options = WebDriverWait(driver, 3).until(
                            EC.presence_of_all_elements_located(locator)
                        )
                        if options and len(options) > index:
                            self.safe_click(driver, options[index])
                            return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    @pytest.mark.ui
    @allure.title("Тест продажи сертификата и проверка \
                  в разделе Лояльность")
    @allure.description("Авторизация, продажа сертификата клиенту Мария, \
                        сохранение кода и проверка в разделе Лояльность")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.feature("Продажи")
    @allure.story("Продажа сертификата")
    def test_sale_certificate_and_verify(self, driver):
        auth = YclientsAuth(driver)

        # Данные для теста
        client_name = "Мария"
        certificate_name = "Приведи друга"
        generated_code = None

        with allure.step("ШАГ 1: Авторизация"):
            auth.login()

        with allure.step("ШАГ 2: Открыть форму продажи"):
            sale_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "button.q-btn-dropdown"))
            )
            self.safe_click(driver, sale_button)
            time.sleep(1)
            auth.take_screenshot("dropdown_opened")

        with allure.step("ШАГ 3: Выбрать 'Сертификат'"):
            cert_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "button[data-locator=\
                                                'button_sale_certificates']"))
            )
            self.safe_click(driver, cert_button)
            time.sleep(2)
            auth.take_screenshot("certificate_form_opened")

        with allure.step(f"ШАГ 4: Ввести имя клиента: {client_name}"):
            name_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "input[data-locator=\
                                                    'client-name']"))
            )
            self.safe_send_keys(driver, name_field, client_name)
            time.sleep(1.5)
            auth.take_screenshot("client_name_entered")

        with allure.step("ШАГ 5: Выбрать клиента из выпадающего списка"):
            time.sleep(1)
            if self.select_from_dropdown(driver, index=0):
                allure.attach("Клиент выбран", name="client_selected",
                              attachment_type=allure.attachment_type.TEXT)
                time.sleep(1)
                auth.take_screenshot("client_selected")

        with allure.step(f"ШАГ 6: Ввести название сертификата: \
                         {certificate_name}"):
            goods_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "input[data-locator=\
                                                    'goods_selling_\
                                                        goods_table_\
                                                            row_good']"))
            )
            self.safe_send_keys(driver, goods_field, certificate_name)
            time.sleep(2)
            auth.take_screenshot("certificate_name_entered")

        with allure.step("ШАГ 7: Выбрать сертификат из выпадающего списка"):
            time.sleep(1)
            if self.select_from_dropdown(driver, index=0):
                allure.attach("Сертификат выбран", name="certificate_selected",
                              attachment_type=allure.attachment_type.TEXT)
                time.sleep(1)
                auth.take_screenshot("certificate_selected")
            else:
                goods_field.send_keys(Keys.ENTER)

        with allure.step("ШАГ 8: Выбрать сотрудника и \
                         сгенерировать код сертификата"):
            # Выбираем сотрудника
            employee_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".q-select"))
            )
            self.safe_click(driver, employee_select)
            time.sleep(1)
            self.select_from_dropdown(driver, index=0)
            time.sleep(1)

            # Генерируем код через AI
            ai_icon = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "i.my-icon-ds-ai"))
            )
            self.safe_click(driver, ai_icon)
            time.sleep(2)
            auth.take_screenshot("ai_icon_clicked")

            code_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "input[data-locator=\
                                                    'certificate-input']"))
            )
            generated_code = code_field.get_attribute("value")

            allure.attach(generated_code, name="generated_certificate_code",
                          attachment_type=allure.attachment_type.TEXT)
            print(f"✅ Сгенерирован код сертификата: {generated_code}")

        with allure.step("ШАГ 9: Сохранить и оплатить"):
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "button[data-locator=\
                                                'go-to-payment-button']"))
            )
            self.safe_click(driver, save_button)
            time.sleep(3)
            auth.take_screenshot("payment_screen")

        with allure.step("ШАГ 10: Проверка, что мы в окне оплаты"):
            # Проверяем, что находимся в окне оплаты
            try:
                payment_modal = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "div[data-locator=\
                                                        'modal_header_\
                                                            title']"))
                )
                assert "Продажа товара" in payment_modal.text or \
                    "Оплата" in payment_modal.text, \
                    f"Неверный заголовок модального окна: {payment_modal.text}"
                allure.attach("Подтверждено нахождение в окне оплаты",
                              name="payment_modal_verified",
                              attachment_type=allure.attachment_type.TEXT)
            except Exception:
                # Делаем скриншот для отладки
                auth.take_screenshot("payment_modal_not_found")
                raise AssertionError("Не удалось найти окно оплаты после \
                                     нажатия 'Сохранить и оплатить'")


class TestYclientsCreateService:
    """Тест создания новой услуги"""

    @pytest.fixture
    def driver(self):
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches",
                                        ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.maximize_window()

        yield driver
        driver.quit()

    def safe_click(self, driver, element, wait_time=0.5):
        """Безопасный клик по элементу с несколькими попытками"""
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: "
                                  "'center', behavior: 'smooth'});", element)
            time.sleep(wait_time)
            element.click()
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                try:
                    ActionChains(driver).move_to_element(element).\
                        click().perform()
                    return True
                except Exception:
                    return False

    def safe_send_keys(self, driver, element, text):
        """Безопасный ввод текста"""
        try:
            element.clear()
            element.send_keys(text)
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].value = '';", element)
                driver.execute_script("arguments[0].value = arguments[1];",
                                      element, text)
                return True
            except Exception:
                try:
                    element.click()
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)
                    element.send_keys(text)
                    return True
                except Exception:
                    return False

    @pytest.mark.ui
    @allure.title("Тест создания новой услуги")
    @allure.description("Авторизация и создание услуги 'Покрытие' \
                        в настройках аналитики")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.feature("Аналитика")
    @allure.story("Создание услуги")
    def test_create_service(self, driver):
        auth = YclientsAuth(driver)

        # Название новой услуги
        service_name = "Покрытие"

        with allure.step("ШАГ 1: Авторизация"):
            auth.login()

        with allure.step("ШАГ 2: Переход в раздел 'Аналитика'"):
            # Ищем меню "Аналитика"
            analytics_menu = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "//a[contains(@href, "
                                                "'/analytics/')]//span\
                                                [contains(text(), "
                                                "'Аналитика')]"))
            )
            self.safe_click(driver, analytics_menu)
            time.sleep(2)
            auth.take_screenshot("analytics_menu_clicked")

        with allure.step("ШАГ 3: Переход в 'Настройки'"):
            # Ищем ссылку "Настройки"
            settings_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "//a[contains(@href, "
                                                "'/settings/menu/') "
                                                "and contains(text(), "
                                                "'Настройки')]"))
            )
            self.safe_click(driver, settings_link)
            time.sleep(2)
            auth.take_screenshot("settings_page")

        with allure.step("ШАГ 4: Переход в 'Услуги'"):
            # Ищем ссылку "Услуги"
            services_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "a[data-locator="
                                            "'link_settings_\
                                            basic.services']"))
            )
            self.safe_click(driver, services_link)
            time.sleep(3)
            auth.take_screenshot("services_page")

        with allure.step("ШАГ 5: Нажать кнопку создания услуги"):
            # Ищем кнопку создания (обычно это плюс или кнопка "Создать")
            create_button = None
            create_locators = [
                (By.CSS_SELECTOR, "button.y-core-simple-button"),
                (By.CSS_SELECTOR,
                 "y-core-button[data-locator='y-core-button']."
                 "erp-services-categories-list-controls__create-dropdown"),
                (By.XPATH, "//button[contains(@class, "
                 "'y-core-simple-button')]"),
                (By.CSS_SELECTOR, "[data-locator*='create']")
            ]

            for locator in create_locators:
                try:
                    create_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    if create_button:
                        break
                except Exception:
                    continue

            if not create_button:
                raise AssertionError("Не найдена кнопка создания услуги")

            self.safe_click(driver, create_button)
            time.sleep(2)
            auth.take_screenshot("create_button_clicked")

        with allure.step("ШАГ 6: Выбрать категорию услуги"):
            category_card = None
            category_locators = [
                (By.CSS_SELECTOR, "y-core-card-button.\
                 create-services-modal__card"),
                (By.CSS_SELECTOR, "y-core-card-button[data-locator=\
                 'y-core-card-button']"),
                (By.CSS_SELECTOR, ".create-services-modal__card"),
                (By.XPATH, "//y-core-card-button[contains(@class, \
                 'create-services-modal__card')]"),
                (By.XPATH, "//y-core-card-button[contains(@class, \
                 'y-core-card-button')]"),
                (By.CSS_SELECTOR, "[data-locator='y-core-card-button']")
            ]

            for locator in category_locators:
                try:
                    category_card = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    if category_card:
                        break
                except Exception:
                    continue

            if category_card:
                self.safe_click(driver, category_card)
                time.sleep(1)
                auth.take_screenshot("category_selected")
                allure.attach("Категория услуги выбрана",
                              name="category_selected",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                allure.attach("Категория не найдена, возможно она уже выбрана",
                              name="category_not_found",
                              attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"ШАГ 7: Ввести название услуги: {service_name}"):
            name_field = None
            name_locators = [
                (By.CSS_SELECTOR, "input.q-field__native.q-placeholder"),
                (By.XPATH, "//input[@placeholder='Например, стрижка']"),
                (By.CSS_SELECTOR, "input[placeholder='Например, стрижка']"),
                (By.CSS_SELECTOR, "input.q-field__native")
            ]

            # Ищем все поля ввода
            all_inputs = driver.find_elements(By.CSS_SELECTOR,
                                              "input.q-field__native")

            for input_field in all_inputs:
                try:
                    placeholder = input_field.get_attribute("placeholder")
                    # Исключаем поле с плейсхолдером "Поиск услуги"
                    if placeholder and "Поиск услуги" in placeholder:
                        continue
                    # Ищем поле с нужным плейсхолдером
                    if placeholder and "Например, стрижка" in placeholder:
                        name_field = input_field
                        break
                except Exception:
                    continue

            # Если не нашли по плейсхолдеру, пробуем локаторы
            if not name_field:
                for locator in name_locators:
                    try:
                        name_field = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(locator)
                        )
                        # Проверяем, что это не поле поиска
                        placeholder = name_field.get_attribute("placeholder")
                        if placeholder and "Поиск услуги" in placeholder:
                            name_field = None
                            continue
                        if name_field and name_field.is_displayed():
                            break
                    except Exception:
                        continue

            if name_field:
                self.safe_send_keys(driver, name_field, service_name)
                time.sleep(1)
                auth.take_screenshot("service_name_entered")
                allure.attach(f"Введено название: {service_name}",
                              name="service_name",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                raise AssertionError("Поле ввода названия услуги не найдено")

        with allure.step("ШАГ 8: Нажать кнопку 'Создать'"):
            save_button = None
            save_locators = [
                # Точный селектор из вашего HTML
                (By.CSS_SELECTOR, "button[data-locator='save_btn']"),
                (By.CSS_SELECTOR, "button.services-settings-\
                 salon-controls__btn"),
                (By.XPATH, "//button[contains(@class, \
                 'services-settings-salon-controls__btn')]"),
                (By.XPATH, "//button[contains(text(), 'Создать')]"),
                (By.CSS_SELECTOR, "button.yc-btn")
            ]

            for locator in save_locators:
                try:
                    save_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    if save_button:
                        break
                except Exception:
                    continue

            if save_button:
                self.safe_click(driver, save_button)
                time.sleep(3)
                auth.take_screenshot("save_button_clicked")
                allure.attach("Кнопка 'Создать' нажата", name="save_clicked",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                raise AssertionError("Кнопка 'Создать' не найдена")

        with allure.step("ШАГ 9: Проверка создания услуги"):
            # Ждем появления сообщения об успехе
            time.sleep(2)

            # Проверка 1: Сообщение об успешном создании (опционально)
            try:
                success_message = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    ".alert-success, \
                                                        .toast-success, \
                                                        .notification-\
                                                            success"))
                )
                success_text = success_message.text
                allure.attach(success_text, name="success_message",
                              attachment_type=allure.attachment_type.TEXT)
            except Exception:
                allure.attach("Сообщение об успешном создании не найдено",
                              name="no_success_message",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("ШАГ 9.1: Вернуться к списку услуг"):
                # Ищем кнопку "Назад"
                back_button = None
                back_locators = [
                                 (By.XPATH, "//span[contains(text(), "
                                  "'Назад')]/ancestor::button"),
                                 (By.CSS_SELECTOR, "button.q-btn"),
                                 (By.XPATH, "//button[.//span[contains(text(),"
                                  "'Назад')]]"),
                                 (By.CSS_SELECTOR, "button"
                                  "[aria-label='Назад']"),
                                 (By.XPATH, "//i[contains(@class, \
                                  'my-icon-ds-arrow-left')]/ancestor::button")
                ]

                for locator in back_locators:
                    try:
                        back_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(locator)
                        )
                        if back_button and back_button.is_displayed():
                            break
                    except Exception:
                        continue

                if back_button:
                    # Скроллим к кнопке
                    driver.execute_script("arguments[0].\
                                          scrollIntoView({block: \
                                          'center'});", back_button)
                    time.sleep(1)
                    self.safe_click(driver, back_button)
                    time.sleep(3)
                    auth.take_screenshot("back_to_list")
                    allure.attach("Нажата кнопка 'Назад'", name="back_clicked",
                                  attachment_type=allure.attachment_type.TEXT)
                else:
                    # Если не нашли кнопку "Назад", пробуем нажать ESC
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(2)
                    allure.attach("Возврат через ESC", name="back_via_esc",
                                  attachment_type=allure.attachment_type.TEXT)

            with allure.step("ШАГ 9.2: Найти и раскрыть категорию с услугой"):
                # Ищем элемент категории (активатор)
                category_activator = None
                category_locators = [
                    (By.CSS_SELECTOR, "y-core-collapse-item"),
                    (By.CSS_SELECTOR, "div.y-core-collapse-item__activator"),
                    (By.XPATH, "//div[contains(@class, \
                     'y-core-collapse-item__activator')]"),
                    (By.XPATH, "//div[contains(text(), 'Содержит услуг:')]"),
                    (By.CSS_SELECTOR, "y-core-collapse-item__icon")
                ]

                for locator in category_locators:
                    try:
                        category_activator = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(locator)
                        )
                        if category_activator:
                            break
                    except Exception:
                        continue

                if category_activator:
                    self.safe_click(driver, category_activator)
                    time.sleep(2)
                    auth.take_screenshot("category_expanded")
                    allure.attach("Категория раскрыта",
                                  name="category_expanded",
                                  attachment_type=allure.attachment_type.TEXT)
                else:
                    allure.attach("Категория не найдена",
                                  name="category_not_found",
                                  attachment_type=allure.attachment_type.TEXT)

            with allure.step(f"ШАГ 9.3: Поиск услуги '{service_name}' \
                             в списке"):
                service_found = False
                service_element = None

                # Локаторы для поиска услуги
                service_locators = [
                    (By.XPATH, f"//a[contains(text(), '{service_name}')]"),
                    (By.XPATH, f"//*[contains(@class, \
                     'service-table-row-title__link') \
                     and contains(text(), '{service_name}')]"),
                    (By.XPATH, f"//div[contains(@class, 'service-table-row')]\
                     //*[contains(text(), '{service_name}')]"),
                    (By.XPATH, f"//*[contains(text(), '{service_name}') \
                     and not(contains(@placeholder, 'Поиск'))]")
                ]

                for locator in service_locators:
                    try:
                        service_element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(locator)
                        )
                        if service_element and service_element.is_displayed():
                            service_found = True
                            allure.attach(f"Услуга найдена по локатору: \
                                          {locator}",
                                          name="service_location",
                                          attachment_type=allure.
                                          attachment_type.TEXT)
                            break
                    except Exception:
                        continue

                # ASSERT: услуга должна быть найдена
                assert service_found, f"❌ Услуга '{service_name}' \
                    не найдена в списке после создания"


class TestYclientsDeleteService:
    """Тест удаления услуги"""

    @pytest.fixture
    def driver(self):
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches",
                                        ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.maximize_window()

        yield driver
        driver.quit()

    def safe_click(self, driver, element, wait_time=0.5):
        """Безопасный клик по элементу с несколькими попытками"""
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: \
                                  'center', behavior: 'smooth'});", element)
            time.sleep(wait_time)
            element.click()
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                try:
                    ActionChains(driver).move_to_element(element).\
                                         click().perform()
                    return True
                except Exception:
                    return False

    def safe_send_keys(self, driver, element, text):
        """Безопасный ввод текста"""
        try:
            element.clear()
            element.send_keys(text)
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].value = '';", element)
                driver.execute_script("arguments[0].value = arguments[1];",
                                      element, text)
                return True
            except Exception:
                try:
                    element.click()
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)
                    element.send_keys(text)
                    return True
                except Exception:
                    return False

    @pytest.mark.ui
    @allure.title("Тест удаления услуги")
    @allure.description("Авторизация и удаление услуги \
                        'Покрытие' в настройках аналитики")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.feature("Аналитика")
    @allure.story("Удаление услуги")
    def test_delete_service(self, driver):
        auth = YclientsAuth(driver)

        # Название услуги для удаления
        service_name = "Покрытие"
        confirm_text = "Удалить"

        with allure.step("ШАГ 1: Авторизация"):
            auth.login()

        with allure.step("ШАГ 2: Переход в раздел 'Аналитика'"):
            analytics_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//a[contains(@href, \
                                                '/analytics/')]\
                                            //span[contains(text(), \
                                                'Аналитика')]"))
            )
            self.safe_click(driver, analytics_menu)
            time.sleep(2)
            auth.take_screenshot("analytics_menu_clicked")

        with allure.step("ШАГ 3: Переход в 'Настройки'"):
            settings_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//a[contains(@href, \
                                                '/settings/menu/') \
                                            and contains(text(), \
                                                'Настройки')]"))
            )
            self.safe_click(driver, settings_link)
            time.sleep(2)
            auth.take_screenshot("settings_page")

        with allure.step("ШАГ 4: Переход в 'Услуги'"):
            services_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "a[data-locator='link_\
                                                settings_basic.services']"))
            )
            self.safe_click(driver, services_link)
            time.sleep(3)
            auth.take_screenshot("services_page")

        with allure.step("ШАГ 5: Найти и раскрыть категорию с услугой"):
            # Ищем элемент категории (активатор)
            category_activator = None
            category_locators = [
                (By.CSS_SELECTOR, "y-core-collapse-item"),
                (By.CSS_SELECTOR, "div.y-core-collapse-item__activator"),
                (By.XPATH, "//div[contains(@class, \
                 'y-core-collapse-item__activator')]"),
                (By.XPATH, "//div[contains(text(), 'Содержит услуг:')]"),
                (By.CSS_SELECTOR, "y-core-collapse-item__icon")
            ]

            for locator in category_locators:
                try:
                    category_activator = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(locator)
                    )
                    if category_activator:
                        break
                except Exception:
                    continue

            if category_activator:
                self.safe_click(driver, category_activator)
                time.sleep(2)
                auth.take_screenshot("category_expanded")
                allure.attach("Категория раскрыта",
                              name="category_expanded",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                allure.attach("Категория не найдена",
                              name="category_not_found",
                              attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"ШАГ 6: Найти услугу '{service_name}' \
                         и открыть в новой вкладке"):
            service_link = None
            service_locators = [
                (By.CSS_SELECTOR, f"a.service-table-row-title__link\
                 [href*='{service_name}']"),
                (By.XPATH, f"//a[contains(text(), '{service_name}')]"),
                (By.XPATH, f"//a[@target='_blank' \
                 and contains(text(), '{service_name}')]")
            ]

            for locator in service_locators:
                try:
                    service_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    if service_link:
                        break
                except Exception:
                    continue

            if service_link:
                # Получаем текущее количество вкладок
                main_window = driver.current_window_handle
                current_windows = driver.window_handles

                # Кликаем по ссылке
                self.safe_click(driver, service_link)
                time.sleep(2)

                # Ждем появления новой вкладки
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.window_handles) > len(current_windows)
                )

                # Переключаемся на новую вкладку
                new_window = [w for w in driver.window_handles if w !=
                              main_window][0]
                driver.switch_to.window(new_window)

                auth.take_screenshot("service_opened")
                allure.attach(f"Услуга '{service_name}' \
                              открыта в новой вкладке", name="service_opened",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                raise AssertionError(f"Услуга '{service_name}' не найдена")

        with allure.step("ШАГ 7: Нажать кнопку 'Удалить услугу'"):
            delete_button = None
            delete_locators = [
                (By.CSS_SELECTOR, "button[data-locator=\
                 'delete_service_btn']"),
                (By.XPATH, "//button[contains(text(), 'Удалить услугу')]"),
                (By.CSS_SELECTOR, "button.services-settings-\
                 salon-controls__btn"),
                (By.XPATH, "//button[contains(@class, \
                 'services-settings-salon-controls__btn') \
                 and contains(text(), 'Удалить')]")
                ]

            for locator in delete_locators:
                try:
                    delete_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    if delete_button:
                        break
                except Exception:
                    continue

            if delete_button:
                self.safe_click(driver, delete_button)
                time.sleep(1)
                auth.take_screenshot("delete_button_clicked")
                allure.attach("Кнопка 'Удалить услугу' нажата",
                              name="delete_clicked",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                raise AssertionError("Кнопка 'Удалить услугу' не найдена")

        with allure.step(f"ШАГ 8: Ввести '{confirm_text}' для подтверждения"):
            confirm_field = None
            confirm_locators = [
                (By.CSS_SELECTOR, "input[data-locator=\
                 'input_confirm_delete']"),
                (By.XPATH, "//input[@placeholder='Удалить']"),
                (By.CSS_SELECTOR, "input.q-field__native.q-placeholder")
            ]

            for locator in confirm_locators:
                try:
                    confirm_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(locator)
                    )
                    if confirm_field and confirm_field.is_displayed():
                        break
                except Exception:
                    continue

            if confirm_field:
                self.safe_send_keys(driver, confirm_field, confirm_text)
                time.sleep(1)
                auth.take_screenshot("confirm_text_entered")
                allure.attach(f"Введено подтверждение: {confirm_text}",
                              name="confirm_entered",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                raise AssertionError("Поле подтверждения "
                                     "удаления не найдено")

        with allure.step("ШАГ 9: Нажать кнопку 'Удалить'"):
            confirm_delete_button = None
            confirm_locators = [
                (By.CSS_SELECTOR, "button[data-locator=\
                 'apply_delete_button']"),
                (By.XPATH, "//button[contains(text(), 'Удалить') \
                 and not(contains(text(), 'услугу'))]"),
                (By.CSS_SELECTOR, "button.yc-btn[data-locator=\
                 'apply_delete_button']")
            ]

            for locator in confirm_locators:
                try:
                    confirm_delete_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    if confirm_delete_button:
                        break
                except Exception:
                    continue

            if confirm_delete_button:
                self.safe_click(driver, confirm_delete_button)
                time.sleep(3)
                auth.take_screenshot("confirm_delete_clicked")
                allure.attach("Кнопка 'Удалить' нажата",
                              name="confirm_delete_clicked",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                raise AssertionError("Кнопка подтверждения \
                                     удаления не найдена")

        # ... после удаления нужно закрыть вкладку и вернуться

        with allure.step("ШАГ 10: Проверка удаления услуги"):
            time.sleep(2)

            # Проверяем наличие сообщения об успешном удалении
            try:
                success_message = driver.find_element(By.CSS_SELECTOR,
                                                      ".alert-success, \
                                                        .toast-success, \
                                                        .notification-success")
                if success_message:
                    allure.attach(success_message.text, name="success_message",
                                  attachment_type=allure.attachment_type.TEXT)
            except Exception:
                pass

            # Закрываем текущую вкладку и возвращаемся на главную
            driver.close()

            # Переключаемся обратно на основную вкладку
            main_window = driver.window_handles[0]
            driver.switch_to.window(main_window)
            time.sleep(2)

            # Обновляем страницу услуг
            driver.refresh()
            time.sleep(3)

            # Раскрываем категорию снова
            category_activator = None
            category_locators = [
                (By.CSS_SELECTOR, "y-core-collapse-item"),
                (By.CSS_SELECTOR, "div.y-core-collapse-item__activator"),
                (By.XPATH, "//div[contains(@class, \
                 'y-core-collapse-item__activator')]"),
                (By.XPATH, "//div[contains(text(), 'Содержит услуг:')]"),
                (By.CSS_SELECTOR, "y-core-collapse-item__icon")
            ]

            for locator in category_locators:
                try:
                    category_activator = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(locator)
                    )
                    if category_activator:
                        break
                except Exception:
                    continue

            if category_activator:
                self.safe_click(driver, category_activator)
                time.sleep(2)
                auth.take_screenshot("category_expanded")
                allure.attach("Категория раскрыта",
                              name="category_expanded",
                              attachment_type=allure.attachment_type.TEXT)
            else:
                allure.attach("Категория не найдена",
                              name="category_not_found",
                              attachment_type=allure.attachment_type.TEXT)

            # Ищем удаленную услугу
            service_exists = driver.find_elements(By.XPATH,
                                                  f"//a[contains(text(), \
                                                  '{service_name}')]")

            if not service_exists:
                allure.attach(f"✅ Услуга '{service_name}' успешно удалена",
                              name="service_deleted",
                              attachment_type=allure.attachment_type.TEXT)
                auth.take_screenshot("service_deleted_success")
            else:
                allure.attach(f"❌ Услуга '{service_name}' \
                              все еще присутствует",
                              name="service_still_exists",
                              attachment_type=allure.attachment_type.TEXT)
                auth.take_screenshot("service_not_deleted")
                raise AssertionError(f"Услуга '{service_name}' \
                                     не была удалена")

            # Проверка: услуга не должна присутствовать в списке
            service_elements = driver.find_elements(By.XPATH,
                                                    f"//a[contains(text(), \
                                                    '{service_name}')]")

            # ASSERT: услуга должна быть удалена
            assert len(service_elements) == 0, f"Услуга '{service_name}' \
                все еще присутствует на странице после удаления"

        with allure.step("ШАГ 11: Финальная проверка"):
            current_url = driver.current_url
            allure.attach(current_url, name="current_url",
                          attachment_type=allure.attachment_type.TEXT)
            auth.take_screenshot("final_state")

        allure.attach(
            f"✅ Тест удаления услуги '{service_name}' успешно завершен",
            name="test_result",
            attachment_type=allure.attachment_type.TEXT
        )
