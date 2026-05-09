import pandas as pd
import os

def export_data_to_excel_file(headers, rows, filepath):
    """Export to a specific file path (for web use)"""
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel(filepath, index=False)
    return filepath

def export_data_to_excel(headers, rows, default_name="Reporte"):
    try:
        from tkinter import filedialog, messagebox
    except ImportError:
        return None
        
    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        initialfile=f"{default_name}.xlsx",
        title="Guardar Excel",
        filetypes=[("Archivos Excel", "*.xlsx")]
    )
    if not filepath:
        return None
    try:
        from tkinter import messagebox
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Éxito", f"Datos exportados a\n{filepath}")
        return filepath
    except Exception as e:
        try:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")
        except:
            pass
        return None
