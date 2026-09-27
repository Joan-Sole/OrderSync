@echo off
:: Paths
SET WP=C:\WINPARF
SET ORDERSYNC=%WP%\ORDERSYNC
echo =============================================================== 
echo   VALIDATION COMMANDE (MAJ SQLSERVER)  %date%   %time%         
echo =============================================================== 
call %ORDERSYNC%\.venv\scripts\activate.bat    
cd  /d %ORDERSYNC%\src
python database_validator_commande.py --keys NOCDE --fields TYPCDE CFOUR CCOMPTE LIBCDE DTCDE HEURECDE NOCHRONO OBSER MODECDE DTLIVPREVU NBJOURS CDECENTRAL TXREM MTCDE MTRECU MAGCDE MAGLIVR RETOUR_CDE DTREC DTFACT FORMAT_EDI STATUTEDI
call %ORDERSYNC%\.venv\scripts\deactivate.bat  
pause