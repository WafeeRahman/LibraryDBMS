CPS510 – Library DBMS (BCNF/3NF)

CLI + GUI Documentation

This repository contains two front-ends for your Oracle Library DBMS:

a9cli.py – Linux CLI that talks to the TMU Oracle server on moon

a9gui.py – Tkinter GUI that talks to a local Oracle XE instance

Both use the same BCNF/3NF schema:

Staff, Author, Customer, Record, RecordAuthor, LibraryInventory, Book, EBook, DVD, Loans, RecordAvailableStock (view)

1. CLI – a9cli.py (Linux / TMU Oracle on moon)
1.1. Requirements

You need:

A Linux shell (e.g., on moon.scs.ryerson.ca)

Python 3 available in PATH

sqlplus client installed and in PATH

A valid Oracle account on the TMU Oracle server:

Host: oracle.scs.ryerson.ca

Port: 1521

SID: orcl

The CLI uses an environment variable called DB_CONN to connect.

1.2. db.env – connection configuration

In the same directory as a9cli.py, create a file called db.env with the following content:

# db.env  (descriptor style)
# NOTE: keep the DB_CONN on ONE line. Use single quotes to avoid shell expansion.

export DB_CONN='username/password@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=oracle.scs.ryerson.ca)(PORT=1521))(CONNECT_DATA=(SID=orcl)))'


Replace:

username → your TMU Oracle username

password → your TMU Oracle password

Important:

export DB_CONN='...' must be one single line.

Use single quotes '...' exactly as shown.

Before using the CLI in any shell session, you must load this file:

source db.env


You can verify it with:

echo $DB_CONN

1.3. Make the CLI executable

From the directory containing a9cli.py and db.env:

chmod u+rwx a9cli.py


This gives you execute permissions on the script.

1.4. Running the CLI

In a shell where you’ve already done source db.env, run:

./a9cli.py


You should see:

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


Menu options:

M – Manual / Connection Info
Show a short help message and display the current DB_CONN string.

1 – Drop Schema
Drops all Library DBMS tables and the RecordAvailableStock view (if they exist).

2 – Create Schema
Creates all tables and the RecordAvailableStock view (BCNF/3NF schema).

3 – Seed Data
Inserts ~50+ demo rows across:

Staff

Author

Customer

Record

RecordAuthor

LibraryInventory

Book

DVD

Loans

4 – Run Predefined Demo Queries
Runs assignment/demo queries to showcase:

Joins across Record, Author, Inventory, Loans

Availability logic from the RecordAvailableStock view

Typical reporting-style queries

5 – Manual SQL Query
Prompts you for a SQL statement, passes it to sqlplus using the DB_CONN environment variable, and prints the output.

E – Exit
Exits the CLI.

You can use CTRL-C at any time to terminate the program.

2. GUI – a9gui.py (Tkinter, local Oracle XE)

The GUI connects to a local Oracle XE instance using cx_Oracle and Oracle Instant Client.
It is intended to run on your own machine (e.g., Windows) with Oracle XE installed.

2.1. Requirements

You need:

Python 3

Tkinter (bundled with standard Python on Windows)

Oracle XE installed locally (e.g., 21c Express Edition)

Oracle Instant Client (Basic or Basic Light package)

Python package cx_Oracle:

pip install cx_Oracle

2.2. Configure Oracle Instant Client path

In a9gui.py you will see a line like:

cx_Oracle.init_oracle_client(
    lib_dir=r"D:\Chrome Downloads\instantclient-basic-windows.x64-23.9.0.25.07\instantclient_23_9"
)


You must change lib_dir to the absolute path where your Instant Client is installed. For example:

cx_Oracle.init_oracle_client(
    lib_dir=r"C:\oracle\instantclient_23_3"
)


or

cx_Oracle.init_oracle_client(
    lib_dir="C:\\oracle\\instantclient_23_3"
)


Make sure that directory contains files like oci.dll (on Windows).

2.3. Setup Oracle XE & credentials

Install Oracle XE and create / know a user with privileges to create tables and views, and insert data.
You will need:

Username (e.g., system or your own schema user)

Password

Host (usually localhost)

Port (usually 1521)

Service name

Often XE or XEPDB1, depending on your XE configuration

These are entered on the GUI’s login screen.

2.4. Running the GUI

From the directory containing a9gui.py:

python a9gui.py


