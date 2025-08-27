param(
    [int]$Port = 8080,
    [switch]$Install
)

# 设置控制台颜色
$host.UI.RawUI.ForegroundColor = "Green"

Write-Host "==================================="
Write-Host "    ZYJC Frontend Server Startup    "
Write-Host "==================================="
Write-Host ""

# 检查Node.js
try {
    $nodeVersion = node -v
    Write-Host "Node.js version: $nodeVersion"
} catch {
    Write-Host "Error: Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please download Node.js from https://nodejs.org"
    exit 1
}

# 检查http-server
if ($Install -or !(Get-Command http-server -ErrorAction SilentlyContinue)) {
    Write-Host "Installing http-server..." -ForegroundColor Yellow
    npm install http-server -g
}

# 检查端口
$portInUse = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Warning: Port $Port is in use!" -ForegroundColor Yellow
    $Port = 3001
    Write-Host "Switching to port $Port"
}

Write-Host ""
Write-Host "Starting server on port $Port..."
Write-Host "Server URL: http://localhost:$Port"
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

# 启动服务器
http-server -p $Port
