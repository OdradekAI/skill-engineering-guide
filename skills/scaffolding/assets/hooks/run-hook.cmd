@REM ================================================================
@REM Polyglot hook runner for Windows
@REM This file is valid as both a .cmd batch script and a bash script.
@REM On Windows: runs via cmd.exe, delegates to Git Bash if available.
@REM On Unix: the @REM lines are comments, bash block runs directly.
@REM ================================================================
@echo off

REM --- Windows (.cmd) path ---
setlocal enabledelayedexpansion

set "HOOK_NAME=%~1"
if "%HOOK_NAME%"=="" (
    echo usage: run-hook.cmd ^<hook-name^> >&2
    exit /b 1
)

set "SCRIPT_DIR=%~dp0"
set "HOOK_PATH=%SCRIPT_DIR%%HOOK_NAME%"

REM Try Git Bash first
where git >nul 2>nul
if %errorlevel% equ 0 (
    for /f "delims=" %%G in ('where git') do set "GIT_EXE=%%G"
    for %%G in ("!GIT_EXE!") do set "GIT_DIR=%%~dpG"
    set "BASH_EXE=!GIT_DIR!..\bin\bash.exe"
    if exist "!BASH_EXE!" (
        "!BASH_EXE!" "%HOOK_PATH%" %*
        exit /b !errorlevel!
    )
)

REM No Git Bash available — exit cleanly so plugin still loads
exit /b 0

REM --- Unix (bash) path — everything below here runs on Unix ---
: '
'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_NAME="${1:?usage: run-hook.cmd <hook-name>}"
shift
exec "$SCRIPT_DIR/$HOOK_NAME" "$@"
