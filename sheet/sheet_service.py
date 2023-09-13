import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from sheet.request import AddRequest

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
creds_file_path = os.path.join(parent_dir, 'sheets_key.json')

scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file_path, scope)


def add_join_request(request: AddRequest):
    client = gspread.authorize(credentials)
    spreadsheet = client.open('Заявки с бота на ДГ')
    worksheet = spreadsheet.worksheet('Заявки с бота')
    values = worksheet.get_all_values()
    first_empty_row = len(values) + 1
    worksheet.update_cell(first_empty_row, 1, request.date)
    worksheet.update_cell(first_empty_row, 2, request.first_name)
    worksheet.update_cell(first_empty_row, 3, request.last_name)
    worksheet.update_cell(first_empty_row, 4, request.telegram)
    worksheet.update_cell(first_empty_row, 5, request.leader_name)
