import numpy as np


class JobBedMesh:
    bedMesh = {
        "preformed": bool,
        "x_count": np.NaN,
        "y_count": np.NaN,
        "min_x": np.NaN,
        "max_x": np.NaN,
        "min_y": np.NaN,
        "max_y": np.NaN,
        "points": np.NaN
    }
    jobID = str

    def __init__(self):
        pass
