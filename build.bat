@echo off
rem ============================================================
rem  dsh-pet personal build - FULL portable webm build
rem  (all 106 animations offline, ~1.9 GB folder / ~1.6 GB zip)
rem
rem  Other targets:
rem      build-slim.bat    slim portable (core 11 clips, ~330 MB zip)
rem      build-setup.bat   slim + single-file setup.exe installer
rem ============================================================
call "%~dp0_build_common.bat" webm full nosetup
