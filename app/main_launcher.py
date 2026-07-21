import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import threading
import logging

# Global modern appearance presets
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ---------------------------------------------------------------------------
# LOGGING SETUP – errors are saved to error.log next to the script
# ---------------------------------------------------------------------------
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CRITICAL PATH MAPPING FOR COMPILED ENVIRONMENTS
# ---------------------------------------------------------------------------
# Handles absolute path tracking whether running loose or inside a frozen installer folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Inject base directories directly into system lookups
for path in [PROJECT_ROOT, CURRENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Create an explicit fallback namespace route container for legacy 'app.xxx' imports
try:
    import app
except ModuleNotFoundError:
    import types
    app = types.ModuleType('app')
    sys.modules['app'] = app

# Securely register old code endpoints into the virtual namespace routing table
import common.excel_handler as excel_handler
import common.updater as updater
import common.version as version
import common.config as config
import common.profile_manager as profile_manager

app.excel_handler = excel_handler
app.updater = updater
app.version = version
app.config = config
app.profile_manager = profile_manager
# ---------------------------------------------------------------------------

# FIXED: Standard Python Native Package Imports.
# Pulls your functions from frozen binary modules packed inside your installer system.
from organizer.gui import UniversalFileOrganizer
from separator.separator import split_file_by_column, get_file_columns

class ApplicationHub:
    def __init__(self, root):
        self.root = root
        self.root.title("Field Operations Toolkit")
        self.root.geometry("600x560")
        self.show_launcher_dashboard()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_launcher_dashboard(self):
        self.clear_window()

        label = ctk.CTkLabel(
            self.root,
            text="Field Operations Toolkit",
            font=("Segoe UI", 24, "bold"),
            text_color=("#1B365D", "#E2E8F0")
        )
        label.pack(pady=(45, 10))

        sub_label = ctk.CTkLabel(
            self.root,
            text="Select an active automated workspace tool below:",
            font=("Segoe UI", 13),
            text_color="gray"
        )
        sub_label.pack(pady=(0, 30))

        btn_organizer = ctk.CTkButton(
            self.root,
            text="📂  Run Universal File Organizer",
            width=360, height=52,
            font=("Segoe UI", 14, "bold"),
            corner_radius=12,
            command=self.launch_file_organizer_interface
        )
        btn_organizer.pack(pady=15)

        btn_separator = ctk.CTkButton(
            self.root,
            text="📊  Run Dynamic File Categorizer & Splitter",
            width=360, height=52,
            font=("Segoe UI", 14, "bold"),
            corner_radius=12,
            command=self.launch_file_separator_interface
        )
        btn_separator.pack(pady=15)

        footer = ctk.CTkLabel(self.root, text="v1.1.5 • Secure Automation Suite", font=("Segoe UI", 11), text_color="gray")
        footer.pack(side="bottom", pady=20)

    def launch_file_organizer_interface(self):
        def execute_handover():
            self.clear_window()
            try:
                self.organizer_app = UniversalFileOrganizer(self.root)
            except TypeError as e:
                if "takes 1 positional argument" in str(e):
                    self.root.destroy()
                    new_root = ctk.CTk()
                    UniversalFileOrganizer()
                    new_root.mainloop()
                else:
                    logging.error("Crash during Organizer Handover", exc_info=True)
                    raise
                    
        self.root.after(100, execute_handover)

    def launch_file_separator_interface(self):
        def execute_handover():
            self.clear_window()
            self._build_separator_ui()
            
        self.root.after(100, execute_handover)
    def _build_separator_ui(self):
        # Top navigation panel
        nav_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=15)

        back_btn = ctk.CTkButton(
            nav_frame,
            text="← Return to Menu",
            width=130, height=32,
            font=("Segoe UI", 12, "bold"),
            fg_color=("#E2E8F0", "#2D3748"),
            text_color=("#2D3748", "#E2E8F0"),
            hover_color=("#CBD5E1", "#4A5568"),
            corner_radius=8
        )
        back_btn.configure(command=self.show_launcher_dashboard)
        back_btn.pack(side="left")

        ctk.CTkLabel(self.root, text="Universal File Categorizer & Splitter", font=("Segoe UI", 18, "bold")).pack(pady=(5, 15))

        # Main parameter setup panel box
        card_frame = ctk.CTkFrame(self.root, corner_radius=14, border_width=1, border_color=("#E2E8F0", "#2D3748"))
        card_frame.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        # Field Set 1: Source File Selection
        ctk.CTkLabel(card_frame, text="Select Master Dataset (Excel or CSV file):", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(20,0))
        file_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=25, pady=5)

        self.file_entry = ctk.CTkEntry(file_frame, height=35, corner_radius=8, placeholder_text="Browse a master datasheet location...")
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def browse_file():
            path = filedialog.askopenfilename(filetypes=[("Data Files", "*.xlsx *.xls *.csv")])
            if path:
                self.file_entry.delete(0, tk.END)
                self.file_entry.insert(0, path)
                default_dir = os.path.dirname(path)
                self.dest_entry.delete(0, tk.END)
                self.dest_entry.insert(0, default_dir)
                columns = get_file_columns(path)
                if columns:
                    self.column_dropdown.configure(values=columns)
                    self.column_dropdown.set(columns[0])
                else:
                    self.column_dropdown.configure(values=["No columns found"])
                    self.column_dropdown.set("No columns found")

        ctk.CTkButton(file_frame, text="Browse File", width=100, height=35, corner_radius=8, command=browse_file).pack(side="right")

        # Field Set 2: Target Destination Folder Selection
        ctk.CTkLabel(card_frame, text="Select Destination Folder (Where to save split files):", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(15,0))
        dest_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        dest_frame.pack(fill="x", padx=25, pady=5)

        self.dest_entry = ctk.CTkEntry(dest_frame, height=35, corner_radius=8, placeholder_text="Choose output directory location...")
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def browse_destination():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.dest_entry.delete(0, tk.END)
                self.dest_entry.insert(0, folder_path)

        ctk.CTkButton(dest_frame, text="Browse Folder", width=100, height=35, corner_radius=8, command=browse_destination).pack(side="right")

        # Field Set 3: Categorization Parameter Dropdown Row
        ctk.CTkLabel(card_frame, text="Select Categorization Column (Automated Dropdown):", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(15, 0))
        self.column_dropdown = ctk.CTkComboBox(card_frame, height=35, corner_radius=8, values=["Please browse and select a file first..."])
        self.column_dropdown.pack(fill="x", padx=25, pady=5)

        # Subtle layout loading progress bar tracker (hidden on init)
        self.progress_bar = ctk.CTkProgressBar(card_frame, mode="indeterminate", height=12, corner_radius=6)
        self.progress_bar.pack(fill="x", padx=25, pady=(15, 0))
        self.progress_bar.pack_forget()

        # Operational triggering controls layout row
        btn_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=15)

        self.btn_process = ctk.CTkButton(
            btn_frame,
            text="⚡  Execute Categorical File Split",
            width=190, height=44,
            font=("Segoe UI", 13, "bold"),
            corner_radius=10,
            fg_color=("#10B981", "#059669"),
            hover_color=("#059669", "#047857"),
            command=self._start_splitting
        )
        self.btn_process.pack(side="left", padx=(0, 15))

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️  Clear All",
            width=120, height=44,
            font=("Segoe UI", 13),
            fg_color=("#E2E8F0", "#2D3748"),
            text_color=("#2D3748", "#E2E8F0"),
            hover_color=("#CBD5E1", "#4A5568"),
            corner_radius=10,
            command=self._clear_splitter_form
        )
        clear_btn.pack(side="left")

        # Status text notification footer bar
        self.status_label = ctk.CTkLabel(
            self.root,
            text="",
            font=("Segoe UI", 12),
            text_color=("gray40", "gray70"),
            anchor="w"
        )
        self.status_label.pack(side="bottom", fill="x", padx=20, pady=10)

    def _start_splitting(self):
        """Validates entry configuration parameters and spins up the processing thread."""
        master_file_path = self.file_entry.get()
        target_column_name = self.column_dropdown.get()
        custom_output_dir = self.dest_entry.get()

        if not master_file_path or not custom_output_dir or "select a file" in target_column_name or "No columns" in target_column_name:
            messagebox.showwarning("Incomplete Fields", "Please make sure to select a file, a valid destination folder, and a splitting column.")
            return

        # Shift visual elements to processing state
        self.btn_process.configure(state="disabled", text="Processing...")
        self.progress_bar.pack(fill="x", padx=25, pady=(15, 0))
        self.progress_bar.start()
        self.status_label.configure(text="Processing file operations, please wait...", text_color=("gray40", "gray70"))

        # Run via separate worker thread to lock out UI freezes on massive databases
        threading.Thread(target=self._run_split_thread_wrapper, daemon=True).start()

    def _run_split_thread_wrapper(self):
        """Worker routing thread evaluating backend tasks and returning hooks via after()."""
        master_file_path = self.file_entry.get()
        target_column_name = self.column_dropdown.get()
        custom_output_dir = self.dest_entry.get()

        try:
            success, msg = split_file_by_column(master_file_path, target_column_name, custom_output_dir)
        except Exception as e:
            success = False
            msg = f"Unexpected processing error: {str(e)}"
            logging.error(f"Data separation core exception failure for {master_file_path}: {e}", exc_info=True)

        # Safely marshal interface state adjustments back into the main loop thread
        self.root.after(0, lambda: self._on_split_complete(success, msg))

    def _on_split_complete(self, success, msg):
        """Resets visual states and reflects final compilation report outcomes on the UI."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_process.configure(state="normal", text="⚡  Execute Categorical File Split")

        if success:
            self.status_label.configure(text=f"✅ {msg}", text_color=("#10B981", "#34D399"))
        else:
            self.status_label.configure(text=f"❌ {msg}", text_color=("#EF4444", "#F87171"))

    def _clear_splitter_form(self):
        """Resets panel entry data frames back to their baseline default layouts."""
        self.file_entry.delete(0, tk.END)
        self.dest_entry.delete(0, tk.END)
        self.column_dropdown.configure(values=["Please browse and select a file first..."])
        self.column_dropdown.set("Please browse and select a file first...")
        self.status_label.configure(text="")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_process.configure(state="normal", text="⚡  Execute Categorical File Split")

if __name__ == "__main__":
    window = ctk.CTk()
    app = ApplicationHub(window)
    window.mainloop()
