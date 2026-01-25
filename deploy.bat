@echo off
setlocal enabledelayedexpansion

:: Addon metadata
set REPO_URL=https://github.com/etqangroup2019/KH-TOOLS.git
set BRANCH=main

echo [KH-Tools] Starting Deployment...

:: Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in PATH.
    pause
    exit /b
)

:: Initialize Git if .git folder doesn't exist
if not exist ".git" (
    echo [KH-Tools] Initializing new Git repository...
    git init
    git remote add origin %REPO_URL%
) else (
    :: Ensure remote origin is correct
    git remote set-url origin %REPO_URL%
)

:: Get version from __init__.py (optional but nice)
set VERSION=1.99

:: Add all files
echo [KH-Tools] Staging files...
git add .

:: Commit
set COMMIT_MSG="Release v%VERSION%: Update and Scatter improvements"
echo [KH-Tools] Committing changes with message: %COMMIT_MSG%
git commit -m %COMMIT_MSG%

:: Push
echo [KH-Tools] Pushing to %BRANCH%...
git branch -M %BRANCH%
git push -u origin %BRANCH%

echo [KH-Tools] Deployment Complete!
pause
