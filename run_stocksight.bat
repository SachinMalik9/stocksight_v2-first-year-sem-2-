@echo off
title Stocksight V2 - Launcher
echo ==========================================
echo    STARTING STOCKSIGHT ENGINE (DOCKER)
echo ==========================================

:: 1. Start the Docker containers in the background
echo [+] Building and starting containers...
docker compose up -d --build

:: 2. Wait a few seconds for the API to initialize
echo [+] Waiting for services to wake up...
timeout /t 5 /nobreak > nul

:: 3. Open the dashboard in your default browser
echo [+] Launching dashboard...
start "" "frontend/index.html"

echo ==========================================
echo    ENGINE IS RUNNING IN BACKGROUND
echo ==========================================
echo.
echo To see logs, type: docker compose logs -f
echo To stop everything, type: docker compose down
echo.
pause