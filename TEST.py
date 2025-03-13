from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# 🔹 Замените на путь к вашему файлу service_account.json
SERVICE_ACCOUNT_FILE = "1.json"

# 🔹 Замените на ваш ID таблицы Google Sheets
SPREADSHEET_ID = "157SyAnS8iMNfQdwAyY3SCZF4eMCZDlDHQxW3MlPplw4"

# 🔹 Укажите лист и диапазон (Example!A1:C1 запишет в одну строку, в ячейки A1, B1, C1)
RANGE = "Example!A1:C1"

# 🔹 Данные для записи (в одной строке)
DATA = [["Привет", "из", "Python"]]

def write_to_google_sheets():
    # Авторизация через сервисный аккаунт
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)

    # Формируем запрос
    body = {"values": DATA}

    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

    print("✅ Данные успешно записаны!")

# Вызываем функцию
write_to_google_sheets()

