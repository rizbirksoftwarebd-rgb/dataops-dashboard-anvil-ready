import anvil.server
import pandas as pd
from io import BytesIO
from datetime import datetime
import anvil
from anvil.tables import app_tables
import pdfplumber

class FileProcessor:
    def __init__(self):
        pass

    def _to_blob(self, buffer, name=None):
        buffer.seek(0)
        fname = name or f'processed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return anvil.BlobMedia('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', buffer.read(), fname)

    def get_excel_columns(self, file1, file2):
        df1 = pd.read_excel(BytesIO(file1.get_bytes()), dtype=str)
        df2 = pd.read_excel(BytesIO(file2.get_bytes()), dtype=str)
        return list(df1.columns), list(df2.columns)

    def process_excel(self, file1, file2, col1, col2):
        df1 = pd.read_excel(BytesIO(file1.get_bytes()), dtype=str)
        df2 = pd.read_excel(BytesIO(file2.get_bytes()), dtype=str)
        df1[col1] = df1[col1].fillna('').astype(str).str.strip()
        df2[col2] = df2[col2].fillna('').astype(str).str.strip()
        matched = df1[df1[col1].isin(df2[col2])].copy()
        unmatched1 = df1[~df1[col1].isin(df2[col2])].copy()
        unmatched2 = df2[~df2[col2].isin(df1[col1])].copy()
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            matched.to_excel(writer, sheet_name='Matched', index=False)
            unmatched1.to_excel(writer, sheet_name='Unmatched_RMS', index=False)
            unmatched2.to_excel(writer, sheet_name='Unmatched_Bank', index=False)
        blob = self._to_blob(out, name='excel_matcher_result.xlsx')
        app_tables.temp_files.add_row(name=blob.name, file=blob, created=datetime.now())
        return blob

    def get_single_excel_columns(self, file):
        df = pd.read_excel(BytesIO(file.get_bytes()), dtype=str)
        return list(df.columns)

    def shuffle_excel(self, file, shuffle_rows=False, shuffle_cols=False):
        df = pd.read_excel(BytesIO(file.get_bytes()), dtype=str)
        import numpy as np
        if shuffle_cols:
            cols = list(df.columns)
            np.random.shuffle(cols)
            df = df[cols]
        if shuffle_rows:
            df = df.sample(frac=1).reset_index(drop=True)
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Shuffled', index=False)
        blob = self._to_blob(out, name='shuffled_result.xlsx')
        app_tables.temp_files.add_row(name=blob.name, file=blob, created=datetime.now())
        return blob

    def get_csv_columns(self, file1, file2):
        df1 = pd.read_csv(BytesIO(file1.get_bytes()), dtype=str)
        df2 = pd.read_csv(BytesIO(file2.get_bytes()), dtype=str)
        return list(df1.columns), list(df2.columns)

    def process_csv(self, file1, file2, col1, col2):
        df1 = pd.read_csv(BytesIO(file1.get_bytes()), dtype=str)
        df2 = pd.read_csv(BytesIO(file2.get_bytes()), dtype=str)
        df1[col1] = df1[col1].fillna('').astype(str).str.strip()
        df2[col2] = df2[col2].fillna('').astype(str).str.strip()
        matched = df1[df1[col1].isin(df2[col2])].copy()
        unmatched1 = df1[~df1[col1].isin(df2[col2])].copy()
        unmatched2 = df2[~df2[col2].isin(df1[col1])].copy()
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            matched.to_excel(writer, sheet_name='Matched', index=False)
            unmatched1.to_excel(writer, sheet_name='Unmatched_File1', index=False)
            unmatched2.to_excel(writer, sheet_name='Unmatched_File2', index=False)
        blob = self._to_blob(out, name='csv_compare_result.xlsx')
        app_tables.temp_files.add_row(name=blob.name, file=blob, created=datetime.now())
        return blob

    def analyze_holding_tax(self, file):
        df = pd.read_excel(BytesIO(file.get_bytes()), dtype=str)
        findings = {}
        cols = list(df.columns)
        findings['columns_present'] = cols
        required = ['holding_no', 'owner_name', 'tax_due', 'payment_status']
        missing = [c for c in required if c not in cols]
        findings['missing_columns'] = missing
        summary = {}
        if 'tax_due' in cols:
            df['tax_due'] = pd.to_numeric(df['tax_due'], errors='coerce').fillna(0)
            summary['total_tax_due'] = float(df['tax_due'].sum())
            summary['average_tax_due'] = float(df['tax_due'].mean())
        else:
            summary['total_tax_due'] = None
            summary['average_tax_due'] = None
        if 'payment_status' in cols:
            pending = df[df['payment_status'].str.lower().str.contains('pending', na=False)]
            summary['pending_count'] = int(len(pending))
        else:
            summary['pending_count'] = None
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            pd.DataFrame([findings]).to_excel(writer, sheet_name='Findings', index=False)
            pd.DataFrame([summary]).to_excel(writer, sheet_name='Summary', index=False)
            df.head(100).to_excel(writer, sheet_name='Sample_Data', index=False)
        blob = self._to_blob(out, name='holding_tax_report.xlsx')
        app_tables.temp_files.add_row(name=blob.name, file=blob, created=datetime.now())
        return blob

    def pdf_to_excel(self, file):
        out = BytesIO()
        try:
            with pdfplumber.open(BytesIO(file.get_bytes())) as pdf:
                writer = pd.ExcelWriter(out, engine='openpyxl')
                sheet_no = 1
                for page in pdf.pages:
                    try:
                        tables = page.extract_tables()
                    except Exception:
                        tables = None
                    if tables:
                        for t in tables:
                            df = pd.DataFrame(t[1:], columns=t[0])
                            df.to_excel(writer, sheet_name=f'Page_{page.page_number}_Tbl_{sheet_no}', index=False)
                            sheet_no += 1
                writer.close()
            out.seek(0)
            blob = self._to_blob(out, name='pdf_extracted.xlsx')
            app_tables.temp_files.add_row(name=blob.name, file=blob, created=datetime.now())
            return blob
        except Exception as e:
            raise e

_processor = FileProcessor()

@anvil.server.callable
def get_excel_columns(file1, file2):
    return _processor.get_excel_columns(file1, file2)

@anvil.server.callable
def process_excel(file1, file2, col1, col2):
    return _processor.process_excel(file1, file2, col1, col2)

@anvil.server.callable
def get_single_excel_columns(file):
    return _processor.get_single_excel_columns(file)

@anvil.server.callable
def shuffle_excel(file, shuffle_rows=False, shuffle_cols=False):
    return _processor.shuffle_excel(file, shuffle_rows, shuffle_cols)

@anvil.server.callable
def get_csv_columns(file1, file2):
    return _processor.get_csv_columns(file1, file2)

@anvil.server.callable
def process_csv(file1, file2, col1, col2):
    return _processor.process_csv(file1, file2, col1, col2)

@anvil.server.callable
def analyze_holding_tax(file):
    return _processor.analyze_holding_tax(file)

@anvil.server.callable
def pdf_to_excel(file):
    return _processor.pdf_to_excel(file)
