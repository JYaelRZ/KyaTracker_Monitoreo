import pandas as pd
import os

def export_data_to_excel_file(headers, rows, filepath):
    """Export to a specific file path (for web use)"""
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel(filepath, index=False)
    return filepath
