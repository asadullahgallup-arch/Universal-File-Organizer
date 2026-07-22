from app.main_launcher import ApplicationHub
import customtkinter as ctk

if __name__ == "__main__":
    root = ctk.CTk()
    app = ApplicationHub(root)
    root.mainloop()