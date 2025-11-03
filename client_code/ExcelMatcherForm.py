from anvil import *
import anvil.server
from ._anvil_designer.ExcelMatcherFormTemplate import ExcelMatcherFormTemplate

class ExcelMatcherForm(ExcelMatcherFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self._file1 = None
        self._file2 = None
        self._last_blob = None
        # developer info
        try:
            self.label_dev.text = "Developer: Rizbi Islam — QA Engineer — Bangladesh"
        except Exception:
            pass

    def file_rms_change(self, file, **event_args):
        self._file1 = file
        self._maybe_enable_preview()

    def file_bank_change(self, file, **event_args):
        self._file2 = file
        self._maybe_enable_preview()

    def _maybe_enable_preview(self):
        if getattr(self, '_file1', None) and getattr(self, '_file2', None):
            try:
                self.btn_preview.enabled = True
            except Exception:
                pass

    def btn_preview_click(self, **event_args):
        cols1, cols2 = anvil.server.call('get_excel_columns', self._file1, self._file2)
        self.drop_rms.items = cols1
        self.drop_bank.items = cols2
        try:
            self.btn_process.enabled = True
        except Exception:
            pass
        alert('Columns loaded. Select columns and click Process.')

    def btn_process_click(self, **event_args):
        col1 = self.drop_rms.selected_value
        col2 = self.drop_bank.selected_value
        if not col1 or not col2:
            alert('Select both columns.')
            return
        blob = anvil.server.call('process_excel', self._file1, self._file2, col1, col2)
        if blob:
            self._last_blob = blob
            try:
                self.btn_download.enabled = True
            except Exception:
                pass
            alert('Processing finished — use Download to retrieve the file.')
        else:
            alert('Processing failed.')

    def btn_download_click(self, **event_args):
        if self._last_blob:
            download(self._last_blob, self._last_blob.name)
        else:
            alert('No file to download.')
