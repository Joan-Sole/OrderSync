@echo off
:: Paths
SET WP=C:\WINPARF
SET ORDERSYNC=%WP%\ORDERSYNC
:: Fichier de log uniquement pour capturer les erreurs de python
SET LOGFILE=%ORDERSYNC%\logs\execution.log
echo =============================================================== >> %LOGFILE%
echo   EXECUTION DATABASE_INITIALIZER  %date%   %time%           >> %LOGFILE%
echo =============================================================== >> %LOGFILE%
call %ORDERSYNC%\.venv\scripts\activate.bat     >> %LOGFILE% 2>&1
cd  /d %ORDERSYNC%\src
python database_initializer.py  >> %LOGFILE% 2>&1
call %ORDERSYNC%\.venv\scripts\deactivate.bat   >> %LOGFILE% 2>&1
exit