from anvil import *
import anvil.server
from ._anvil_designer.PDFtoExcelFormTemplate import PDFtoExcelFormTemplate

class PDFtoExcelForm(PDFtoExcelFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self._file = None
        self._last_blob = None

    def file_pdf_change(self, file, **event_args):
        self._file = file
        try:
            self.btn_convert.enabled = True
        except Exception:
            pass

    def btn_convert_click(self, **event_args):
        blob = anvil.server.call('pdf_to_excel', self._file)
        if blob:
            self._last_blob = blob
            try:
                self.btn_download.enabled = True
            except Exception:
                pass
            alert('PDF converted. Click Download to fetch Excel.')
        else:
            alert('Conversion failed.')

    def btn_download_click(self, **event_args):
        if self._last_blob:
            download(self._last_blob, self._last_blob.name)
        else:
            alert('No file to download.')
