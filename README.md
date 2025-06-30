# 🔥 Palo Alto Firewall Automation using Python

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Network](https://img.shields.io/badge/network-automation-orange.svg)
![Palo Alto](https://img.shields.io/badge/palo%20alto-firewall-red.svg)

Comprehensive two-phase automation solution for Palo Alto firewall deployment with High Availability configuration, interface management, security policies, and real-time monitoring using Python.

## 🌟 Key Features

### ⚡ Two-Phase Deployment Architecture
- **Phase 1**: High Availability setup and device pairing
- **Phase 2**: Complete firewall configuration and synchronization

### 🛡️ Comprehensive Configuration Management
- **Interface Configuration**: IP addressing and zone assignments
- **Security Zones**: Network segmentation and traffic control
- **Routing Configuration**: Virtual router and static routes
- **Security Policies**: Traffic filtering and access control
- **NAT Configuration**: Source NAT rules and address translation
- **HA Synchronization**: Automated config sync between peers

### 📊 Advanced Monitoring & Tracking
- **Real-time Progress Bars**: Visual progress tracking for each operation
- **Comprehensive Logging**: Detailed audit trails and error reporting
- **Job Monitoring**: Commit operation tracking with progress percentage
- **HA Status Monitoring**: Real-time sync status verification

## 📁 Project Architecture

```
eve-ng_automation_PA/
├── 📋 data/                                    # Configuration data
│   ├── 🔧 automation_urls_pa.json             # Automation file paths configuration
│   ├── 🔑 dev_creds_pa.json                   # Device credentials (renamed from pa_credentials.json)
│   └── 📄 payload/                             # XML configuration templates
│       ├── 🔌 data_interface.xml              # Interface configuration template
│       ├── 📋 initial_config_template.txt     # Initial firewall setup commands
│       ├── 🤝 paloalto_ha_template_config.xml # HA device configuration
│       ├── 🔗 paloalto_interface_ha_template.xml # HA interface settings
│       ├── 🛡️ security_policy_template.xml    # Security policies template
│       ├── 🔄 source_nat_template.xml         # Source NAT rules template
│       ├── 🛣️ static_route_template.xml       # Static routing configuration
│       ├── 🌐 virtual_router_template.xml     # Virtual router setup
│       └── 🏛️ zones.xml                       # Security zones configuration
├── 📝 log/                                    # Automation logs
│   └── 2025-06-27 15:55:07_main_log_file.log # Example log file
├── 📖 README.md                               # Project documentation
├── 📦 requirements.txt                        # Python dependencies
└── 📦 src/                                    # Source code
    ├── ⚠️ exceptions_pa.py                    # Custom exceptions
    ├── 🎯 main_pa.py                          # Main orchestrator
    ├── ⚙️ pa_deployment_config.py             # Complete firewall configuration
    ├── 🤝 pa_deployment_ha.py                 # HA configuration manager
    ├── 🗂️ __pycache__/                        # Python cache files
    │   ├── exceptions_pa.cpython-310.pyc
    │   ├── pa_deployment_config.cpython-310.pyc
    │   ├── pa_deployment.cpython-310.pyc
    │   ├── pa_deployment_ha.cpython-310.pyc
    │   └── utils_pa.cpython-310.pyc
    └── 🛠️ utils_pa.py                         # Utilities and helpers
```

## 🚀 Installation

### Prerequisites
- **Python 3.8 - 3.12**
- **Git** (for cloning the repository)
- **Palo Alto firewalls** (physical or virtual)
- **Network connectivity** to firewall management interfaces

### Windows Setup Guide

**Step-by-Step Windows Installation:**

1. **Clone the repository**
   ```cmd
   git clone https://github.com/jotape75/eve-ng_automation_PA.git
   cd eve-ng_automation_PA
   ```

2. **Create Virtual Environment**
   ```cmd
   # Create virtual environment (use Command Prompt, not PowerShell)
   python -m venv venv311
   
   # Activate virtual environment
   venv311\Scripts\activate.bat
   
   # Verify activation (should show (venv311) prefix)
   ```

3. **Install Dependencies**
   ```cmd
   # Install required packages
   pip install -r requirements.txt
   ```

### Linux Setup Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jotape75/eve-ng_automation_PA.git
   cd eve-ng_automation_PA
   ```

2. **Fix file permissions (Linux/Mac only):**
   ```bash
   # Ensure you own all project files
   sudo chown -R $USER:$USER ./
   
   # Set proper directory permissions
   find . -type d -exec chmod 755 {} \;
   
   # Set proper file permissions
   find . -type f -exec chmod 644 {} \;
   
   # Make Python scripts executable
   chmod +x src/*.py
   ```

3. **Create and activate a virtual environment (recommended):**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   ```

4. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify installation:**
   ```bash
   # Test Python dependencies
   python -c "import requests, tqdm, pandas, pyfiglet; print('All dependencies installed successfully!')"
   
   # Test script execution
   python src/main_pa.py --help
   ```

### ⚠️ Important Notes
Always run the automation as your regular user, not as root:

```bash
# ❌ DON'T do this:
sudo python src/main_pa.py

# ✅ DO this instead:
python src/main_pa.py
```

## ⚙️ Configuration

### 1. Edit Credential Files

**Device Credentials:**
Modify `data/credentials/pa_credentials.json` with your Palo Alto firewall credentials:

```json
[
    {
        "host": "192.168.1.10",
        "username": "admin",
        "password": "your_password_here"
    },
    {
        "host": "192.168.1.11",
        "username": "admin",
        "password": "your_password_here"
    }
]
```

### 2. Configure Automation Settings

**File Paths** - Replace `<YOUR_PROJECT_PATH>` with your actual project directory:

Update `data/automation_urls_pa.json`:

```json
{
    "urls": {
        "pa_creds_file": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/credentials/pa_credentials.json",
        "pa_initial_config": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/pa_initial_config.xlsx",
        "pa_ha_config_template": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/payload/paloalto_ha_template_config.xml",
        "pa_ha_int_template": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/payload/paloalto_interface_ha_template.xml",
        "pa_interface_template": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/payload/data_interface.xml",
        "pa_zone_template": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/payload/zones.xml",
        "pa_virtual_router_template": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/payload/virtual_router_template.xml",
        "pa_static_routes_template": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/payload/static_route_template.xml",
        "pa_security_policy_template": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/payload/security_policy_template.xml",
        "pa_source_nat_template": "<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/payload/source_nat_template.xml"
    }
}
```

### 3. Customize XML Templates

**Files requiring customization:**

**Data Interface File:**
Modify the `<entry name="<YOUR_IP>"/>` in `data/payload/data_interface.xml` with your actual IP address:

```xml
<ip>
    <entry name="192.168.100.1/24"/>
</ip>
```

**Static Route File:**
Modify the `<ip-address>"NEXT_HOP"</ip-address>` in `data/payload/static_route_template.xml` with your actual next hop IP address:

```xml
<nexthop>
    <ip-address>192.168.1.1</ip-address>
</nexthop>
```

**NAT File:**
Modify the `<ip>"YOUR_UNTRUST_IP"</ip>` in `data/payload/source_nat_template.xml` with your actual source NAT IP address:

```xml
<translated-address>
    <ip>192.168.100.1</ip>
</translated-address>
```

**Files that typically don't require modification:**
- `data/payload/paloalto_ha_template_config.xml` - HA device configuration
- `data/payload/paloalto_interface_ha_template.xml` - HA interface settings
- `data/payload/zones.xml` - Security zones
- `data/payload/security_policy_template.xml` - Security policies

### 4. Update Main File Configuration

**Update Utils File (`src/utils_pa.py`):**
```python
# Replace <YOUR_PROJECT_PATH> with your actual project path
with open('<YOUR_PROJECT_PATH>/eve-ng_automation_PA/data/automation_urls_pa.json', 'r') as config_file:
    files_path = json.load(config_file)
```

**Update Main File (`src/main_pa.py`):**
```python
# Update log file path and select correct timestamp format for your OS

# For Linux/Mac:
formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

# For Windows:
# formatted_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

LOG_FILE = f'<YOUR_PROJECT_PATH>/eve-ng_automation_PA/log/{formatted_timestamp}_main_log_file.log'
```

## 🎯 Usage

### Basic Execution
```bash
cd src
python main_pa.py
```

### Automation Workflow

**Phase 1: HA Setup**
```
🔑 Generating API Keys        ████████████████ 100%
🔌 Enabling HA Interfaces    ████████████████ 100%
🤝 Configuring HA Pairs      ████████████████ 100%
```

**Phase 2: Configuration**
```
🎯 Getting Active Firewall   ████████████████ 100%
🔧 Configuring Interfaces    ████████████████ 100%
🏛️ Configuring Zones         ████████████████ 100%
🛣️ Configuring Routes        ████████████████ 100%
🛡️ Configuring Policies      ████████████████ 100%
🔄 Configuring NAT Rules     ████████████████ 100%
✅ Committing Changes        ████████████████ 100%
🔄 Syncing HA Configuration  ████████████████ 100%
```

## 🛡️ Security & Production Considerations

### 🔒 Security Features
- **HTTPS Communication**: All API calls encrypted in transit
- **Secure Credential Management**: API keys handled securely
- **Data Masking**: Sensitive information masked in logs
- **SSL Verification**: Configurable per environment

### 🏭 Production Readiness
- **Comprehensive Error Handling**: Graceful failure management
- **Operation Timeouts**: Prevents hanging operations
- **Audit Logging**: Complete operation history
- **Rollback Capabilities**: Configuration recovery options

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🔧 Maintenance and Updates

This project is actively maintained to ensure compatibility with the latest versions of Palo Alto PAN-OS and Python. Here's how updates and maintenance are handled:

### Bug Fixes:
- Known issues are tracked in the GitHub Issues section
- Fixes are prioritized based on their impact and severity

### Feature Updates:
- New features, such as support for additional PA configurations or policies, are added periodically
- Suggestions for new features are welcome! Feel free to open an issue or submit a pull request

### Compatibility:
- The project is tested with the latest versions of Python and PAN-OS
- Dependencies are updated regularly to ensure compatibility and security

### Community Contributions:
- Contributions from the community are encouraged
- If you'd like to contribute, please follow the guidelines in the Contributing section

### Versioning:
- The project follows semantic versioning (e.g., v1.0.0)
- Major updates, minor improvements, and patches are documented in the Changelog

## 👨‍💻 Contact

**João Pinheiro (JP)**

For any questions or support, feel free to reach out:

- **🐙 GitHub**: [jotape75](https://github.com/jotape75)
- **💼 LinkedIn**: [linkedin.com/in/joaopaulocp](https://www.linkedin.com/in/joaopaulocp/)
- **📧 Email**: [degraus@gmail.com](mailto:degraus@gmail.com)

## 🔗 Related Projects

Explore my other network automation projects:

- [🔥 **FTD Automation**](https://github.com/jotape75/eve-ng_automation_FTD) - Cisco FTD firewall automation with FMC management

## ⭐ Support

If this project helped you, please give it a star! ⭐

---
