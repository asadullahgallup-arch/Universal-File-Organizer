from datetime import datetime
from pathlib import Path
import pandas as pd


class ReportGenerator:

    def __init__(self):
        self.records = []

    def add_record(
        self,
        filename,
        status,
        source,
        destination,
        remarks
    ):

        self.records.append({

            "File Name": filename,

            "Status": status,

            "Source": source,

            "Destination": destination,

            "Remarks": remarks

        })

    def save_report(self, folder):

        if not self.records:
            return

        df = pd.DataFrame(self.records)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(folder) / f"Organization_Report_{timestamp}.xlsx"

        df.to_excel(
            report_path,
            index=False
        )

        return str(report_path)
