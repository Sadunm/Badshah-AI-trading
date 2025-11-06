@echo off
chcp 65001 >nul
echo ========================================
echo GitHub Push Helper
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Step 1: Create GitHub Repository
echo --------------------------------
echo 1. Go to: https://github.com/new
echo 2. Repository name: BADSHAI-AI-TRADING-MACHINE
echo 3. Choose Private or Public
echo 4. DO NOT initialize with README
echo 5. Click "Create repository"
echo.
pause

echo.
echo Step 2: Enter Your GitHub Details
echo --------------------------------
set /p GITHUB_USERNAME="Enter your GitHub username: "
set /p REPO_NAME="Enter repository name (default: BADSHAI-AI-TRADING-MACHINE): "

if "%REPO_NAME%"=="" set REPO_NAME=BADSHAI-AI-TRADING-MACHINE

echo.
echo Step 3: Adding Remote...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

if errorlevel 1 (
    echo ERROR: Failed to add remote
    pause
    exit /b 1
)

echo.
echo Step 4: Setting main branch...
git branch -M main

echo.
echo Step 5: Pushing to GitHub...
echo.
echo NOTE: You will be asked for credentials:
echo - Username: %GITHUB_USERNAME%
echo - Password: Use Personal Access Token (NOT your password)
echo.
echo To create token: https://github.com/settings/tokens
echo Select scope: repo (all)
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Common issues:
    echo 1. Wrong username or repository name
    echo 2. Need to use Personal Access Token (not password)
    echo 3. Repository not created on GitHub yet
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCCESS! Repository pushed to GitHub!
    echo ========================================
    echo.
    echo Your repository: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo.
)

pause

