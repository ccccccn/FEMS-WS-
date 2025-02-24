import numpy as np
from django.db import models


# Create your models here.
class PLCConnectStatus():
    plc_connected = np.zeros(3)


PLCConnectStatu = PLCConnectStatus()
