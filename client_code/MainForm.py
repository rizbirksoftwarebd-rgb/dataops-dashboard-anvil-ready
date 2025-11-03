from anvil import *
import anvil.server
from .ExcelMatcherForm import ExcelMatcherForm
from .ColumnShufflerForm import ColumnShufflerForm
from .CompareCSVForm import CompareCSVForm
from .HoldingTaxForm import HoldingTaxForm
from .PDFtoExcelForm import PDFtoExcelForm

from ._anvil_designer.MainFormTemplate import MainFormTemplate

class MainForm(MainFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        # show login at start
        open_form('LoginForm')

    def link_excel_matcher_click(self, **event_args):
        self.content_area.clear()
        self.content_area.add_component(ExcelMatcherForm())

    def link_column_shuffler_click(self, **event_args):
        self.content_area.clear()
        self.content_area.add_component(ColumnShufflerForm())

    def link_compare_csv_click(self, **event_args):
        self.content_area.clear()
        self.content_area.add_component(CompareCSVForm())

    def link_holding_tax_click(self, **event_args):
        self.content_area.clear()
        self.content_area.add_component(HoldingTaxForm())

    def link_pdf_to_excel_click(self, **event_args):
        self.content_area.clear()
        self.content_area.add_component(PDFtoExcelForm())

    def link_logout_click(self, **event_args):
        open_form('LoginForm')
