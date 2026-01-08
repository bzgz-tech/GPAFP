$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       GPAFP 平台启动脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 切换到脚本所在目录 (由于使用 Invoke-Expression，直接使用当前目录)
# Set-Location $PSScriptRoot 

# 检测虚拟环境
$venvActivate = $null
if (Test-Path ".venv\Scripts\activate.bat") {
    Write-Host "[信息] 发现根目录虚拟环境。" -ForegroundColor Green
    $venvActivate = ".venv\Scripts\activate.bat"
} elseif (Test-Path "backend\.venv\Scripts\activate.bat") {
    Write-Host "[信息] 发现后端目录虚拟环境。" -ForegroundColor Green
    $venvActivate = "backend\.venv\Scripts\activate.bat"
}

Write-Host ""
Write-Host "[1/2] 正在启动后端服务..." -ForegroundColor Yellow

if ($venvActivate) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "chcp 65001 && cd backend && call ..\$venvActivate && python -m uvicorn app.main:app --reload --port 8000 --no-use-colors" -WindowStyle Normal
} else {
    Write-Host "[警告] 未找到虚拟环境。尝试使用系统 Python..." -ForegroundColor Red
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "chcp 65001 && cd backend && python -m uvicorn app.main:app --reload --port 8000 --no-use-colors" -WindowStyle Normal
}

Write-Host "[2/2] 正在启动前端服务..." -ForegroundColor Yellow
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "[信息] 未找到 node_modules。正在安装依赖..." -ForegroundColor Cyan
    cmd /c "cd frontend && npm install"
}
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd frontend && npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "成功！服务正在新窗口中启动。" -ForegroundColor Green
Write-Host "------------------------------------------"
Write-Host "后端接口文档: http://localhost:8000/docs"
Write-Host "前端访问地址: http://localhost:5173"
Write-Host "------------------------------------------"
Write-Host ""
Read-Host "按回车键退出..."
