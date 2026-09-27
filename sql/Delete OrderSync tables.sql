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
