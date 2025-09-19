# Complete VSCode & Cursor Setup Guide for Home Assistant

```yaml
---
# Metadata
type: comprehensive-tutorial
category: Home-Assistant-Development
primary_tools:
  - VSCode
  - Cursor-IDE
  - ESPHome
  - Home-Assistant
tags:
  - home-assistant
  - vscode
  - cursor
  - esphome
  - yaml
  - automation
  - smart-home
created: "{{date:YYYY-MM-DD}}"
updated: "{{date:YYYY-MM-DD}}"
status: complete
difficulty: beginner-to-advanced
estimated_time: 1-3 hours
scope: full-development-environment
dependencies:
  - Home Assistant (any installation)
  - Docker (for ESPHome)
  - Git (recommended)
target_audience:
  - ESPHome Builder graduates
  - Home Assistant configuration editors
  - Smart home developers
aliases:
  - ha-vscode-setup
  - cursor-esphome-guide
  - smart-home-ide
related_notes: []
---
```

## Overview

This comprehensive guide covers three approaches to using VSCode/Cursor with Home Assistant, from basic configuration editing to advanced ESPHome development. Based on community insights and real-world implementations, this guide will transform your Home Assistant development workflow.

**Key Benefits:**
- Move from 1,500+ line ESPHome applications taking weeks to complete in efficient workflows
- Complete complex 2000+ line ESPHome applications in a week instead of months
- Eliminate switching between multiple editors and interfaces
- AI-assisted development with intelligent code completion

---

## Three Development Approaches

### 🖥️ **Approach 1: Local VSCode/Cursor Installation**
**Best for:** Advanced users, complex projects, AI-assisted development
**Pros:** Full feature set, AI integration, custom extensions
**Cons:** Requires local setup, file synchronization needed

### 🌐 **Approach 2: VSCode Server Add-on (Browser)**
**Best for:** Beginners, quick edits, embedded experience  
**Pros:** No local installation, pre-configured, integrated with HA interface
**Cons:** Limited extensions, browser-dependent performance

### ☁️ **Approach 3: GitHub Codespaces**
**Best for:** Collaboration, temporary environments, cross-platform access
**Pros:** Cloud-based, consistent environment, automatic sync
**Cons:** Internet dependent, usage limits, still in preview

---

## Approach 1: Local VSCode/Cursor Setup (Recommended)

### Step 1: Choose Your Editor

