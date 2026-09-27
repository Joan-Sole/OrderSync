@echo off
:: Paths
SET WP=C:\WINPARF
SET ORDERSYNC=%WP%\ORDERSYNC
echo ===============================================================  
echo   VALIDATION LGCDE (MAJ SQLSERVER  %date%   %time%          
echo =============================================================== 
call %ORDERSYNC%\.venv\scripts\activate.bat     
cd  /d %ORDERSYNC%\src
python database_validator_lgcde.py --fields PAAR PAMP QTESTK QTECDE TXREM TVA QTERECU QTEREFUS QTEFAC MTLIG  
call %ORDERSYNC%\.venv\scripts\deactivate.bat   
pause