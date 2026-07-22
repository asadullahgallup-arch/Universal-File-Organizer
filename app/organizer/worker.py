from pathlib import Path

import pandas as pd

from app.organizer.indexer import FileIndexer
from app.organizer.matcher import FileMatcher
from app.organizer.organizer import FileOrganizer
from app.organizer.report import ReportGenerator


class Worker:
    """Runs one organization job and reports all outcomes to the GUI."""

    def __init__(self, gui):
        self.gui = gui
        self.indexer = FileIndexer()
        self.organizer = FileOrganizer()
        self.report = ReportGenerator()

    def organize(self):
        config = self.gui.job_config
        source = Path(config["source_folder"]).expanduser()
        destination = Path(config["destination_folder"]).expanduser()
        file_type = config["file_type"]
        matching_mode = config["matching_mode"]
        duplicate_mode = config["duplicate_mode"]
        operation = config["operation"]
        sheet = config["sheet"]
        file_column = config["file_column"]

        self._validate(source, destination, sheet, file_column)
        destination.mkdir(parents=True, exist_ok=True)
        self.gui.add_log("========== Starting Organization ==========")
        self.gui.add_log(f"Operation: {operation} | Match: {matching_mode}")

        index = self.indexer.build_index(source, file_type)
        matcher = FileMatcher(index)
        dataframe = self.gui.excel_handler.get_dataframe(sheet)
        folder_columns = [
            column for column in config["folder_levels"]
            if column in dataframe.columns
        ]

        self.gui.add_log(f"Indexed {len(index)} unique filenames; processing {len(dataframe)} Excel rows.")
        total, completed, transferred, missing, errors = len(dataframe), 0, 0, 0, 0

        for position, (_, row) in enumerate(dataframe.iterrows(), start=1):
            requested_name = self._cell_text(row.get(file_column))
            if not requested_name:
                errors += 1
                self.report.add_record("", "Skipped", "", "", "Blank file-name cell")
                self.gui.add_log(f"Row {position}: skipped (blank file-name cell).")
                self.gui.update_progress(position, total, transferred, missing, "Blank value")
                continue

            matches = matcher.find_files(requested_name, matching_mode)
            if duplicate_mode == "First Match":
                matches = matches[:1]

            if not matches:
                missing += 1
                self.report.add_record(requested_name, "Missing", "", "", "File not found")
                self.gui.add_log(f"Missing: {requested_name}")
                self.gui.update_progress(position, total, transferred, missing, requested_name)
                continue

            folder_values = [self._cell_text(row.get(column)) for column in folder_columns]
            destination_folder = self.organizer.create_folder(destination, folder_values)
            for source_file in matches:
                try:
                    if operation == "Move":
                        saved_file = self.organizer.move_file(source_file, destination_folder)
                        status = "Moved"
                    else:
                        saved_file = self.organizer.copy_file(source_file, destination_folder)
                        status = "Copied"
                    self.report.add_record(requested_name, status, source_file, saved_file, "Success")
                    transferred += 1
                    self.gui.add_log(f"{status}: {Path(source_file).name}")
                except OSError as error:
                    errors += 1
                    self.report.add_record(requested_name, "Error", source_file, destination_folder, str(error))
                    self.gui.add_log(f"Error: {Path(source_file).name} — {error}")

            completed = position
            self.gui.update_progress(completed, total, transferred, missing, requested_name)

        report_path = self.report.save_report(destination) if config.get("generate_report", True) else None
        self.gui.add_log(f"Completed: {transferred} transferred, {missing} missing, {errors} skipped/errors.")
        if report_path:
            self.gui.add_log(f"Report saved: {report_path}")
        return {"transferred": transferred, "missing": missing, "errors": errors, "report": report_path}

    @staticmethod
    def _cell_text(value):
        if value is None or pd.isna(value):
            return ""
        return str(value).strip()

    @staticmethod
    def _validate(source, destination, sheet, file_column):
        if not source.is_dir():
            raise ValueError("Select an existing source folder.")
        if not str(destination):
            raise ValueError("Select a destination folder.")
        if not sheet:
            raise ValueError("Select an Excel worksheet.")
        if not file_column or file_column == "Select File Column":
            raise ValueError("Select the Excel column that contains file names.")
        try:
            destination.resolve().relative_to(source.resolve())
        except ValueError:
            return
        raise ValueError("The destination folder cannot be the source folder or a folder inside it.")
