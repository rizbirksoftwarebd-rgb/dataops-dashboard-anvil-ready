from anvil import *
import anvil.server
from ._anvil_designer.ColumnShufflerFormTemplate import ColumnShufflerFormTemplate

class ColumnShufflerForm(ColumnShufflerFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self._file = None
        self._last_blob = None

    def file_upload_change(self, file, **event_args):
        self._file = file
        try:
            self.btn_preview.enabled = True
        except Exception:
            pass

    def btn_preview_click(self, **event_args):
        cols = anvil.server.call('get_single_excel_columns', self._file)
        self.drop_columns.items = cols
        alert('Columns loaded. Choose options and press Process.')

    def btn_process_click(self, **event_args):
        shuffle_rows = getattr(self, 'cb_shuffle_rows', None) and self.cb_shuffle_rows.checked
        shuffle_cols = getattr(self, 'cb_shuffle_columns', None) and self.cb_shuffle_columns.checked
        if not (shuffle_rows or shuffle_cols):
            alert('Select at least one option.')
            return
        blob = anvil.server.call('shuffle_excel', self._file, shuffle_rows, shuffle_cols)
        if blob:
            self._last_blob = blob
            try:
                self.btn_download.enabled = True
            except Exception:
                pass
            alert('Shuffled. Click Download.')
        else:
            alert('Failed to shuffle.')

    def btn_download_click(self, **event_args):
        if self._last_blob:
            download(self._last_blob, self._last_blob.name)
        else:
            alert('No file to download.')
