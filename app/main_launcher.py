import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location, module_from_spec
import threading
import logging
import inspect
import webbrowser

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

SEARCH_DIRECTORIES = [
    PROJECT_ROOT,
    CURRENT_DIR,
    os.path.join(CURRENT_DIR, 'common'),
    os.path.join(CURRENT_DIR, 'organizer'),
    os.path.join(CURRENT_DIR, 'separator')
]

for folder in SEARCH_DIRECTORIES:
    if folder not in sys.path:
        sys.path.insert(0, folder)

class ResilientNamespaceInterceptor(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("app."):
            module_target = fullname.split(".")[-1]
            for folder in SEARCH_DIRECTORIES:
                potential_file_path = os.path.join(folder, f"{module_target}.py")
                if os.path.exists(potential_file_path):
                    return spec_from_file_location(fullname, potential_file_path)
        return None

sys.meta_path.insert(0, ResilientNamespaceInterceptor())

# Dynamic imports – internal class names remain unchanged
gui_file_path = os.path.join(CURRENT_DIR, 'organizer', 'gui.py')
gui_spec = spec_from_file_location("organizer_gui_module", gui_file_path)
gui_module = module_from_spec(gui_spec)
sys.modules["organizer_gui_module"] = gui_module
gui_spec.loader.exec_module(gui_module)
UniversalFileOrganizer = getattr(gui_module, "UniversalFileOrganizer")

org_params = list(inspect.signature(UniversalFileOrganizer.__init__).parameters.keys())
HAS_PARENT = len(org_params) >= 2

separator_file_path = os.path.join(CURRENT_DIR, 'separator', 'separator.py')
sep_spec = spec_from_file_location("separator_logic_module", separator_file_path)
sep_module = module_from_spec(sep_spec)
sys.modules["separator_logic_module"] = sep_module
sep_spec.loader.exec_module(sep_module)
split_file_by_column = getattr(sep_module, "split_file_by_column")
get_file_columns = getattr(sep_module, "get_file_columns")

from app.updater import UpdateChecker
from app.version import APP_VERSION


class BidirectionalScrollableFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.v_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.h_scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self._on_vertical_scroll,
                              xscrollcommand=self._on_horizontal_scroll)

        self.content_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.content_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        self.content_frame.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_vertical_scroll(self, *args):
        self.v_scrollbar.set(*args)
        self.canvas.yview(*args)
        self._update_scrollbar_visibility()

    def _on_horizontal_scroll(self, *args):
        self.h_scrollbar.set(*args)
        self.canvas.xview(*args)
        self._update_scrollbar_visibility()

    def _update_scrollbar_visibility(self):
        bbox = self.canvas.bbox("all")
        if bbox:
            content_w = bbox[2] - bbox[0]
            content_h = bbox[3] - bbox[1]
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            if content_h > canvas_h:
                self.v_scrollbar.pack(side="right", fill="y")
            else:
                self.v_scrollbar.pack_forget()
            if content_w > canvas_w:
                self.h_scrollbar.pack(side="bottom", fill="x")
            else:
                self.h_scrollbar.pack_forget()

    def _on_content_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar_visibility()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.content_window, width=event.width)
        self._update_scrollbar_visibility()

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_vertical_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_horizontal_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")

    def _on_vertical_mousewheel(self, event):
        if self.v_scrollbar.winfo_ismapped():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_horizontal_mousewheel(self, event):
        if self.h_scrollbar.winfo_ismapped():
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")


