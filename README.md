# CPS510 – Library DBMS (BCNF/3NF)

CLI + GUI Documentation

This repository contains two front-ends for the Oracle Library DBMS:

- `a9cli.py` — Linux CLI that talks to the TMU Oracle server (moon)  
- `a9gui.py` — Tkinter GUI that talks to a local Oracle XE instance

Both use the same BCNF/3NF schema:
Staff, Author, Customer, Record, RecordAuthor, LibraryInventory, Book, EBook, DVD, Loans, RecordAvailableStock (view)

---

## 1. CLI — `a9cli.py` (Linux / TMU Oracle on moon)

### 1.1 Requirements
- Linux shell (e.g., on `moon.scs.ryerson.ca`)
- Python 3 on PATH
- `sqlplus` client installed and on PATH
- Valid Oracle account on TMU server:
    - Host: `oracle.scs.ryerson.ca`
    - Port: `1521`
    - SID: `orcl`

The CLI reads an environment variable named `DB_CONN` to connect.

### 1.2 `db.env` — connection configuration
In the same directory as `a9cli.py`, create `db.env` with:

```bash
# db.env (descriptor style)
# NOTE: keep the DB_CONN on ONE line. Use single quotes to avoid shell expansion.

export DB_CONN='username/password@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=oracle.scs.ryerson.ca)(PORT=1521))(CONNECT_DATA=(SID=orcl)))'
```

Replace:
- `username` → your TMU Oracle username
- `password` → your TMU Oracle password

Important:
- The `export DB_CONN='...'` must be a single line.
- Use single quotes as shown.
- Before using CLI in a shell session: `source db.env`
- Verify: `echo $DB_CONN`

### 1.3 Make the CLI executable
From the directory containing `a9cli.py` and `db.env`:
```bash
chmod u+rwx a9cli.py
```

### 1.4 Running the CLI
After `source db.env`:
```bash
./a9cli.py
```

Expected main menu (example):
```
-----------------------------------------------------------------
Main Menu - Library DBMS (BCNF/3NF)
<CTRL-C anytime to exit>

    M) View Manual / Connection Info
    1) Drop Schema (tables + view)
    2) Create Schema (tables + view)
    3) Seed Data
    4) Run Predefined Demo Queries
    5) Manual SQL Query
    E) End/Exit
-----------------------------------------------------------------
```

Menu options summary:
- M — Manual / Connection Info (shows DB_CONN)
- 1 — Drop schema (tables + view)
- 2 — Create schema (tables + view)
- 3 — Seed demo data (~50+ rows across tables)
- 4 — Run predefined demo/assignment queries
- 5 — Manual SQL: prompts for SQL, runs via `sqlplus`
- E or Ctrl-C — exit

---

## 2. GUI — `a9gui.py` (Tkinter, local Oracle XE)

### 2.1 Requirements
- Python 3
- Tkinter (bundled on Windows)
[- Oracle XE installed locally (e.g., 21c XE)](https://www.oracle.com/ca-en/database/technologies/xe-downloads.html)
[- Oracle Instant Client (Basic or Basic Light)](https://www.oracle.com/ca-en/database/technologies/instant-client/downloads.html)
- Python package `cx_Oracle`:
```bash
pip install cx_Oracle
```

### 2.2 Configure Oracle Instant Client path
Edit `a9gui.py` and set `lib_dir` to your Instant Client path, e.g.:

```python
cx_Oracle.init_oracle_client(
        lib_dir=r"C:\oracle\instantclient_23_3"
)
```
Ensure the directory contains `oci.dll` (Windows) or appropriate shared libs.

### 2.3 Setup Oracle XE & credentials
![GUI Login Page](https://github.com/WafeeRahman/librarydbms/blob/main/Screenshot%202025-11-16%20202143.png)
You need a user with privileges to create tables/views and insert data. On the GUI login provide:
- Username
- Password
- Host (usually `localhost`)
- Port (usually `1521`)
- Service name (e.g., `XE` or `XEPDB1`)
- Optional: Connect as SYSDBA

### 2.4 Running the GUI
From the directory with `a9gui.py`:
```bash
python a9gui.py
```
Login dialog appears; on successful connect the main GUI will show connection status and a log.

### 2.5 GUI Overview
The GUI has three main tabs plus a log panel: Schema, Browse & Edit, SQL Console.

#### 2.5.1 Schema Tab
[GUI Schema Tab](https://github.com/WafeeRahman/librarydbms/blob/main/Screenshot%202025-11-16%20203031.png)
Buttons:
- Create Tables & View — creates the BCNF/3NF tables and view
- Drop Tables & View — drops view and tables in correct order
- Seed Database — inserts demo data (Staff, Author, Customer, Record, RecordAuthor, Inventory, Book, DVD, Loans, etc.)

Note: DATE fields in forms expect `YYYY-MM-DD`.

#### 2.5.2 Browse & Edit Tab
[GUI Edit Tab](https://github.com/WafeeRahman/librarydbms/blob/main/Screenshot%202025-11-16%20202834.png)

Top controls:
- Table/View dropdown (choices: `STAFF`, `AUTHOR`, `CUSTOMER`, `RECORD`, `RECORDAUTHOR`, `LIBRARYINVENTORY`, `BOOK`, `EBOOK`, `DVD`, `LOANS`, `RECORDAVAILABLESTOCK`)

Actions:
- Load — runs `SELECT * FROM <table>` and displays results
- Search — searches textual columns using `LOWER(col) LIKE '%term%'`

Main area: Treeview grid with rows and vertical scrollbar.

Row actions (bottom):
- Add Row — opens a form (one field per column); DATE = `YYYY-MM-DD`; inserts row (disabled for read-only view)
- Edit Row — edit selected row; first column treated as PK, used in WHERE clause. note when editing dates, remove the trailing `0:00:00` to avoid a date error.
- Delete Row — deletes selected row based on first column (PK)
- Refresh — reloads current table/view

`RECORDAVAILABLESTOCK` view is read-only.

#### 2.5.3 SQL Console Tab
[GUI SQL Tab](https://github.com/WafeeRahman/librarydbms/blob/main/Screenshot%202025-11-16%20203010.png)
- Multiline SQL editor
- Execute SQL:
    - If statement begins with `SELECT` (case-insensitive): runs and displays result set
    - Otherwise: executes as non-SELECT, commits, clears results and logs status

#### 2.5.4 Log Panel
Shows connection events, schema actions, seeding progress, errors, and user actions.

---
