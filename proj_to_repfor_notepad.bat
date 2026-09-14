SET basedir=C:\PROJECTS\OrderSync
SET repdir=%basedir%\rep_txt
del %repdir%\*
pause
copy %basedir%\src\database_initializer.py %repdir%
copy %basedir%\src\main.py %repdir%
copy %basedir%\src\repositories\hyperfile_repository.py %repdir%
copy %basedir%\src\repositories\sqlserver_repository.py %repdir%
copy %basedir%\src\models\commande.py %repdir%
copy %basedir%\src\models\lgcde.py %repdir%
copy %basedir%\src\core\logger.py %repdir%
copy %basedir%\src\core\settings.py %repdir%
copy %basedir%\src\core\exceptions.py %repdir%
copy %basedir%\src\core\sqlserver.py %repdir%
copy %basedir%\src\core\hyperfile.py %repdir%
copy %basedir%\config\config.yaml %repdir%
copy %basedir%\sql\table_creation.sql %repdir%

