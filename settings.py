import json
import os

def get_setting(setting: str) -> str:
    """
    Get the setting from the settings.json file.
    Args:
        setting: The settings string looks like: "DEVICE/LOCATION_ID"
                 with the equivalent jason key being [DEVICE"]["LOCATION_ID"]

    Returns: The value of the json key
    Examples: get_setting("DEVICE/LOCATION_ID")

    See Also: settings.json
    References: settings_example.json
    """
    # Construct the full path to settings.json relative to this script's location
    dir_path = os.path.dirname(os.path.realpath(__file__))
    settings_file_path = os.path.join(dir_path, 'settings.json')

    # Open and load the settings.json file
    with open(settings_file_path, 'r') as f:
        settings = json.load(f)

    # Parse the setting key to access nested dictionary values
    keys = setting.split('/')
    value = settings
    for key in keys:
        value = value[key]

    return value
