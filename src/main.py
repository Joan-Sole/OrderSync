"""
OrderSync

Module:
	main.py
	
Location:
	src\

Description:
	Main entry point for the OrderSync application.

Author:
    Joan Solé
"""

from pathlib import Path
import logging
import time

from core.settings import load_settings
from core.logger import initialise_logger
from core.sqlserver import SqlServerConnection
from core.hyperfile import HyperFileConnection

from repositories.hyperfile_repository import HyperFileRepository
from repositories.sqlserver_repository import SqlServerRepository

from services.synchronization_service import SynchronizationService

def main() -> None:

	# script location /OrderSync/src/main.py  target location /OrderSync
	project_root = Path(__file__).resolve().parents[1]

	# final target location /OrderSync/config
	config_directory = project_root / "config"

#	config_directory.mkdir(parents=True, exist_ok=True)
	config_file = config_directory / "config.yaml"

	settings = load_settings(config_file)

	initialise_logger(settings)
	logger = logging.getLogger(__name__)
	
	with HyperFileConnection(settings) as hyper:
		with SqlServerConnection(settings) as sql:

			source_repository = HyperFileRepository(
				hyper
			)

			destination_repository = SqlServerRepository(
				sql
			)

			synchronization_service = SynchronizationService(
				source_repository,
				destination_repository,
				settings.application.maj_periode,
			)

			stats = synchronization_service.synchronize()
			print(f"Synchronization stats: {stats}")
if __name__ == "__main__":
	main()