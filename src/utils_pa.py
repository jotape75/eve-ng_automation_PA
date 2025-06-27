"""
Palo Alto Firewall Automation - Utility Functions.

Provides utility functions for PA firewall automation including:
- Configuration file loading and validation
- XML template management  
- Terminal color formatting
- Project banner display

Functions:
    file_path(): Load all configuration files and XML templates
    color_text(): Define terminal color codes
    banner(): Display project information banner
"""

import json
import pandas as pd # Data manipulation library
import pyfiglet # ASCII art library
from exceptions_pa import FileNotFoundError, InvalidConfigurationError

def file_path():
    """
    Load configuration files and XML templates for PA automation.
    
    Reads automation_urls_pa.json to get file paths, then loads all 
    required credential files and XML templates for firewall configuration.

    Returns:
        tuple: Contains credentials and all XML templates (9 elements):
            - pa_credentials (list): Device credentials  
            - pa_ha_config_tmp (str): HA configuration XML
            - pa_ha_int_tmp (str): HA interface XML
            - pa_interface_tmp (str): Interface configuration XML
            - pa_zones_tmp (str): Security zones XML
            - pa_route_settings_tmp (str): Router settings XML
            - pa_static_routes_tmp (str): Static routes XML
            - pa_security_policy_tmp (str): Security policies XML
            - pa_source_nat_tmp (str): NAT rules XML

    Raises:
        FileNotFoundError: When configuration files are missing
        InvalidConfigurationError: When JSON files are malformed
    """
    
    try:
    # Open the configuration file
        with open('/home/user/pystudies/myenv/pythonbasic/projects/eve-ng_automation_PA/data/automation_urls_pa.json', 'r') as config_file:
            files_path = json.load(config_file)
        # PA creds
            dev_creds_pa_file = files_path["urls"]['pa_creds_file']
            pa_ha_config_template = files_path["urls"]['pa_ha_config_template']
            pa_ha_int_template = files_path["urls"]['pa_ha_int_template']
            pa_interface_template = files_path["urls"]['pa_interface_template']
            pa_zones_template = files_path["urls"]['pa_zone_template']
            pa_virtual_router_template = files_path["urls"]['pa_virtual_router_template']
            pa_static_routes_template = files_path["urls"]['pa_static_routes_template']
            pa_security_policy_template = files_path["urls"]['pa_security_policy_template']
            pa_source_nat_template = files_path["urls"]['pa_source_nat_template']
    except FileNotFoundError:
        # logger.error("The configuration file 'automation_urls.json' was not found.")
        raise FileNotFoundError("The configuration file 'automation_urls.json' was not found.")
        
    except json.JSONDecodeError:
        # logger.error("The configuration file 'automation_urls.json' is invalid or malformed.")
        raise InvalidConfigurationError("The configuration file 'automation_urls.json' is invalid or malformed.")
    try:
        with open(dev_creds_pa_file, 'r') as f0, \
             open(pa_ha_config_template, 'r') as f1, \
             open(pa_ha_int_template, 'r') as f2, \
             open(pa_interface_template, 'r') as f3, \
             open(pa_zones_template, 'r') as f4, \
             open(pa_virtual_router_template, 'r') as f5, \
             open(pa_static_routes_template, 'r') as f6,\
             open(pa_security_policy_template, 'r') as f7, \
             open(pa_source_nat_template, 'r') as f8:
                 
                 

            pa_credentials = json.load(f0)
            pa_ha_config_tmp = f1.read()
            pa_ha_int_tmp = f2.read()
            pa_interface_tmp = f3.read()
            pa_zones_tmp = f4.read()
            pa_route_settings_tmp = f5.read()
            pa_static_routes_tmp = f6.read()
            pa_security_policy_tmp = f7.read()
            pa_source_nat_tmp = f8.read()
            
    except FileNotFoundError:
        raise FileNotFoundError(f" file not found: {files_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid XML in file: {files_path}")
    
    return pa_credentials, \
           pa_ha_config_tmp, \
           pa_ha_int_tmp, \
           pa_interface_tmp, \
           pa_zones_tmp, \
           pa_route_settings_tmp, \
           pa_static_routes_tmp, \
           pa_security_policy_tmp, \
           pa_source_nat_tmp

def color_text():
    """
    Define color codes for terminal output.

    Returns:
        dict: A dictionary containing color codes for formatting.   
    """

    # Define color codes for terminal output
    green = "\033[1;32m"
    red = "\033[1;31m"
    yellow = "\033[1;33m"
    blue = "\033[1;34m"
    cyan = "\033[1;36m"
    reset = "\033[0m"
    colors = {
        "green": green,
        "red": red,
        "yellow": yellow,
        "blue": blue,
        "cyan": cyan,
        "reset": reset
    }
    return colors

def banner(colors):
    """
    Display a banner with the project name and version.

    Args:
        colors (dict): Dictionary containing color codes for terminal output.
    """

    linkedin_url = "https://www.linkedin.com/in/joaopaulocp/"
    github_url = "https://github.com/jotape75/"
    
    # Create ASCII art WITHOUT color codes first
    ascii_art = pyfiglet.figlet_format("Pylo Alto", font="standard")
    ascii_lines = ascii_art.splitlines()  # Split the ASCII art into lines

    # Add empty padding lines
    print()  # Empty line at top
    print()

    # Add the ASCII art - LEFT-ALIGNED and COLORED
    for line in ascii_lines:
        # Apply yellow color to the ASCII art line (no centering)
        colored_line = f"{colors['yellow']}{line}{colors['reset']}"
        print(colored_line)

    # Add empty line after ASCII art
    print()

    # Add the additional message - LEFT-ALIGNED
    additional_message = "Eve-ng Palo Alto Firewall automated \n deployment using Python"
    for line in additional_message.split("\n"):
        # No centering, just strip whitespace and print
        print(f"{colors['cyan']}{line.strip()}{colors['reset']}")

    # Add more empty padding lines
    print()
    print()

    # Fixed color formatting - using consistent colors dict
    print(f"{colors['green']}[+] {colors['reset']}{colors['yellow']} Version     :{colors['reset']}{colors['cyan']} 1.0{colors['reset']}")
    print(f"{colors['green']}[+] {colors['yellow']}Created By   : {colors['reset']}{colors.get('cyan')}João Pinheiro (JP){colors['reset']}")
    print(f"{colors['green']} └→ {colors['yellow']}LinkedIn     : {colors['reset']}{colors.get('cyan')}{linkedin_url}{colors['reset']}")
    print(f"{colors['green']} └→ {colors['yellow']}Github       : {colors['reset']}{colors.get('cyan')}{github_url}{colors['reset']}\n")