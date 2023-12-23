import moonrakerpy as moonpy
import time


printer = moonpy.MoonrakerPrinter('http://192.168.1.59')


movement = {
    "x_neg": """G91
G1 x-50 F7800
G90""",
    "x_pos": """G91
G1 x50 F7800
G90""",
    "y_pos": """G91
G1 y50 F7800
G90""",
    "y_neg": """G91
G1 y-50 F7800
G90"""
}


def main():

    for _ in range(1000):
        printer.send_gcode(movement["x_pos"])
        printer.send_gcode(movement["x_neg"])
        printer.send_gcode(movement["y_pos"])
        printer.send_gcode(movement["y_neg"])


if __name__ == "__main__":
    main()
