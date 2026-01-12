# ==========================================
# GPAFP 平台服务启动脚本
# ==========================================

# 设置控制台输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       GPAFP 平台启动脚本 (优化版)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# -------------------------------------------------
# 函数: 停止占用指定端口的进程
# -------------------------------------------------
function Stop-PortProcess {
    param ( [int]$Port, [string]$Name )
    
    Write-Host "[检查] 端口 $Port ($Name)..." -NoNewline -ForegroundColor Yellow
    
    # 获取占用端口的 TCP 连接
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    
    if (-not $connections) {
        Write-Host " 空闲" -ForegroundColor Green
        return
    }

    Write-Host " 占用中，准备清理..." -ForegroundColor Red

    # 收集需要终止的 PID
    $pidsToKill = @{}
    foreach ($conn in $connections) {
        $pid_val = $conn.OwningProcess
        # 跳过系统空闲进程 (0) 和无效 PID
        if ($pid_val -gt 0) {
            $pidsToKill[$pid_val] = $true
        }
    }

    # 执行终止
    foreach ($pid_val in $pidsToKill.Keys) {
        try {
            $process = Get-Process -Id $pid_val -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "       正在停止 PID: $pid_val ..." -ForegroundColor Gray
                Stop-Process -Id $pid_val -Force -ErrorAction SilentlyContinue
            }
        } catch {
            # 忽略权限不足或进程已退出的错误
        }
    }
    
    # 等待释放
    Start-Sleep -Milliseconds 1000
}

# -------------------------------------------------
# 函数: 清理/重置日志文件
# -------------------------------------------------
function Reset-LogFile {
    param ([string]$FilePath)
    
    if (Test-Path $FilePath) {
        try {
            Remove-Item $FilePath -Force -ErrorAction Stop
        } catch {
            Write-Host "[警告] 无法删除 $FilePath (被占用)，尝试清空内容..." -ForegroundColor Yellow
            try {
                Clear-Content $FilePath -ErrorAction SilentlyContinue
            } catch {
                Write-Host "[错误] 无法清理 $FilePath" -ForegroundColor Red
            }
        }
    }
}

# -------------------------------------------------
# 1. 环境准备
# -------------------------------------------------
Write-Host "`n[1/4] 清理环境..." -ForegroundColor Cyan

# 停止旧服务
Stop-PortProcess -Port 8000 -Name "后端服务"
Stop-PortProcess -Port 5173 -Name "前端服务"

# 清理日志
Reset-LogFile "backend.log"
Reset-LogFile "frontend.log"

# -------------------------------------------------
# 2. 检测虚拟环境
# -------------------------------------------------
Write-Host "`n[2/4] 检测运行环境..." -ForegroundColor Cyan
$venvActivate = $null
if (Test-Path ".venv\Scripts\activate.bat") {
    $venvActivate = ".venv\Scripts\activate.bat"
    Write-Host "       使用根目录虚拟环境" -ForegroundColor Green
} elseif (Test-Path "backend\.venv\Scripts\activate.bat") {
    $venvActivate = "backend\.venv\Scripts\activate.bat"
    Write-Host "       使用后端目录虚拟环境" -ForegroundColor Green
} else {
    Write-Host "       [注意] 未找到虚拟环境，使用系统 Python" -ForegroundColor Yellow
}

if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "       未找到 node_modules，正在安装依赖..." -ForegroundColor Yellow
    cmd /c "cd frontend && npm install"
}

# -------------------------------------------------
# 3. 启动后端服务
# -------------------------------------------------
Write-Host "`n[3/4] 启动后端服务..." -ForegroundColor Cyan
Write-Host "       日志: backend.log (含时间戳)" -ForegroundColor Gray

$backendCmd = ""
if ($venvActivate) {
    $backendCmd = "chcp 65001 && cd backend && call ..\$venvActivate && python -m uvicorn app.main:app --reload --port 8000 --no-use-colors --log-config log_conf.yaml > ..\backend.log 2>&1"
} else {
    $backendCmd = "chcp 65001 && cd backend && python -m uvicorn app.main:app --reload --port 8000 --no-use-colors --log-config log_conf.yaml > ..\backend.log 2>&1"
}

Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $backendCmd -WindowStyle Hidden

# -------------------------------------------------
# 4. 启动前端服务
# -------------------------------------------------
Write-Host "`n[4/4] 启动前端服务..." -ForegroundColor Cyan
Write-Host "       日志: frontend.log (含时间戳)" -ForegroundColor Gray

# 构建前端命令：
# 1. 设置 NO_COLOR 禁止 ANSI 颜色代码
# 2. npm run dev 运行服务
# 3. 管道捕获输出，添加时间戳
# 4. 输出到文件
$frontendScriptBlock = {
    Set-Location frontend
    $env:NO_COLOR = '1'
    npm run dev | ForEach-Object { 
        "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $_ 
    } | Out-File -Encoding UTF8 ..\frontend.log
}

# 将脚本块转换为 base64 编码命令，避免复杂的转义问题
$encodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($frontendScriptBlock.ToString()))
Start-Process -FilePath "powershell.exe" -ArgumentList "-WindowStyle Hidden", "-EncodedCommand", $encodedCommand -WindowStyle Hidden

# -------------------------------------------------
# 完成
# -------------------------------------------------
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "       服务已在后台启动成功！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host " 后端地址: http://localhost:8000/docs"
Write-Host " 前端地址: http://localhost:5173"
Write-Host " 日志位置: 项目根目录"
Write-Host "------------------------------------------"
Write-Host " 提示: 关闭此窗口不影响服务运行"
Write-Host "       如需停止，请运行相关停止脚本或手动结束进程"
Write-Host "=========================================="
Start-Sleep -Seconds 3
