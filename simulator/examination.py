from simulator.scanlist import Scanlist

from pydicom.uid import generate_uid

import datetime


class Examination:
    def __init__(self, name, model):
        self.name = name
        self.model = model
        self.scanlist = Scanlist()
        self.study_instance_uid = generate_uid()
        self.study_date = datetime.datetime.now().strftime("%Y%m%d")
        self.study_time = datetime.datetime.now().strftime("%H%M%S.%f")
