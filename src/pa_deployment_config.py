"""
Palo Alto Firewall Complete Configuration Automation.

Provides automated configuration for Palo Alto firewalls including:
- Active firewall identification in HA pairs
- Interface configuration with IP addressing and zones
- Security zone creation and management
- Virtual router and static route configuration
- Security policy deployment
- Source NAT configuration
- Automated commit operations with job monitoring
- HA configuration synchronization

Classes:
    PaloAltoFirewall_config: Complete firewall configuration manager

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

class PaloAltoFirewall_config:

    """
    Palo Alto Firewall Complete Configuration Manager.
    
    Handles comprehensive firewall configuration including interfaces, zones,
    routing, security policies, NAT rules, and HA synchronization with
    automated progress tracking and commit operations.
    
    Args:
        pa_credentials (list): Device credentials and connection info
        colors (dict): Terminal color codes for formatted output
        api_keys_list (list): API key headers from HA setup phase
        pa_interface_tmp (str): Interface configuration XML template
        pa_zones_tmp (str): Security zones XML template
        pa_route_settings_tmp (str): Virtual router settings XML template
        pa_static_routes_tmp (str): Static routes XML template
        pa_security_policy_tmp (str): Security policies XML template
        pa_source_nat_tmp (str): Source NAT rules XML template
    """
    def __init__(
        self,
        pa_credentials,
        colors, 
        api_keys_list,
        pa_interface_tmp,
        pa_zones_tmp,
        pa_route_settings_tmp,
        pa_static_routes_tmp,
        pa_security_policy_tmp,
        pa_source_nat_tmp
        ):
        
        self.pa_credentials = pa_credentials
        self.colors = colors
        self.api_keys_list = api_keys_list
        self.pa_interface_tmp = pa_interface_tmp
        self.pa_zones_tmp = pa_zones_tmp
        self.pa_route_settings_tmp = pa_route_settings_tmp
        self.pa_static_routes_tmp = pa_static_routes_tmp
        self.pa_security_policy_tmp = pa_security_policy_tmp
        self.pa_source_nat_tmp = pa_source_nat_tmp
        self.active_fw_list = []
        self.active_fw_headers = []

        self.total_devices = 1
        
        
        self.get_act_fw  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Getting ACTIVE Firewall{colors.get("reset")}', position=5, leave=True, ncols=100)
        self.conf_act_fw_int  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Configuring Interfaces on ACTIVE Firewall{colors.get("reset")}', position=6, leave=True, ncols=100) 
        self.act_fw_zone  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Configuring Zones on ACTIVE Firewall{colors.get("reset")}', position=7, leave=True, ncols=100)   
        self.act_fw_route  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Configuring Routes on ACTIVE Firewall{colors.get("reset")}', position=8, leave=True, ncols=100)   
        self.act_fw_policy  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Configuring Security Policy on ACTIVE Firewall{colors.get("reset")}', position=9, leave=True, ncols=100) 
        self.act_fw_nat  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Configuring Source NAT Policy on ACTIVE Firewall{colors.get("reset")}', position=10, leave=True, ncols=100) 
        self.act_fw_commit  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Commit Changes on ACTIVE Firewall{colors.get("reset")}', position=11, leave=True, ncols=100)   
        self.act_fw_check_sync  = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Check Sync Running Config{colors.get("reset")}', position=12, leave=True, ncols=100)   

    def get_active_fw(self):
        
        """
        Identify active firewall from HA pair.
        
        Queries HA status on all devices to find the active firewall
        for configuration deployment.
        
        Returns:
            tuple: Active firewall device info and API headers
            
        Raises:
            requests.RequestException: For HA status query failures
        """
        try:
            for device, headers in zip(self.pa_credentials, self.api_keys_list):
                ha_state_link = f"https://{device['host']}/api/"
                ha_state_api = f"{ha_state_link}?type=op&cmd=<show><high-availability><state></state></high-availability></show>"
                response_ha_state = requests.get(ha_state_api, headers=headers, verify=False)
                if response_ha_state.status_code == 200:
                    xml_response_state = response_ha_state.text
                    root = ET.fromstring(xml_response_state)
                    ha_state = root.find(".//state").text
                    if ha_state == "active":
                        self.active_fw_list.append(device)
                        self.active_fw_headers.append(headers)
                        self.get_act_fw.update(1)
                        break
                else:
                    logger.error(f"Failed to get HA state for {device['host']}: {response_ha_state.status_code}")
            logger.info(f"Active firewall: {self.active_fw_list}")
            
            return self.active_fw_list, self.active_fw_headers
        except requests.exceptions.RequestException as e:
            logger.error(f"KeyError: {e} - 'active_fw' not found in credentials.")

    def act_fw_int_config(self):
        """
        Configure physical interfaces on active firewall.
        
        Applies interface IP addressing, zone assignments, and Layer 3
        settings using predefined XML templates.
        
        Raises:
            Exception: For interface configuration failures
        """
        try:

            interface_xpath = f"/config/devices/entry[@name='localhost.localdomain']/network/interface/ethernet"
            
            # Apply configuration to active firewall
            config_url = f"https://{self.active_fw_list[0]['host']}/api/"
            interface_params = {
                'type': 'config',
                'action': 'set',
                'xpath': interface_xpath,
                'element': self.pa_interface_tmp,
                'key': self.active_fw_headers[0]['X-PAN-KEY']
            }

            response_interface = requests.get(config_url, params=interface_params, verify=False)
            
            if response_interface.status_code == 200:
                logger.info(f"Interfaces configured successfully on {self.active_fw_list[0]['host']}")
                logger.info(f"Response: {response_interface.text}")
            else:
                logger.error(f"Failed to configure interfaces on {self.active_fw_list[0]['host']}: {response_interface.status_code}")
                logger.error(f"Response: {response_interface.text}")

            # Update progress bar after all interfaces are configured
            self.conf_act_fw_int.update(1)
            #self.commit_changes(self.conf_act_fw_int_commit)
        except Exception as e:
            logger.error(f"Error in interface configuration process: {e}")

    def act_fw_zone_config(self):
        """
        Configure security zones on active firewall.
        
        Creates security zones for network segmentation and traffic control.
        
        Raises:
            Exception: For zone configuration failures
        """
        try:
            zone_xpath = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/zone"
            zone_config_url = f"https://{self.active_fw_list[0]['host']}/api/"
            zone_params = {
                'type': 'config',
                'action': 'set',
                'xpath': zone_xpath,
                'element': self.pa_zones_tmp,
                'key': self.active_fw_headers[0]['X-PAN-KEY']
            }
            response_zone= requests.get(zone_config_url, params=zone_params, verify=False)
            if response_zone.status_code == 200:
                logger.info(f"Zones configured successfully on {self.active_fw_list[0]['host']}")
                logger.info(f"Response: {response_zone.text}")
                self.act_fw_zone.update(1)
            else:
                logger.error(f"Failed to configure zones on {self.active_fw_list[0]['host']}: {response_zone.status_code}")
                logger.error(f"Response: {response_zone.text}")
            
        except Exception as e:
            logger.error(f"Error configuring zones: {e}")
            
    def act_fw_route_config(self):

        """
        Configure virtual router and static routes on active firewall.
        
        Sets up virtual router settings and default static routes
        for network connectivity.
        
        Raises:
            Exception: For routing configuration failures
        """
        try:
        
                  
            route_xpath = f"/config/devices/entry[@name='localhost.localdomain']/network/virtual-router/entry[@name='default']"
            route_config_url = f"https://{self.active_fw_list[0]['host']}/api/"
            route_params = {
                'type': 'config',
                'action': 'set',
                'xpath': route_xpath,
                'element': self.pa_route_settings_tmp,
                'key': self.active_fw_headers[0]['X-PAN-KEY']
            }
            response_route = requests.get(route_config_url, params=route_params, verify=False)
            if response_route.status_code == 200:
                logger.info(f"Route settings configured successfully on {self.active_fw_list[0]['host']}")
                logger.info(f"Response: {response_route.text}")
            else:
                logger.error(f"Failed to configure route settings on {self.active_fw_list[0]['host']}: {response_route.status_code}")
                logger.error(f"Response: {response_route.text}")
            
        # Configure default route
            default_route_xpath = "/config/devices/entry[@name='localhost.localdomain']/network/virtual-router/entry[@name='default']/routing-table/ip/static-route/entry[@name='default_route']"
            default_route_config_url = f"https://{self.active_fw_list[0]['host']}/api/"
            default_route_params = {
                'type': 'config',
                'action': 'set',
                'xpath': default_route_xpath,
                'element': self.pa_static_routes_tmp,
                'key': self.active_fw_headers[0]['X-PAN-KEY']
            }
            response_default_route = requests.get(default_route_config_url, params=default_route_params, verify=False)
            if response_default_route.status_code == 200:
                logger.info(f"Default route configured successfully on {self.active_fw_list[0]['host']}")
                logger.info(f"Response: {response_default_route.text}")
                self.act_fw_route.update(1)
            else:
                logger.error(f"Failed to configure default route on {self.active_fw_list[0]['host']}: {response_default_route.status_code}")
                logger.error(f"Response: {response_default_route.text}")
        except Exception as e:
            logger.error(f"Error configuring routes {self.active_fw_list[0]['host']}: {e}")
    def act_fw_security_policy_config(self):
        """
        Configure security policies on active firewall.
        
        Deploys security rules for traffic filtering and access control.
        
        Raises:
            Exception: For security policy configuration failures
        """
        try:
            security_policy_xpath = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/rulebase/security/rules"
            security_policy_config_url = f"https://{self.active_fw_list[0]['host']}/api/"
            security_policy_params = {
                'type': 'config',
                'action': 'set',
                'xpath': security_policy_xpath,
                'element': self.pa_security_policy_tmp,
                'key': self.active_fw_headers[0]['X-PAN-KEY']
            }
            response_security_policy = requests.get(security_policy_config_url, params=security_policy_params, verify=False)
            if response_security_policy.status_code == 200:
                logger.info(f"Security policies configured successfully on {self.active_fw_list[0]['host']}")
                logger.info(f"Response: {response_security_policy.text}")
                self.act_fw_policy.update(1)
            else:
                logger.error(f"Failed to configure security policies on {self.active_fw_list[0]['host']}: {response_security_policy.status_code}")
                logger.error(f"Response: {response_security_policy.text}")
        except Exception as e:
            logger.error(f"Error configuring security policies: {e}")   
    def act_fw_source_nat_config(self):
        """
        Configure source NAT rules on active firewall.
        
        Sets up NAT rules for address translation and traffic masquerading.
        
        Raises:
            Exception: For NAT configuration failures
        """
        try:
            source_nat_xpath = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/rulebase/nat/rules"
            source_nat_config_url = f"https://{self.active_fw_list[0]['host']}/api/"
            source_nat_params = {
                'type': 'config',
                'action': 'set',
                'xpath': source_nat_xpath,
                'element': self.pa_source_nat_tmp,
                'key': self.active_fw_headers[0]['X-PAN-KEY']
            }
            response_source_nat = requests.get(source_nat_config_url, params=source_nat_params, verify=False)
            if response_source_nat.status_code == 200:
                logger.info(f"Source NAT configured successfully on {self.active_fw_list[0]['host']}")
                logger.info(f"Response: {response_source_nat.text}")
                self.act_fw_nat.update(1)
            else:
                logger.error(f"Failed to configure source NAT on {self.active_fw_list[0]['host']}: {response_source_nat.status_code}")
                logger.error(f"Response: {response_source_nat.text}")
        except Exception as e:
            logger.error(f"Error configuring source NAT: {e}")
                   
    def commit_changes(self):
        """
        Commit configuration changes and monitor job completion.
        
        Initiates commit operation, tracks job progress until completion
        or timeout, and updates progress indicators.
        
        Raises:
            Exception: For commit operation failures
        """
        # Step 1: Start commits and collect job IDs
        try:
            commit_url = f"https://{self.active_fw_list[0]['host']}/api/"
            commit_params = {
                'type': 'commit',
                'cmd': '<commit></commit>',
                'key': self.active_fw_headers[0]['X-PAN-KEY']  
            }
            
            response_commit = requests.get(commit_url, params=commit_params, verify=False, timeout=60)
            
            if response_commit.status_code == 200:
                xml_response_commit = response_commit.text
                root = ET.fromstring(xml_response_commit)
                result= root.find(".//result")
                if result is not None:
                    jobid = result.findtext("job")
                    if jobid:
                        logger.info(f"Commit job ID for {self.active_fw_list[0]['host']}: {jobid}")
                    else:
                        logger.error(f"No job ID found in commit response for {self.active_fw_list[0]['host']}")
                        return
                else:
                    logger.error(f"Invalid commit response for {self.active_fw_list[0]['host']}: {xml_response_commit}")
                    return
            else:
                logger.error(f"Failed to start commit for {self.active_fw_list[0]['host']}: {response_commit.status_code}")
                return
        except Exception as e:
            logger.debug(f"Error committing changes for {self.active_fw_list[0]['host']}: {e}") 
    # Check if any jobs were started       
        if not jobid:
            logger.error("No commit jobs started")
            return
            # Step 2: Monitor jobs until all complete
        try:
            while jobid:
                # Check job status for this specific device
                job_url = f"https://{self.active_fw_list[0]['host']}/api/"
                job_params = {
                    'type': 'op',
                    'cmd': f'<show><jobs><id>{jobid}</id></jobs></show>',
                    'key': self.active_fw_headers[0]['X-PAN-KEY']
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
                            logger.info(f"Commit running for {self.active_fw_list[0]['host']}, progress {job_progress}% - job ID: {jobid}")
                            logger.info(f"logging job XML response for {self.active_fw_list[0]['host']}: {job_xml_response}")
                            time.sleep(15)  # Wait before checking again
                        elif job_status == "FIN":
                            if job_result == "OK":
                                logger.info(f"Commit completed successfully for {self.active_fw_list[0]['host']} - job ID: {jobid}")
                                logger.info(f"logging job XML response for {self.active_fw_list[0]['host']}: {job_xml_response}")
                                self.act_fw_commit.update(1)
                                break
                            else:
                                logger.error(f"Job {jobid} failed on {self.active_fw_list[0]['host']}: {job_result}")
                                logger.error(f"logging job XML response for {self.active_fw_list[0]['host']}: {job_xml_response}")                                
        except Exception as e:
            logger.error(f"Error committing changes for {self.active_fw_list[0]['host']}: {e}")

    def force_sync_config(self):
        """
        Force HA configuration synchronization to passive peer.
        
        Checks sync status and initiates synchronization if needed.
        Monitors sync progress until completion.
        
        Raises:
            Exception: For HA sync operation failures
        """
        try:
            check_sync_url = f"https://{self.active_fw_list[0]['host']}/api/"
            check_sync_params = {
                'type': 'op',
                'cmd': '<show><high-availability><state></state></high-availability></show>',
                'key': self.active_fw_headers[0]['X-PAN-KEY']
            }
            response_sync = requests.get(check_sync_url, params=check_sync_params, verify=False, timeout=30)
            logger.info(f"Response: {response_sync.status_code}")
            if response_sync.status_code == 200:
                xml_response_sync = response_sync.text
                root = ET.fromstring(xml_response_sync)
                config_state = root.findtext(".//group/running-sync")
                if config_state == "synchronized":
                    logger.info(f"Configuration is already synced on {self.active_fw_list[0]['host']}")
                elif config_state == "synchronization in progress":
                    self.wait_for_sync_completion()
                elif config_state == "not synchronized":
                    sync_params = {
                        'type': 'op',
                        'cmd': '<request><high-availability><sync-to-remote><running-config></running-config></sync-to-remote></high-availability></request>',
                        'key': self.active_fw_headers[0]['X-PAN-KEY']
                    }
                    response_sync = requests.get(check_sync_url, params=sync_params, verify=False, timeout=30)
                    if response_sync.status_code == 200:
                        logger.info(f"Configuration sync initiated on {self.active_fw_list[0]['host']}")
                        logger.info(f"Response: {response_sync.text}")
                        self.wait_for_sync_completion()
                    else:
                        logger.error(f"Failed to initiate configuration sync on {self.active_fw_list[0]['host']}: {response_sync.status_code}")
                        logger.error(f"Response: {response_sync.text}")
                self.act_fw_check_sync.update(1)
            else:
                logger.error(f"Failed to sync configuration on {self.active_fw_list[0]['host']}: {response_sync.status_code}")
        except Exception as e:
            logger.error(f"Error during configuration sync: {e}")
    def wait_for_sync_completion(self):
        """
        Monitor HA synchronization progress until completion.
        
        Polls HA sync status periodically and reports progress
        until synchronization completes or times out.
        
        Raises:
            Exception: For sync monitoring failures
        """
        try:
            max_checks = 8  # Check each 15 seconds for a maximum of 2 minutes
            check_sync_url = f"https://{self.active_fw_list[0]['host']}/api/"

            for check in range(max_checks):
                time.sleep(15)  # Wait between checks
                
                check_params = {
                    'type': 'op',
                    'cmd': '<show><high-availability><state></state></high-availability></show>',
                    'key': self.active_fw_headers[0]['X-PAN-KEY']
                }
                
                response = requests.get(check_sync_url, params=check_params, verify=False)
                
                if response.status_code == 200:
                    root = ET.fromstring(response.text)
                    current_state = root.findtext(".//group/running-sync")
                    
                    logger.info(f" Sync check {check + 1}/{max_checks}: Status = {current_state}")
                    
                    if current_state == "synchronized":
                        logger.info(f"Running Config synchronization completed successfully!")
                        break
                        
                    elif current_state in ["synchronization in progress", "sync in progress", "syncing"]:
                        continue
        except Exception as e:
            logger.error(f"Error monitoring sync completion: {e}")