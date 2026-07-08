# OrderSync

## Overview

OrderSync is a Python-based ETL application that synchronizes purchase orders from a HyperFile database to a Microsoft SQL Server database.

The synchronization is **unidirectional**:

```
HyperFile  --->  SQL Server
```

The application is designed to run automatically in **batch mode**, typically once per night.

---

# Objectives

The main objectives of OrderSync are:

* Synchronize order headers (`COMMANDE`)
* Synchronize order detail lines (`LGCDE`)
* Preserve referential integrity between both tables
* Synchronize only new or modified records
* Skip completed ("frozen") orders according to business rules
* Validate all incoming data before writing it to SQL Server
* Produce detailed execution and validation logs
* Provide a reliable and maintainable synchronization framework

---

# Technologies

* Python 3.13
* HyperFile ODBC Driver
* Microsoft SQL Server
* pyodbc
* PyYAML
* pytest

---

# Database Architecture

## Source

HyperFile database

Main tables:

* COMMANDE
* LGCDE

## Destination

Microsoft SQL Server

Tables:

* COMMANDE
* LGCDE
* ETL_CONTROL
* ETL_RUN

---

# Synchronization Principles

* One-way synchronization (HyperFile → SQL Server)
* Orders are processed one at a time
* One SQL transaction per order
* Only modified records are updated
* New records are inserted
* Validation is performed before any write operation
* Synchronization statistics are recorded after every execution

---

# Business Rules

## COMMANDE

Primary key

```
NOCDE
```

## LGCDE

Unique key

```
NOCDE
CMARQ
CCATEG
CPROD
```

A product may only appear once within a given order.

---

# Frozen Orders

Orders satisfying the following conditions are considered frozen and are not synchronized anymore:

* TYPCDE = 'V'
* DTCDE older than the configured frozen period (default: 3 months)

---

# Validation Rules

For invalid predefined values:

| Field Type | Stored Value |
| ---------- | ------------ |
| Character  | Blank string |
| Numeric    | 0            |
| Date       | 2000-01-01   |

Every validation error is logged.

Memo fields are truncated to 100 characters.

---

# Project Structure

```
OrderSync/
│
├── src/
│   ├── core/
│   ├── repositories/
│   ├── sync/
│   ├── validators/
│   ├── models/
│   ├── utils/
│   └── main.py
│
├── config/
│
├── sql/
│
├── tests/
│
├── logs/
│
├── docs/
│
├── requirements.txt
│
└── README.md
```

---

# Configuration

Application settings are stored in:

```
config/config.yaml
```

The configuration includes:

* HyperFile connection
* SQL Server connection
* Application version
* Frozen period
* Logging parameters

---

# Logging

Two log files are maintained:

* ordersync.log
* validation.log

Execution statistics are also stored in:

* ETL_CONTROL
* ETL_RUN

---

# Testing

The project includes automated tests covering:

* Configuration loading
* Database connectivity
* Validation rules
* Order synchronization
* Frozen order handling
* Repository classes

---

# Versioning

The project follows Semantic Versioning.

Examples:

```
1.0.0
1.0.1
1.1.0
2.0.0
```

---

# Development Principles

* Python 3.13
* Type hints throughout the project
* Modular architecture
* No duplicated code
* No `SELECT *` statements
* No hard-coded configuration values
* One responsibility per module
* Every sprint produces a runnable application

---

# Current Status

**Version:** 1.0.0

Current phase:

> Infrastructure development

Implemented:

* Project architecture
* SQL Server schema
* ETL control tables
* Python virtual environment
* Git repository
* Configuration module

Next milestone:

* Logging framework
* Custom exceptions
* SQL Server connection
* HyperFile connection
* Infrastructure smoke test
