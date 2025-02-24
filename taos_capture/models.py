import numpy as np
from django.db import models
from .shared_data import FLC_NUM


# Create your models here.

class PLCConnectionStatus:
    connected = np.zeros(FLC_NUM)


plc_connection_status = PLCConnectionStatus()
