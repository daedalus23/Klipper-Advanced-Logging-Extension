import moonrakerpy as moonpy

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


def move_test(cycles=1001):
    for i in range(cycles):
        printer.send_gcode(movement["x_pos"])
        printer.send_gcode(movement["x_neg"])
        printer.send_gcode(movement["y_pos"])
        printer.send_gcode(movement["y_neg"])
        print(f"Cycle {i+1} of {cycles}")

def home_all():
    printer.send_gcode("G28")
