import os
import json
from influxdb import InfluxDBClient
import pandas as pd

def get_files_by_prefix(directory, prefix):
    matching_files = []
    for file_name in os.listdir(directory):
        if file_name.startswith(prefix) and file_name.endswith(('.json', '.csv')):
            matching_files.append(os.path.join(directory, file_name))
    return matching_files

def parse_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except json.JSONDecodeError:
        raise ValueError(f"The file {file_path} is not a valid JSON.")

def modify_json_data(json_data, measurement_name):
    if not isinstance(json_data, list):
        raise ValueError("Expected a list of dictionaries as JSON data.")

    for record in json_data:
        if 'dateTime' in record:
            record['time'] = record.pop('dateTime')  # Rename 'dateTime' to 'time'
        record['measurement'] = measurement_name  # Add 'measurement' field
        if 'value' in record:
            record['fields'] = {'value': float(record.pop('value'))}  # Move 'value' into 'fields' array

    return json_data

def read_config(config_file):
    """
    Reads a configuration file and returns the configuration as a dictionary.

    :param config_file: Path to the configuration file (JSON format).
    :return: A dictionary containing the configuration.
    :raises: FileNotFoundError if the file does not exist.
             ValueError if the file is not a valid JSON.
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
        required_keys = ['devicename', 'dbname', 'dbhost', 'dbport', 'dbuser', 'dbpassword']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"The configuration file {config_file} does not exist.")
    except json.JSONDecodeError:
        raise ValueError(f"The configuration file {config_file} is not a valid JSON.")

# Example usage:
# config = read_config("config.json")
# print(config)

# Load configuration
config = read_config("config.json")

# Initialize InfluxDB client using the configuration
client = InfluxDBClient(
    host=config['dbhost'],
    port=config['dbport'],
    username=config['dbuser'],
    password=config['dbpassword']
)
client.switch_database(config['dbname'])

device_name = config['devicename']

## Sleep data, from JSON
for prefix in ["sleep"]:
    files=get_files_by_prefix("Takeout/Fitbit/Global Export Data",prefix)
    for file in files:
        print("Importing "+prefix+" from "+file)
        collected_records = []
        if file.endswith('.json'):
            try:
                data = parse_json_file(file)
                for record in data:
                    try:
                        minutesLight= record['levels']['summary']['light']['minutes']
                        minutesREM = record['levels']['summary']['rem']['minutes']
                        minutesDeep = record['levels']['summary']['deep']['minutes']
                    except:
                        minutesLight= record['levels']['summary']['asleep']['minutes']
                        minutesREM = record['levels']['summary']['restless']['minutes']
                        minutesDeep = 0

                    collected_records.append({
                            "measurement":  "Sleep Summary",
                            "time": record["startTime"],
                            "tags": {
                                "Device": device_name
                                #"isMainSleep": record["isMainSleep"],
                            },
                            "fields": {
                                'efficiency': record["efficiency"],
                                'minutesAfterWakeup': record['minutesAfterWakeup'],
                                'minutesAsleep': record['minutesAsleep'],
                                'minutesToFallAsleep': record['minutesToFallAsleep'],
                                'minutesInBed': record['timeInBed'],
                                'minutesAwake': record['minutesAwake'],
                                'minutesLight': minutesLight,
                                'minutesREM': minutesREM,
                                'minutesDeep': minutesDeep
                            }
                        })
                    
                    sleep_level_mapping = {'wake': 3, 'rem': 2, 'light': 1, 'deep': 0, 'asleep': 1, 'restless': 2, 'awake': 3, 'unknown': 4}
                    for sleep_stage in record['levels']['data']:
                        collected_records.append({
                                "measurement":  "Sleep Levels",
                                "time": sleep_stage["dateTime"],
                                "tags": {
                                    "Device": device_name
                                    #"isMainSleep": record["isMainSleep"],
                                },
                                "fields": {
                                    'level': sleep_level_mapping[sleep_stage["level"]],
                                    'duration_seconds': sleep_stage["seconds"]
                                }
                            })
                    collected_records.append({
                                "measurement":  "Sleep Levels",
                                "time": record["endTime"],
                                "tags": {
                                    "Device": device_name
                                    #"isMainSleep": record["isMainSleep"],
                                },
                                "fields": {
                                    'level': sleep_level_mapping['wake'],
                                    'duration_seconds': None
                                }
                            })
                client.write_points(collected_records)
            except Exception as e:
                print(f"Error parsing {file}: {e}")
        else:
            print(f"{file} is not a JSON file.") 


#Various Activity Data, from CSV, heart_rate is damn slow
for prefix in ["steps","active_minutes","calories","heart_rate","altitude","demographic_vo2max","floors","oxygen_saturation","daily_resting_heart_rate"]:
#for prefix in ["daily_resting_heart_rate"]:
    files=get_files_by_prefix("Takeout/Fitbit/Physical Activity_GoogleData",prefix)
    for file in files:
        print("Importing "+prefix+" from "+file)
        points=[]
        data = pd.read_csv(file,index_col=False)
        for _, row in data.iterrows():
            point = {
                "measurement": prefix,
                "tags": {'Device': device_name},
                "time": row.get("timestamp", None),
                "fields": {col: row[col] for col in data.columns if col != "timestamp"} 
            }
            points.append(point)
        client.write_points(points)

""" for prefix in ["sleep_score"]:
    files=get_files_by_prefix("Takeout/Fitbit/Sleep Score",prefix)
    for file in files:
        print("Importing "+prefix+" from "+file)
        points=[]
        data = pd.read_csv(file,index_col=False)        
        for _, row in data.iterrows():
            point = {
                "measurement": prefix,
                "tags": {'Device': device_name},
                "time": row.get("timestamp", None),
                "fields": {col: row[col] for col in data.columns if col != "timestamp"} 
            }
            points.append(point)
        client.write_points(points) """

for prefix in ["Daily Heart Rate Variability Summary","Daily Respiratory Rate Summary"]:
    files=get_files_by_prefix("Takeout/Fitbit/Heart Rate Variability",prefix)
    for file in files:
        print("Importing "+prefix+" from "+file)
        points=[]
        data = pd.read_csv(file,index_col=False)        
        for _, row in data.iterrows():
            point = {
                "measurement": prefix,
                "tags": {'Device': device_name},
                "time": row.get("timestamp", None),
                "fields": {col: row[col] for col in data.columns if col != "timestamp"} 
            }
            points.append(point)
        client.write_points(points)

for prefix in ["activity_level"]:
    files=get_files_by_prefix("Takeout/Fitbit/Physical Activity_GoogleData",prefix)
    for file in files:
        print("Importing "+prefix+" from "+file)
        points=[]
        data = pd.read_csv(file,index_col=False)
        for _, row in data.iterrows():
            point = {
                "measurement": prefix,
                "tags": {'Device': device_name,'level':row['level']},
                "time": row.get("timestamp", None),
                "fields": {'value':1} 
            }
            points.append(point)
        client.write_points(points)

