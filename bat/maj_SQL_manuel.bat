@echo off
:: Paths
SET WP=C:\WINPARF
SET ORDERSYNC=%WP%\ORDERSYNC
:: Fichier de log uniquement pour capturer les erreurs de python
echo ===============================================================
echo   EXECUTION ORDERSYNC  %date%   %time%          
echo =============================================================== 
call %ORDERSYNC%\.venv\scripts\activate.bat    
cd  /d %ORDERSYNC%\src
python main.py 
call %ORDERSYNC%\.venv\scripts\deactivate.bat  
pause