from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class Canvas(FigureCanvasQTAgg):
    def __init__(self) -> None:
        fig = Figure(figsize=(10, 10), dpi=100)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
