@echo off
SET basedir=C:\PROJECTS\OrderSync
SET repdir=%basedir%\rep_txt
cd  %repdir%
echo .
echo      VISUAL STUDIO CODE %basedir%   ----------------^>    %repdir%
echo .
pause
del %repdir%\*
copy %basedir%\src\database_initializer.py %repdir%
copy %basedir%\src\main.py %repdir%
copy %basedir%\src\main_test.py %repdir%
copy %basedir%\src\repositories\hyperfile_repository.py %repdir%
copy %basedir%\src\repositories\sqlserver_repository.py %repdir%
copy %basedir%\src\models\commande.py %repdir%
copy %basedir%\src\models\lgcde.py %repdir%
copy %basedir%\src\core\logger.py %repdir%
copy %basedir%\src\core\settings.py %repdir%
copy %basedir%\src\core\exceptions.py %repdir%
copy %basedir%\src\core\sqlserver.py %repdir%
copy %basedir%\src\core\hyperfile.py %repdir%
copy %basedir%\config\config.yaml %repdir%\config.yaml.py
copy %basedir%\sql\table_creation.sql %repdir%\table_creation.sql.py
copy %basedir%\src\services\synchronization_service.py %repdir%
copy %basedir%\src\tools\database_validator_commande.py %repdir%
copy %basedir%\src\tools\database_validator_lgcde.py %repdir%
copy %basedir%\.vscode\launch.json %repdir% \launch.json.py
copy %basedir%\.vscode\settings.json %repdir%\settings.json.py

