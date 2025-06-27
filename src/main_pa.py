"""
Palo Alto Firewall Complete Automation - Main Execution Module.

This is the primary entry point for comprehensive Palo Alto firewall deployment
automation that handles both High Availability setup AND complete configuration
management. The module orchestrates a two-phase approach using specialized classes
for HA deployment and configuration management.

Two-Phase Automation Workflow:

PHASE 1 - High Availability Setup (PaloAltoFirewall_HA):
    1. Generate API keys for all firewall devices
    2. Enable HA-specific interfaces (ethernet1/4, ethernet1/5)
    3. Configure High Availability pairs with failover settings
    4. Establish HA heartbeat and data synchronization links

PHASE 2 - Complete Configuration (PaloAltoFirewall_config):
    1. Identify active firewall in HA pair
    2. Configure physical interfaces with IP addressing and zones
    3. Create security zones for network segmentation
    4. Configure virtual router settings and static routes
    5. Deploy security policies for traffic control
    6. Configure source NAT rules for address translation
    7. Commit all configuration changes with monitoring
    8. Force HA synchronization to passive peer
Args:
    None: Loads all configuration from utils_pa.file_path()

Returns:
    int: Exit code (0 for success, non-zero for failure)

Raises:
    requests.exceptions.RequestException: For HTTP/API communication errors
    xml.etree.ElementTree.ParseError: For invalid XML responses
    ValueError: For invalid configuration parameters or missing credentials
    TimeoutError: When operations exceed configured timeout limits
    FileNotFoundError: When required configuration files are missing
    Exception: For unexpected errors with full error reporting
    
"""
import logging
import datetime

from utils_pa import file_path,color_text,banner
from pa_deployment_ha import PaloAltoFirewall_HA
from pa_deployment_config import PaloAltoFirewall_config

# Configure logging
timestamp = datetime.datetime.now()
formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S") # Format the timestamp for the log file name for LINUX
#formatted_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # Format the timestamp for the 
# log file name for WINDOWS

LOG_FILE = f'/home/user/pystudies/myenv/pythonbasic/projects/eve-ng_automation_PA/log/{formatted_timestamp}_main_log_file.log'  # Specify the log file path
logging.basicConfig(
    filename=LOG_FILE,  # Log file
    level=logging.DEBUG,  # Log level (DEBUG captures all levels)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S"  # Date format
)

def main():

    try:
        # Step 1: Load credentials from file

        pa_credentials, \
        pa_ha_config_tmp, \
        pa_ha_int_tmp,\
        pa_interface_tmp,\
        pa_zones_tmp,\
        pa_route_settings_tmp, \
        pa_static_routes_tmp, \
        pa_security_policy_tmp, \
        pa_source_nat_tmp \
        = file_path()
        colors = color_text()
        banner(colors)
        
        # Step 2: Create firewall object with credentials
        firewall_deployer_ha = PaloAltoFirewall_HA(
            pa_credentials,
            colors,
            pa_ha_config_tmp,
            pa_ha_int_tmp
        )

        #Step 3: Call method on the object to configure firewall HA
        api_keys_list= firewall_deployer_ha.get_api_key()
        firewall_deployer_ha.enable_HA_interfaces()
        firewall_deployer_ha.ha_configuration()
        
        # Step 4: Create a configuration object with the credentials and templates
        firewall_config = PaloAltoFirewall_config(
            pa_credentials, 
            colors, 
            api_keys_list,
            pa_interface_tmp,
            pa_zones_tmp,
            pa_route_settings_tmp,
            pa_static_routes_tmp,
            pa_security_policy_tmp,
            pa_source_nat_tmp
            
        )

        # Step 5: Apply the configuration to the firewall
        firewall_config.get_active_fw()
        firewall_config.act_fw_int_config()
        firewall_config.act_fw_zone_config()
        firewall_config.act_fw_route_config()
        firewall_config.act_fw_security_policy_config()
        firewall_config.act_fw_source_nat_config()
        firewall_config.commit_changes()
        firewall_config.force_sync_config()
        
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()

