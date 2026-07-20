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


class UniversalFileOrganizer(ctk.CTk):


    def __init__(self):

        super().__init__()


        # ================================
        # Window Settings
        # ================================

        self.title(
            f"{APP_NAME} - {APP_FULL_VERSION}"
        )

        self.geometry(
            "1280x850"
        )

        self.minsize(
            1100,
            750
        )

        # ================================
        # UI Configuration
        # ================================

        self.colors = {

            "primary": "#2563eb",
            "primary_hover": "#1d4ed8",
            "success": "#16a34a",
            "warning": "#ca8a04",
            "danger": "#dc2626",
            "card": "#ffffff"
        }


        self.fonts = {

            "title": ("Segoe UI", 26, "bold"),
            "header": ("Segoe UI", 32, "bold"),
            "section": ("Segoe UI", 18, "bold"),
            "normal": ("Segoe UI", 14),
            "small": ("Segoe UI", 12)
        }


        self.dimensions = {

            "entry_width": 500,
            "combo_width": 420,
            "button_width": 180,
            "button_height": 40,
            "card_radius": 15
        }


        # ================================
        # Application Icon
        # ================================

        try:

            self.iconbitmap(
                self.resource_path(
                    "assets/app.ico"
                )
            )

        except Exception:

            pass

        ctk.set_appearance_mode(
            "System"
        )

        self.appearance_mode = ctk.StringVar(
            value="System"
        )
        
        self.color_theme = ctk.StringVar(
            value="blue"
        )
        
        ctk.set_default_color_theme(
            "blue"
        )

        # ================================
        # Variables
        # ================================

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
        
        # Progress Variables

        self.progress_value = ctk.DoubleVar(value=0)

        self.status_text = ctk.StringVar(value="Ready")
        self.header_status = ctk.StringVar(
            value="🟢 System Ready"
        )
        self.bottom_status = ctk.StringVar(
            value="Universal File Organizer | Ready"
        )

        self.current_file = ctk.StringVar(value="-")

        self.processed_files = ctk.StringVar(value="0")

        self.copied_files = ctk.StringVar(value="0")

        self.missing_files = ctk.StringVar(value="0")

        self.total_files_value = ctk.StringVar(value="0")
        self.copied_files_value = ctk.StringVar(value="0")
        self.missing_files_value = ctk.StringVar(value="0")

        # ================================
        # Start GUI
        # ================================

        self.create_header()

        self.create_tabs()

        self.create_status_bar()
        self.after(100, self._poll_ui_events)
        self.after(1500, lambda: self.check_for_updates(manual=False))
    
    # ================================
    # Resource Path Helper
    # ================================    
        
    def resource_path(self, relative_path):

        try:
            base_path = sys._MEIPASS

        except Exception:

            base_path = os.path.abspath(".")

        return os.path.join(
            base_path,
            relative_path
        )

    # ================================
    # Header
    # ================================

    def create_header(self):

        header = ctk.CTkFrame(
            self,
            corner_radius=15
        )


        header.pack(
            fill="x",
            padx=30,
            pady=20
        )


        ctk.CTkLabel(
            header,
            text="📁 Universal File Organizer",
            font=("Segoe UI",32,"bold")
        ).pack(
            pady=(15,5)
        )


        ctk.CTkLabel(
            header,
            text="Smart File Management Automation Tool\n"
                "Excel Driven | Intelligent Matching | Duplicate Control",
            font=("Segoe UI",15)
        ).pack()


        self.app_status = ctk.CTkLabel(
            header,
            textvariable=self.header_status,
            font=("Segoe UI",14,"bold")
        )

        self.app_status.pack(
            pady=10
        )

    # ================================
    # Status Bar
    # ================================

    def create_status_bar(self):

        self.status_bar = ctk.CTkLabel(
            self,
            textvariable=self.bottom_status,
            anchor="w",
            font=("Segoe UI",12)
        )


        self.status_bar.pack(
            fill="x",
            padx=20,
            pady=(0,8)
        )
    # ================================
    # Change Theme
    # ================================

    def change_theme(self, choice):

        ctk.set_appearance_mode(
            choice
        )

        self.appearance_mode.set(
            choice
        )

    # ================================
    # Tabs
    # ================================

    def create_tabs(self):


        self.tabview = ctk.CTkTabview(
            self,
            width=1150,
            height=650,
            corner_radius=15
        )

        self.tabview.configure(
            segmented_button_fg_color=(
                "#e5e7eb",
                "#1f2937"
            ),
            segmented_button_selected_color=(
                "#3b82f6",
                "#2563eb"
            ),
            segmented_button_selected_hover_color=(
                "#60a5fa",
                "#1d4ed8"
            )
        )
        self.tabview.pack(
            padx=30,
            pady=30,
            fill="both",
            expand=True
        )


        self.project_tab = self.tabview.add(
            "📁 Project"
        )


        self.organization_tab = self.tabview.add(
            "⚙ Organization"
        )


        self.reports_tab = self.tabview.add(
            "📊 Reports"
        )


        self.settings_tab = self.tabview.add(
            "🔧 Settings"
        )


        self.create_project_tab()

        self.create_organization_tab()

        self.create_reports_tab()

        self.create_settings_tab()




    # ================================
    # Project Tab
    # ================================

    def create_project_tab(self):


        # Main Scrollable Frame

        self.project_frame = ctk.CTkScrollableFrame(
            self.project_tab
        )

        self.project_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


        # Title

        ctk.CTkLabel(
            self.project_frame,
            text="📁 Project Setup",
            font=("Segoe UI",24,"bold")
        ).pack(
            pady=(15,25)
        )



        # ==================================
        # Folder Configuration Card
        # ==================================

        folder_card = ctk.CTkFrame(
            self.project_frame
        )

        folder_card.pack(
            fill="x",
            padx=40,
            pady=10
        )


        ctk.CTkLabel(
            folder_card,
            text="📂 Folder Configuration",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=15
        )



        self.create_path_row(
            folder_card,
            "Source Folder",
            self.source_folder,
            self.select_source_folder
        )


        self.create_path_row(
            folder_card,
            "Destination Folder",
            self.destination_folder,
            self.select_destination_folder
        )




        # ==================================
        # Excel Configuration Card
        # ==================================


        excel_card = ctk.CTkFrame(
            self.project_frame
        )


        excel_card.pack(
            fill="x",
            padx=40,
            pady=10
        )



        ctk.CTkLabel(
            excel_card,
            text="📊 Excel Configuration",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=15
        )



        self.create_path_row(
            excel_card,
            "Excel File",
            self.excel_file,
            self.select_excel_file
        )



        ctk.CTkLabel(
            excel_card,
            text="Excel Sheet"
        ).pack(
            pady=(15,5)
        )



        self.sheet_dropdown = ctk.CTkComboBox(
            excel_card,
            values=[],
            width=500,
            command=self.load_columns
        )


        self.sheet_dropdown.pack(
            pady=10
        )




        # ==================================
        # Project Actions Card
        # ==================================


        action_card = ctk.CTkFrame(
            self.project_frame
        )


        action_card.pack(
            fill="x",
            padx=40,
            pady=20
        )



        ctk.CTkLabel(
            action_card,
            text="💾 Project Management",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=15
        )



        button_frame = ctk.CTkFrame(
            action_card,
            fg_color="transparent"
        )


        button_frame.pack(
            pady=10
        )



        ctk.CTkButton(
            button_frame,
            text="💾 Save Project",
            width=180,
            height=40,
            command=self.save_project
        ).pack(
            side="left",
            padx=15
        )



        ctk.CTkButton(
            button_frame,
            text="📂 Load Project",
            width=180,
            height=40,
            command=self.load_project
        ).pack(
            side="left",
            padx=15
        )

    # ================================
    # Browse Row
    # ================================

    def create_path_row(
            self,
            parent,
            label_text,
            variable,
            command
    ):


        frame = ctk.CTkFrame(
            parent
        )


        frame.pack(
            fill="x",
            padx=40,
            pady=10
        )


        label = ctk.CTkLabel(
            frame,
            text=label_text,
            width=170
        )


        label.pack(
            side="left",
            padx=10
        )


        entry = ctk.CTkEntry(
            frame,
            textvariable=variable,
            width=500
        )


        entry.pack(
            side="left",
            padx=10
        )


        button = ctk.CTkButton(
            frame,
            text="Browse",
            command=command
        )


        button.pack(
            side="left"
        )



    # ================================
    # Browse Functions
    # ================================

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


        file = filedialog.askopenfilename(
            filetypes=[
                (
                    "Excel Files",
                    "*.xlsx *.xls"
                )
            ]
        )


        if file:

            self.excel_file.set(file)
            


            self.sheet_names = (
                self.excel_handler
                .load_excel(file)
            )


            self.sheet_dropdown.configure(
                values=self.sheet_names
            )


            if self.sheet_names:

                self.sheet_dropdown.set(
                    self.sheet_names[0]
                )


                self.load_columns(
                    self.sheet_names[0]
                )
                
                self.update_configuration_summary()


    # ================================
    # Load Excel Columns
    # ================================

    def load_columns(
            self,
            sheet_name
    ):


        self.columns = (
            self.excel_handler
            .load_sheet(sheet_name)
        )


        self.file_column_dropdown.configure(
            values=self.columns
        )


        if hasattr(
            self,
            "folder_dropdowns"
        ):

            for dropdown in self.folder_dropdowns:

                dropdown.configure(
                    values=self.columns
                )

    # =====================================
    # Test Indexer
    # =====================================

    def test_indexer(self):

        if not self.source_folder.get():
            print("Please select a source folder first.")
            return

        file_type = self.file_type_dropdown.get()

        index = self.indexer.build_index(
            self.source_folder.get(),
            file_type
        )
        
        matcher = FileMatcher(index)

        print("\nTesting Matcher\n")

        mode = self.matching_dropdown.get()

        test_value = input(
            "Enter filename to search: "
        )

        results = matcher.find_files(
            test_value,
            mode
        )

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


    # ================================
    # Organization Tab
    # ================================

    def create_organization_tab(self):


        # Main Scrollable Container

        self.organization_frame = ctk.CTkScrollableFrame(
            self.organization_tab
        )

        self.organization_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


        # ==============================
        # Header
        # ==============================

        ctk.CTkLabel(
            self.organization_frame,
            text="⚙ Organization Configuration",
            font=("Segoe UI",26,"bold")
        ).pack(
            pady=(10,25)
        )



        # ==============================
        # Main Layout
        # ==============================


        main_frame = ctk.CTkFrame(
            self.organization_frame,
            fg_color="transparent"
        )

        main_frame.pack(
            fill="both",
            expand=True
        )


        main_frame.grid_columnconfigure(
            0,
            weight=3
        )

        main_frame.grid_columnconfigure(
            1,
            weight=2
        )



        # ===================================
        # LEFT SIDE CONFIGURATION
        # ===================================


        config_frame = ctk.CTkFrame(
            main_frame
        )


        config_frame.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew"
        )



        # --------------------------
        # File Processing Section
        # --------------------------


        ctk.CTkLabel(
            config_frame,
            text="📂 File Processing Rules",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=15
        )



        ctk.CTkLabel(
            config_frame,
            text="File Type"
        ).pack()


        self.file_type_dropdown = ctk.CTkComboBox(
            config_frame,
            values=list(FILE_TYPES.keys()),
            width=420
        )


        self.file_type_dropdown.pack(
            pady=8
        )


        self.file_type_dropdown.set(
            "Audio"
        )



        ctk.CTkLabel(
            config_frame,
            text="Duplicate Handling"
        ).pack()


        self.duplicate_dropdown = ctk.CTkComboBox(
            config_frame,
            values=DUPLICATE_MODES,
            width=420
        )


        self.duplicate_dropdown.pack(
            pady=8
        )


        self.duplicate_dropdown.set(
            "Copy All"
        )



        ctk.CTkLabel(
            config_frame,
            text="Operation"
        ).pack()


        self.operation_dropdown = ctk.CTkComboBox(
            config_frame,
            values=[
                "Copy",
                "Move"
            ],
            width=420
        )


        self.operation_dropdown.pack(
            pady=8
        )


        self.operation_dropdown.set(
            "Copy"
        )

        ctk.CTkFrame(
            config_frame,
            height=2
        ).pack(
            fill="x",
            padx=20,
            pady=15
        )

        # --------------------------
        # Matching Section
        # --------------------------


        ctk.CTkLabel(
            config_frame,
            text="🔍 Matching Rules",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=(25,15)
        )



        ctk.CTkLabel(
            config_frame,
            text="Matching Mode"
        ).pack()


        self.matching_dropdown = ctk.CTkComboBox(
            config_frame,
            values=MATCHING_MODES,
            width=420
        )


        self.matching_dropdown.pack(
            pady=8
        )


        self.matching_dropdown.set(
            "Exact Match"
        )


        ctk.CTkFrame(
            config_frame,
            height=2
        ).pack(
            fill="x",
            padx=20,
            pady=15
        )
        
        # --------------------------
        # Excel Mapping
        # --------------------------


        ctk.CTkLabel(
            config_frame,
            text="📊 Excel Mapping",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=(25,15)
        )



        ctk.CTkLabel(
            config_frame,
            text="File Name Column"
        ).pack()



        self.file_column_dropdown = ctk.CTkComboBox(
            config_frame,
            values=[],
            width=420
        )


        self.file_column_dropdown.pack(
            pady=8
        )


        self.file_column_dropdown.set(
            "Select File Column"
        )

        ctk.CTkFrame(
            config_frame,
            height=2
        ).pack(
            fill="x",
            padx=20,
            pady=15
        )

        # --------------------------
        # Folder Structure
        # --------------------------


        ctk.CTkLabel(
            config_frame,
            text="📁 Folder Structure",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=(25,10)
        )


        self.folder_dropdowns = []


        for i in range(1,6):


            dropdown = ctk.CTkComboBox(
                config_frame,
                values=[],
                width=420
            )


            dropdown.pack(
                pady=5
            )


            dropdown.set(
                f"Folder Level {i}"
            )


            self.folder_dropdowns.append(
                dropdown
            )



        # ===================================
        # RIGHT SIDE SUMMARY
        # ===================================


        summary_frame = ctk.CTkFrame(
            main_frame
        )


        summary_frame.grid(
            sticky="nsew"
        )


        summary_frame.configure(
            width=350
        )



        ctk.CTkLabel(
            summary_frame,
            text="📋 Configuration Summary",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=20
        )



        self.config_summary = ctk.CTkLabel(
            summary_frame,
            text=
            "File Type:\n"
            "-\n\n"
            "Matching Mode:\n"
            "-\n\n"
            "Operation:\n"
            "-\n\n"
            "Folder Levels:\n"
            "-",
            justify="left",
            font=("Segoe UI",14)
        )


        self.config_summary.pack(
            padx=20,
            pady=20
        )

        self.ready_status = ctk.CTkLabel(
            summary_frame,
            text="🟢 Ready",
            font=("Segoe UI",16,"bold")
        )

        self.ready_status.configure(
            text_color="#22c55e"
        )

        self.ready_status.pack(
            pady=20
        )


        # Auto Update Summary

        for dropdown in [
            self.file_type_dropdown,
            self.matching_dropdown,
            self.duplicate_dropdown,
            self.operation_dropdown,
            self.file_column_dropdown
        ]:

            dropdown.configure(
                command=lambda _: self.update_configuration_summary()
            )


        for dropdown in self.folder_dropdowns:

            dropdown.configure(
                command=lambda _: self.update_configuration_summary()
            )
            
            
    # ================================
    # Organization Helper Functions
    # ================================

    def update_configuration_summary(self, *args):

        folder_levels = []

        for dropdown in self.folder_dropdowns:

            value = dropdown.get()

            if value and not value.startswith("Folder Level"):

                folder_levels.append(value)


        if not folder_levels:

            folder_text = "-"

        else:

            folder_text = "\n".join(
                folder_levels
            )


        summary = (
            f"File Type:\n"
            f"{self.file_type_dropdown.get()}\n\n"

            f"Matching Mode:\n"
            f"{self.matching_dropdown.get()}\n\n"

            f"Duplicate Handling:\n"
            f"{self.duplicate_dropdown.get()}\n\n"

            f"Operation:\n"
            f"{self.operation_dropdown.get()}\n\n"

            f"File Column:\n"
            f"{self.file_column_dropdown.get()}\n\n"

            f"Folder Levels:\n"
            f"{folder_text}"
        )


        self.config_summary.configure(
            text=summary
        )


        self.check_configuration_status()



    def check_configuration_status(self):


        errors = []


        if not self.source_folder.get():

            errors.append(
                "Source folder missing"
            )


        if not self.destination_folder.get():

            errors.append(
                "Destination folder missing"
            )


        if not self.excel_file.get():

            errors.append(
                "Excel file missing"
            )


        if (
            self.file_column_dropdown.get()
            ==
            "Select File Column"
        ):

            errors.append(
                "File column not selected"
            )


        if errors:


            self.ready_status.configure(

                text=
                "🟡 " +
                errors[0]

            )


        else:


            self.ready_status.configure(

                text=
                "🟢 Configuration Ready"

            )

    # ================================
    # Reports Tab
    # ================================

    def create_reports_tab(self):


        self.reports_frame = ctk.CTkScrollableFrame(
            self.reports_tab
        )


        self.reports_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


        ctk.CTkLabel(
            self.reports_frame,
            text="📊 Reports & Processing Monitor",
            font=("Segoe UI",24,"bold")
        ).pack(
            pady=(10,25)
        )


        # ============================
        # Progress Card
        # ============================


        progress_card = ctk.CTkFrame(
            self.reports_frame
        )


        progress_card.pack(
            fill="x",
            padx=40,
            pady=10
        )


        ctk.CTkLabel(
            progress_card,
            text="Processing Progress",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=15
        )


        self.progress_bar = ctk.CTkProgressBar(
            progress_card,
            width=700,
            height=20
        )


        self.progress_bar.pack(
            pady=15
        )


        self.progress_bar.set(
            0
        )


        ctk.CTkLabel(
            progress_card,
            textvariable=self.status_text,
            font=("Segoe UI",15)
        ).pack(
            pady=5
        )


        ctk.CTkLabel(
            progress_card,
            textvariable=self.current_file
        ).pack(
            pady=5
        )


        stats_frame = ctk.CTkFrame(
            progress_card,
            fg_color="transparent"
        )

        stats_frame.pack(
            pady=15
        )


        # Total Files Card

        total_card = ctk.CTkFrame(
            stats_frame,
            width=180,
            height=120
        )

        total_card.configure(
            corner_radius=15
        )
        
        total_card.pack(
            side="left",
            padx=15
        )


        ctk.CTkLabel(
            total_card,
            text="Total Files",
            font=("Segoe UI",14)
        ).pack(
            pady=5
        )


        ctk.CTkLabel(
            total_card,
            textvariable=self.total_files_value,
            font=("Segoe UI",22,"bold")
        ).pack()



        # Copied Card

        copied_card = ctk.CTkFrame(
            stats_frame,
            width=180,
            height=120
        )

        copied_card.configure(
            corner_radius=15
        )

        copied_card.pack(
            side="left",
            padx=15
        )


        ctk.CTkLabel(
            copied_card,
            text="Copied Files",
            font=("Segoe UI",14)
        ).pack(
            pady=5
        )


        ctk.CTkLabel(
            copied_card,
            textvariable=self.copied_files_value,
            font=("Segoe UI",22,"bold")
        ).pack()



        # Missing Card

        missing_card = ctk.CTkFrame(
            stats_frame,
            width=180,
            height=120
        )

        missing_card.configure(
            corner_radius=15
        )

        missing_card.pack(
            side="left",
            padx=15
        )


        ctk.CTkLabel(
            missing_card,
            text="Missing Files",
            font=("Segoe UI",14)
        ).pack(
            pady=5
        )


        ctk.CTkLabel(
            missing_card,
            textvariable=self.missing_files_value,
            font=("Segoe UI",22,"bold")
        ).pack()


        # ============================
        # Control Buttons
        # ============================


        button_frame = ctk.CTkFrame(
            self.reports_frame,
            fg_color="transparent"
        )


        button_frame.pack(
            pady=15
        )


        test_button = ctk.CTkButton(
            button_frame,
            text="🔍 Test Indexer",
            width=200,
            height=40,
            command=self.test_indexer
        )


        test_button.pack(
            side="left",
            padx=10
        )


        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ Start Organization",
            width=200,
            height=40,
            command=self.start_organization
        )


        self.start_button.pack(
            side="left",
            padx=10
        )



        # ============================
        # Log Section
        # ============================


        log_card = ctk.CTkFrame(
            self.reports_frame
        )


        log_card.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=10
        )


        ctk.CTkLabel(
            log_card,
            text="📜 Processing Log",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=10
        )


        self.log_box = ctk.CTkTextbox(
            log_card,
            height=180
        )


        self.log_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )


        self.log_box.insert(
            "end",
            "Application Ready...\n"
        )


        self.log_box.configure(
            state="disabled"
        )

    # ================================
    # Settings Tab
    # ================================

    def create_settings_tab(self):


        # Main Scrollable Frame

        self.settings_frame = ctk.CTkScrollableFrame(
            self.settings_tab
        )

        self.settings_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )



        # ==============================
        # Header
        # ==============================

        ctk.CTkLabel(
            self.settings_frame,
            text="🔧 Application Settings",
            font=("Segoe UI",26,"bold")
        ).pack(
            pady=(15,25)
        )



        # ==============================
        # Appearance Card
        # ==============================

        appearance_card = ctk.CTkFrame(
            self.settings_frame,
            corner_radius=15
        )

        appearance_card.pack(
            fill="x",
            padx=40,
            pady=10
        )


        ctk.CTkLabel(
            appearance_card,
            text="🎨 Appearance",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=15
        )


        ctk.CTkLabel(
            appearance_card,
            text="Select Application Theme"
        ).pack()



        self.theme_dropdown = ctk.CTkComboBox(
            appearance_card,
            values=[
                "System",
                "Light",
                "Dark"
            ],
            width=350,
            command=self.change_theme
        )


        self.theme_dropdown.pack(
            pady=15
        )


        self.theme_dropdown.set(
            "System"
        )

        # ==============================
        # Color Theme
        # ==============================

        ctk.CTkLabel(
            appearance_card,
            text="Select Color Theme"
        ).pack(
            pady=(15,5)
        )


        self.color_theme_dropdown = ctk.CTkComboBox(
            appearance_card,
            values=[
                "blue",
                "green",
                "dark-blue"
            ],
            width=350,
            command=self.change_color_theme
        )


        self.color_theme_dropdown.pack(
            pady=10
        )


        self.color_theme_dropdown.set(
            "blue"
        )
        # ==============================
        # Application Preferences
        # ==============================


        preference_card = ctk.CTkFrame(
            self.settings_frame
        )


        preference_card.pack(
            fill="x",
            padx=40,
            pady=10
        )



        ctk.CTkLabel(
            preference_card,
            text="⚙ Preferences",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=15
        )



        self.auto_save_checkbox = ctk.CTkCheckBox(
            preference_card,
            text="Auto Save Project Configuration"
        )


        self.auto_save_checkbox.pack(   
            pady=8
        )



        self.confirm_checkbox = ctk.CTkCheckBox(
            preference_card,
            text="Confirm Before Moving Files"
        )


        self.confirm_checkbox.pack(
            pady=8
        )



        self.report_checkbox = ctk.CTkCheckBox(
            preference_card,
            text="Generate Processing Report After Completion"
        )


        self.report_checkbox.pack(
            pady=8
        )
        self.report_checkbox.select()




        # ==============================
        # Application Information
        # ==============================


        info_card = ctk.CTkFrame(
            self.settings_frame
        )


        info_card.pack(
            fill="x",
            padx=40,
            pady=10
        )



        ctk.CTkLabel(
            info_card,
            text="ℹ About Application",
            font=("Segoe UI",18,"bold")
        ).pack(
            pady=15
        )



        ctk.CTkLabel(
            info_card,
            text=
            f"{APP_NAME}\n\n"
            f"Version: {APP_FULL_VERSION}\n"
            "Developed for Internal File Management\n\n"
            "Features:\n"
            "• Smart File Matching\n"
            "• Excel Based Organization\n"
            "• Duplicate Handling\n"
            "• Processing Reports",
            justify="left",
            font=("Segoe UI",14)
        ).pack(
            padx=20,
            pady=15
        )

        self.update_button = ctk.CTkButton(
            info_card,
            text="Check for Updates",
            command=lambda: self.check_for_updates(manual=True),
        )
        self.update_button.pack(pady=(0, 20))

    # ==============================
    # Change Theme
    # ==============================
    
    def change_theme(self, mode):


        if mode == "System":

            ctk.set_appearance_mode(
                "System"
            )


        elif mode == "Light":

            ctk.set_appearance_mode(
                "Light"
            )


        elif mode == "Dark":

            ctk.set_appearance_mode(
                "Dark"
            )
            
    # ==============================
    # Change Color Theme
    # ==============================

    def change_color_theme(self, theme):

        self.color_theme.set(
            theme
        )

        self.add_log(
            f"Color theme changed to {theme}. Restart application to apply."
        )
        
    # ================================
    # Start Organization
    # ================================

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
            "generate_report": bool(self.report_checkbox.get()),
        }


        self.start_button.configure(
            state="disabled"
        )

        self.header_status.set(
            "🟡 Processing Files..."
        )

        self.bottom_status.set(
            "Universal File Organizer | Starting..."
        )


        thread = threading.Thread(
            target=self.run_worker,
            daemon=True
        )


        thread.start()

    # ================================
    # Run Worker
    # ================================
    
    def run_worker(self):

        try:
            result = Worker(self).organize()
            self._ui_events.put(("_finish_job", (result, None)))
        except Exception as error:
            self._ui_events.put(("_finish_job", (None, str(error))))
        return

        '''Legacy direct UI updates retained only for source-history reference.
        worker = Worker(self)

        worker.organize()

        self.after(
            0,
            lambda:
            self.header_status.set(
                "🟢 Completed Successfully ✓"
            )
        )

        self.bottom_status.set(
            "Universal File Organizer | Completed Successfully ✓"
        )


        self.start_button.configure(
            state="normal"
        )
    
        '''
    # ================================
    # Update Progress Method
    # ================================        
        
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
            self.bottom_status.set("Universal File Organizer | Processing failed")
            self.status_text.set("Processing failed")
            self.add_log(f"Processing failed: {error}")
            messagebox.showerror("Organization failed", error)
            return
        self.header_status.set("Completed successfully")
        self.bottom_status.set("Universal File Organizer | Completed successfully")
        self.status_text.set("Completed successfully")

    def check_for_updates(self, manual=True):
        if hasattr(self, "update_button"):
            self.update_button.configure(state="disabled", text="Checking for updates...")
        thread = threading.Thread(target=self._run_update_check, args=(manual,), daemon=True)
        thread.start()

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
                f"Version {latest} is available. You have {APP_VERSION}.\n\nOpen the download page now?",
            )
            if should_open and result.get("download_url"):
                webbrowser.open(result["download_url"])
            return
        if manual:
            messagebox.showinfo("Universal File Organizer", result.get("reason", "You already have the latest version."))

    def update_progress(
        self,
        current,
        total,
        copied,
        missing,
        current_file
    ):
        if threading.current_thread() is not threading.main_thread():
            self._ui_events.put(("update_progress", (current, total, copied, missing, current_file)))
            return
        self.header_status.set(
            f"🟡 Processing {current}/{total}"
        )

        percent = current / total

        self.progress_bar.set(percent)

        self.status_text.set(
            f"{int(percent*100)}% Completed ({current}/{total})"
        )

        self.current_file.set(
            f"Processing: {current_file}"
        )

        self.total_files_value.set(
            str(total)
        )

        self.copied_files_value.set(
            str(copied)
        )

        self.missing_files_value.set(
            str(missing)
        )
        
        self.bottom_status.set(
            f"Processing: {current_file}"
        )
        
        self.update_idletasks()

    # ================================
    # Logging Function
    # ================================        
        
    def add_log(self, message):
        if threading.current_thread() is not threading.main_thread():
            self._ui_events.put(("add_log", (message,)))
            return
        self.log_box.configure(state="normal")

        self.log_box.insert(
            "end",
            message + "\n"
        )

        self.log_box.see("end")

        self.log_box.configure(state="disabled")

        self.update_idletasks()
        
    def clear_log(self):

        self.log_box.configure(state="normal")

        self.log_box.delete(
            "1.0",
            "end"
        )

        self.log_box.configure(state="disabled")
        
    # ===============================
    # Save Project Method
    # ===============================
                
    def save_project(self):

        profile = {

            "source_folder":
                self.source_folder.get(),

            "destination_folder":
                self.destination_folder.get(),

            "excel_file":
                self.excel_file.get(),

            "sheet":
                self.sheet_dropdown.get(),

            "file_type":
                self.file_type_dropdown.get(),

            "matching_mode":
                self.matching_dropdown.get(),

            "duplicate_mode":
                self.duplicate_dropdown.get(),

            "operation":
                self.operation_dropdown.get(),

            "file_column":
                self.file_column_dropdown.get(),

            "folder_levels":[
                dropdown.get()
                for dropdown in self.folder_dropdowns
            ]

        }

        file = filedialog.asksaveasfilename(

            defaultextension=".ufo",

            filetypes=[
                (
                    "Universal Organizer Project",
                    "*.ufo"
                )
            ]
        )

        if file:

            self.profile_manager.save_profile(
                file,
                profile
            )

            print("Project Saved.")
            
    # ===============================
    # Load Project Method
    # ===============================
    
    def load_project(self):
        file = filedialog.askopenfilename(
            filetypes=[("Universal Organizer Project", "*.ufo"), ("JSON files", "*.json")]
        )
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
