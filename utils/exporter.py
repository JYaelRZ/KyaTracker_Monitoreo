import pandas as pd
import os
from tkinter import filedialog, messagebox

def export_data_to_excel_file(headers, rows, filepath):
    """Export to a specific file path (for web use)"""
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel(filepath, index=False)
    return filepath

def export_data_to_excel(headers, rows, default_name="Reporte"):
    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        initialfile=f"{default_name}.xlsx",
        title="Guardar Excel",
        filetypes=[("Archivos Excel", "*.xlsx")]
    )
    if not filepath:
        return None
    try:
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Éxito", f"Datos exportados a\n{filepath}")
        return filepath
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar:\n{e}")
        return None
