SET WP=C:\WINPARF
SET ORDERSYNC=%WP%\ORDERSYNC
cd %ORDERSYNC%

call .venv\Scripts\activate
echo installation des modules python
echo .
python -m pip install --upgrade pip
pip install pyodbc
call .venv\scripts\deactivate.bat 
pause
exit
