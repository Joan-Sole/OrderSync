@echo off
:: Paths
SET WP=C:\WINPARF
SET ORDERSYNC=%WP%\ORDERSYNC
:: Fichier de log uniquement pour capturer les erreurs de python
SET LOGFILE=%ORDERSYNC%\logs\execution.log
echo =============================================================== >> %LOGFILE%
echo   EXECUTION ORDERSYNC  %date%   %time%           >> %LOGFILE%
echo =============================================================== >> %LOGFILE%
call %ORDERSYNC%\.venv\scripts\activate.bat     >> %LOGFILE% 2>&1
cd  /d %ORDERSYNC%\src
python main.py  >> %LOGFILE% 2>&1
python database_validator_commande.py --keys NOCDE --fields TYPCDE CFOUR CCOMPTE LIBCDE DTCDE HEURECDE NOCHRONO OBSER MODECDE DTLIVPREVU NBJOURS CDECENTRAL TXREM MTCDE MTRECU MAGCDE MAGLIVR RETOUR_CDE DTREC DTFACT FORMAT_EDI STATUTEDI >> %LOGFILE% 2>&1
python database_validator_lgcde.py --fields TYPCDE PAAR PAMP QTESTK QTECDE TXREM TVA QTERECU QTEREFUS QTEFAC MTLIG  >> %LOGFILE% 2>&1
call %ORDERSYNC%\.venv\scripts\deactivate.bat   >> %LOGFILE% 2>&1
exit