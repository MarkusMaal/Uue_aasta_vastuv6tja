@echo off
:: see skript otsib arvutist Pythoni ja käivitab
:: serveri
setlocal EnableDelayedExpansion
for /f %%p in ('where pip') do SET PIPPATH=%%p
if "!PIPPATH!"=="" (
echo.
echo Python ja Pip pole arvutisse paigaldatud^^!
echo.
echo Serveri laadimiseks on vaja Python3 installida
echo.
pause
exit /b
)
"!PIPPATH!" install flask mutagen waitress
if %ERRORLEVEL% NEQ 0 (
	echo Ilmnes viga. Veastaatus: %ERRORLEVEL%
	pause
) else (
	echo Valmis.
	pause
)