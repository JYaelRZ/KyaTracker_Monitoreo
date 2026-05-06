import os
import sys
import customtkinter as ctk

from database.setup_db import init_db
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

        # Cargar UI Principal
        self.main_frame = MonitoreoDashboard(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = App()
    app.mainloop()
