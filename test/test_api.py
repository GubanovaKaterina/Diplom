import requests
import allure
import pytest
from datetime import datetime, timedelta

# Данные авторизации
login = 'gubanova.katerina@internet.ru'
password = 'chxe44'
base_url = 'https://api.yclients.com/api/v1'
bearer_token = 'kfmybpg59cagpga4ms5j'
partner_token = 1819386
id = 13990248
user_token = 'a3628804633cfc22113f7c37183e6234'
api_id = 15093
company_id = 1819386
staff_id = 5171175
service_id = 27725655

# Заголовки
headers = {
    "Authorization": f"{bearer_token}",
    "X-Custom-Auth": f"<Bearer {partner_token}>, <User {user_token}>",
    "Accept": "application/vnd.yclients.v2+json",
    "Content-Type": "application/json"
}

# Базовое тело запроса для создания
base_payload = {
    "phone": "79000000000",
    "fullname": "ДИМА",
    "email": "d@yclients.com",
    "code": "38829",
    "comment": "тестовая запись!",
    "type": "mobile",
    "notify_by_sms": 6,
    "notify_by_email": 24,
    "api_id": str(api_id),
    "custom_fields": {
        "my_client_custom_field": 789,
        "some_another_client_field": [
            "first client value",
            "next client value"
        ]
    },
    "appointments": [
        {
            "id": 1,
            "services": [service_id],
            "staff_id": staff_id,
            "datetime": "2026-04-02 12:00:00",
            "custom_fields": {
                "my_custom_field": 123,
                "some_another_field": [
                    "first value",
                    "next value"
                ]
            }
        }
    ]
}


@allure.step("Создание записи клиента")
def create_booking(booking_datetime="2026-04-02 12:00:00"):
    """POST запрос на создание записи клиента"""
    url = f"{base_url}/book_record/{company_id}"
    payload = base_payload.copy()
    payload["appointments"][0]["datetime"] = booking_datetime

    with allure.step("Отправка POST запроса на создание записи"):
        response = requests.post(url, headers=headers, json=payload)

    with allure.step("Проверка ответа"):
        allure.attach(str(response.status_code), name="Status Code",
                      attachment_type=allure.attachment_type.TEXT
                      )
        allure.attach(response.text, name="Response Body",
                      attachment_type=allure.attachment_type.JSON
                      )

        if response.status_code == 201:
            response_data = response.json()
            booking_info = response_data['data'][0]
            return {
                "record_id": booking_info.get('record_id'),
                "record_hash": booking_info.get('record_hash'),
                "success": True
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "response": response.text
            }


@allure.step("Получение информации о записи")
def get_booking_info(record_id, record_hash):
    """GET запрос на получение информации о записи"""
    url = f"{base_url}/book_record/{company_id}/{record_id}/{record_hash}"

    with allure.step("Отправка GET запроса"):
        response = requests.get(url, headers=headers)

    with allure.step("Проверка ответа"):
        allure.attach(str(response.status_code), name="Status Code",
                      attachment_type=allure.attachment_type.TEXT)
        allure.attach(response.text, name="Response Body",
                      attachment_type=allure.attachment_type.JSON)

        if response.status_code == 200:
            response_data = response.json()

            # Добавляем логирование для отладки
            if response_data.get('data'):
                allure.attach(f"Дата в ответе: \
                    {response_data['data'].get('datetime')}",
                    name="Raw datetime from API",
                    attachment_type=allure.attachment_type.TEXT)

            return response_data
        else:
            raise Exception(f"Ошибка получения информации. \
                Status: {response.status_code}"
                )


@allure.step("Изменение записи клиента")
def update_booking(record_id, record_hash, new_datetime, new_comment):
    """PUT запрос на изменение записи клиента"""
    url = f"{base_url}/book_record/{company_id}/{record_id}/{record_hash}"
    payload = {
        "datetime": new_datetime,
        "comment": new_comment
    }

    with allure.step("Отправка PUT запроса"):
        response = requests.put(url, headers=headers, json=payload)

    with allure.step("Проверка ответа"):
        allure.attach(str(response.status_code), name="Status Code",
                      attachment_type=allure.attachment_type.TEXT
                      )
        allure.attach(response.text, name="Response Body",
                      attachment_type=allure.attachment_type.JSON
                      )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Ошибка изменения записи. \
                            Status: {response.status_code}"
                            )


