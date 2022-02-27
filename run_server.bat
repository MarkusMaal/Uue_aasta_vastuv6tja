@echo off
:: see skript otsib arvutist Pythoni ja käivitab
:: serveri
setlocal EnableDelayedExpansion
for /f %%p in ('where python') do SET PYTHONPATH=%%p
if "!PYTHONPATH!"=="" (
echo.
echo Python pole arvutisse paigaldatud^^!
echo.
echo Serveri laadimiseks on vaja Python3 installida
echo.
pause
exit /b
)
start "" "!PYTHONPATH!" pyserver.py
if %ERRORLEVEL% NEQ 0 (
	echo Ilmnes viga. Veastaatus: %ERRORLEVEL%
	pause
)