from backend.python.enums import Mobility
from backend.python.point.Transporter import Transporter
from backend.python.transport.Tuktuk import Tuktuk


class TuktukDriver(Transporter):

    def __init__(self):
        super().__init__()
        self.main_trans = Tuktuk(Mobility.RANDOM.value)
        self.max_latches = 3
