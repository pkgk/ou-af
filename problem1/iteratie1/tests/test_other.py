import pytest
from extrataak.src.diagnosecontroller import DiagnosisController

### reading influence diagram file should raise exception when file not found"""
def test_influencediagram_file_exception():
    with pytest.raises(Exception):
        dc = DiagnosisController()
        dc.load_influencediagram("a_nonexisting_filename")


#@TODO not a valid label as evidence