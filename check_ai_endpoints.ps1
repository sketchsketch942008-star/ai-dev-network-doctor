# AI Endpoint & Developer Network Doctor (Windows PowerShell, zero third-party dependencies)
# Checks local proxy env vars, WinHTTP settings, DNS resolution, IPv4/IPv6 reachability, and TLS latency.

param(
    [int]$TimeoutMs = 5000
)

$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$endpoints = @(
    @{ Name = "OpenAI API";       Host = "api.openai.com";                      Port = 443 },
    @{ Name = "Google Gemini API";Host = "generativelanguage.googleapis.com";   Port = 443 },
    @{ Name = "Anthropic Claude"; Host = "api.anthropic.com";                   Port = 443 },
    @{ Name = "GitHub";           Host = "github.com";                          Port = 443 },
    @{ Name = "npm Registry";     Host = "registry.npmjs.org";                Port = 443 }
)

Write-Host "=== 1. Local Proxy Environment Check ==="
foreach ($var in @("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY")) {
    $val = [Environment]::GetEnvironmentVariable($var)
    if ($val) {
        Write-Host ("  [ENV] {0} = {1}" -f $var, $val)
    }
}

$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
$proxyEnable = (Get-ItemProperty -Path $regPath -Name ProxyEnable).ProxyEnable
$proxyServer = (Get-ItemProperty -Path $regPath -Name ProxyServer).ProxyServer
Write-Host ("  [WinINet] ProxyEnable={0}, ProxyServer={1}" -f ($proxyEnable -as [string]), ($proxyServer -as [string]))

Write-Host "`n=== 2. DNS + TCP + TLS Handshake Latency Probe ==="
foreach ($ep in $endpoints) {
    $h = $ep.Host
    $port = $ep.Port
    $label = $ep.Name

    $ips = @()
    try {
        $addrs = [System.Net.Dns]::GetHostAddresses($h)
        $ips = $addrs | ForEach-Object { $_.IPAddressToString }
    } catch {
        Write-Host ("  [FAIL] {0,-18} ({1}) DNS resolution failed" -f $label, $h)
        continue
    }

    $v4 = ($ips | Where-Object { $_ -notmatch ":" } | Select-Object -First 1)
    $v6 = ($ips | Where-Object { $_ -match ":" } | Select-Object -First 1)

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $tcpOk = $false
    $tlsOk = $false
    $errMsg = ""
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect($h, $port, $null, $null)
        if (-not $iar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)) {
            throw "TCP timeout (${TimeoutMs}ms)"
        }
        $client.EndConnect($iar)
        $tcpOk = $true
        $tcpMs = $sw.ElapsedMilliseconds

        $ssl = New-Object System.Net.Security.SslStream($client.GetStream(), $false)
        $ssl.ReadTimeout = $TimeoutMs
        $ssl.WriteTimeout = $TimeoutMs
        $ssl.AuthenticateAsClient($h)
        $tlsOk = $true
        $totalMs = $sw.ElapsedMilliseconds
        $proto = $ssl.SslProtocol.ToString()
        $ssl.Close()
        Write-Host ("  [OK]   {0,-18} tcp={1,4}ms tls={2,4}ms proto={3} v4={4} v6={5}" -f $label, $tcpMs, $totalMs, $proto, ($v4 -as [string]), ($v6 -as [string]))
    } catch {
        $errMsg = $_.Exception.Message
        Write-Host ("  [WARN] {0,-18} ({1}) error: {2} (v4={3}, v6={4})" -f $label, $h, $errMsg, ($v4 -as [string]), ($v6 -as [string]))
    } finally {
        $client.Close()
    }
}
