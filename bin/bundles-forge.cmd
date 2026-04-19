@echo off
setlocal

set "ENTRY=%~dp0bundles-forge"

if not exist "%ENTRY%" (
    echo bundles-forge: error: entry point not found: %ENTRY% >&2
    exit /b 1
)

for %%P in (python3 python) do (
    %%P --version >nul 2>&1 && (
        %%P "%ENTRY%" %*
        exit /b %ERRORLEVEL%
    )
)

echo bundles-forge: error: Python 3.9+ required but not found >&2
echo   Tried: python3, python >&2
echo   Install: https://www.python.org/downloads/ >&2
exit /b 1
