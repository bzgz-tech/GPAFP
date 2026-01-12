# 设置控制台输出编码为 UTF-8，防止乱码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       GPAFP 平台启动脚本 (静默模式)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# --- 停止旧服务 ---
Write-Host "[信息] 正在检查运行中的服务..." -ForegroundColor Yellow

function Stop-PortProcess {
    param ( [int]$Port, [string]$Name )
    # 获取占用端口的 TCP 连接
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        # 使用哈希表去重 PID，避免重复处理同一个进程
        $pidsToKill = @{}
        foreach ($conn in $connections) {
            $pid_val = $conn.OwningProcess
            # 跳过系统空闲进程 (PID 0) 和无效 PID
            if ($pid_val -gt 0) {
                $pidsToKill[$pid_val] = $true
            }
        }

        foreach ($pid_val in $pidsToKill.Keys) {
            try {
                $process = Get-Process -Id $pid_val -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "[信息] 正在停止 $Name (PID: $pid_val)..." -ForegroundColor Gray
                    Stop-Process -Id $pid_val -Force -ErrorAction SilentlyContinue
                    # 等待进程完全释放资源
                    Start-Sleep -Milliseconds 500
                }
            } catch {
                # 忽略无法访问的进程错误
            }
        }
    }
}

Stop-PortProcess -Port 8000 -Name "后端服务"
Stop-PortProcess -Port 5173 -Name "前端服务"

# --- 清理日志 ---
Write-Host "[信息] 正在清理日志文件..." -ForegroundColor Yellow
# 增加重试机制，防止文件被占用导致删除失败
function Remove-LogFile {
    param ([string]$FilePath)
    if (Test-Path $FilePath) {
        try {
            Remove-Item $FilePath -Force -ErrorAction Stop
        } catch {
            Write-Host "[警告] 无法删除 $FilePath (可能正被占用)，尝试清空内容..." -ForegroundColor Yellow
            try {
                Clear-Content $FilePath -ErrorAction SilentlyContinue
            } catch {
                # 忽略清空失败
            }
        }
    }
}

Remove-LogFile "backend.log"
Remove-LogFile "frontend.log"

# --- 检测虚拟环境 ---
$venvActivate = $null
if (Test-Path ".venv\Scripts\activate.bat") {
    Write-Host "[信息] 发现根目录虚拟环境。" -ForegroundColor Green
    $venvActivate = ".venv\Scripts\activate.bat"
} elseif (Test-Path "backend\.venv\Scripts\activate.bat") {
    Write-Host "[信息] 发现后端目录虚拟环境。" -ForegroundColor Green
    $venvActivate = "backend\.venv\Scripts\activate.bat"
}

Write-Host ""
Write-Host "[1/2] 正在启动后端服务 (后台)..." -ForegroundColor Yellow
Write-Host "      日志文件: backend.log" -ForegroundColor Gray

if ($venvActivate) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "chcp 65001 && cd backend && call ..\$venvActivate && python -m uvicorn app.main:app --reload --port 8000 --no-use-colors > ..\backend.log 2>&1" -WindowStyle Hidden
} else {
    Write-Host "[警告] 未找到虚拟环境。尝试使用系统 Python..." -ForegroundColor Red
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "chcp 65001 && cd backend && python -m uvicorn app.main:app --reload --port 8000 --no-use-colors > ..\backend.log 2>&1" -WindowStyle Hidden
}

Write-Host "[2/2] 正在启动前端服务 (后台)..." -ForegroundColor Yellow
Write-Host "      日志文件: frontend.log" -ForegroundColor Gray

if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "[信息] 未找到 node_modules。正在安装依赖..." -ForegroundColor Cyan
    cmd /c "cd frontend && npm install"
}
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "chcp 65001 && set NO_COLOR=1 && cd frontend && npm run dev > ..\frontend.log 2>&1" -WindowStyle Hidden

Write-Host ""
Write-Host "成功！服务已在后台启动。" -ForegroundColor Green
Write-Host "------------------------------------------"
Write-Host "后端接口文档: http://localhost:8000/docs"
Write-Host "前端访问地址: http://localhost:5173"
Write-Host "------------------------------------------"
Write-Host ""
Write-Host "日志文件已生成在项目根目录。"
Start-Sleep -Seconds 3
