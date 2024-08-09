import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Google Sheets'e bağlanma fonksiyonu
def get_google_sheet(sheet_name, worksheet_name):
    BASE_DIR = os.path.expanduser('~')
    CREDENTIALS_FILE = os.path.join(BASE_DIR, 'fluted-galaxy-428615-a2-28fb403d7d23.json')
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Menü alma fonksiyonu
def get_menu():
    df = get_google_sheet("yemek_listesi", "Sheet1")  # Google Sheets dosyanızın adı ve çalışma sayfası adı
    df['Tarih'] = pd.to_datetime(df['Tarih'], dayfirst=True)  # Tarih sütununu datetime formatına çevir
    today = pd.Timestamp(datetime.now().date())  # Bugünün tarihini al
    today_menu = df[df['Tarih'] == today]  # Bugünün tarihine ait satırı al
    if not today_menu.empty:
        row = today_menu.iloc[0]
        menu = f"{row['Tarih'].strftime('%d.%m.%Y')}:\n{row['Yemek']}"
    else:
        menu = "Bugün için bir yemek listesi bulunamadı."
    return menu

# Start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Merhaba! /menu yazarak yemek listesini alabilirsiniz.')

# Menu komutu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu = get_menu()
    await update.message.reply_text(menu)

def main():
    # Botun API token'ı
    API_TOKEN = '5902942569:AAHkdZVOASVwe-NiY8wuEgGxkBsAxEIRBk4'

    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))

    application.run_polling()

if __name__ == '__main__':
    main()
