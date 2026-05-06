import pandas as pd
import os
from tkinter import filedialog, messagebox

def export_data_to_excel(headers, rows, default_name="Reporte_Monitoreo"):
    if not rows:
        messagebox.showwarning("Sin datos", "No hay datos para exportar.")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        initialfile=default_name,
        title="Exportar a Excel",
        filetypes=[("Archivos Excel", "*.xlsx")]
    )
    
    if not filepath:
        return

    try:
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Exportación Exitosa", f"Datos exportados correctamente en:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al exportar:\n{e}")

def export_data_to_excel_file(headers, rows, filepath):
    """Export to a specific file path (for web use)"""
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel(filepath, index=False)
    return filepath
