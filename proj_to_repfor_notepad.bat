@echo off
SET basedir=C:\PROJECTS\OrderSync
SET repdir=%basedir%\search_sandbox
cd  %repdir%
echo .
echo      VISUAL STUDIO CODE %basedir%   ----------------^>    %repdir%
echo .
pause
del %repdir%\*
copy %basedir%\src\*.py %repdir%
copy %basedir%\src\repositories\*.py %repdir%
copy %basedir%\src\models\*.py %repdir%
copy %basedir%\src\core\*.py %repdir%
copy %basedir%\config\config.yaml %repdir%\config.yaml.py
copy %basedir%\sql\* %repdir%\*.sql.py
copy %basedir%\src\services\*.py %repdir%
copy %basedir%\src\tools\*.py %repdir%
copy %basedir%\.vscode\* %repdir% \*.json.py
copy %basedir%\bat\*  %repdir%\*.bat.py
copy %basedir%\.VSCODE\*  %repdir%\*.json.py

