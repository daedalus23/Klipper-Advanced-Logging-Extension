import pandas as pd
import re
import os

from configreader import Configuration
from klipperjob import JobBedMesh


configPath = r"./bin/jobparser.ini"
configuration = Configuration(configPath)


class KlipperLogParser(JobBedMesh):

    def __init__(self, log_file_path):
        super(KlipperLogParser, self).__init__()
        self.log_file_path = log_file_path

    def extract_bed_mesh_points(self, job_content, x_count):
        """Extract bed mesh points from job content."""
        points_start_str = "save_config: set [bed_mesh default] points ="
        start_index = job_content.find(points_start_str)

        # If the starting string is not found, return an empty list
        if start_index == -1:
            self.bedMesh["preformed"] = False

        # Start from the line after the identified string
        lines = job_content[start_index:].split("\n")[
                1:x_count + 1]  # +1 because the first line is the identified string itself

        # Extract points from each line
        points = []
        for line in lines:
            points_row = list(map(float, line.strip().split(", ")))
            points.append(points_row)
        self.bedMesh["points"] = points

    def parse_stats_line_v3(self, stats_line):
        """Extract details from a single 'Stats' line."""
        patterns = configuration.content["stats_regex"]["patterns"]
        substrs = configuration.content["stats_regex"]["substrs"]
        parsed_details = {}
        for detail, pattern in patterns.items():
            match = re.search(pattern, stats_line)
            if match:
                # Determine if the value is a float or integer based on the key
                if any(sub_str in detail for sub_str in substrs):
                    parsed_details[detail] = float(match.group(1))
                else:
                    parsed_details[detail] = int(match.group(1))
        return parsed_details

    def extract_job_details_improved(self, job_content):
        """Extract key details from a job's content using the improved points extraction."""
        patterns = {
            'x_count': r"x_count = (\d+)",
            'y_count': r"y_count = (\d+)",
            'min_x': r"min_x = ([\d.]+)",
            'max_x': r"max_x = ([\d.]+)",
            'min_y': r"min_y = ([\d.]+)",
            'max_y': r"max_y = ([\d.]+)"
        }
        details = {}
        for detail, pattern in patterns.items():
            detail_match = re.search(pattern, job_content)
            if detail_match:
                # Determine if the value is a float or integer
                if any(sub_str in detail for sub_str in ['min_x', 'max_x', 'min_y', 'max_y']):
                    details[detail] = float(detail_match.group(1))
                else:
                    details[detail] = int(detail_match.group(1))

        # Extract bed mesh points using the improved function
        x_count = details.get('x_count', 0)
        y_count = details.get('y_count', 0)
        details['points'] = extract_bed_mesh_points(job_content, x_count, y_count)

        return details

    def parse_detailed_log_to_dataframe_v5(self):
        with open(log_file_path, "r") as file:
            content = file.read()

        job_start_marker = "Starting SD card print (position"
        job_end_marker = "Exiting SD card print (position"

        jobs = []
        job_parts = content.split(job_start_marker)
        for job in job_parts[1:]:
            job_content = job.split(job_end_marker)[0]
            jobs.append(job_start_marker + job_content)

        all_job_details = []
        for job in jobs:
            job_details = {}
            if 'Mesh Bed Leveling Complete' in job:
                job_details = extract_job_details_improved(job)

                stats_pattern = r"Stats (\d+\.\d+):"
                stats_matches = re.findall(stats_pattern, job)
                if stats_matches:
                    job_details['Job ID'] = stats_matches[0]
                    stats_details = []
                    for stats_match in stats_matches:
                        line_start = job.find(f"Stats {stats_match}:")
                        line_end = job.find("\n", line_start)
                        stats_line = job[line_start:line_end]
                        stats_details.append(parse_stats_line_v3(stats_line))
                    job_details['Stats Data'] = pd.DataFrame(stats_details)
            all_job_details.append(job_details)

        df = pd.DataFrame(all_job_details)
        return df

    def export_data_to_csv(self, bed_mesh_output, stats_data_output):
        """
         Parses the log file, extracts relevant data, and exports to two separate CSV files.

         Parameters:
         - log_file_path: Path to the log file to be parsed.
         - bed_mesh_output: Path where the Bed Mesh Leveling Details CSV will be saved.
         - stats_data_output: Path where the Stats Data CSV will be saved.
         """
        # Parse the log file
        detailed_df = parse_detailed_log_to_dataframe_v5(log_file_path)

        # Export Bed Mesh Leveling Details
        expected_columns = ['x_count', 'y_count', 'min_x', 'max_x', 'min_y', 'max_y', 'points']
        columns_to_extract = [col for col in expected_columns if col in detailed_df.columns]
        bed_mesh_df = detailed_df[columns_to_extract].copy()
        bed_mesh_df.to_csv(bed_mesh_output, index=False)

        # Export Stats Data
        all_stats_data = pd.DataFrame()
        for idx, row in detailed_df.iterrows():
            if isinstance(row['Stats Data'], pd.DataFrame):
                stats_data = row['Stats Data'].copy()
                stats_data['Job ID'] = row['Job ID']
                all_stats_data = pd.concat([all_stats_data, stats_data], ignore_index=True)
        all_stats_data.to_csv(stats_data_output, index=False)

    def export_jobs_to_separate_csvs(self, output_directory):
        """
        Parses the log file, extracts relevant data, and exports each job's details to separate CSV files.

        Parameters:
        - log_file_path: Path to the log file to be parsed.
        - output_directory: Directory where the CSV files will be saved.
        """
        # Ensure output directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Parse the log file
        detailed_df = parse_detailed_log_to_dataframe_v5(log_file_path)

        # Export each job's details to separate CSV files
        for idx, row in detailed_df.iterrows():
            # Exporting Bed Mesh Leveling Details
            if not pd.isna(row['x_count']):
                bed_mesh_filename = os.path.join(output_directory, f"BedMesh_Job_{row['Job ID']}.csv")
                bed_mesh_data = {key: row[key] for key in
                                 ['x_count', 'y_count', 'min_x', 'max_x', 'min_y', 'max_y', 'points']}
                bed_mesh_df = pd.DataFrame([bed_mesh_data])
                bed_mesh_df.to_csv(bed_mesh_filename, index=False)

            # Exporting Stats Data
            if isinstance(row['Stats Data'], pd.DataFrame):
                stats_filename = os.path.join(output_directory, f"Job_{row['Job ID']}.csv")
                row['Stats Data'].to_csv(stats_filename, index=False)


parser = KlipperLogParser("klippy.log")
detailed_df_v5 = parser.parse_detailed_log_to_dataframe_v5()

bed_mesh_output_path = "bed_mesh_details.csv"
stats_data_output_path = "stats_data.csv"
parser.export_data_to_csv(bed_mesh_output_path, stats_data_output_path)

output_dir = "jobs_export"
parser.export_jobs_to_separate_csvs(output_dir)
