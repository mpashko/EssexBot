import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Spreadsheet:
    def __init__(self, file=None, config=None):
        scope = ["https://spreadsheets.google.com/feeds"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(config, scope)
        gc = gspread.authorize(credentials)
        self.wks = gc.open(file)
        self.worksheet = None

    def write_to_spreadsheet(self, sheet='Sheet1'):
        self.worksheet = self.wks.worksheet(sheet)
        self.worksheet.update_cell(1, 1, "I'm here!")


if __name__ == "__main__":
    s = Spreadsheet(file='dou_vacancies', config='creds_google_spreadsheets.json')
    s.write_to_spreadsheet()