#### Option A: Cursor AI (Highly Recommended)
- **Download:** [cursor.com](https://cursor.com)
- **Why Cursor:** Game-changing AI assistance for ESPHome development, VSCode-based with integrated AI
- **Installation:** Direct download, no prerequisites needed
- **Platforms:** Windows, macOS, Linux (Ubuntu tested)

#### Option B: Visual Studio Code
- **Download:** [code.visualstudio.com](https://code.visualstudio.com)
- **Why VSCode:** Mature ecosystem, extensive extension library
- **Installation:** Standard VSCode installation

### Step 2: Essential Extensions Installation

Install these extensions through the Extensions panel (`Ctrl+Shift+X`):

#### Core Home Assistant Extensions
```bash
# Search and install these extensions:
1. Home Assistant Config Helper (keesschollaart.vscode-home-assistant)
2. ESPHome (ESPHome.esphome-vscode)  
3. ESPHome Snippets (vscode-esphome-snippets)
4. YAML Language Support (redhat.vscode-yaml)
5. Run In Terminal (fabiospampinato.vscode-run-in-terminal)
```

#### Optional but Recommended
```bash
6. GitLens (eamodio.gitlens) - Git enhancement
7. Better Comments (aaron-bond.better-comments) - Comment styling
8. Bracket Pair Colorizer (CoenraadS.bracket-pair-colorizer-2)
9. Path Intellisense (christian-kohler.path-intellisense)
10. Material Icon Theme (PKief.material-icon-theme) - Better file icons
```

### Step 3: Home Assistant Connection Setup

#### Configure HA Integration
1. Open VSCode/Cursor Settings (`Ctrl+,`)
2. Search for "Home Assistant"
3. Configure these settings:

```json
{
  "homeassistant.hostUrl": "http://homeassistant.local:8123",
  "homeassistant.longLivedAccessToken": "your_access_token_here",
  "homeassistant.ignoreCertificates": false
}
```

#### Generate Long-Lived Access Token
1. In Home Assistant: Profile → Security → Long-Lived Access Tokens
2. Click "Create Token"
3. Copy token to VSCode settings
4. **Never commit tokens to version control!**

### Step 4: File Access Configuration

#### Option A: Samba Share (Windows/macOS)
1. Install **Samba Share** add-on in Home Assistant
2. Configure share settings:
```yaml
username: your_username
password: your_password
workgroup: WORKGROUP
compatibility_mode: false
```
3. Map network drive or mount share
4. Open folder in VSCode: `\\homeassistant.local\config`

#### Option B: SSH Access (Linux/Advanced)
1. Install **SSH & Web Terminal** add-on
2. Configure SSH key authentication
3. Use VSCode Remote-SSH extension
4. Connect to `username@homeassistant.local`

#### Option C: Git Repository (Recommended)
1. Initialize git in HA config directory
2. Use private GitHub/GitLab repository
3. Edit locally, push changes
4. Use Git Pull add-on for automatic updates

---

## ESPHome Development Setup

### Docker Integration for Compilation

Based on the community guide, set up efficient ESPHome compilation:

#### Step 1: Identify ESPHome Container
```bash
# Find your ESPHome container name
docker ps -a | grep esphome

# Common names:
# addon_15ef4d2f_esphome
# addon_a0d7b954_esphome
```

#### Step 2: VSCode Terminal Setup
1. Open integrated terminal (`Ctrl+`` `)
2. SSH to Home Assistant system:
```bash
ssh your_user@homeassistant.local
```

#### Step 3: Automate Docker Access
Add to your `~/.bashrc` file:
```bash
# ESPHome Docker Shortcuts
export PS1='\[\e[0;36m\]\u\[\e[0m\]@\[\e[0;33m\]\h\[\e[0m\]:\[\e[0;35m\]\w\[\e[0m\]> '
alias esphome-shell='sudo docker exec -it -w /config/esphome addon_15ef4d2f_esphome bash'
alias esp-run='esphome run'
alias esp-logs='esphome logs'
alias esp-compile='esphome compile'
```

#### Step 4: Streamlined Workflow
```bash
# One-command development cycle:
ssh user@homeassistant.local
esphome-shell
esphome run your-device.yaml  # Compiles, uploads, shows logs
```

---

## Advanced Cursor AI Integration

### AI-Assisted Development Setup

#### Create .cursorrules File
```yaml
# Place in project root
# ESPHome/Home Assistant Development Rules
- Always validate YAML syntax before suggesting changes
- Use Home Assistant entity naming conventions (snake_case)
- Include safety considerations for all sensor/actuator configurations
- Suggest appropriate update intervals based on sensor types
- Always include Home Assistant integration patterns in ESPHome configs
- Consider power consumption in battery-powered designs
- Include comprehensive error handling and fallback states
- Use semantic versioning for configuration comments
- Prioritize security in all automation suggestions
- Always validate entity IDs exist in Home Assistant before referencing
```

#### Cursor Hotkey Configuration
Set up efficient development hotkeys:
```json
{
  "key": "ctrl+r",
  "command": "workbench.action.terminal.sendSequence",
  "args": {
    "text": "esphome run ${fileBasename}\n"
  },
  "when": "resourceExtname == .yaml"
}
```

### AI Prompt Strategies for HA Development

#### Effective ESPHome Prompts
```
"Create an ESPHome configuration for ESP32 with:
- DHT22 temperature/humidity sensor on GPIO 4
- BMP280 pressure sensor on I2C (SDA: 21, SCL: 22)
- Two relay outputs on GPIO 16, 17
- Home Assistant integration with descriptive entity names
- Appropriate filtering and update intervals
- Include diagnostic sensors (WiFi signal, uptime)"
```

#### Home Assistant Automation Prompts
```
"Create a Home Assistant automation that:
- Triggers when bedroom temperature exceeds 25°C
- Only during sleep hours (10 PM - 7 AM)  
- Turns on ceiling fan for 15 minutes
- Sends notification to phone
- Includes conditions to prevent multiple triggers
- Add manual override capability"
```

---

## Approach 2: VSCode Server Add-on Setup

### Installation Process
1. **Add Repository:** Settings → Add-ons → Add-on Store → ⋮ → Repositories
2. **Repository URL:** `https://github.com/hassio-addons/repository`
3. **Install:** Search "Visual Studio Code" → Install
4. **Configure:** Set password and optional SSL settings
5. **Start:** Start add-on and enable "Start on boot"

### Configuration Options
```yaml
# Add-on Configuration
packages:
  - mariadb-client  # For database access
  - git             # Version control
init_commands:
  - echo "Welcome to HA VSCode Server"
```

### Key Features
- Pre-installed Home Assistant and YAML extensions with auto-completion working out of the box
- Direct file access to `/config` directory
- Integrated terminal for Home Assistant CLI
- No external file sync required

---

## Home Assistant Integration Features

### Core Functionality

#### 1. **Entity Auto-completion**
- Real-time entity suggestions while typing
- Works in automations, scripts, and ESPHome configs
- Validates entity existence against live HA instance

#### 2. **Schema Validation**
- YAML syntax validation
- Home Assistant configuration schema checking
- ESPHome component validation
- Real-time error highlighting

#### 3. **Navigation & Go-to Definition**
- Jump between included files
- Navigate `!include` and `!include_dir_named` references
- Package organization support

#### 4. **Snippets System**
- Pre-built automation templates
- ESPHome component snippets
- Common configuration patterns
- Custom snippet creation

#### 5. **Home Assistant Commands**
```bash
# Available via Command Palette (Ctrl+Shift+P):
- Home Assistant: Restart
- Home Assistant: Reload Automations  
- Home Assistant: Reload Scripts
- Home Assistant: Check Configuration
- Home Assistant: Developer Tools
```

### Advanced Features

#### Service Call Integration
- Auto-complete service names
- Parameter suggestions with descriptions
- Service domain awareness
- Entity filtering by domain

#### Template Development
- Jinja2 syntax highlighting
- Template testing capabilities  
- State and attribute suggestions
- Template function auto-complete

---

## Project Structure Best Practices

### Recommended Directory Structure
```
config/
├── automations/
│   ├── lighting.yaml
│   ├── climate.yaml
│   └── security.yaml
├── esphome/
│   ├── devices/
│   │   ├── bedroom-sensors.yaml
│   │   └── living-room-hub.yaml
│   ├── common/
│   │   ├── wifi.yaml
│   │   └── base-config.yaml
│   └── secrets.yaml
├── scripts/
│   ├── morning-routine.yaml
│   └── night-routine.yaml
├── packages/
│   ├── weather.yaml
│   └── energy.yaml
├── .gitignore
├── .cursorrules
└── README.md
```

### Version Control Setup
```bash
# Initialize repository
git init
git add .
git commit -m "Initial Home Assistant configuration"

# Create .gitignore
echo "secrets.yaml" >> .gitignore
echo "known_devices.yaml" >> .gitignore
echo "*.log" >> .gitignore
echo ".storage/" >> .gitignore
```

---

## Development Workflows

### Daily Development Routine

#### 1. **Morning Setup**
```bash
# Update local repository
git pull origin main

# Check HA logs for overnight issues
ha core logs --follow
```

#### 2. **Development Cycle**
```bash
# Edit configurations in VSCode/Cursor
# Use AI assistance for complex automations
# Validate syntax with real-time checking
# Test changes incrementally
```

#### 3. **Testing & Deployment**
```bash
# Check configuration
ha core check

# Restart specific services
ha core restart

# Monitor logs
ha core logs --follow
```

#### 4. **Commit Changes**
```bash
git add .
git commit -m "Add bedroom climate automation"
git push origin main
```

### ESPHome Development Workflow

#### 1. **Device Setup**
```bash
# Create new device configuration
cursor esphome/devices/new-sensor.yaml

# Use AI to generate base configuration
# Add specific sensors/actuators
# Configure Home Assistant integration
```

#### 2. **Compilation & Upload**
```bash
# From VSCode integrated terminal
esphome run new-sensor.yaml

# Or use Cursor hotkey (Ctrl+R)
# Automatically compiles and uploads
```

#### 3. **Testing & Iteration**
```bash
# Monitor device logs
esphome logs new-sensor.yaml

# Make adjustments
# Re-compile and upload
# Validate in Home Assistant
```

---

## Troubleshooting Guide

### Common Issues & Solutions

#### Connection Problems
**Issue:** Can't connect to Home Assistant
**Solutions:**
- Verify host URL format: `http://homeassistant.local:8123`
- Check long-lived access token validity
- Test network connectivity: `ping homeassistant.local`
- Disable SSL verification for local networks

#### Auto-completion Not Working
**Issue:** No entity suggestions appearing
**Solutions:**
- Verify Home Assistant connection in settings
- Check access token permissions
- Restart VSCode/Cursor
- Clear extension cache: `Ctrl+Shift+P` → "Reload Window"

#### ESPHome Compilation Errors
**Issue:** Docker compilation fails
**Solutions:**
- Verify container name: `docker ps -a | grep esphome`
- Check file permissions in `/config/esphome`
- Update ESPHome add-on to latest version
- Clear compilation cache: delete `.esphome` directory

#### File Access Issues
**Issue:** Cannot edit files / permission denied
**Solutions:**
- For Samba: Check username/password configuration
- For SSH: Verify key authentication setup
- For Git: Check repository permissions and credentials
- Use correct user account with file access rights

---

## Performance Optimization

### VSCode/Cursor Performance
```json
{
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/*/**": true,
    "**/.hg/store/**": true,
    "**/.esphome/**": true,
    "**/tts/**": true,
    "**/deps/**": true
  },
  "search.exclude": {
    "**/home-assistant_v2.db": true,
    "**/.storage": true,
    "**/deps": true
  }
}
```

### Git Configuration
```bash
# Optimize for large repositories
git config core.preloadindex true
git config core.fscache true
git config gc.auto 256

# Ignore large files
echo "home-assistant_v2.db" >> .gitignore
echo "*.db-journal" >> .gitignore
```

---

## Advanced Tips & Tricks

### Cursor AI Maximization
- **Context Awareness:** Always include relevant files using `@filename`
- **Incremental Development:** Build features step-by-step with AI assistance
- **Error Resolution:** Paste complete error messages for accurate diagnosis
- **Code Review:** Ask AI to review configurations for security and efficiency

### VSCode Power Features
- **Multi-cursor Editing:** `Ctrl+D` for multiple selections
- **Command Palette:** `Ctrl+Shift+P` for quick actions
- **Quick File Open:** `Ctrl+P` for rapid file navigation
- **Integrated Git:** Built-in version control management

### Home Assistant Integration
- **Live Entity Testing:** Use Developer Tools → States for real-time testing
- **Automation Tracing:** Monitor automation execution in real-time
- **Service Calling:** Test service calls directly from VSCode using HA commands
- **Log Monitoring:** Tail logs while developing for immediate feedback

---

## Security Considerations

### Token Management
- **Never commit access tokens** to version control
- **Use environment variables** for sensitive data
- **Rotate tokens regularly** (every 90 days recommended)
- **Limit token scope** to minimum required permissions

### Network Security
- **Use HTTPS** for external connections
- **VPN access** for remote development
- **Firewall rules** for VSCode Server add-on
- **Regular updates** for all components

### Configuration Security
```yaml
# Example secure secrets management
secrets.yaml:
  wifi_password: "your_wifi_password"
  api_password: "your_api_password"
  
# Reference in configurations
wifi:
  ssid: "Your_Network"
  password: !secret wifi_password
```

---

## Community Resources

### Essential Links
- **Home Assistant Config Examples:** [GitHub awesome-home-assistant repository](https://github.com/frenck/awesome-home-assistant)
- **ESPHome Component Library:** [ESPHome.io documentation](https://esphome.io/)
- **VSCode Extension:** [Home Assistant Config Helper](https://marketplace.visualstudio.com/items?itemName=keesschollaart.vscode-home-assistant)
- **Community Forum:** [Home Assistant Community](https://community.home-assistant.io/)

### Configuration Inspiration
Based on Kees Schollaart's presentation insights, explore these community configurations:
- **Geek's Repository:** Hardware documentation and device configurations
- **Frenck's Configuration:** Integration-based organization and area automation patterns
- **Community Showcases:** Real-world implementations and creative solutions

---

## Conclusion

This comprehensive setup transforms Home Assistant development from basic text editing to professional IDE-powered development with AI assistance. Whether you choose local VSCode/Cursor, browser-based editing, or cloud development, these tools eliminate the need to switch between multiple interfaces while providing intelligent assistance for complex configurations.

**Key Takeaways:**
- Almost 40,000 developers are already using these tools, proving their effectiveness
- AI assistance can reduce complex ESPHome development from months to weeks
- Integrated workflows eliminate context switching and improve productivity
- Proper setup enables professional development practices for smart home automation

Start with the approach that matches your technical comfort level, then gradually adopt advanced features as your projects grow in complexity.

---

## Related Notes

- [[ESPHome Advanced Configurations]]
- [[Home Assistant Automation Patterns]]  
- [[Git Workflows for Smart Home]]
- [[AI-Assisted Development Techniques]]

*Last updated: {{date:YYYY-MM-DD}}*