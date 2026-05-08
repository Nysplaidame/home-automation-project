$out = @()
$out += "=== Tool Verification ==="
$out += ""
$out += "--- ssh ---"
try {
    $sshOutput = & ssh -V 2>&1 | Out-String
    $out += $sshOutput.Trim()
} catch { $out += "ssh ERROR: $_" }
$out += ""
$out += "--- python ---"
try {
    $pyOutput = & python --version 2>&1 | Out-String
    $out += $pyOutput.Trim()
} catch { $out += "python ERROR: $_" }
$out += ""
$out += "--- pwsh ---"
try {
    $pwshOutput = & pwsh --version 2>&1 | Out-String
    $out += $pwshOutput.Trim()
} catch { $out += "pwsh ERROR: $_" }
$out += ""
$out += "--- ssh-keygen ---"
try {
    $kgOutput = & ssh-keygen -V 2>&1 | Out-String
    $out += $kgOutput.Trim()
} catch { $out += "ssh-keygen ERROR: $_" }
$out += ""
$out += "--- IPv4 ---"
$ip = ipconfig | Select-String "IPv4" | Out-String
$out += $ip.Trim()
$out -join "`n" | Set-Content 'D:\Other computers\NOT A COMPUTER\home-automation-project\main\_check.txt' -Encoding UTF8
