import os
import datetime
import uuid
import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import messagebox, filedialog

from database.connection import SessionLocal
from database.models import MonitoringService
from utils.exporter import export_data_to_excel
from utils.ticket_generator import generate_monitoring_ticket_pdf

class MonitoreoDashboard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#F4F7FE", **kwargs)
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        
        self.current_editing_id = None
        
        self.create_top_bar()
        self.create_form_panel()
        self.create_grid_panel()
        self.load_data()
        
    def create_top_bar(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))
        top_frame.grid_columnconfigure(1, weight=1)

        lbl_title = ctk.CTkLabel(
            top_frame, text="KyaTracker Monitoreo y Custodia Digital",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#1E293B"
        )
        lbl_title.grid(row=0, column=0, sticky="w")
        
        # Summary Cards container
        summary_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        summary_frame.grid(row=0, column=1, sticky="e")
        
        self.card_active = self.create_summary_card(summary_frame, "En Ruta", "0")
        self.card_active.pack(side="left", padx=10)
        
        self.card_revenue = self.create_summary_card(summary_frame, "Ingresos Mensuales", "$0.00")
        self.card_revenue.pack(side="left", padx=10)

    def create_summary_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E2E8F0")
        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color="#2D6ADF")
        lbl_val.pack(padx=20, pady=(15, 0))
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Inter", size=12), text_color="#64748B")
        lbl_title.pack(padx=20, pady=(0, 15))
        card.lbl_val = lbl_val
        return card

    def update_summary_cards(self, active_count, total_revenue):
        self.card_active.lbl_val.configure(text=str(active_count))
        self.card_revenue.lbl_val.configure(text=f"${total_revenue:,.2f}")

    def create_form_panel(self):
        self.form_frame = ctk.CTkScrollableFrame(self, fg_color="#FFFFFF", corner_radius=20)
        self.form_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        
        self.lbl_form_title = ctk.CTkLabel(
            self.form_frame, text="Nuevo Servicio",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#2D6ADF"
        )
        self.lbl_form_title.pack(pady=(15, 15))

        # Campos
        self.entry_unit = self._create_input("Unidad / Vehículo:", "Ej. Tracto 01")
        self.entry_operator = self._create_input("Operador:", "Nombre del operador")
        self.entry_client = self._create_input("Cliente:", "Nombre del cliente")
        self.entry_origin = self._create_input("Origen:", "Dirección/Lugar de inicio")
        self.entry_dest = self._create_input("Destino:", "Dirección/Lugar de llegada")
        self.entry_rate = self._create_input("Tarifa por Hora ($):", "Ej. 250.00")

        # Botones
        self.btn_start = ctk.CTkButton(
            self.form_frame, text="🚀 Registrar Salida",
            fg_color="#2D6ADF", hover_color="#1E4EAA", corner_radius=12,
            font=ctk.CTkFont(weight="bold"), command=self.save_service
        )
        self.btn_start.pack(pady=(20, 5), fill="x", padx=20)
        
        self.btn_arrive = ctk.CTkButton(
            self.form_frame, text="🏁 Registrar Llegada",
            fg_color="#27AE60", hover_color="#219653", corner_radius=12,
            font=ctk.CTkFont(weight="bold"), command=self.register_arrival
        )
        self.btn_arrive.pack(pady=5, fill="x", padx=20)
        self.btn_arrive.configure(state="disabled")

        self.btn_ticket = ctk.CTkButton(
            self.form_frame, text="📄 Generar Ticket",
            fg_color="#8E44AD", hover_color="#732D91", corner_radius=12,
            font=ctk.CTkFont(weight="bold"), command=self.generate_ticket
        )
        self.btn_ticket.pack(pady=5, fill="x", padx=20)
        self.btn_ticket.configure(state="disabled")

        self.btn_reset = ctk.CTkButton(
            self.form_frame, text="🧹 Limpiar",
            fg_color="transparent", border_width=1, border_color="#CBD5E1",
            text_color="#64748B", corner_radius=12,
            command=self.reset_form
        )
        self.btn_reset.pack(pady=(15, 10), fill="x", padx=20)

    def _create_input(self, label_text, placeholder):
        ctk.CTkLabel(self.form_frame, text=label_text, text_color="#475569", font=ctk.CTkFont(weight="bold", size=12)).pack(pady=(10, 0), anchor="w", padx=20)
        entry = ctk.CTkEntry(self.form_frame, placeholder_text=placeholder, height=35, corner_radius=8, border_color="#E2E8F0")
        entry.pack(pady=4, fill="x", padx=20)
        return entry

    def create_grid_panel(self):
        grid_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20)
        grid_container.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        grid_container.grid_rowconfigure(1, weight=1)
        grid_container.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(grid_container, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=15)

        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="🔍 Buscar por unidad o cliente...", width=300, corner_radius=8, border_color="#E2E8F0")
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())

        self.btn_export = ctk.CTkButton(
            top_bar, text="⬇ Exportar a Excel", width=120,
            fg_color="#10B981", hover_color="#059669", corner_radius=8,
            command=self.do_export
        )
        self.btn_export.pack(side="right")

        # Treeview styling to look modern
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#FFFFFF", foreground="#1E293B", 
                        rowheight=40, fieldbackground="#FFFFFF", borderwidth=0)
        style.map('Treeview', background=[('selected', '#F1F5F9')], foreground=[('selected', '#0F172A')])
        style.configure("Treeview.Heading", font=('Inter', 10, 'bold'), background="#F8FAFC", foreground="#475569", borderwidth=0)

        columns = ("id", "unit", "client", "operator", "start", "end", "mins", "cost", "status")
        self.tree = ttk.Treeview(grid_container, columns=columns, show="headings", style="Treeview")

        headings = {
            "id":       ("ID", 0), 
            "unit":     ("Unidad", 100),
            "client":   ("Cliente", 150),
            "operator": ("Operador", 120),
            "start":    ("Salida", 130),
            "end":      ("Llegada", 130),
            "mins":     ("Mins", 60),
            "cost":     ("Costo", 80),
            "status":   ("Estado", 120),
        }
        for col, (text, w) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center" if col in ("mins", "cost", "status") else "w")
        
        self.tree.column("id", width=0, stretch=False) # Hide ID

        self.tree.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.tree.bind("<Double-1>", self.on_tree_select)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        q = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""

        with SessionLocal() as db:
            query = db.query(MonitoringService).order_by(MonitoringService.created_at.desc())
            services = query.all()
            
            active_count = 0
            total_rev = 0.0

            for s in services:
                if s.arrival_time is None:
                    active_count += 1
                if s.financial_status in ['Facturado y pagado', 'Pagado'] and s.total_cost:
                    total_rev += s.total_cost

                if q and q not in f"{s.unit} {s.client} {s.operator}".lower():
                    continue

                start_str = s.start_time.strftime("%d/%m %H:%M") if s.start_time else ""
                end_str = s.arrival_time.strftime("%d/%m %H:%M") if s.arrival_time else "En Ruta"
                cost_str = f"${s.total_cost:.2f}" if s.total_cost is not None else "—"
                mins_str = str(s.billed_minutes) if s.billed_minutes is not None else "—"

                self.tree.insert("", "end", values=(
                    s.id, s.unit, s.client, s.operator,
                    start_str, end_str, mins_str, cost_str, s.financial_status
                ))
            
            self.update_summary_cards(active_count, total_rev)

    def save_service(self):
        unit = self.entry_unit.get().strip()
        op = self.entry_operator.get().strip()
        client = self.entry_client.get().strip()
        orig = self.entry_origin.get().strip()
        dest = self.entry_dest.get().strip()
        rate_str = self.entry_rate.get().strip()

        if not all([unit, op, client, orig, dest, rate_str]):
            messagebox.showwarning("Faltan datos", "Por favor completa todos los campos para registrar la salida.")
            return

        try:
            rate = float(rate_str)
        except ValueError:
            messagebox.showerror("Error", "La tarifa debe ser numérica.")
            return

        with SessionLocal() as db:
            if self.current_editing_id:
                s = db.query(MonitoringService).filter(MonitoringService.id == self.current_editing_id).first()
                if s:
                    s.unit = unit
                    s.operator = op
                    s.client = client
                    s.origin = orig
                    s.destination = dest
                    s.hourly_rate = rate
                    db.commit()
                    messagebox.showinfo("Éxito", "Servicio actualizado correctamente.")
            else:
                s = MonitoringService(
                    id=str(uuid.uuid4()),
                    unit=unit, operator=op, client=client, origin=orig, destination=dest,
                    start_time=datetime.datetime.now(datetime.timezone.utc),
                    hourly_rate=rate,
                    financial_status="En proceso de facturación"
                )
                db.add(s)
                db.commit()
                messagebox.showinfo("Éxito", "Salida registrada. El monitoreo ha comenzado.")
                
        self.reset_form()
        self.load_data()

    def register_arrival(self):
        if not self.current_editing_id: return
        if messagebox.askyesno("Confirmar Llegada", "¿Estás seguro de registrar la llegada para este servicio?\nSe calculará el costo y los minutos automáticamente."):
            with SessionLocal() as db:
                s = db.query(MonitoringService).filter(MonitoringService.id == self.current_editing_id).first()
                if s and not s.arrival_time:
                    s.arrival_time = datetime.datetime.now(datetime.timezone.utc)
                    s.financial_status = "Facturado y pagado" 
                    db.commit()
                    messagebox.showinfo("Llegada Registrada", "El servicio ha finalizado y el costo se ha calculado en base a la tarifa por hora.")
            self.reset_form()
            self.load_data()

    def generate_ticket(self):
        if not self.current_editing_id: return
        with SessionLocal() as db:
            s = db.query(MonitoringService).filter(MonitoringService.id == self.current_editing_id).first()
            if not s or not s.arrival_time:
                messagebox.showwarning("Aviso", "No se puede generar ticket si el servicio aún está en ruta.")
                return
            
            output_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=f"Ticket_Monitoreo_{s.unit}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                title="Guardar Ticket PDF",
                filetypes=[("Archivos PDF", "*.pdf")]
            )
            if not output_path: return
            
            try:
                generate_monitoring_ticket_pdf(
                    output_path=output_path,
                    folio=s.id.split('-')[0].upper(),
                    client_name=s.client,
                    unit=s.unit,
                    origin=s.origin,
                    destination=s.destination,
                    start_time=s.start_time.strftime("%d/%m/%Y %H:%M"),
                    arrival_time=s.arrival_time.strftime("%d/%m/%Y %H:%M"),
                    billed_minutes=s.billed_minutes,
                    total_amount=s.total_cost
                )
                messagebox.showinfo("Éxito", f"Ticket generado en:\n{output_path}")
                try: os.startfile(output_path)
                except: pass
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al generar PDF:\n{str(e)}")

    def on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel: return
        s_id = self.tree.item(sel[0])['values'][0]
        
        with SessionLocal() as db:
            s = db.query(MonitoringService).filter(MonitoringService.id == s_id).first()
            if not s: return
            
            self.current_editing_id = s.id
            self.lbl_form_title.configure(text=f"Editando Servicio")
            self.btn_start.configure(text="💾 Guardar Cambios")
            
            self.entry_unit.delete(0, 'end'); self.entry_unit.insert(0, s.unit)
            self.entry_operator.delete(0, 'end'); self.entry_operator.insert(0, s.operator)
            self.entry_client.delete(0, 'end'); self.entry_client.insert(0, s.client)
            self.entry_origin.delete(0, 'end'); self.entry_origin.insert(0, s.origin)
            self.entry_dest.delete(0, 'end'); self.entry_dest.insert(0, s.destination)
            self.entry_rate.delete(0, 'end'); self.entry_rate.insert(0, str(s.hourly_rate))
            
            if not s.arrival_time:
                self.btn_arrive.configure(state="normal")
                self.btn_ticket.configure(state="disabled")
            else:
                self.btn_arrive.configure(state="disabled")
                self.btn_start.configure(state="disabled") 
                self.btn_ticket.configure(state="normal")

    def do_export(self):
        rows = []
        for item in self.tree.get_children():
            v = self.tree.item(item)['values']
            rows.append(v[1:]) # Exclude ID
            
        export_data_to_excel(
            headers=["Unidad", "Cliente", "Operador", "Salida", "Llegada", "Minutos", "Costo", "Estado"],
            rows=rows, default_name="Reporte_Monitoreo"
        )

    def reset_form(self):
        self.current_editing_id = None
        self.lbl_form_title.configure(text="Nuevo Servicio")
        self.btn_start.configure(text="🚀 Registrar Salida", state="normal")
        self.btn_arrive.configure(state="disabled")
        self.btn_ticket.configure(state="disabled")
        
        for e in [self.entry_unit, self.entry_operator, self.entry_client, 
                  self.entry_origin, self.entry_dest, self.entry_rate]:
            e.delete(0, 'end')
