from anvil import *
import anvil.server
from ._anvil_designer.HoldingTaxFormTemplate import HoldingTaxFormTemplate

class HoldingTaxForm(HoldingTaxFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self._file = None
        self._last_blob = None

    def file_upload_change(self, file, **event_args):
        self._file = file
        try:
            self.btn_analyze.enabled = True
        except Exception:
            pass

    def btn_analyze_click(self, **event_args):
        blob = anvil.server.call('analyze_holding_tax', self._file)
        if blob:
            self._last_blob = blob
            try:
                self.btn_download.enabled = True
            except Exception:
                pass
            alert('Analysis complete. Click Download.')
        else:
            alert('Analysis failed.')

    def btn_download_click(self, **event_args):
        if self._last_blob:
            download(self._last_blob, self._last_blob.name)
        else:
            alert('No report available.')
