USE [WINPARF];
GO

-- Primer eliminem la taula filla
IF OBJECT_ID('dbo.LGCDE', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.LGCDE;
END
GO

-- Després eliminem la taula pare
IF OBJECT_ID('dbo.COMMANDE', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.COMMANDE;
END
GO

-- Després eliminem la taula etl_run
IF OBJECT_ID('dbo.ETL_RUN', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.ETL_RUN;
END
GO

-- Després eliminem la taula etl_control
IF OBJECT_ID('dbo.ETL_CONTROL', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.ETL_CONTROL;
END
GO