On startup:

A login window appears, where you must enter the Oracle XE connection info:

Username

Password

Host

Port

Service Name

Optional checkbox: “Connect as SYSDBA”

After clicking Connect:

If successful, the main GUI appears.

The status bar shows something like:
Connected as myuser@localhost/XE

The log section at the bottom prints connection details and Oracle version.

2.5. GUI Overview

The GUI is organized into three tabs: Schema, Browse & Edit, and SQL Console, plus a log panel at the bottom.

2.5.1. Schema Tab

Buttons:

Create Tables & View
Creates all Library DBMS tables and the RecordAvailableStock view.

Drop Tables & View
Drops the view and all schema tables in the correct dependency order.

Seed Database
Inserts demo data:

10 Staff rows

10 Authors

10 Customers

18+ Book records (with Inventory + Book subtype)

2 DVD records (with Inventory + DVD subtype)

15 Loan records

Info label:

Reminds you that DATE fields in forms (Add/Edit) expect YYYY-MM-DD format.

2.5.2. Browse & Edit Tab

Top controls:

Table / View dropdown
Choose from:

STAFF

AUTHOR

CUSTOMER

RECORD

RECORDAUTHOR

LIBRARYINVENTORY

BOOK

EBOOK

DVD

LOANS

RECORDAVAILABLESTOCK (view)

Load
Executes SELECT * FROM <chosen table> and loads results into a Treeview grid.

Search
Text input + “Go” button.
Searches all textual columns (CHAR/VARCHAR/CLOB) in the currently selected table using:

LOWER(col) LIKE '%term%'


Main area:

Treeview showing rows of the selected table/view, with a vertical scrollbar.

Bottom row action buttons:

Add Row

Opens a form with one field per column (based on USER_TAB_COLUMNS metadata).

DATE columns must be typed as YYYY-MM-DD.

Inserts the row via INSERT INTO ... and refreshes the table on success.

Disabled for the RECORDAVAILABLESTOCK view (view is treated as read-only).

Edit Row

Requires a selected row in the Treeview.

Displays a form with current values pre-filled.

The first column (assumed PK) is disabled and used in the WHERE clause.

Saves changes via UPDATE ... WHERE PK = ....

Delete Row

Requires a selected row.

Confirms, then deletes based on the first column (assumed PK).

RECORDAVAILABLESTOCK cannot be edited or deleted (read-only).

Refresh

Reloads the current table/view from the database.

2.5.3. SQL Console Tab

Multiline text area to type any SQL statement.

Execute SQL button:

If the text begins with SELECT (case-insensitive):

Executes it and displays the result set in a Treeview grid.

Otherwise:

Executes the statement as a non-SELECT (e.g., INSERT, UPDATE, DELETE, CREATE, etc.).

Commits the transaction.

Clears the result grid and updates the status/log.

This tab is useful for one-off debugging and running arbitrary queries without leaving the GUI.

2.5.4. Log Panel

At the bottom of the window:

Shows a rolling log of actions:

Connection events

Table/view creation/dropping

Seeding progress

Errors returned by Oracle

Browse, search, and console actions

Helpful for debugging and for demonstrating what operations were performed.

3. Quick Reference / TL;DR
CLI (a9cli.py) – TMU Oracle on moon

In your CLI repo folder, create db.env:

export DB_CONN='username/password@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=oracle.scs.ryerson.ca)(PORT=1521))(CONNECT_DATA=(SID=orcl)))'


Make the script executable:

chmod u+rwx a9cli.py


Each time you open a new shell to use it:

source db.env
./a9cli.py


Use the menu options to:

Drop schema

Create schema

Seed data

Run demo queries

Execute manual SQL

GUI (a9gui.py) – Local Oracle XE

Install Oracle XE and Instant Client.

Install Python dependencies:

pip install cx_Oracle


Edit a9gui.py and set the correct Instant Client path in:

cx_Oracle.init_oracle_client(lib_dir=...)


Run:

python a9gui.py


Use the login dialog to connect with your local XE credentials.

Use the GUI tabs to:

Create/drop schema

Seed data

Browse, search, add, edit, and delete rows

Run ad-hoc SQL queries

You now have a complete Library DBMS demo with both a Linux CLI (against TMU’s Oracle server) and a Tkinter GUI (against local Oracle XE), sharing the same BCNF/3NF schema and seed data.