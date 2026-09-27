@echo off
:: Paths
SET WP=C:\WINPARF
SET ORDERSYNC=%WP%\ORDERSYNC
SET repdir=%ORDERSYNC%\research_sandbox
cd  %repdir%
echo .
echo      VISUAL STUDIO CODE %ORDERSYNC%   ----------------^>    %repdir%
echo .
pause
del %repdir%\*
copy %ORDERSYNC%\src\*.py %repdir%
copy %ORDERSYNC%\src\repositories\*.py %repdir%
copy %ORDERSYNC%\src\models\*.py %repdir%
copy %ORDERSYNC%\src\core\*.py %repdir%
copy %ORDERSYNC%\config\config.yaml %repdir%\config.yaml.py
copy %ORDERSYNC%\sql\* %repdir%\*.sql.py
copy %ORDERSYNC%\src\services\*.py %repdir%
copy %ORDERSYNC%\src\tools\*.py %repdir%
copy %ORDERSYNC%\.vscode\* %repdir% \*.json.py
copy %ORDERSYNC%\bat\*  %repdir%\*.bat.py
copy %ORDERSYNC%\.VSCODE\*  %repdir%\*.json.py

