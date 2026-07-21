import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import os
import sys
from app.excel_handler import ExcelHandler
from app.config import FILE_TYPES, MATCHING_MODES, DUPLICATE_MODES
from app.indexer import FileIndexer
from app.matcher import FileMatcher
from app.worker import Worker
import threading
import queue
import webbrowser
from app.profile_manager import ProfileManager
from app.version import APP_NAME, APP_FULL_VERSION
from app.version import APP_VERSION
from app.updater import UpdateChecker


class UniversalFileOrganizer(ctk.CTkFrame):

    def __init__(self, parent=None):
        if parent is None:
            self.root = ctk.CTk()
            self.is_standalone = True
        else:
            self.root = parent
            self.is_standalone = False

        super().__init__(self.root)

        if self.is_standalone:
            self.root.title("Field Data Organizer")
            self.root.geometry("1280x850")
            self.root.minsize(1100, 750)
            try:
                self.root.iconbitmap(self.resource_path("assets/app.ico"))
            except Exception:
                pass

        self.pack(fill="both", expand=True)
        self._build_ui(self)

        if self.is_standalone:
            self.root.mainloop()

    def _build_ui(self, parent):
        self.colors = {
            "primary": "#2563eb", "primary_hover": "#1d4ed8",
            "success": "#16a34a", "warning": "#ca8a04",
            "danger": "#dc2626", "card": "#ffffff"
        }
        self.fonts = {
            "title": ("Segoe UI", 26, "bold"),
            "header": ("Segoe UI", 32, "bold"),
            "section": ("Segoe UI", 18, "bold"),
            "normal": ("Segoe UI", 14),
            "small": ("Segoe UI", 12)
        }
        self.dimensions = {
            "entry_width": 500, "combo_width": 420,
            "button_width": 180, "button_height": 40, "card_radius": 15
        }

        self.source_folder = ctk.StringVar()
        self.destination_folder = ctk.StringVar()
        self.excel_file = ctk.StringVar()
        self.excel_handler = ExcelHandler()
        self.indexer = FileIndexer()
        self.sheet_names = []
        self.columns = []
        self.selected_file_type = ctk.StringVar()
        self.selected_matching_mode = ctk.StringVar()
        self.profile_manager = ProfileManager()
        self.job_config = None
        self._ui_events = queue.Queue()

        self.progress_value = ctk.DoubleVar(value=0)
        self.status_text = ctk.StringVar(value="Ready")
        self.header_status = ctk.StringVar(value="🟢 System Ready")
        self.bottom_status = ctk.StringVar(value="Field Data Organizer | Ready")
        self.current_file = ctk.StringVar(value="-")
        self.processed_files = ctk.StringVar(value="0")
        self.copied_files = ctk.StringVar(value="0")
        self.missing_files = ctk.StringVar(value="0")
        self.total_files_value = ctk.StringVar(value="0")
        self.copied_files_value = ctk.StringVar(value="0")
        self.missing_files_value = ctk.StringVar(value="0")
        self.report_checkbox_var = tk.BooleanVar(value=True)

        self._build_header(parent)
        self._build_tabs(parent)
        self._build_status_bar(parent)
        self.after(100, self._poll_ui_events)

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, corner_radius=15)
        header.pack(fill="x", padx=30, pady=20)

        if not self.is_standalone:
            back_btn = ctk.CTkButton(
                header, text="← Return to Menu", width=130, height=32,
                font=("Segoe UI", 12, "bold"),
                fg_color=("#E2E8F0", "#2D3748"),
                text_color=("#2D3748", "#E2E8F0"),
                hover_color=("#CBD5E1", "#4A5568"),
                corner_radius=8,
                command=self.go_back_to_launcher
            )
            back_btn.pack(anchor="nw", padx=10, pady=(10, 5))

        ctk.CTkLabel(header, text="📁 Field Data Organizer",
                     font=("Segoe UI",32,"bold")).pack(pady=(15,5))
        ctk.CTkLabel(header, text="Smart Data Management Automation Tool\n"
                    "Excel Driven | Intelligent Matching | Duplicate Control",
                     font=("Segoe UI",15)).pack()
        self.app_status = ctk.CTkLabel(header, textvariable=self.header_status,
                                       font=("Segoe UI",14,"bold"))
        self.app_status.pack(pady=10)

    def _build_status_bar(self, parent):
        self.status_bar = ctk.CTkLabel(parent, textvariable=self.bottom_status,
                                       anchor="w", font=("Segoe UI",12))
        self.status_bar.pack(fill="x", padx=20, pady=(0,8))

    def _build_tabs(self, parent):
        self.tabview = ctk.CTkTabview(parent, width=1150, height=650, corner_radius=15)
        self.tabview.configure(
            segmented_button_fg_color=("#e5e7eb", "#1f2937"),
            segmented_button_selected_color=("#3b82f6", "#2563eb"),
            segmented_button_selected_hover_color=("#60a5fa", "#1d4ed8")
        )
        self.tabview.pack(padx=30, pady=30, fill="both", expand=True)

        self.project_tab = self.tabview.add("📁 Project")
        self.organization_tab = self.tabview.add("⚙ Organization")
        self.reports_tab = self.tabview.add("📊 Reports")

        self._build_project_tab()
        self._build_organization_tab()
        self._build_reports_tab()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def go_back_to_launcher(self):
        self.destroy()
        if hasattr(self.root, 'app_hub'):
            self.root.app_hub.show_launcher_dashboard()

    # ========== Project Tab ==========
    def _build_project_tab(self):
        self.create_project_tab()

    def create_project_tab(self):
        self.project_frame = ctk.CTkScrollableFrame(self.project_tab)
        self.project_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.project_frame, text="📁 Project Setup",
                     font=("Segoe UI",24,"bold")).pack(pady=(15,25))

        folder_card = ctk.CTkFrame(self.project_frame)
        folder_card.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(folder_card, text="📂 Folder Configuration",
                     font=("Segoe UI",18,"bold")).pack(pady=15)
        self.create_path_row(folder_card, "Source Folder", self.source_folder, self.select_source_folder)
        self.create_path_row(folder_card, "Destination Folder", self.destination_folder, self.select_destination_folder)

        excel_card = ctk.CTkFrame(self.project_frame)
        excel_card.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(excel_card, text="📊 Excel Configuration",
                     font=("Segoe UI",18,"bold")).pack(pady=15)
        self.create_path_row(excel_card, "Excel File", self.excel_file, self.select_excel_file)
        ctk.CTkLabel(excel_card, text="Excel Sheet").pack(pady=(15,5))
        self.sheet_dropdown = ctk.CTkComboBox(excel_card, values=[], width=500, command=self.load_columns)
        self.sheet_dropdown.pack(pady=10)

        action_card = ctk.CTkFrame(self.project_frame)
        action_card.pack(fill="x", padx=40, pady=20)
        ctk.CTkLabel(action_card, text="💾 Project Management",
                     font=("Segoe UI",18,"bold")).pack(pady=15)
        button_frame = ctk.CTkFrame(action_card, fg_color="transparent")
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="💾 Save Project", width=180, height=40,
                      command=self.save_project).pack(side="left", padx=15)
        ctk.CTkButton(button_frame, text="📂 Load Project", width=180, height=40,
                      command=self.load_project).pack(side="left", padx=15)
        ctk.CTkButton(button_frame, text="🗑️  Clear All", width=180, height=40,
                      font=("Segoe UI", 13),
                      fg_color=("#E2E8F0", "#2D3748"),
                      text_color=("#2D3748", "#E2E8F0"),
                      hover_color=("#CBD5E1", "#4A5568"),
                      corner_radius=10,
                      command=self.clear_all_fields).pack(side="left", padx=15)

    def clear_all_fields(self):
        self.source_folder.set("")
        self.destination_folder.set("")
        self.excel_file.set("")
        self.sheet_names = []
        self.sheet_dropdown.configure(values=[])
        self.sheet_dropdown.set("")
        self.columns = []
        if hasattr(self, "file_column_dropdown"):
            self.file_column_dropdown.configure(values=[])
            self.file_column_dropdown.set("Select File Column")
        if hasattr(self, "folder_dropdowns"):
            for i, dropdown in enumerate(self.folder_dropdowns):
                dropdown.configure(values=[])
                dropdown.set(f"Folder Level {i+1}")
        if hasattr(self, "file_type_dropdown"):
            self.file_type_dropdown.set("Audio")
        if hasattr(self, "duplicate_dropdown"):
            self.duplicate_dropdown.set("Copy All")
        if hasattr(self, "operation_dropdown"):
            self.operation_dropdown.set("Copy")
        if hasattr(self, "matching_dropdown"):
            self.matching_dropdown.set("Exact Match")
        self.update_configuration_summary()
        if hasattr(self, "progress_bar"):
            self.progress_bar.set(0)
        self.status_text.set("Ready")
        self.header_status.set("🟢 System Ready")
        self.bottom_status.set("Field Data Organizer | Ready")
        self.current_file.set("-")
        self.total_files_value.set("0")
        self.copied_files_value.set("0")
        self.missing_files_value.set("0")
        if hasattr(self, "log_box"):
            self.clear_log()
            self.add_log("All fields have been cleared. Ready for new configuration.")
        if hasattr(self, "start_button"):
            self.start_button.configure(state="normal")

    def create_path_row(self, parent, label_text, variable, command):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(frame, text=label_text, width=170).pack(side="left", padx=10)
        ctk.CTkEntry(frame, textvariable=variable, width=500).pack(side="left", padx=10)
        ctk.CTkButton(frame, text="Browse", command=command).pack(side="left")

    def select_source_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)
            self.update_configuration_summary()

    def select_destination_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_folder.set(folder)
            self.update_configuration_summary()

    def select_excel_file(self):
        file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if file:
            self.excel_file.set(file)
            self.sheet_names = self.excel_handler.load_excel(file)
            self.sheet_dropdown.configure(values=self.sheet_names)
            if self.sheet_names:
                self.sheet_dropdown.set(self.sheet_names[0])
                self.load_columns(self.sheet_names[0])
                self.update_configuration_summary()

    def load_columns(self, sheet_name):
        self.columns = self.excel_handler.load_sheet(sheet_name)
        self.file_column_dropdown.configure(values=self.columns)
        if hasattr(self, "folder_dropdowns"):
            for dropdown in self.folder_dropdowns:
                dropdown.configure(values=self.columns)

    def test_indexer(self):
        if not self.source_folder.get():
            print("Please select a source folder first.")
            return
        file_type = self.file_type_dropdown.get()
        index = self.indexer.build_index(self.source_folder.get(), file_type)
        matcher = FileMatcher(index)
        print("\nTesting Matcher\n")
        mode = self.matching_dropdown.get()
        test_value = input("Enter filename to search: ")
        results = matcher.find_files(test_value, mode)
        if not results:
            print("\nNo matching files found.")
        else:
            print(f"\nFound {len(results)} file(s):\n")
            for file in results:
                print(file)
        print("\n--------------------------------")
        print(f"Indexed {len(index)} unique file names")
        print("--------------------------------")
        for key, files in list(index.items())[:10]:
            print(f"\n{key}")
            for file in files:
                print(f"   └── {file}")

    # ========== Organization Tab ==========
    def _build_organization_tab(self):
        self.create_organization_tab()

    def create_organization_tab(self):
        self.organization_frame = ctk.CTkScrollableFrame(self.organization_tab)
        self.organization_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.organization_frame, text="⚙ Organization Configuration",
                     font=("Segoe UI",26,"bold")).pack(pady=(10,25))

        main_frame = ctk.CTkFrame(self.organization_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=2)

        config_frame = ctk.CTkFrame(main_frame)
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(config_frame, text="📂 File Processing Rules",
                     font=("Segoe UI",18,"bold")).pack(pady=15)
        ctk.CTkLabel(config_frame, text="File Type").pack()
        self.file_type_dropdown = ctk.CTkComboBox(config_frame, values=list(FILE_TYPES.keys()), width=420)
        self.file_type_dropdown.pack(pady=8)
        self.file_type_dropdown.set("Audio")

        ctk.CTkLabel(config_frame, text="Duplicate Handling").pack()
        self.duplicate_dropdown = ctk.CTkComboBox(config_frame, values=DUPLICATE_MODES, width=420)
        self.duplicate_dropdown.pack(pady=8)
        self.duplicate_dropdown.set("Copy All")

        ctk.CTkLabel(config_frame, text="Operation").pack()
        self.operation_dropdown = ctk.CTkComboBox(config_frame, values=["Copy", "Move"], width=420)
        self.operation_dropdown.pack(pady=8)
        self.operation_dropdown.set("Copy")

        ctk.CTkFrame(config_frame, height=2).pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(config_frame, text="🔍 Matching Rules",
                     font=("Segoe UI",18,"bold")).pack(pady=(25,15))
        ctk.CTkLabel(config_frame, text="Matching Mode").pack()
        self.matching_dropdown = ctk.CTkComboBox(config_frame, values=MATCHING_MODES, width=420)
        self.matching_dropdown.pack(pady=8)
        self.matching_dropdown.set("Exact Match")
        ctk.CTkFrame(config_frame, height=2).pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(config_frame, text="📊 Excel Mapping",
                     font=("Segoe UI",18,"bold")).pack(pady=(25,15))
        ctk.CTkLabel(config_frame, text="File Name Column").pack()
        self.file_column_dropdown = ctk.CTkComboBox(config_frame, values=[], width=420)
        self.file_column_dropdown.pack(pady=8)
        self.file_column_dropdown.set("Select File Column")
        ctk.CTkFrame(config_frame, height=2).pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(config_frame, text="📁 Folder Structure",
                     font=("Segoe UI",18,"bold")).pack(pady=(25,10))
        self.folder_dropdowns = []
        for i in range(1,6):
            dropdown = ctk.CTkComboBox(config_frame, values=[], width=420)
            dropdown.pack(pady=5)
            dropdown.set(f"Folder Level {i}")
            self.folder_dropdowns.append(dropdown)

        summary_frame = ctk.CTkFrame(main_frame)
        summary_frame.grid(sticky="nsew")
        summary_frame.configure(width=350)

        ctk.CTkLabel(summary_frame, text="📋 Configuration Summary",
                     font=("Segoe UI",18,"bold")).pack(pady=20)
        self.config_summary = ctk.CTkLabel(summary_frame, text=
            "File Type:\n-\n\nMatching Mode:\n-\n\nOperation:\n-\n\nFolder Levels:\n-",
            justify="left", font=("Segoe UI",14))
        self.config_summary.pack(padx=20, pady=20)
        self.ready_status = ctk.CTkLabel(summary_frame, text="🟢 Ready",
                                         font=("Segoe UI",16,"bold"))
        self.ready_status.configure(text_color="#22c55e")
        self.ready_status.pack(pady=20)

        for dropdown in [self.file_type_dropdown, self.matching_dropdown,
                         self.duplicate_dropdown, self.operation_dropdown,
                         self.file_column_dropdown]:
            dropdown.configure(command=lambda _: self.update_configuration_summary())
        for dropdown in self.folder_dropdowns:
            dropdown.configure(command=lambda _: self.update_configuration_summary())

    def update_configuration_summary(self, *args):
        folder_levels = []
        for dropdown in self.folder_dropdowns:
            value = dropdown.get()
            if value and not value.startswith("Folder Level"):
                folder_levels.append(value)
        folder_text = "\n".join(folder_levels) if folder_levels else "-"
        summary = (
            f"File Type:\n{self.file_type_dropdown.get()}\n\n"
            f"Matching Mode:\n{self.matching_dropdown.get()}\n\n"
            f"Duplicate Handling:\n{self.duplicate_dropdown.get()}\n\n"
            f"Operation:\n{self.operation_dropdown.get()}\n\n"
            f"File Column:\n{self.file_column_dropdown.get()}\n\n"
            f"Folder Levels:\n{folder_text}"
        )
        self.config_summary.configure(text=summary)
        self.check_configuration_status()

    def check_configuration_status(self):
        errors = []
        if not self.source_folder.get():
            errors.append("Source folder missing")
        if not self.destination_folder.get():
            errors.append("Destination folder missing")
        if not self.excel_file.get():
            errors.append("Excel file missing")
        if self.file_column_dropdown.get() == "Select File Column":
            errors.append("File column not selected")
        if errors:
            self.ready_status.configure(text="🟡 " + errors[0])
        else:
            self.ready_status.configure(text="🟢 Configuration Ready")

    # ========== Reports Tab ==========
    def _build_reports_tab(self):
        self.create_reports_tab()

    def create_reports_tab(self):
        self.reports_frame = ctk.CTkScrollableFrame(self.reports_tab)
        self.reports_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.reports_frame, text="📊 Reports & Processing Monitor",
                     font=("Segoe UI",24,"bold")).pack(pady=(10,25))

        progress_card = ctk.CTkFrame(self.reports_frame)
        progress_card.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(progress_card, text="Processing Progress",
                     font=("Segoe UI",18,"bold")).pack(pady=15)
        self.progress_bar = ctk.CTkProgressBar(progress_card, width=700, height=20)
        self.progress_bar.pack(pady=15)
        self.progress_bar.set(0)
        ctk.CTkLabel(progress_card, textvariable=self.status_text,
                     font=("Segoe UI",15)).pack(pady=5)
        ctk.CTkLabel(progress_card, textvariable=self.current_file).pack(pady=5)

        stats_frame = ctk.CTkFrame(progress_card, fg_color="transparent")
        stats_frame.pack(pady=15)

        total_card = ctk.CTkFrame(stats_frame, width=180, height=120, corner_radius=15)
        total_card.pack(side="left", padx=15)
        ctk.CTkLabel(total_card, text="Total Files", font=("Segoe UI",14)).pack(pady=5)
        ctk.CTkLabel(total_card, textvariable=self.total_files_value,
                     font=("Segoe UI",22,"bold")).pack()

        copied_card = ctk.CTkFrame(stats_frame, width=180, height=120, corner_radius=15)
        copied_card.pack(side="left", padx=15)
        ctk.CTkLabel(copied_card, text="Copied Files", font=("Segoe UI",14)).pack(pady=5)
        ctk.CTkLabel(copied_card, textvariable=self.copied_files_value,
                     font=("Segoe UI",22,"bold")).pack()

        missing_card = ctk.CTkFrame(stats_frame, width=180, height=120, corner_radius=15)
        missing_card.pack(side="left", padx=15)
        ctk.CTkLabel(missing_card, text="Missing Files", font=("Segoe UI",14)).pack(pady=5)
        ctk.CTkLabel(missing_card, textvariable=self.missing_files_value,
                     font=("Segoe UI",22,"bold")).pack()

        self.report_checkbox = ctk.CTkCheckBox(
            self.reports_frame,
            text="Generate Processing Report After Completion",
            variable=self.report_checkbox_var,
            font=("Segoe UI", 14)
        )
        self.report_checkbox.pack(pady=(10, 5))

        button_frame = ctk.CTkFrame(self.reports_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        ctk.CTkButton(button_frame, text="🔍 Test Indexer", width=200, height=40,
                      command=self.test_indexer).pack(side="left", padx=10)
        self.start_button = ctk.CTkButton(button_frame, text="▶ Start Organization",
                                          width=200, height=40, command=self.start_organization)
        self.start_button.pack(side="left", padx=10)

        log_card = ctk.CTkFrame(self.reports_frame)
        log_card.pack(fill="both", expand=True, padx=40, pady=10)
        ctk.CTkLabel(log_card, text="📜 Processing Log",
                     font=("Segoe UI",18,"bold")).pack(pady=10)
        self.log_box = ctk.CTkTextbox(log_card, height=180)
        self.log_box.pack(fill="both", expand=True, padx=20, pady=10)
        self.log_box.insert("end", "Application Ready...\n")
        self.log_box.configure(state="disabled")

    # ========== Core logic (unchanged) ==========
    def start_organization(self):
        self.job_config = {
            "source_folder": self.source_folder.get(),
            "destination_folder": self.destination_folder.get(),
            "file_type": self.file_type_dropdown.get(),
            "matching_mode": self.matching_dropdown.get(),
            "duplicate_mode": self.duplicate_dropdown.get(),
            "operation": self.operation_dropdown.get(),
            "sheet": self.sheet_dropdown.get(),
            "file_column": self.file_column_dropdown.get(),
            "folder_levels": [dropdown.get() for dropdown in self.folder_dropdowns],
            "generate_report": self.report_checkbox_var.get(),
        }
        self.start_button.configure(state="disabled")
        self.header_status.set("🟡 Processing Files...")
        self.bottom_status.set("Field Data Organizer | Starting...")
        threading.Thread(target=self.run_worker, daemon=True).start()

    def run_worker(self):
        try:
            result = Worker(self).organize()
            self._ui_events.put(("_finish_job", (result, None)))
        except Exception as error:
            self._ui_events.put(("_finish_job", (None, str(error))))

    def _poll_ui_events(self):
        while True:
            try:
                method, args = self._ui_events.get_nowait()
            except queue.Empty:
                break
            getattr(self, method)(*args)
        self.after(100, self._poll_ui_events)

    def _finish_job(self, result, error):
        self.start_button.configure(state="normal")
        if error:
            self.header_status.set("Processing failed")
            self.bottom_status.set("Field Data Organizer | Processing failed")
            self.status_text.set("Processing failed")
            self.add_log(f"Processing failed: {error}")
            messagebox.showerror("Organization failed", error)
            return
        self.header_status.set("Completed successfully")
        self.bottom_status.set("Field Data Organizer | Completed successfully")
        self.status_text.set("Completed successfully")

    def check_for_updates(self, manual=True):
        if hasattr(self, "update_button"):
            self.update_button.configure(state="disabled", text="Checking for updates...")
        threading.Thread(target=self._run_update_check, args=(manual,), daemon=True).start()

    def _run_update_check(self, manual):
        try:
            result = UpdateChecker().check(APP_VERSION)
            self._ui_events.put(("_show_update_result", (result, manual, None)))
        except Exception as error:
            self._ui_events.put(("_show_update_result", (None, manual, str(error))))

    def _show_update_result(self, result, manual, error):
        if hasattr(self, "update_button"):
            self.update_button.configure(state="normal", text="Check for Updates")
        if error:
            if manual:
                messagebox.showwarning("Update check unavailable", error)
            return
        if result.get("available"):
            latest = result["latest_version"]
            should_open = messagebox.askyesno(
                "Update available",
                f"Version {latest} is available. You have {APP_VERSION}.\n\nOpen the download page now?"
            )
            if should_open and result.get("download_url"):
                webbrowser.open(result["download_url"])
            return
        if manual:
            messagebox.showinfo("Field Data Organizer", result.get("reason", "You already have the latest version."))

    def update_progress(self, current, total, copied, missing, current_file):
        if threading.current_thread() is not threading.main_thread():
            self._ui_events.put(("update_progress", (current, total, copied, missing, current_file)))
            return
        self.header_status.set(f"🟡 Processing {current}/{total}")
        percent = current / total
        self.progress_bar.set(percent)
        self.status_text.set(f"{int(percent*100)}% Completed ({current}/{total})")
        self.current_file.set(f"Processing: {current_file}")
        self.total_files_value.set(str(total))
        self.copied_files_value.set(str(copied))
        self.missing_files_value.set(str(missing))
        self.bottom_status.set(f"Processing: {current_file}")
        self.update_idletasks()

    def add_log(self, message):
        if threading.current_thread() is not threading.main_thread():
            self._ui_events.put(("add_log", (message,)))
            return
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.update_idletasks()

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def save_project(self):
        profile = {
            "source_folder": self.source_folder.get(),
            "destination_folder": self.destination_folder.get(),
            "excel_file": self.excel_file.get(),
            "sheet": self.sheet_dropdown.get(),
            "file_type": self.file_type_dropdown.get(),
            "matching_mode": self.matching_dropdown.get(),
            "duplicate_mode": self.duplicate_dropdown.get(),
            "operation": self.operation_dropdown.get(),
            "file_column": self.file_column_dropdown.get(),
            "folder_levels": [dropdown.get() for dropdown in self.folder_dropdowns]
        }
        file = filedialog.asksaveasfilename(defaultextension=".ufo",
                                            filetypes=[("Organizer Project", "*.ufo")])
        if file:
            self.profile_manager.save_profile(file, profile)
            print("Project Saved.")

    def load_project(self):
        file = filedialog.askopenfilename(filetypes=[("Organizer Project", "*.ufo"), ("JSON files", "*.json")])
        if not file:
            return
        try:
            profile = self.profile_manager.load_profile(file)
            self.source_folder.set(profile.get("source_folder", ""))
            self.destination_folder.set(profile.get("destination_folder", ""))
            excel_path = profile.get("excel_file", "")
            self.excel_file.set(excel_path)
            if excel_path and os.path.isfile(excel_path):
                self.sheet_names = self.excel_handler.load_excel(excel_path)
                self.sheet_dropdown.configure(values=self.sheet_names)
                sheet = profile.get("sheet")
                if sheet in self.sheet_names:
                    self.sheet_dropdown.set(sheet)
                    self.load_columns(sheet)
            for dropdown, value in zip(self.folder_dropdowns, profile.get("folder_levels", [])):
                dropdown.set(value)
            for dropdown, key in [
                (self.file_type_dropdown, "file_type"),
                (self.matching_dropdown, "matching_mode"),
                (self.duplicate_dropdown, "duplicate_mode"),
                (self.operation_dropdown, "operation"),
                (self.file_column_dropdown, "file_column"),
            ]:
                if profile.get(key):
                    dropdown.set(profile[key])
            self.update_configuration_summary()
            self.add_log(f"Project loaded: {file}")
        except (OSError, ValueError, KeyError) as error:
            messagebox.showerror("Could not load project", str(error))