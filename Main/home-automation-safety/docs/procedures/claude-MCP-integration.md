# Windows MCP Setup - Prerequisites and Installation

## ✅ Confirmed: Works on Windows

MCP (Model Context Protocol) fully supports Windows and integrates seamlessly with Claude Desktop on Windows 10/11.

## Software Prerequisites

### Required Software

#### 1. Claude Desktop (Windows)
- **Download:** https://claude.ai/download
- **Minimum:** Windows 10 or Windows 11
- **Status:** ✅ You likely already have this

#### 2. Node.js (LTS Version)
- **Download:** https://nodejs.org/en/download/
- **Recommended Version:** 18.x or 20.x LTS
- **Why needed:** Runs the MCP GitHub server
- **Installation:** Standard Windows installer (.msi)

#### 3. Git for Windows
- **Download:** https://git-scm.com/download/win
- **Status:** ✅ You already have this installed
- **Includes:** Git Bash, Git GUI, command line tools

### Optional but Recommended

#### 4. Windows Terminal
- **Download:** Microsoft Store or GitHub releases
- **Benefits:** Better command line experience
- **Alternative:** PowerShell or Command Prompt work fine

#### 5. Visual Studio Code (Optional)
- **Download:** https://code.visualstudio.com/
- **Benefits:** Easy JSON editing for config files
- **Alternative:** Any text editor works (Notepad++, etc.)

## Step-by-Step Windows Installation

### Step 1: Install Node.js
```powershell
# Check if already installed
node --version
npm --version

# If not installed:
# 1. Download from https://nodejs.org/
# 2. Run the .msi installer
# 3. Follow installation wizard (accept defaults)
# 4. Restart PowerShell/Command Prompt
```

### Step 2: Install MCP GitHub Server
```powershell
# Open PowerShell as Administrator (recommended)
# Install globally
npm install -g @modelcontextprotocol/server-github

# Verify installation
npm list -g @modelcontextprotocol/server-github
```

### Step 3: Create GitHub Token
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes:
   - ☑️ `repo` (full repository access)
   - ☑️ `workflow` (GitHub Actions)
4. Copy token immediately

### Step 4: Set Environment Variable (Recommended)
```powershell
# Option A: PowerShell (Temporary - current session)
$env:GITHUB_TOKEN = "your_github_token_here"

# Option B: PowerShell (Permanent - requires Admin)
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "your_github_token_here", "User")

# Option C: Windows GUI
# 1. Win + R → "sysdm.cpl" → Advanced → Environment Variables
# 2. User Variables → New
# 3. Variable Name: GITHUB_TOKEN
# 4. Variable Value: your_github_token_here
```

### Step 5: Configure Claude Desktop
1. **Open config file location:**
   ```powershell
   # Navigate to Claude config directory
   explorer %APPDATA%\Claude
   ```

2. **Create/Edit `claude_desktop_config.json`:**
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": [
           "@modelcontextprotocol/server-github"
         ],
         "env": {
           "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
         }
       }
     }
   }
   ```

### Step 6: Restart Claude Desktop
- Close Claude Desktop completely
- Restart from Start Menu or Desktop shortcut

## Windows-Specific Considerations

### File Paths
- **Config Location:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Full Path Example:** `C:\Users\YourName\AppData\Roaming\Claude\claude_desktop_config.json`

### PowerShell vs Command Prompt
Work on both, PowerShell recommended:
```powershell
npm install -g @modelcontextprotocol/server-github
```

### Windows Defender/Antivirus
- Node.js and npm are safe and widely used
- Some antivirus may flag Node.js modules initially
- Add exceptions if necessary

### Network/Corporate Environments
If behind corporate firewall:
```powershell
# Set npm proxy if needed
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080
```

## Troubleshooting Windows Issues

### Issue 1: "node is not recognized"
```powershell
# Check if Node.js is in PATH
echo $env:PATH

# If not, reinstall Node.js or add manually:
# Add to PATH: C:\Program Files\nodejs\
```

### Issue 2: "Permission denied" during npm install
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → "Run as Administrator"
npm install -g @modelcontextprotocol/server-github
```

### Issue 3: "npx not found"
```powershell
# npx comes with Node.js, verify installation
npx --version

# If missing, reinstall Node.js
```

### Issue 4: Claude Desktop config not found
```powershell
# Create directory if missing
mkdir "$env:APPDATA\Claude"

# Create config file
New-Item -Path "$env:APPDATA\Claude\claude_desktop_config.json" -ItemType File
```

## Testing Your Installation

### Test 1: Node.js and npm
```powershell
node --version    # Should show v18.x.x or v20.x.x
npm --version     # Should show 9.x.x or 10.x.x
```

### Test 2: MCP GitHub Server
```powershell
# Test the server directly
npx @modelcontextprotocol/server-github --help
```

### Test 3: Environment Variable
```powershell
# Check if token is set
echo $env:GITHUB_TOKEN
```

### Test 4: Claude Desktop Integration
1. Open Claude Desktop
2. Type: "Can you list the files in my GitHub repository?"
3. Should see MCP connection working

## Hardware Requirements

### Minimum System Requirements
- **OS:** Windows 10 version 1903 or Windows 11
- **RAM:** 4GB (8GB recommended)
- **Storage:** 500MB for Node.js + dependencies
- **Processor:** Any modern x64 processor
- **Network:** Internet connection for npm packages

### Performance Notes
- Node.js is lightweight (~50MB)
- MCP server uses minimal resources
- No impact on Claude Desktop performance

## Security on Windows

### Best Practices
1. **Use environment variables** for tokens (not hardcoded)
2. **Regular token rotation** (every 90 days)
3. **Minimum permissions** on GitHub token
4. **Windows Credential Manager** can store tokens securely

### Token Storage Options
```powershell
# Option 1: Environment Variable (Recommended)
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "token", "User")

# Option 2: Windows Credential Manager
# Store via Control Panel → Credential Manager
```

## What's Next After Setup

Once installed, you'll be able to:
- **Manage your home-automation-project repo** directly through Claude
- **Update session states** automatically
- **Commit OpenWrt configurations** as you develop them
- **Create branches** for different implementation phases
- **Automate documentation** updates

The integration works seamlessly on Windows and will significantly streamline your project workflow!