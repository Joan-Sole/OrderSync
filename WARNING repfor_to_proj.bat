SET basedir=C:\PROJECTS\OrderSync
SET repdir=%basedir%\rep_txt
echo:  WARNING : Do you want to overwrite the project files and folders?
pause
copy %repdir%\database_initializer.py %basedir%\src
copy %repdir%\main.py %basedir%\src
copy %repdir%\hyperfile_repository.py %basedir%\src\repositories
copy %repdir%\sqlserver_repository.py %basedir%\src\repositories
copy %repdir%\commande.py %basedir%\src\models
copy %repdir%\lgcde.py %basedir%\src\models
copy %repdir%\logger.py %basedir%\src\core
copy %repdir%\settings.py %basedir%\src\core
copy %repdir%\exceptions.py %basedir%\src\core
copy %repdir%\sqlserver.py %basedir%\src\core
copy %repdir%\hyperfile.py %basedir%\src\core
copy %repdir%\config.yaml %basedir%\config
copy %repdir%\table_creation.sql %basedir%\sql

