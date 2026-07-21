import pandas as pd


class ExcelHandler:

    def __init__(self):

        self.file_path = None
        self.excel_file = None
        self.sheets = []


    # ================================
    # Load Excel Workbook
    # ================================

    def load_excel(self, file_path):

        self.file_path = file_path

        self.excel_file = pd.ExcelFile(file_path)

        self.sheets = self.excel_file.sheet_names

        return self.sheets


    # ================================
    # Load Column Names
    # ================================

    def load_sheet(self, sheet_name):

        if self.excel_file is None:
            return []

        df = self.excel_file.parse(sheet_name)

        return list(df.columns)


    # ================================
    # Return Complete DataFrame
    # ================================

    def get_dataframe(self, sheet_name):

        if self.excel_file is None:
            return pd.DataFrame()

        return self.excel_file.parse(sheet_name)
