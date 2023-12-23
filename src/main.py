import moonrakerpy as moonpy
import pandas as pd
import datetime
import time

printer = moonpy.MoonrakerPrinter('http://192.168.1.59')

movements = {
    "x_neg": "G91\nG1 x-10 F7800\nG90",
    "x_pos": "G91\nG1 x10 F7800\nG90",
    "y_pos": "G91\nG1 y10 F7800\nG90",
    "y_neg": "G91\nG1 y-10 F7800\nG90",
    "z_pos": "G91\nG1 z10 F600\nG90",
    "z_neg": "G91\nG1 z-10 F600\nG90"

}

commands = {
    "home_all": "G28"
}

def collect_motion_data():
    """ Collects and returns the current motion data from the printer """
    data = printer.query_status("motion_report")
    timestamp = datetime.datetime.now().isoformat()  # ISO 8601 format timestamp
    return {
        'timestamp': timestamp,
        'X': data.get('live_position')[0],
        'Y': data.get('live_position')[1],
        'Z': data.get('live_position')[2],
        'Blank': data.get('live_position')[-1],
        'live_velocity': data.get('live_velocity', ''),
        'live_extruder_velocity': data.get('live_extruder_velocity', ''),
        'steppers': ','.join(data.get('steppers', [])),
        'trapq': ','.join(data.get('trapq', []))
    }

def main():
    accumulator = []
    # printer.send_gcode(commands["home_all"])
    # time.sleep(3)

    for move in movements:
        # Collect data before movement
        before_move_data = collect_motion_data()
        accumulator.append(before_move_data)

        # Execute movement
        printer.send_gcode(movements[move])
        time.sleep(3)  # Wait for movement to complete

        # Collect data after movement
        after_move_data = collect_motion_data()
        accumulator.append(after_move_data)

    # Convert accumulated data to DataFrame and save to CSV
    motion_data_df = pd.DataFrame(accumulator)
    motion_data_df.to_csv('output.csv', index=False)

if __name__ == "__main__":
    main()

