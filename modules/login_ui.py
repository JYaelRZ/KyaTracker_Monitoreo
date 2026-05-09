import customtkinter as ctk
from PIL import Image, ImageTk
import os
from tkinter import messagebox
from database.connection import SessionLocal
from database.models import User
from werkzeug.security import generate_password_hash, check_password_hash

class LoginWindow(ctk.CTkFrame):
    def __init__(self, master, on_login_success, **kwargs):
        super().__init__(master, fg_color="#0A0B1A", **kwargs)
        self.on_login_success = on_login_success
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.create_left_panel()
        self.create_right_panel()

    def create_left_panel(self):
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=60, pady=60)
        
        # Center contents
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(8, weight=1)

        # Title
        title = ctk.CTkLabel(self.left_frame, text="Sign in account", 
                             font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color="white")
        title.grid(row=1, column=0, pady=(0, 5))
        
        subtitle = ctk.CTkLabel(self.left_frame, text="Log in to your account to continue.", 
                                font=ctk.CTkFont(family="Inter", size=14), text_color="#64748B")
        subtitle.grid(row=2, column=0, pady=(0, 40))

        # Inputs
        self.email_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Email", width=350, height=45, 
                                        corner_radius=10, fg_color="#12142B", border_color="#1E2243", text_color="white")
        self.email_entry.grid(row=3, column=0, pady=10)

        self.password_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Password", width=350, height=45, 
                                           corner_radius=10, fg_color="#12142B", border_color="#1E2243", text_color="white", show="*")
        self.password_entry.grid(row=4, column=0, pady=10)

        # Login button
        self.login_btn = ctk.CTkButton(self.left_frame, text="Login", width=350, height=45, 
                                       corner_radius=20, fg_color="#2D6ADF", hover_color="#1E4EAA",
                                       font=ctk.CTkFont(weight="bold"), command=self.do_login)
        self.login_btn.grid(row=5, column=0, pady=(20, 10))
        
        # Register switch (for admins or first setup)
        self.mode = "login"
        self.switch_mode_btn = ctk.CTkButton(self.left_frame, text="Don't have an account? Register", 
                                             fg_color="transparent", text_color="#2D6ADF", hover_color="#0A0B1A",
                                             command=self.toggle_mode)
        self.switch_mode_btn.grid(row=6, column=0)

    def create_right_panel(self):
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)

        # Simulate the gradient background and logo
        bg_frame = ctk.CTkFrame(self.right_frame, fg_color="#0D112A", corner_radius=20)
        bg_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # You would load the actual Kya Logo here
        # For now, we put a large text or placeholder
        logo_label = ctk.CTkLabel(bg_frame, text="KYA", 
                                  font=ctk.CTkFont(family="Inter", size=100, weight="bold"), 
                                  text_color="#2D6ADF")
        logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        sub_logo = ctk.CTkLabel(bg_frame, text="TRACKER", 
                                font=ctk.CTkFont(family="Inter", size=30, weight="bold"), 
                                text_color="white")
        sub_logo.place(relx=0.5, rely=0.6, anchor="center")

    def toggle_mode(self):
        if self.mode == "login":
            self.mode = "register"
            self.switch_mode_btn.configure(text="Already have an account? Login")
            self.login_btn.configure(text="Register")
        else:
            self.mode = "login"
            self.switch_mode_btn.configure(text="Don't have an account? Register")
            self.login_btn.configure(text="Login")

    def do_login(self):
        email = self.email_entry.get().strip()
        pwd = self.password_entry.get().strip()
        
        if not email or not pwd:
            messagebox.showwarning("Error", "Please fill all fields")
            return

        with SessionLocal() as db:
            if self.mode == "register":
                # Check if user exists
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    messagebox.showerror("Error", "User already exists.")
                    return
                # Make first user admin, subsequent normal
                count = db.query(User).count()
                role = "admin" if count == 0 else "normal"
                
                new_user = User(
                    email=email,
                    password=generate_password_hash(pwd),
                    role=role
                )
                db.add(new_user)
                db.commit()
                messagebox.showinfo("Success", f"User registered successfully as {role}")
                self.on_login_success(new_user)
            else:
                user = db.query(User).filter(User.email == email).first()
                if user and check_password_hash(user.password, pwd):
                    self.on_login_success(user)
                else:
                    messagebox.showerror("Error", "Invalid credentials")