@allure.step("Удаление записи клиента")
def delete_booking(record_id, record_hash):
    """DELETE запрос на удаление записи клиента"""
    url = f"{base_url}/user/records/{record_id}/{record_hash}"

    with allure.step("Отправка DELETE запроса"):
        response = requests.delete(url, headers=headers)

    with allure.step("Проверка ответа"):
        allure.attach(str(response.status_code), name="Status Code",
                      attachment_type=allure.attachment_type.TEXT
                      )

        if response.status_code in [200, 204]:
            return {"success": True, "status_code": response.status_code}
        else:
            raise Exception(f"Ошибка удаления записи. \
                            Status: {response.status_code}"
                            )


# ==================== ПОЗИТИВНЫЕ ТЕСТЫ ====================
@pytest.mark.api
@allure.feature("Управление записями")
@allure.story("Создание записи")
@allure.title("Позитивный тест: Создание новой записи")
def test_create_booking_positive():
    """
    Тест 1: Создание новой записи
    Проверяет успешное создание записи и получение record_id
    """
    with allure.step("Создание записи на 12:00"):
        result = create_booking("2026-04-02 12:00:00")

    with allure.step("Проверка результата"):
        assert result["success"] is True, f"Запись не создана: {result}"
        assert result["record_id"] is not None, "Record ID не получен"
        assert result["record_hash"] is not None, "Record Hash не получен"

        allure.attach(str(result["record_id"]), name="Record ID",
                      attachment_type=allure.attachment_type.TEXT
                      )
        allure.attach(result["record_hash"], name="Record Hash",
                      attachment_type=allure.attachment_type.TEXT
                      )

    # Очистка: удаляем созданную запись
    with allure.step("Очистка: удаление созданной записи"):
        delete_booking(result["record_id"], result["record_hash"])

    print(f"\n✅ Тест пройден: Запись создана с ID {result['record_id']}")


@pytest.mark.api
@allure.feature("Управление записями")
@allure.story("Изменение записи")
@allure.title("Позитивный тест: Изменение существующей записи")
def test_update_booking_positive():
    """
    Тест 2: Изменение существующей записи
    Проверяет успешное изменение времени и комментария
    """
    # Подготовка: создаем запись
    with allure.step("Подготовка: создание записи"):
        create_result = create_booking("2026-04-02 12:00:00")
        assert create_result["success"] is True, \
            "Не удалось создать запись для теста"
        record_id = create_result["record_id"]
        record_hash = create_result["record_hash"]

    try:
        # Изменение записи
        with allure.step("Изменение времени записи на \
                         15:00 и комментария"):
            new_datetime = "2026-04-02 15:00:00"
            new_comment = "DODO!"
            update_result = update_booking(
                            record_id,
                            record_hash, new_datetime,
                            new_comment
            )

        with allure.step("Проверка результата изменения"):
            assert update_result["success"] is True, "Изменение не успешно"

        # Проверка, что изменения применились
        with allure.step("Проверка примененных изменений"):
            get_result = get_booking_info(record_id, record_hash)

            # Нормализуем форматы дат для сравнения
            actual_datetime = get_result["data"]["datetime"]

            # Функция нормализации даты
            def normalize_datetime(dt_str):
                """Приводит дату к формату YYYY-MM-DD HH:MM:SS"""
                # Если дата в формате ISO с часовым поясом
                if 'T' in dt_str:
                    # Убираем часовой пояс и заменяем T на пробел
                    dt_str = dt_str.split('+')[0]  # Убираем +0300
                    dt_str = dt_str.replace('T', ' ')
                    # Обрезаем до 19 символов (YYYY-MM-DD HH:MM:SS)
                    return dt_str[:19]
                return dt_str

            normalized_actual = normalize_datetime(actual_datetime)

            allure.attach(f"Ожидаемая дата: {new_datetime}",
                          name="Expected Datetime",
                          attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Фактическая дата (сырая): {actual_datetime}",
                          name="Actual Datetime (raw)",
                          attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Фактическая дата (нормализованная): \
                          {normalized_actual}",
                          name="Actual Datetime (normalized)",
                          attachment_type=allure.attachment_type.TEXT)

            assert normalized_actual == new_datetime, \
                f"Дата не обновилась. Ожидалось: {new_datetime}, \
                    Получено: {normalized_actual} (сырая: {actual_datetime})"

            assert get_result["data"]["comment"] == new_comment, \
                f"Комментарий не обновился. Ожидалось: {new_comment}, \
                    Получено: {get_result['data']['comment']}"

            print(f"\n✅ Тест пройден: Запись {record_id} успешно изменена")
            print(f"   Дата изменена с 12:00 на {normalized_actual}")
            print(f"   Комментарий изменен на: {new_comment}")

    finally:
        # Очистка: удаляем запись
        with allure.step("Очистка: удаление записи"):
            delete_booking(record_id, record_hash)


