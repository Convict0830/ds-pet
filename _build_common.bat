@echo off
rem ============================================================
rem  Shared build pipeline - called by build.bat / build-slim.bat
rem  / build-setup.bat. Do not double-click this file directly.
rem
rem  Arguments: %1 = variant (webm | webm-chat | gif | gif-chat)
rem             %2 = mode    (full | slim)
rem             %3 = setup   (setup | nosetup)
rem
rem  Steps:
rem   [1/3] deps check -> [2/3] frame-sequence material (cached)
rem   -> [3/3] PyInstaller + self-checks + smoke test
rem   -> (optional) Inno Setup single-file installer
rem
rem  Notes:
rem   - First material conversion is one-time (~20-40 min); cached after.
rem   - A running pet with the same exe name is closed automatically.
rem   - The smoke test launches the built exe twice, then closes it.
rem ============================================================
setlocal
cd /d "%~dp0"

set VARIANT=%1
if "%VARIANT%"=="" set VARIANT=webm
set MODE=%2
if "%MODE%"=="" set MODE=full
set WANT_SETUP=%3

if /i "%MODE%"=="slim" (
    set SLIM_SWITCH=-SlimAssets
) else (
    set SLIM_SWITCH=
)

rem Force UTF-8 for the whole build chain, INCLUDING pip: requirements.txt has
rem Chinese comments in UTF-8, and pip on a GBK-locale Windows console would
rem decode it with GBK and crash (UnicodeDecodeError) without this.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo [1/3] Checking build dependencies (fast if already installed)...
python -m pip install -r requirements.txt pyinstaller --disable-pip-version-check -q
if errorlevel 1 goto :fail

echo.
echo [2/3] Preparing frame-sequence material (first run: 20-40 min, then cached)...
python scripts\prepare_frameseq_bundle.py --character shenshen --include random,events
if errorlevel 1 goto :fail

echo.
echo [3/3] PyInstaller build + self-checks + smoke test (3-10 min)...
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_onedir.ps1 -Variant %VARIANT% %SLIM_SWITCH%
if errorlevel 1 goto :fail

if not "%WANT_SETUP%"=="setup" goto :done

rem ---------- single-file installer (Inno Setup 6) ----------
set ISCC=
where iscc >nul 2>nul && set ISCC=iscc
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe
if not defined ISCC if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe
if not defined ISCC (
    echo.
    echo [setup] Inno Setup 6 not found - skipping the installer.
    echo          Install it from https://jrsoftware.org/isdl.php then rerun.
    goto :done
)

for /f "delims=" %%v in ('python -c "import pet; print(pet.__version__)"') do set VERSION=%%v
echo.
echo [setup] Compiling installer with Inno Setup (version %VERSION%)...

if /i "%VARIANT%"=="webm" (
    "%ISCC%" /DMyAppShortName=dsh-pet-standalone-webm /DMyAppExeName=dsh-pet-standalone-webm.exe /DMyAppDir=..\dist-onedir\dsh-pet-standalone-webm /DMyAppId={{ED2590E4-A968-4E8D-B7C4-75DFE012D0E9} "/DMyAppDisplay=dsh-pet-standalone (WebM)" /DMyAppVersion=%VERSION% packaging\dsh-pet.iss
    if errorlevel 1 goto :fail
) else if /i "%VARIANT%"=="webm-chat" (
    "%ISCC%" /DMyAppVersion=%VERSION% packaging\dsh-pet.iss
    if errorlevel 1 goto :fail
) else (
    echo [setup] installer defines not configured for variant "%VARIANT%" - skipped.
    goto :done
)

echo [setup] installer OK.

:done
echo.
echo ============================================================
echo  BUILD OK
echo  Onedir folder : dist-onedir\dsh-pet-standalone-%VARIANT%\
echo  Main exe      : dist-onedir\dsh-pet-standalone-%VARIANT%\dsh-pet-standalone-%VARIANT%.exe
echo  Portable zip  : dist-onedir\dsh-pet-standalone-%VARIANT%-portable.zip
if "%WANT_SETUP%"=="setup" echo  Installer exe : dist-onedir\dsh-pet-standalone-%VARIANT%-setup.exe
echo.
echo  Full bundle = all 106 animations offline (about 1.9 GB).
echo  Slim bundle  = core 11 animations (about 300 MB); extras install
echo                 online via Settings - Pet - Character packs.
echo ============================================================
endlocal
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  BUILD FAILED - scroll up and copy the error message above.
echo ============================================================
endlocal
pause
exit /b 1
