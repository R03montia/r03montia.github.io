@echo off
rem Launch the idle-lock helper with a visible console so startup errors are not hidden.
rem Close this window to stop the helper. pushd handles UNC paths too.
pushd "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py "idle-lock.py"
) else (
  python "idle-lock.py"
)
popd
echo.
echo idle-lock stopped. Press any key to close.
pause >nul
