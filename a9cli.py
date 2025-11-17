#!/usr/bin/env python3
"""
Library DBMS – Python CLI (Linux, sqlplus-based, no cx_Oracle)

- Uses DB_CONN env var, same as shell:
    export DB_CONN='user/pass@(DESCRIPTION=...)'

- All logic in this file (like the GUI version):
    * Drop schema
    * Create schema (BCNF version)
    * Seed data (same as GUI, per-record style)
    * Predefined demo queries
    * Manual SQL query option
"""

import os
import sys
import subprocess
import textwrap

# Change this to "sqlplus" if your environment doesn't use sqlplus64
SQLPLUS_CMD = "sqlplus64"



def ensure_db_conn():
    db_conn = os.getenv("DB_CONN", "").strip()
    if not db_conn:
        print("ERROR: DB_CONN environment variable is not set.")
        print("Example:")
        print("  export DB_CONN='w3rahman/09242733@(DESCRIPTION=...)'")
        sys.exit(1)
    return db_conn


def run_sqlplus(sql: str):
    """
    Run a SQL*Plus script and print its output.
    `sql` can contain multiple statements separated by ';' or '/'.
    """
    db_conn = ensure_db_conn()

    script = textwrap.dedent(f"""
    SET PAGESIZE 100
    SET LINESIZE 200
    SET FEEDBACK ON
    SET SERVEROUTPUT ON
    {sql}
    EXIT;
    """)

    try:
        result = subprocess.run(
            [SQLPLUS_CMD, "-s", db_conn],
            input=script.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        print(f"ERROR: {SQLPLUS_CMD} not found on PATH. Is Oracle client installed?")
        sys.exit(1)

    output = result.stdout.decode(errors="ignore")
    print(output)


def pause():
    input("\nPress ENTER to continue... ")


def print_banner():
    print("=================================================================")
    print("| Library DBMS – Oracle CLI (Python + sqlplus, no cx_Oracle)    |")
    print("=================================================================")




def drop_schema():
    """
    Drops the view and tables for the BCNF schema.
    Uses PL/SQL blocks so DROP doesn't error out if objects don't exist.
    """
    sql = """
    -- Drop view (ignore if not exists)
    BEGIN
      EXECUTE IMMEDIATE 'DROP VIEW RecordAvailableStock';
    EXCEPTION
      WHEN OTHERS THEN NULL;
    END;
    /

    -- Drop tables in FK-safe order
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE Loans CASCADE CONSTRAINTS PURGE';        EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE DVD CASCADE CONSTRAINTS PURGE';          EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE EBook CASCADE CONSTRAINTS PURGE';        EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE Book CASCADE CONSTRAINTS PURGE';         EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE LibraryInventory CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE RecordAuthor CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE Record CASCADE CONSTRAINTS PURGE';       EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE Customer CASCADE CONSTRAINTS PURGE';     EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE Author CASCADE CONSTRAINTS PURGE';       EXCEPTION WHEN OTHERS THEN NULL; END;
    /
    BEGIN EXECUTE IMMEDIATE 'DROP TABLE Staff CASCADE CONSTRAINTS PURGE';        EXCEPTION WHEN OTHERS THEN NULL; END;
    /

    COMMIT;
    """

    print("\n[Dropping schema (tables + view)...]")
    run_sqlplus(sql)
    print("[Drop schema completed]\n")



def create_schema():
    sql = """
    -- 1) STAFF
    CREATE TABLE Staff (
      StaffID   INT PRIMARY KEY,
      StaffName VARCHAR2(100) NOT NULL
    );

    -- 2) AUTHOR
    CREATE TABLE Author (
      AuthorID   INT PRIMARY KEY,
      AuthorName VARCHAR2(100) NOT NULL
    );

    -- 3) CUSTOMER
    CREATE TABLE Customer (
       CustomerID  NUMBER(9)  PRIMARY KEY,
       FirstName   VARCHAR2(50) NOT NULL,
       LastName    VARCHAR2(50) NOT NULL,
       PhoneNumber VARCHAR2(10),
       Address     VARCHAR2(254)
    );

    -- 4) RECORD (no AvailableStock; BCNF)
    CREATE TABLE Record (
        RecordID          INT           PRIMARY KEY,
        Title             VARCHAR2(255) NOT NULL,
        Genre             VARCHAR2(100),
        DateOfPublication DATE,
        CatalogedBy       INT           NOT NULL,
        CONSTRAINT fk_Record_Staff
            FOREIGN KEY (CatalogedBy)
            REFERENCES Staff(StaffID)
    );

    -- 5) RECORDAUTHOR (M:N)
    CREATE TABLE RecordAuthor (
        RecordID INT NOT NULL,
        AuthorID INT NOT NULL,
        CONSTRAINT pk_RecordAuthor
            PRIMARY KEY (RecordID, AuthorID),
        CONSTRAINT fk_RA_Record
            FOREIGN KEY (RecordID)
            REFERENCES Record(RecordID),
        CONSTRAINT fk_RA_Author
            FOREIGN KEY (AuthorID)
            REFERENCES Author(AuthorID)
    );

    -- 6) LIBRARY INVENTORY
    CREATE TABLE LibraryInventory (
        ItemID     INT PRIMARY KEY,
        RecordID   INT NOT NULL,
        TotalStock INT DEFAULT 1,
        CONSTRAINT fk_LI_Record
            FOREIGN KEY (RecordID)
            REFERENCES Record(RecordID)
    );

    -- 7) BOOK (subtype of Record)
    CREATE TABLE Book (
        RecordID INT PRIMARY KEY,
        ISBN     VARCHAR2(20),
        Binding  VARCHAR2(50),
        CONSTRAINT fk_Book_Record
            FOREIGN KEY (RecordID)
            REFERENCES Record(RecordID)
    );

    -- 8) EBOOK (subtype of Record)
    CREATE TABLE EBook (
        RecordID   INT PRIMARY KEY,
        DRMType    VARCHAR2(50),
        FileFormat VARCHAR2(20),
        CONSTRAINT fk_EBook_Record
            FOREIGN KEY (RecordID)
            REFERENCES Record(RecordID)
    );

    -- 9) DVD (subtype of Record)
    CREATE TABLE DVD (
        RecordID INT PRIMARY KEY,
        RunTime  INT,
        PGRating VARCHAR2(10),
        CONSTRAINT fk_DVD_Record
            FOREIGN KEY (RecordID)
            REFERENCES Record(RecordID)
    );

    -- 10) LOANS (simplified constraints: all column-level)
    CREATE TABLE Loans (
      loanId     NUMBER       PRIMARY KEY,
      customerId NUMBER(9)    NOT NULL REFERENCES Customer(CustomerID) ON DELETE CASCADE,
      itemId     NUMBER       NOT NULL REFERENCES LibraryInventory(ItemID) ON DELETE CASCADE,
      staffId    NUMBER       NOT NULL REFERENCES Staff(StaffID),
      loanDate   DATE         DEFAULT SYSDATE NOT NULL,
      dueDate    DATE         NOT NULL,
      overdue    CHAR(1)      DEFAULT 'N' CHECK (overdue IN ('Y','N')),
      CHECK (dueDate > loanDate)
    );

    -- 11) VIEW – RecordAvailableStock
    CREATE OR REPLACE VIEW RecordAvailableStock AS
    SELECT
      r.RecordID,
      r.Title,
      r.Genre,
      r.DateOfPublication,
      r.CatalogedBy,
      li.ItemID,
      li.TotalStock                         AS TotalCopies,
      NVL(al.active_loans, 0)               AS ActiveLoans,
      GREATEST(li.TotalStock - NVL(al.active_loans, 0), 0)
        AS AvailableStock
    FROM Record r
    JOIN LibraryInventory li
      ON li.RecordID = r.RecordID
    LEFT JOIN (
      SELECT itemId, COUNT(*) AS active_loans
      FROM Loans
      GROUP BY itemId
    ) al
      ON al.itemId = li.ItemID;

    COMMIT;
    """

    print("\n[Creating schema (tables + view)...]")
    run_sqlplus(sql)
    print("[Create schema completed]\n")



def seed_data():
    sql = """
    -- 1) STAFF (1–10 so all CatalogedBy values are valid)
    INSERT INTO Staff (StaffID, StaffName) VALUES (1, 'Alice Johnson');
    INSERT INTO Staff (StaffID, StaffName) VALUES (2, 'Bob Martinez');
    INSERT INTO Staff (StaffID, StaffName) VALUES (3, 'Carol Singh');
    INSERT INTO Staff (StaffID, StaffName) VALUES (4, 'David Chen');
    INSERT INTO Staff (StaffID, StaffName) VALUES (5, 'Emma Brown');
    INSERT INTO Staff (StaffID, StaffName) VALUES (6, 'Frank Miller');
    INSERT INTO Staff (StaffID, StaffName) VALUES (7, 'Grace Park');
    INSERT INTO Staff (StaffID, StaffName) VALUES (8, 'Hannah Scott');
    INSERT INTO Staff (StaffID, StaffName) VALUES (9, 'Ian Wright');
    INSERT INTO Staff (StaffID, StaffName) VALUES (10,'Julia Roberts');

    -- 2) AUTHORS
    INSERT INTO Author (AuthorID, AuthorName) VALUES (1, 'George Orwell');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (2, 'Jane Austen');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (3, 'J.K. Rowling');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (4, 'J.R.R. Tolkien');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (5, 'Agatha Christie');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (6, 'Stephen King');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (7, 'Isaac Asimov');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (8, 'Yuval Noah Harari');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (9, 'Malcolm Gladwell');
    INSERT INTO Author (AuthorID, AuthorName) VALUES (10,'Neil Gaiman');

    -- 3) CUSTOMERS (10)
    INSERT INTO Customer VALUES (1001, 'John',   'Doe',    '4165550001', '123 King St, Toronto');
    INSERT INTO Customer VALUES (1002, 'Jane',   'Smith',  '4165550002', '456 Queen St, Toronto');
    INSERT INTO Customer VALUES (1003, 'Michael','Brown',  '4165550003', '789 Dundas St, Toronto');
    INSERT INTO Customer VALUES (1004, 'Sarah',  'Lee',    '4165550004', '12 Bloor St, Toronto');
    INSERT INTO Customer VALUES (1005, 'Daniel', 'Kim',    '4165550005', '34 Spadina Ave, Toronto');
    INSERT INTO Customer VALUES (1006, 'Emily',  'Wilson', '4165550006', '56 Yonge St, Toronto');
    INSERT INTO Customer VALUES (1007, 'Kevin',  'Nguyen', '4165550007', '78 Bay St, Toronto');
    INSERT INTO Customer VALUES (1008, 'Olivia', 'Patel',  '4165550008', '90 College St, Toronto');
    INSERT INTO Customer VALUES (1009, 'Liam',   'Garcia', '4165550009', '101 Front St, Toronto');
    INSERT INTO Customer VALUES (1010, 'Sophia','Lopez',  '4165550010', '202 King St, Toronto');

    -- 4) BOOK RECORDS (Record + RecordAuthor + Inventory + Book)
    -- (RecordID, ItemID, Title, Genre, PubDate, StaffID, AuthorID, ISBN, Binding, TotalStock)
    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (1, '1984', 'Dystopian', TO_DATE('1949-06-08','YYYY-MM-DD'), 1);
    INSERT INTO RecordAuthor VALUES (1, 1);
    INSERT INTO LibraryInventory VALUES (101, 1, 4);
    INSERT INTO Book VALUES (1, '9780451524935', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (2, 'Animal Farm', 'Political Satire', TO_DATE('1945-08-17','YYYY-MM-DD'), 1);
    INSERT INTO RecordAuthor VALUES (2, 1);
    INSERT INTO LibraryInventory VALUES (102, 2, 3);
    INSERT INTO Book VALUES (2, '9780451526342', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (3, 'Pride and Prejudice', 'Romance', TO_DATE('1813-01-28','YYYY-MM-DD'), 2);
    INSERT INTO RecordAuthor VALUES (3, 2);
    INSERT INTO LibraryInventory VALUES (103, 3, 3);
    INSERT INTO Book VALUES (3, '9780141439518', 'Hardcover');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (4, 'Harry Potter and the Philosopher''s Stone', 'Fantasy', TO_DATE('1997-06-26','YYYY-MM-DD'), 3);
    INSERT INTO RecordAuthor VALUES (4, 3);
    INSERT INTO LibraryInventory VALUES (104, 4, 5);
    INSERT INTO Book VALUES (4, '9780747532699', 'Hardcover');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (5, 'Harry Potter and the Chamber of Secrets', 'Fantasy', TO_DATE('1998-07-02','YYYY-MM-DD'), 3);
    INSERT INTO RecordAuthor VALUES (5, 3);
    INSERT INTO LibraryInventory VALUES (105, 5, 4);
    INSERT INTO Book VALUES (5, '9780747538493', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (6, 'The Hobbit', 'Fantasy', TO_DATE('1937-09-21','YYYY-MM-DD'), 4);
    INSERT INTO RecordAuthor VALUES (6, 4);
    INSERT INTO LibraryInventory VALUES (106, 6, 3);
    INSERT INTO Book VALUES (6, '9780261102217', 'Hardcover');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (7, 'The Fellowship of the Ring', 'Fantasy', TO_DATE('1954-07-29','YYYY-MM-DD'), 4);
    INSERT INTO RecordAuthor VALUES (7, 4);
    INSERT INTO LibraryInventory VALUES (107, 7, 2);
    INSERT INTO Book VALUES (7, '9780261102354', 'Hardcover');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (8, 'Murder on the Orient Express', 'Mystery', TO_DATE('1934-01-01','YYYY-MM-DD'), 5);
    INSERT INTO RecordAuthor VALUES (8, 5);
    INSERT INTO LibraryInventory VALUES (108, 8, 3);
    INSERT INTO Book VALUES (8, '9780007119318', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (9, 'The Shining', 'Horror', TO_DATE('1977-01-28','YYYY-MM-DD'), 6);
    INSERT INTO RecordAuthor VALUES (9, 6);
    INSERT INTO LibraryInventory VALUES (109, 9, 2);
    INSERT INTO Book VALUES (9, '9780307743657', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (10, 'IT', 'Horror', TO_DATE('1986-09-15','YYYY-MM-DD'), 6);
    INSERT INTO RecordAuthor VALUES (10, 6);
    INSERT INTO LibraryInventory VALUES (110, 10, 2);
    INSERT INTO Book VALUES (10, '9781501142970', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (11, 'Foundation', 'Science Fiction', TO_DATE('1951-06-01','YYYY-MM-DD'), 7);
    INSERT INTO RecordAuthor VALUES (11, 7);
    INSERT INTO LibraryInventory VALUES (111, 11, 3);
    INSERT INTO Book VALUES (11, '9780553293357', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (12, 'I, Robot', 'Science Fiction', TO_DATE('1950-12-02','YYYY-MM-DD'), 7);
    INSERT INTO RecordAuthor VALUES (12, 7);
    INSERT INTO LibraryInventory VALUES (112, 12, 3);
    INSERT INTO Book VALUES (12, '9780553382563', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (13, 'Sapiens', 'Non-Fiction', TO_DATE('2011-01-01','YYYY-MM-DD'), 2);
    INSERT INTO RecordAuthor VALUES (13, 8);
    INSERT INTO LibraryInventory VALUES (113, 13, 4);
    INSERT INTO Book VALUES (13, '9780771038501', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (14, 'Homo Deus', 'Non-Fiction', TO_DATE('2015-01-01','YYYY-MM-DD'), 2);
    INSERT INTO RecordAuthor VALUES (14, 8);
    INSERT INTO LibraryInventory VALUES (114, 14, 3);
    INSERT INTO Book VALUES (14, '9780771038693', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (15, 'Outliers', 'Non-Fiction', TO_DATE('2008-11-18','YYYY-MM-DD'), 9);
    INSERT INTO RecordAuthor VALUES (15, 9);
    INSERT INTO LibraryInventory VALUES (115, 15, 2);
    INSERT INTO Book VALUES (15, '9780316017923', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (16, 'The Tipping Point', 'Non-Fiction', TO_DATE('2000-03-01','YYYY-MM-DD'), 9);
    INSERT INTO RecordAuthor VALUES (16, 9);
    INSERT INTO LibraryInventory VALUES (116, 16, 2);
    INSERT INTO Book VALUES (16, '9780316346627', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (17, 'American Gods', 'Fantasy', TO_DATE('2001-06-19','YYYY-MM-DD'), 10);
    INSERT INTO RecordAuthor VALUES (17, 10);
    INSERT INTO LibraryInventory VALUES (117, 17, 3);
    INSERT INTO Book VALUES (17, '9780380789030', 'Paperback');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (18, 'Coraline', 'Fantasy', TO_DATE('2002-08-02','YYYY-MM-DD'), 10);
    INSERT INTO RecordAuthor VALUES (18, 10);
    INSERT INTO LibraryInventory VALUES (118, 18, 3);
    INSERT INTO Book VALUES (18, '9780380807345', 'Paperback');

    -- 5) DVD RECORDS
    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (19, 'Inception', 'Sci-Fi Movie', TO_DATE('2010-07-16','YYYY-MM-DD'), 4);
    INSERT INTO RecordAuthor VALUES (19, 10);
    INSERT INTO LibraryInventory VALUES (119, 19, 5);
    INSERT INTO DVD VALUES (19, 148, 'PG-13');

    INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
      VALUES (20, 'The Matrix', 'Sci-Fi Movie', TO_DATE('1999-03-31','YYYY-MM-DD'), 4);
    INSERT INTO RecordAuthor VALUES (20, 7);
    INSERT INTO LibraryInventory VALUES (120, 20, 5);
    INSERT INTO DVD VALUES (20, 136, 'R');

    -- 6) LOANS (15 example rows)
    INSERT INTO Loans VALUES (1, 1001, 101, 1, TO_DATE('2025-11-01','YYYY-MM-DD'), TO_DATE('2025-11-15','YYYY-MM-DD'), 'Y');
    INSERT INTO Loans VALUES (2, 1002, 104, 2, TO_DATE('2025-11-10','YYYY-MM-DD'), TO_DATE('2025-11-24','YYYY-MM-DD'), 'N');
    INSERT INTO Loans VALUES (3, 1003, 119, 3, TO_DATE('2025-11-12','YYYY-MM-DD'), TO_DATE('2025-11-26','YYYY-MM-DD'), 'N');
    INSERT INTO Loans VALUES (4, 1004, 120, 4, TO_DATE('2025-11-05','YYYY-MM-DD'), TO_DATE('2025-11-19','YYYY-MM-DD'), 'Y');
    INSERT INTO Loans VALUES (5, 1005, 113, 5, TO_DATE('2025-11-08','YYYY-MM-DD'), TO_DATE('2025-11-22','YYYY-MM-DD'), 'N');
    INSERT INTO Loans VALUES (6, 1006, 114, 1, TO_DATE('2025-11-03','YYYY-MM-DD'), TO_DATE('2025-11-17','YYYY-MM-DD'), 'Y');
    INSERT INTO Loans VALUES (7, 1007, 115, 2, TO_DATE('2025-11-09','YYYY-MM-DD'), TO_DATE('2025-11-23','YYYY-MM-DD'), 'N');
    INSERT INTO Loans VALUES (8, 1008, 116, 3, TO_DATE('2025-11-11','YYYY-MM-DD'), TO_DATE('2025-11-25','YYYY-MM-DD'), 'N');
    INSERT INTO Loans VALUES (9, 1009, 117, 4, TO_DATE('2025-11-02','YYYY-MM-DD'), TO_DATE('2025-11-16','YYYY-MM-DD'), 'Y');
    INSERT INTO Loans VALUES (10,1010, 118, 5, TO_DATE('2025-11-04','YYYY-MM-DD'), TO_DATE('2025-11-18','YYYY-MM-DD'), 'Y');
    INSERT INTO Loans VALUES (11,1001, 104, 1, TO_DATE('2025-11-13','YYYY-MM-DD'), TO_DATE('2025-11-27','YYYY-MM-DD'), 'N');
    INSERT INTO Loans VALUES (12,1002, 105, 2, TO_DATE('2025-11-14','YYYY-MM-DD'), TO_DATE('2025-11-28','YYYY-MM-DD'), 'N');
    INSERT INTO Loans VALUES (13,1003, 106, 3, TO_DATE('2025-11-06','YYYY-MM-DD'), TO_DATE('2025-11-20','YYYY-MM-DD'), 'Y');
    INSERT INTO Loans VALUES (14,1004, 107, 4, TO_DATE('2025-11-07','YYYY-MM-DD'), TO_DATE('2025-11-21','YYYY-MM-DD'), 'N');
    INSERT INTO Loans VALUES (15,1005, 108, 5, TO_DATE('2025-11-15','YYYY-MM-DD'), TO_DATE('2025-11-29','YYYY-MM-DD'), 'N');

    COMMIT;
    """

    print("\n[Seeding data...]")
    run_sqlplus(sql)
    print("[Seed data completed]\n")




def predefined_queries():
    while True:
        print("""
-------------------------------------------
Predefined Queries
-------------------------------------------
1) Show RecordAvailableStock
2) Show all Loans with customer + title
3) Show overdue loans only
4) Show number of records cataloged by each staff
B) Back to main menu
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            sql = """
            SELECT *
            FROM RecordAvailableStock
            ORDER BY RecordID;
            """
            run_sqlplus(sql)

        elif choice == "2":
            sql = """
            SELECT
              l.loanId,
              c.CustomerID,
              c.FirstName || ' ' || c.LastName AS CustomerName,
              r.Title,
              l.loanDate,
              l.dueDate,
              l.overdue
            FROM Loans l
            JOIN Customer c          ON c.CustomerID = l.customerId
            JOIN LibraryInventory li ON li.ItemID    = l.itemId
            JOIN Record r            ON r.RecordID   = li.RecordID
            ORDER BY l.loanId;
            """
            run_sqlplus(sql)

        elif choice == "3":
            sql = """
            SELECT
              l.loanId,
              c.CustomerID,
              c.FirstName || ' ' || c.LastName AS CustomerName,
              r.Title,
              l.loanDate,
              l.dueDate,
              l.overdue
            FROM Loans l
            JOIN Customer c          ON c.CustomerID = l.customerId
            JOIN LibraryInventory li ON li.ItemID    = l.itemId
            JOIN Record r            ON r.RecordID   = li.RecordID
            WHERE l.overdue = 'Y'
            ORDER BY l.dueDate;
            """
            run_sqlplus(sql)

        elif choice == "4":
            sql = """
            SELECT
              s.StaffID,
              s.StaffName,
              COUNT(r.RecordID) AS RecordsCataloged
            FROM Staff s
            LEFT JOIN Record r ON r.CatalogedBy = s.StaffID
            GROUP BY s.StaffID, s.StaffName
            ORDER BY RecordsCataloged DESC, s.StaffName;
            """
            run_sqlplus(sql)

        elif choice in ("B", "b"):
            break

        else:
            print("Invalid choice.")

        pause()




def manual_sql():
    print("""
-------------------------------------------
Manual SQL Console (sqlplus via Python)
-------------------------------------------
Enter a single SQL statement (without the trailing ';').
It will be executed via sqlplus and the output printed.

Examples:
  SELECT * FROM Staff;
  SELECT * FROM RecordAvailableStock;

Leave empty and press ENTER to return to main menu.
""")
    stmt = input("SQL> ").strip()
    if not stmt:
        print("No SQL entered. Returning to main menu.")
        return

    if not stmt.endswith(";"):
        stmt = stmt + ";"

    run_sqlplus(stmt)


def view_manual():
    print("\n=== Manual / Connection Info ===")
    db_conn = os.getenv("DB_CONN", "(not set)")
    print(f"DB_CONN = {db_conn}")
    print("\nThis CLI expects:")
    print("  - Oracle sqlplus/sqlplus64 on PATH")
    print("  - DB_CONN exported in your shell (same as your .sh scripts)")
    pause()


def main_menu():
    while True:
        print("""
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
""")
        choice = input("Choose: ").strip()

        if choice in ("M", "m"):
            view_manual()

        elif choice == "1":
            drop_schema()
            pause()

        elif choice == "2":
            create_schema()
            pause()

        elif choice == "3":
            seed_data()
            pause()

        elif choice == "4":
            predefined_queries()

        elif choice == "5":
            manual_sql()
            pause()

        elif choice in ("E", "e"):
            print("Exiting...")
            break

        else:
            print("Invalid choice.")
            pause()


if __name__ == "__main__":
    print_banner()
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n(Interrupted by user)")
