#!/usr/bin/env pwsh
# Ticket API 測試執行腳本

param(
    [string]$TestType = "all",  # all, unit, integration, specific
    [string]$Marker = ""        # 特定標記（如 integration）
)

$projectRoot = Get-Location

Write-Host "🧪 Ticket API 測試執行工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

switch ($TestType) {
    "all" {
        Write-Host "`n📋 運行所有測試..." -ForegroundColor Yellow
        python -m pytest tests/ -v --tb=short
    }
    "unit" {
        Write-Host "`n📋 運行單元測試..." -ForegroundColor Yellow
        python -m pytest tests/unit/ -v --tb=short
    }
    "integration" {
        Write-Host "`n📋 運行集成測試..." -ForegroundColor Yellow
        python -m pytest tests/integration/ -v -m integration --tb=short
    }
    "coverage" {
        Write-Host "`n📋 運行帶覆蓋率的測試..." -ForegroundColor Yellow
        python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
        Write-Host "`n✅ 覆蓋率報告已生成: htmlcov/index.html" -ForegroundColor Green
    }
    "router" {
        Write-Host "`n📋 運行路由層測試..." -ForegroundColor Yellow
        python -m pytest tests/unit/routers/ -v --tb=short
    }
    "service" {
        Write-Host "`n📋 運行服務層測試..." -ForegroundColor Yellow
        python -m pytest tests/unit/services/ -v --tb=short
    }
    "quick" {
        Write-Host "`n📋 運行快速測試（服務層 + 路由層）..." -ForegroundColor Yellow
        python -m pytest tests/unit/ -v --tb=short -q
    }
    "smoke" {
        Write-Host "`n📋 運行冒煙測試（首個集成測試）..." -ForegroundColor Yellow
        python -m pytest "tests/integration/test_tickets.py::TestTicketIntegration::test_create_and_retrieve_ticket" -v
    }
    default {
        Write-Host "`n❌ 不支援的測試類型: $TestType" -ForegroundColor Red
        Write-Host "`n支援的類型:" -ForegroundColor Yellow
        Write-Host "  - all: 運行所有測試"
        Write-Host "  - unit: 運行單元測試"
        Write-Host "  - integration: 運行集成測試"
        Write-Host "  - coverage: 運行帶覆蓋率的測試"
        Write-Host "  - router: 運行路由層測試"
        Write-Host "  - service: 運行服務層測試"
        Write-Host "  - quick: 運行快速測試"
        Write-Host "  - smoke: 運行冒煙測試"
        exit 1
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ 測試執行完成！" -ForegroundColor Green
} else {
    Write-Host "`n❌ 測試執行失敗！" -ForegroundColor Red
    exit 1
}
