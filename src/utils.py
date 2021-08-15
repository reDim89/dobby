# -*- coding: utf-8 -*-
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pygsheets
import numpy as np

def get_sheet(spreadsheet_id: str):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    gc = pygsheets.authorize(client_secret='credentials.json',
                             service_account_file='service_account_file.json',
                             scopes=SCOPES)

    # Open spreadsheet and then worksheet
    sh = gc.open_by_key(key=spreadsheet_id)
    return sh.sheet1

def abstract_insert(data: str, worksheet: pygsheets.Worksheet, range: tuple):
    worksheet.update_value(range, data)
    return

def find_first_blank_row(worksheet: pygsheets.Worksheet)->int:
    cells = worksheet.get_col(1)
    row = cells.index('')
    return row + 1

def insert_task(data: str, worksheet: pygsheets.Worksheet, row: int):
    col = 1
    abstract_insert(data, worksheet, (row, col))
    return

def insert_phone(data: str, worksheet: pygsheets.Worksheet, row: int):
    col = 2
    abstract_insert(data, worksheet, (row, col))
    return

def insert_price(data: str, worksheet: pygsheets.Worksheet, row: int):
    col = 3
    abstract_insert(data, worksheet, (row, col))
    return

if __name__ == '__main__':
    ws = get_sheet('1cVqI3DKrgQSRnSow1hDxpYNn2oSlx-teQhBI3KQITao')
    row = find_first_blank_row(ws)
    insert_task('Купи билеты в сочи', ws, row)
    insert_phone('+79150991011', ws, row)
    insert_price('500', ws, row)