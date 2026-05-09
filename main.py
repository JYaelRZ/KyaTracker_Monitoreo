import os
import sys
import customtkinter as ctk

from database.setup_db import init_db
from modules.login_ui import LoginWindow
from modules.dashboard_ui import MonitoreoDashboard

ctk.set_appearance_mode("light") # Coincide con las capturas de Crextio
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("KyaTracker Monitoreo y Custodia")
        self.geometry("1200x800")
        self.configure(bg="#F4F7FE") 
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Inicializar Base de Datos en Supabase
        init_db()

        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        # The login window is dark theme
        self.configure(bg="#0A0B1A") 
        self.current_frame = LoginWindow(self, on_login_success=self.show_dashboard)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_dashboard(self, user):
        if self.current_frame:
            self.current_frame.destroy()
        
        # Reset to light theme for dashboard
        self.configure(bg="#F4F7FE") 
        
        # Pass user to dashboard
        self.current_frame = MonitoreoDashboard(self, user=user)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = App()
    app.mainloop()