@pytest.mark.api
@allure.feature("Управление записями")
@allure.story("Удаление записи")
@allure.title("Позитивный тест: Удаление существующей записи")
def test_delete_booking_positive():
    """
    Тест 3: Удаление существующей записи
    Проверяет успешное удаление записи
    """
    # Подготовка: создаем запись
    with allure.step("Подготовка: создание записи"):
        create_result = create_booking("2026-04-02 12:00:00")
        assert create_result["success"] is True, \
            "Не удалось создать запись для теста"
        record_id = create_result["record_id"]
        record_hash = create_result["record_hash"]

    # Удаление записи
    with allure.step("Удаление записи"):
        delete_result = delete_booking(record_id, record_hash)

    with allure.step("Проверка успешного удаления"):
        assert delete_result["success"] is True, "Удаление не успешно"
        assert delete_result["status_code"] in [200, 204], \
            f"Неверный статус код: {delete_result['status_code']}"

    # Проверка, что запись действительно удалена
    with allure.step("Проверка, что запись больше не существует"):
        try:
            get_booking_info(record_id, record_hash)
            assert False, "Запись все еще существует после удаления"
        except Exception as e:
            assert "404" in str(e) or "Not Found" in str(e), \
                f"Неожиданная ошибка: {e}"
            allure.attach("Запись не найдена (404) - ожидаемый результат",
                          name="Verification",
                          attachment_type=allure.attachment_type.TEXT)

    print(f"\n✅ Тест пройден: Запись {record_id} успешно удалена")


# ==================== НЕГАТИВНЫЕ ТЕСТЫ ====================
@pytest.mark.api
@allure.feature("Управление записями")
@allure.story("Негативные сценарии")
@allure.title("Негативный тест: Попытка записи на занятое время")
def test_create_booking_busy_time():
    """
    Негативный тест 1: Попытка записи на занятое время
    Ожидаемый результат: статус код 422 (Unprocessable Entity)
    """
    # Подготовка: создаем первую запись на 12:00
    with allure.step("Подготовка: создание первой записи на 12:00"):
        first_booking = create_booking("2026-04-02 12:00:00")
        assert first_booking["success"] is True, \
            "Не удалось создать первую запись"
        record_id_1 = first_booking["record_id"]
        record_hash_1 = first_booking["record_hash"]
        allure.attach(str(record_id_1), name="Первая запись ID",
                      attachment_type=allure.attachment_type.TEXT)

    try:
        # Попытка создать вторую запись на то же время
        with allure.step("Попытка создать вторую запись \
                        на то же время (12:00)"):
            second_booking = create_booking("2026-04-02 12:00:00")

        with allure.step("Проверка результата"):
            # Ожидаем, что запись не создастся
            assert second_booking["success"] is False, \
                "Вторая запись не должна была создаться"
            assert second_booking["status_code"] == 422, \
                f"Ожидался статус 422, получен {second_booking['status_code']}"

            allure.attach(f"Статус код: {second_booking['status_code']}",
                          name="Expected 422",
                          attachment_type=allure.attachment_type.TEXT)
            allure.attach(second_booking["response"],
                          name="Error Response",
                          attachment_type=allure.attachment_type.TEXT)

    finally:
        # Очистка: удаляем первую запись
        with allure.step("Очистка: удаление первой записи"):
            delete_booking(record_id_1, record_hash_1)


@pytest.mark.api
@allure.feature("Управление записями")
@allure.story("Негативные сценарии")
@allure.title("Негативный тест: Попытка записи на прошедшую дату")
def test_create_booking_past_date():
    """
    Негативный тест 2: Попытка записи на прошедшую дату
    Ожидаемый результат: статус код 422 (Unprocessable Entity)
    """
    # Формируем прошедшую дату (вчера)
    past_date = (datetime.now() -
                 timedelta(days=1)).strftime("%Y-%m-%d 12:00:00")

    with allure.step(f"Попытка создать запись на прошедшую дату: {past_date}"):
        result = create_booking(past_date)

    with allure.step("Проверка результата"):
        # Ожидаем, что запись не создастся
        assert result["success"] is False, \
            "Запись на прошедшую дату не должна создаваться"
        assert result["status_code"] == 422, \
            f"Ожидался статус 422, получен {result['status_code']}"

        allure.attach(f"Дата: {past_date}", name="Past date",
                      attachment_type=allure.attachment_type.TEXT)
        allure.attach(f"Статус код: {result['status_code']}",
                      name="Expected 422",
                      attachment_type=allure.attachment_type.TEXT)
        allure.attach(result["response"],
                      name="Error Response",
                      attachment_type=allure.attachment_type.TEXT)

        print("\n✅ Негативный тест пройден: \
              Запись на прошедшую дату отклонена (422)")