class ApplicationHub:
    def __init__(self, root):
        self.root = root
        self.root.title("Field Operations Toolkit")
        self.root.geometry("600x560")
        self.root.minsize(500, 400)
        self.root.app_hub = self

        self.appearance_mode = tk.StringVar(value="System")
        self.color_theme = tk.StringVar(value="blue")

        self.show_launcher_dashboard()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_launcher_dashboard(self):
        self.clear_window()
        self.root.geometry("600x560")

        main_scroll = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(main_scroll, text="Field Operations Toolkit",
                     font=("Segoe UI", 28, "bold"), text_color=("#1B365D", "#E2E8F0")).pack(pady=(45, 5))
        ctk.CTkLabel(main_scroll, text="Professional Field Data Management & Automation",
                     font=("Segoe UI", 13), text_color="gray").pack(pady=(0, 30))

        btn_organizer = ctk.CTkButton(main_scroll, text="📂  Launch Field Data Organizer",
                                      width=360, height=52, font=("Segoe UI", 14, "bold"),
                                      corner_radius=12, command=self.launch_file_organizer_interface)
        btn_organizer.pack(pady=15)

        btn_separator = ctk.CTkButton(main_scroll, text="📊  Launch Field Data Splitter",
                                      width=360, height=52, font=("Segoe UI", 14, "bold"),
                                      corner_radius=12, command=self.launch_file_separator_interface)
        btn_separator.pack(pady=15)

        settings_btn = ctk.CTkButton(main_scroll, text="⚙ Settings", width=160, height=36,
                                     font=("Segoe UI", 12, "bold"),
                                     fg_color=("#E2E8F0", "#2D3748"),
                                     text_color=("#2D3748", "#E2E8F0"),
                                     hover_color=("#CBD5E1", "#4A5568"),
                                     corner_radius=10,
                                     command=self.show_settings)
        settings_btn.pack(pady=(20, 10))

        ctk.CTkLabel(main_scroll, text="Field Operations Toolkit v1.0.2 • Secure Automation",
                     font=("Segoe UI", 11), text_color="gray").pack(pady=20)

    def show_settings(self):
        self.clear_window()
        self.root.geometry("600x560")

        nav_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(nav_frame, text="← Return to Menu", width=130, height=32,
                      font=("Segoe UI", 12, "bold"),
                      fg_color=("#E2E8F0", "#2D3748"),
                      text_color=("#2D3748", "#E2E8F0"),
                      hover_color=("#CBD5E1", "#4A5568"),
                      corner_radius=8,
                      command=self.show_launcher_dashboard).pack(side="left")

        ctk.CTkLabel(self.root, text="Settings", font=("Segoe UI", 20, "bold")).pack(pady=(10, 10))

        card = BidirectionalScrollableFrame(self.root, corner_radius=14, border_width=1,
                                            border_color=("#E2E8F0", "#2D3748"))
        card.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        ctk.CTkLabel(card.content_frame, text="🎨 Appearance", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=25, pady=(20, 10))
        ctk.CTkLabel(card.content_frame, text="Appearance Mode", font=("Segoe UI", 12)).pack(anchor="w", padx=25)
        mode_dropdown = ctk.CTkComboBox(card.content_frame, values=["System", "Light", "Dark"],
                                        variable=self.appearance_mode, width=250)
        mode_dropdown.pack(fill="x", padx=25, pady=(0, 15))
        mode_dropdown.set(self.appearance_mode.get())

        ctk.CTkLabel(card.content_frame, text="Color Theme", font=("Segoe UI", 12)).pack(anchor="w", padx=25)
        color_dropdown = ctk.CTkComboBox(card.content_frame, values=["blue", "green", "dark-blue"],
                                         variable=self.color_theme, width=250)
        color_dropdown.pack(fill="x", padx=25, pady=(0, 25))
        color_dropdown.set(self.color_theme.get())

        ctk.CTkButton(card.content_frame, text="Apply Settings", width=200, height=40,
                      font=("Segoe UI", 13, "bold"),
                      command=lambda: self.apply_global_settings(mode_dropdown.get(), color_dropdown.get())
                     ).pack(pady=(10, 20))

        ctk.CTkFrame(card.content_frame, height=2, fg_color="#CBD5E1").pack(fill="x", padx=25, pady=(10, 5))
        ctk.CTkLabel(card.content_frame, text="🔄 Updates", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=25, pady=(10, 5))
        ctk.CTkLabel(card.content_frame, text="Check for a newer version of Field Operations Toolkit.",
                     font=("Segoe UI", 12)).pack(anchor="w", padx=25)
        ctk.CTkButton(card.content_frame, text="Check for Updates", width=200, height=40,
                      font=("Segoe UI", 13, "bold"),
                      command=self.check_for_updates).pack(pady=(15, 20))

    def apply_global_settings(self, mode, color):
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme(color)
        self.appearance_mode.set(mode)
        self.color_theme.set(color)
        messagebox.showinfo("Settings Applied", "The new appearance settings have been applied.")

    def check_for_updates(self, manual=True):
        threading.Thread(target=self._run_update_check, args=(manual,), daemon=True).start()

    def _run_update_check(self, manual):
        try:
            result = UpdateChecker().check(APP_VERSION)
            self.root.after(0, lambda: self._show_update_result(result, manual, None))
        except Exception as error:
            logging.error("Update check failed", exc_info=True)
            self.root.after(0, lambda: self._show_update_result(None, manual, str(error)))

    def _show_update_result(self, result, manual, error):
        if error:
            if manual:
                messagebox.showwarning("Update check unavailable", error)
            return
        if result.get("available"):
            latest = result["latest_version"]
            if messagebox.askyesno("Update available",
                                   f"Version {latest} is available. You have {APP_VERSION}.\n\nOpen download page?"):
                if result.get("download_url"):
                    webbrowser.open(result["download_url"])
        elif manual:
            messagebox.showinfo("Field Operations Toolkit", result.get("reason", "You already have the latest version."))

    def launch_file_organizer_interface(self):
        if HAS_PARENT:
            self.clear_window()
            self.root.geometry("1200x800")
            try:
                ctk.set_appearance_mode(self.appearance_mode.get())
                ctk.set_default_color_theme(self.color_theme.get())
                self.organizer_app = UniversalFileOrganizer(self.root)
            except Exception as e:
                logging.error("Failed to start Organizer", exc_info=True)
                messagebox.showerror("Error", f"Could not start Organizer:\n{e}")
        else:
            self.root.destroy()
            new_root = ctk.CTk()
            ctk.set_appearance_mode(self.appearance_mode.get())
            ctk.set_default_color_theme(self.color_theme.get())
            UniversalFileOrganizer()
            new_root.mainloop()

    def launch_file_separator_interface(self):
        self.clear_window()
        self.root.geometry("600x560")
        self._build_separator_ui()

    def _build_separator_ui(self):
        nav_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(nav_frame, text="← Return to Menu", width=130, height=32,
                      font=("Segoe UI", 12, "bold"),
                      fg_color=("#E2E8F0", "#2D3748"), text_color=("#2D3748", "#E2E8F0"),
                      hover_color=("#CBD5E1", "#4A5568"), corner_radius=8,
                      command=self.show_launcher_dashboard).pack(side="left")

        ctk.CTkLabel(self.root, text="Field Data Splitter",
                     font=("Segoe UI", 18, "bold")).pack(pady=(5, 10))

        card_frame = BidirectionalScrollableFrame(self.root, corner_radius=14, border_width=1,
                                                  border_color=("#E2E8F0", "#2D3748"))
        card_frame.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        ctk.CTkLabel(card_frame.content_frame, text="Select Master Dataset (Excel or CSV file):",
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(20,0))
        file_frame = ctk.CTkFrame(card_frame.content_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=25, pady=5)

        self.file_entry = ctk.CTkEntry(file_frame, height=35, corner_radius=8,
                                       placeholder_text="Browse a master datasheet location...")
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

        ctk.CTkButton(file_frame, text="Browse File", width=100, height=35,
                      corner_radius=8, command=browse_file).pack(side="right")

        ctk.CTkLabel(card_frame.content_frame, text="Select Destination Folder (Where to save split files):",
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(15,0))
        dest_frame = ctk.CTkFrame(card_frame.content_frame, fg_color="transparent")
        dest_frame.pack(fill="x", padx=25, pady=5)

        self.dest_entry = ctk.CTkEntry(dest_frame, height=35, corner_radius=8,
                                       placeholder_text="Choose output directory location...")
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def browse_destination():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.dest_entry.delete(0, tk.END)
                self.dest_entry.insert(0, folder_path)

        ctk.CTkButton(dest_frame, text="Browse Folder", width=100, height=35,
                      corner_radius=8, command=browse_destination).pack(side="right")

        ctk.CTkLabel(card_frame.content_frame, text="Select Categorization Column (Automated Dropdown):",
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(15, 0))
        self.column_dropdown = ctk.CTkComboBox(card_frame.content_frame, height=35, corner_radius=8,
                                               values=["Please browse and select a file first..."])
        self.column_dropdown.pack(fill="x", padx=25, pady=5)

        self.progress_bar = ctk.CTkProgressBar(card_frame.content_frame, mode="indeterminate", height=12, corner_radius=6)
        self.progress_bar.pack_forget()

        btn_frame = ctk.CTkFrame(card_frame.content_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=15)

        self.btn_process = ctk.CTkButton(
            btn_frame, text="⚡  Execute Data Split", width=190, height=44,
            font=("Segoe UI", 13, "bold"), corner_radius=10,
            fg_color=("#10B981", "#059669"), hover_color=("#059669", "#047857"),
            command=self._start_splitting
        )
        self.btn_process.pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            btn_frame, text="🗑️  Clear All", width=120, height=44,
            font=("Segoe UI", 13),
            fg_color=("#E2E8F0", "#2D3748"), text_color=("#2D3748", "#E2E8F0"),
            hover_color=("#CBD5E1", "#4A5568"), corner_radius=10,
            command=self._clear_splitter_form
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            self.root, text="", font=("Segoe UI", 12),
            text_color=("gray40", "gray70"), anchor="w"
        )
        self.status_label.pack(side="bottom", fill="x", padx=20, pady=10)

    def _start_splitting(self):
        master_file_path = self.file_entry.get()
        target_column_name = self.column_dropdown.get()
        custom_output_dir = self.dest_entry.get()

        if not master_file_path or not custom_output_dir or \
           "select a file" in target_column_name or "No columns" in target_column_name:
            messagebox.showwarning("Incomplete Fields",
                                   "Please make sure to select a file, a valid destination folder, and a splitting column.")
            return

        self.btn_process.configure(state="disabled", text="Processing...")
        self.progress_bar.pack(fill="x", padx=25, pady=(15, 0))
        self.progress_bar.start()
        self.status_label.configure(text="Processing file operations, please wait...", text_color=("gray40", "gray70"))

        threading.Thread(target=self._run_split_thread_wrapper, daemon=True).start()

    def _run_split_thread_wrapper(self):
        master_file_path = self.file_entry.get()
        target_column_name = self.column_dropdown.get()
        custom_output_dir = self.dest_entry.get()

        try:
            success, msg = split_file_by_column(master_file_path, target_column_name, custom_output_dir)
        except Exception as e:
            success = False
            msg = f"Unexpected processing error: {str(e)}"
            logging.error(f"Data separation core exception failure for {master_file_path}: {e}", exc_info=True)

        self.root.after(0, lambda: self._on_split_complete(success, msg))

    def _on_split_complete(self, success, msg):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_process.configure(state="normal", text="⚡  Execute Data Split")

        if success:
            self.status_label.configure(text=f"✅ {msg}", text_color=("#10B981", "#34D399"))
        else:
            self.status_label.configure(text=f"❌ {msg}", text_color=("#EF4444", "#F87171"))

    def _clear_splitter_form(self):
        self.file_entry.delete(0, tk.END)
        self.dest_entry.delete(0, tk.END)
        self.column_dropdown.configure(values=["Please browse and select a file first..."])
        self.column_dropdown.set("Please browse and select a file first...")
        self.status_label.configure(text="")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_process.configure(state="normal", text="⚡  Execute Data Split")

if __name__ == "__main__":
    window = ctk.CTk()
    app = ApplicationHub(window)
    window.mainloop()