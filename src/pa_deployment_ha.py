"""
Palo Alto Firewall High Availability Setup Automation.

Provides automated HA configuration for Palo Alto firewalls including:
- API key generation and authentication
- HA interface enablement and configuration  
- HA pair setup with priority and peer settings
- Automated commit operations with progress monitoring

Classes:
    PaloAltoFirewall_HA: Main HA configuration manager

Dependencies:
    - requests: HTTP API communication
    - xml.etree.ElementTree: XML response parsing
    - tqdm: Progress bar visualization
    - logging: Operation logging and error tracking
"""

import requests
import xml.etree.ElementTree as ET
import logging
import urllib3
from urllib.parse import urlencode
from tqdm import tqdm
import time

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()
logger = logging.getLogger()

class PaloAltoFirewall_HA:
    """
    Palo Alto Firewall High Availability Configuration Manager.
    
    Handles initial HA setup including API key generation, HA interface
    enablement, and HA pair configuration with automated progress tracking.
    
    Args:
        pa_credentials (list): Device credentials and connection info
        colors (dict): Terminal color codes for formatted output
        pa_ha_config_tmp (str): HA device configuration XML template
        pa_ha_int_tmp (str): HA interface configuration XML template
    """
        
    def __init__(self,pa_credentials,colors,pa_ha_config_tmp,pa_ha_int_tmp):
        """
        Initialize HA configuration manager with credentials and templates.
        
        Sets up progress bars and prepares for multi-device HA deployment.
        """
        self.pa_credentials = pa_credentials
        self.pa_ha_config_tmp = pa_ha_config_tmp
        self.pa_ha_int_tmp = pa_ha_int_tmp
        self.colors = colors
        self.rest_api_keys_list = []
        self.api_keys_list = []
        self.rest_api_headers = {
        "Content-Type": "application/json",
        }
        self.total_devices = len(pa_credentials)
        
        self.get_api_keys  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Getting API Keys{colors.get("reset")}', position=0, leave=True, ncols=100) 
        self.config_int  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Enabling Interfaces for HA{colors.get("reset")}', position=1, leave=True, ncols=100)        
        self.commit_interfaces  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Commit Changes - HA Interfaces{colors.get("reset")}', position=2, leave=True, ncols=100)        
        self.enable_ha  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Enable HA{colors.get("reset")}', position=3, leave=True, ncols=100)
        self.commit_ha  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Commit Changes- HA Config{colors.get("reset")}', position=4, leave=True, ncols=100)        

    def get_api_key(self):
        """
        Generate API keys for all firewall devices.
        
        Authenticates with each device and retrieves API keys for
        subsequent configuration operations.
        
        Returns:
            list: API key headers for each device
            
        Raises:
            requests.RequestException: For authentication failures
        """
        for device in self.pa_credentials:

            try:
                # API key request URL
                get_api_keys = f"https://{device['host']}/api/?type=keygen&user={device['username']}&password={device['password']}"

                response_api_key = requests.get(get_api_keys, headers=self.rest_api_headers, verify=False)
                if response_api_key.status_code == 200:
                    # Parse the XML response
                    xml_response = response_api_key.text
                    PA_api_key = xml_response.split("<key>")[1].split("</key>")[0]
                    
                    rest_headers = {
                    "Content-Type": "application/json",
                    "X-PAN-KEY": PA_api_key
                    }
                    xml_headers = {
                        "Content-Type": "application/xml",
                        "X-PAN-KEY": PA_api_key
                    }
                    self.rest_api_keys_list.append(rest_headers)
                    self.api_keys_list.append(xml_headers)
                    self.get_api_keys.update(1)  # Update the progress bar for each device

                else:
                    logger.info("Failed to get API key. Status code:", response_api_key.status_code)
            except requests.exceptions.RequestException as e:
                logger.error("Error occurred while making the API request:", e)

        return self.api_keys_list

    def enable_HA_interfaces(self):
        """
        Enable HA interfaces (ethernet1/4 and ethernet1/5) on all devices.
        
        Configures interfaces for HA heartbeat and data synchronization.
        Automatically commits changes after configuration.
        
        Raises:
            Exception: For interface configuration failures
        """
        for device, headers in zip(self.pa_credentials, self.api_keys_list):
            interfaces = ['ethernet1/4','ethernet1/5']
            try:
                ha_interfaces_link_url = f"https://{device['host']}/api/"
                for interface in interfaces:
                    interfaces_xml_parms = {
                        'type': 'config',
                        'action': 'set',
                        'xpath': f"/config/devices/entry[@name='localhost.localdomain']/network/interface/ethernet/entry[@name='{interface}']",
                        'element': '<ha/>',
                        'override': 'yes',
                        'key': headers['X-PAN-KEY']  # API key as parameter
                    }
                    response_control = requests.get(ha_interfaces_link_url, params=interfaces_xml_parms, verify=False, timeout=30)
                if response_control.status_code == 200:
                    xml_response_control = response_control.text
                    logger.info(xml_response_control)
                else:
                    logger.error(f"Failed to enable HA interfaces on {device['host']}: {response_control.status_code}")
                self.config_int.update(1)  # Update the progress bar for each device
            except Exception as e:
                logging.error(f"Error in HA configuration for {device['host']}: {e}")
        self.commit_changes(self.commit_interfaces)  # Commit changes after enabling interfaces   
    def ha_configuration(self):
        """
        Configure High Availability pairs with priorities and peer settings.
        
        Sets up HA groups with device priorities, preemption settings,
        and interface IP addresses for heartbeat communication.
        Automatically commits changes after configuration.
        
        Raises:
            Exception: For HA configuration failures
        """      
        ha_configs = [
            {'device_priority': '100', 'preemptive': 'yes', 'peer_ip': '1.1.1.2'}, # ha config for first device
            {'device_priority': '110', 'preemptive': 'no', 'peer_ip': '1.1.1.1'} # ha config for second device
        ]

        interface_configs = [
        {'ha1_ip': '1.1.1.1'}, # ha interface config for first device
        {'ha1_ip': '1.1.1.2'} # ha interface config for second device
        ]
        
        for i, (device, headers) in enumerate(zip(self.pa_credentials, self.api_keys_list)):
            try:
                ha_url = f"https://{device['host']}/api/"
                
                # Step 1: Enable basic HA
                basic_ha_params = {
                    'type': 'config',
                    'action': 'set',
                    'xpath': f"/config/devices/entry[@name='localhost.localdomain']/deviceconfig/high-availability",
                    'element': '<enabled>yes</enabled>',
                    'key': headers['X-PAN-KEY']
                }
                response_basic = requests.get(ha_url, params=basic_ha_params, verify=False, timeout=30)
                if response_basic.status_code == 200:
                    logger.info(f"Basic HA enabled on {device['host']}")
                    logger.info(response_basic.text)
                else:
                    logger.error(f"Failed to enable basic HA on {device['host']}: {response_basic.status_code}")
                    continue
                    
                # Step 2: Configure group
                ha_config = ha_configs[i]
                group_xml = self.pa_ha_config_tmp.format(
                    device_priority=ha_config['device_priority'],
                    preemptive=ha_config['preemptive'],
                    peer_ip=ha_config['peer_ip']
                )
                group_params = {
                    'type': 'config',
                    'action': 'set',
                    'xpath': f"/config/devices/entry[@name='localhost.localdomain']/deviceconfig/high-availability/group",
                    'element': group_xml,
                    'override': 'yes',
                    'key': headers['X-PAN-KEY']
                }
                response_group = requests.get(ha_url, params=group_params, verify=False, timeout=30)
                if response_group.status_code == 200:
                    logger.info(f"HA group configured on {device['host']}")
                    logger.info(response_group.text)
                else:
                    logger.error(f"Failed to configure HA group on {device['host']}: {response_group.status_code}")
                    continue
                # Step 3: Configure HA interfaces
                config = interface_configs[i]
                interface_xml = self.pa_ha_int_tmp.format(ha1_ip=config['ha1_ip'])                
                interface_params = {
                    'type': 'config',
                    'action': 'set',
                    'xpath': f"/config/devices/entry[@name='localhost.localdomain']/deviceconfig/high-availability/interface",
                    'override': 'yes',
                    'element': interface_xml,
                    'key': headers['X-PAN-KEY']
                }
                response_int = requests.get(ha_url, params=interface_params, verify=False, timeout=30)
                if response_int.status_code == 200:
                    logger.info(f"HA interfaces configured on {device['host']}")
                    logger.info(response_int.text)
                else:
                    logger.error(f"Failed to configure HA interfaces on {device['host']}: {response_int.status_code}")
                self.enable_ha.update(1)

            except Exception as e:
                logger.error(f"Error configuring HA for {device['host']}: {e}")

        self.commit_changes(self.commit_ha) # Commit changes after HA configuration
                 
    def commit_changes(self, progress_bar):
        """
        Commit configuration changes and monitor job completion.
        
        Initiates commit operations on all devices, tracks job progress,
        and updates specified progress bar when commits complete.
        
        Args:
            progress_bar (tqdm): Progress bar to update on completion
            
        Raises:
            Exception: For commit operation failures
        """
        jobid_dict = {}
        ready_devices = {}

        # Step 1: Start commits and collect job IDs
        for device, headers in zip(self.pa_credentials, self.api_keys_list):  
            try:
                commit_url = f"https://{device['host']}/api/"
                commit_params = {
                    'type': 'commit',
                    'cmd': '<commit></commit>',
                    'key': headers['X-PAN-KEY']  
                }
                
                response = requests.get(commit_url, params=commit_params, verify=False, timeout=60)
                
                if response.status_code == 200:
                    xml_response = response.text
                    root = ET.fromstring(xml_response)
                    result= root.find(".//result")
                    if result is not None:
                        jobid = result.findtext("job")
                        # Store device info with job ID
                        unique_key = f"{device['host']}_{jobid}"
                        jobid_dict[unique_key] = {
                            'device': device,
                            'headers': headers,
                            'host': device['host'],
                            'jobid': jobid
                        }
                        logger.info(f"Commit job ID for {device['host']}: {jobid}")
            except Exception as e:
                logger.debug(f"Error committing changes for {device['host']}: {e}") 
        # Check if any jobs were started       
        if not jobid_dict:
            logger.error("No commit jobs started")
            return
            # Step 2: Monitor jobs until all complete
        logger.info(jobid_dict)
        try:
            while jobid_dict:
                completed_jobs = []
                for unique_key, job_info in jobid_dict.items():
                    device = job_info['device']
                    headers = job_info['headers']
                    host = job_info['host']
                    jobid = job_info ['jobid']
                    
                    # Check job status for this specific device
                    job_url = f"https://{host}/api/"
                    job_params = {
                        'type': 'op',
                        'cmd': f'<show><jobs><id>{jobid}</id></jobs></show>',
                        'key': headers['X-PAN-KEY']
                    }
                    job_response = requests.get(job_url, params=job_params, verify=False, timeout=30)
                    
                    if job_response.status_code == 200:
                        job_xml_response = job_response.text
                        root = ET.fromstring(job_xml_response)
                        job = root.find(".//job")
                        
                        if job is not None:
                            job_status = job.findtext("status")
                            job_progress = job.findtext("progress", "0")
                            job_result = job.findtext("result", "")
                            
                            if job_status == "ACT":
                                logger.info(f"Commit running for {host}, progress {job_progress}% - job ID: {jobid}")
                                logger.info(f"logging job XML response for {host}: {job_xml_response}")
                                time.sleep(15)  # Wait before checking again
                            elif job_status == "FIN":
                                if job_result == "OK":
                                    logger.info(f"Commit completed successfully for {host} - job ID: {jobid}")
                                    logger.info(f"logging job XML response for {host}: {job_xml_response}")
                                    ready_devices[host] = [host]
                                    progress_bar.update(1)
                                else:
                                    logger.error(f"Job {jobid} failed on {host}: {job_result}")
                                    logger.error(f"logging job XML response for {host}: {job_xml_response}")
                                completed_jobs.append(unique_key) # Mark job as completed
                                
                # remove completed jobs from the dictionary
                for unique_key in completed_jobs:
                    if unique_key in jobid_dict:
                        host = jobid_dict[unique_key]['host']
                        logger.info(f"Removing completed job {unique_key} for {host} from monitoring")
                        del jobid_dict[unique_key]
                                    
                if len(ready_devices) == len(self.pa_credentials):
                    logger.info("All commits completed successfully!")
                    break
                else:
                    logger.info(f"{len(ready_devices)}/{len(self.pa_credentials)} commits completed")

        except Exception as e:
            logger.error(f"Error committing changes for {device['host']}: {e}")

