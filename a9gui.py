import tkinter as tk
from tkinter import ttk, messagebox
import cx_Oracle


# CPS510 – Library DBMS GUI
#   Schema in 3NF / BCNF with:
#   Staff, Author, Address, Customer, Record, RecordAuthor,
#   LibraryInventory, Book, EBook, DVD, Loans, RecordAvailableStock
#
#   Wafee Rahman, Richie Au, Umair Ansar


connection = None
cursor = None
oracle_client_initialized = False  # ensure init_oracle_client only once

TABLE_NAMES = [
    "STAFF",
    "AUTHOR",
    "ADDRESS",
    "CUSTOMER",
    "RECORD",
    "RECORDAUTHOR",
    "LIBRARYINVENTORY",
    "BOOK",
    "EBOOK",
    "DVD",
    "LOANS",
    "RECORDAVAILABLESTOCK",  # view
]

current_table = None
current_columns = []  # column names in the table Treeview



# STATUS + LOG

def set_status(msg):
    status_var.set(msg)


def log(msg):
    log_text.configure(state="normal")
    log_text.insert("end", msg + "\n")
    log_text.see("end")
    log_text.configure(state="disabled")



# LOGIN DIALOG (runs once on startup)

def show_login_dialog(root):
    """
    Show a modal login dialog.
    On successful login, sets global connection + cursor and closes the dialog.
    On cancel before connecting, exits the app.
    """
    global connection, cursor, oracle_client_initialized

    if connection is not None:
        return

    dlg = tk.Toplevel(root)
    dlg.title("Oracle Login")
    dlg.geometry("350x250")
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()

    # Center the dialog over root
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - 175
    y = root.winfo_y() + (root.winfo_height() // 2) - 125
    dlg.geometry(f"+{x}+{y}")

    # Fields
    tk.Label(dlg, text="Username:").grid(row=0, column=0, sticky="e", padx=8, pady=4)
    user_var = tk.StringVar(value="")
    tk.Entry(dlg, textvariable=user_var, width=25).grid(row=0, column=1, padx=8, pady=4)

    tk.Label(dlg, text="Password:").grid(row=1, column=0, sticky="e", padx=8, pady=4)
    pwd_var = tk.StringVar(value="")
    tk.Entry(dlg, textvariable=pwd_var, show="*", width=25).grid(row=1, column=1, padx=8, pady=4)

    tk.Label(dlg, text="Host:").grid(row=2, column=0, sticky="e", padx=8, pady=4)
    host_var = tk.StringVar(value="localhost")
    tk.Entry(dlg, textvariable=host_var, width=25).grid(row=2, column=1, padx=8, pady=4)

    tk.Label(dlg, text="Port:").grid(row=3, column=0, sticky="e", padx=8, pady=4)
    port_var = tk.StringVar(value="1521")
    tk.Entry(dlg, textvariable=port_var, width=25).grid(row=3, column=1, padx=8, pady=4)

    tk.Label(dlg, text="Service name:").grid(row=4, column=0, sticky="e", padx=8, pady=4)
    svc_var = tk.StringVar(value="XE")
    tk.Entry(dlg, textvariable=svc_var, width=25).grid(row=4, column=1, padx=8, pady=4)

    sysdba_var = tk.BooleanVar(value=False)
    tk.Checkbutton(dlg, text="Connect as SYSDBA", variable=sysdba_var).grid(
        row=5, column=0, columnspan=2, pady=4
    )

    def do_connect():
        nonlocal dlg
        global connection, cursor, oracle_client_initialized

        user = user_var.get().strip()
        pwd = pwd_var.get()
        host = host_var.get().strip()
        port = port_var.get().strip()
        svc = svc_var.get().strip()

        if not user or not pwd or not host or not port or not svc:
            messagebox.showwarning("Missing info", "Please fill in all fields.")
            return

        # Initialize Oracle client once
        if not oracle_client_initialized:
            try:
                # TODO: Replace this path with your actual Instant Client directory
                cx_Oracle.init_oracle_client(
                    lib_dir=r"D:\Chrome Downloads\instantclient-basic-windows.x64-23.9.0.25.07\instantclient_23_9"
                )
            except cx_Oracle.ProgrammingError:
                # Already initialized
                pass
            oracle_client_initialized = True

        try:
            dsn = cx_Oracle.makedsn(host, int(port), service_name=svc)
            connect_kwargs = {
                "user": user,
                "password": pwd,
                "dsn": dsn,
                "encoding": "UTF-8",
            }
            if sysdba_var.get():
                connect_kwargs["mode"] = cx_Oracle.SYSDBA

            conn = cx_Oracle.connect(**connect_kwargs)
            cur = conn.cursor()

            connection = conn
            cursor = cur

            set_status(f"Connected as {user}@{host}/{svc}")
            log("Connected to Oracle, version: " + connection.version)

            dlg.grab_release()
            dlg.destroy()
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Connection Error", str(e))
            set_status("Connection failed")
            log("Connection failed: " + str(e))

    def on_cancel():
        # If no connection yet and user cancels, close the whole app
        if connection is None:
            root.destroy()
        dlg.grab_release()
        dlg.destroy()

    btn_frame = tk.Frame(dlg)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

    tk.Button(btn_frame, text="Connect", command=do_connect, width=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancel", command=on_cancel, width=10).pack(side="left", padx=5)

    dlg.protocol("WM_DELETE_WINDOW", on_cancel)
    dlg.wait_window()  # Make it modal



# DDL: CREATE / DROP TABLES & VIEW 
def create_tables():
    if cursor is None:
        messagebox.showwarning("Not Connected", "Connect to the database first.")
        return

    log("Creating tables and view...")
    set_status("Creating tables...")

    ddl_statements = [
        # 1) Staff
        """
        CREATE TABLE Staff (
          StaffID   INT PRIMARY KEY,
          StaffName VARCHAR2(100) NOT NULL
        )
        """,
        # 2) Author
        """
        CREATE TABLE Author (
          AuthorID   INT PRIMARY KEY,
          AuthorName VARCHAR2(100) NOT NULL
        )
        """,
        # 3) Address
        """
        CREATE TABLE Address (
          AddressID  INT           PRIMARY KEY,
          Street     VARCHAR2(100),
          City       VARCHAR2(100),
          Province   VARCHAR2(50),
          PostalCode VARCHAR2(10)
        )
        """,
        # 4) Customer
        """
        CREATE TABLE Customer (
          CustomerID  NUMBER(9)    PRIMARY KEY,
          FirstName   VARCHAR2(50) NOT NULL,
          LastName    VARCHAR2(50) NOT NULL,
          PhoneNumber VARCHAR2(15),
          AddressID   INT,
          CONSTRAINT fk_Customer_Address
            FOREIGN KEY (AddressID)
            REFERENCES Address(AddressID)
        )
        """,
        # 5) Record
        """
        CREATE TABLE Record (
           RecordID          INT           PRIMARY KEY,
           Title             VARCHAR2(255) NOT NULL,
           Genre             VARCHAR2(100),
           DateOfPublication DATE,
           CatalogedBy       INT           NOT NULL,
           CONSTRAINT fk_Record_Staff
              FOREIGN KEY (CatalogedBy)
              REFERENCES Staff(StaffID)
        )
        """,
        # 6) RecordAuthor
        """
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
        )
        """,
        # 7) LibraryInventory
        """
        CREATE TABLE LibraryInventory (
           ItemID     INT PRIMARY KEY,
           RecordID   INT NOT NULL,
           TotalStock INT DEFAULT 1,
           CONSTRAINT fk_LI_Record
              FOREIGN KEY (RecordID)
              REFERENCES Record(RecordID)
        )
        """,
        # 8) Book
        """
        CREATE TABLE Book (
           RecordID INT PRIMARY KEY,
           DRMType  VARCHAR2(50),
           Binding  VARCHAR2(50),
           CONSTRAINT fk_Book_Record
              FOREIGN KEY (RecordID)
              REFERENCES Record(RecordID)
        )
        """,
        # 9) EBook
        """
        CREATE TABLE EBook (
           RecordID   INT PRIMARY KEY,
           DRMType    VARCHAR2(50),
           FileFormat VARCHAR2(20),
           CONSTRAINT fk_EBook_Record
              FOREIGN KEY (RecordID)
              REFERENCES Record(RecordID)
        )
        """,
        # 10) DVD
        """
        CREATE TABLE DVD (
           RecordID INT PRIMARY KEY,
           RunTime  INT,
           PGRating VARCHAR2(10),
           CONSTRAINT fk_DVD_Record
              FOREIGN KEY (RecordID)
              REFERENCES Record(RecordID)
        )
        """,
        # 11) Loans
        """
        CREATE TABLE Loans (
          loanId     NUMBER       PRIMARY KEY,
          customerId NUMBER(9)    NOT NULL,
          itemId     NUMBER       NOT NULL,
          staffId    NUMBER       NOT NULL,
          loanDate   DATE         DEFAULT SYSDATE NOT NULL,
          dueDate    DATE         NOT NULL,
          overdue    CHAR(1)      DEFAULT 'N' CHECK (overdue IN ('Y','N')),

          CONSTRAINT fkLoansCustomer FOREIGN KEY (customerId)
           REFERENCES Customer(CustomerID) ON DELETE CASCADE,

          CONSTRAINT fkLoansItem FOREIGN KEY (itemId)
           REFERENCES LibraryInventory(ItemID) ON DELETE CASCADE,

          CONSTRAINT fkLoansStaff FOREIGN KEY (staffId)
           REFERENCES Staff(StaffID),

          CONSTRAINT chkDueDate CHECK (dueDate > loanDate)
        )
        """,
    ]

    for ddl in ddl_statements:
        try:
            cursor.execute(ddl)
            log("Executed DDL successfully.")
        except cx_Oracle.DatabaseError as e:
            log("Issue creating object (maybe exists): " + str(e))

    view_sql = """
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
      ON al.itemId = li.ItemID
    """

    try:
        cursor.execute(view_sql)
        log("View RecordAvailableStock created/replaced.")
    except cx_Oracle.DatabaseError as e:
        log("Issue creating view: " + str(e))

    connection.commit()
    set_status("Tables and view created")
    log("DDL completed.")


def drop_tables():
    if cursor is None:
        messagebox.showwarning("Not Connected", "Connect to the database first.")
        return

    if not messagebox.askyesno("Confirm", "Drop all Library DBMS tables and view?"):
        return

    log("Dropping view and tables...")
    set_status("Dropping schema...")

    try:
        cursor.execute("DROP VIEW RecordAvailableStock")
        log("View RecordAvailableStock dropped.")
    except cx_Oracle.DatabaseError as e:
        log("Issue dropping view (maybe it doesn't exist): " + str(e))

    tables = [
        "Loans",
        "DVD",
        "EBook",
        "Book",
        "LibraryInventory",
        "RecordAuthor",
        "Record",
        "Customer",
        "Address",
        "Author",
        "Staff",
    ]

    for t in tables:
        try:
            cursor.execute(f"DROP TABLE {t} CASCADE CONSTRAINTS")
            log(f"Table {t} dropped.")
        except cx_Oracle.DatabaseError as e:
            log(f"Issue dropping {t} (maybe it doesn't exist): {e}")

    connection.commit()
    set_status("Schema dropped")
    log("Drop completed.")



# SEED DATA 
def seed_data():
    if cursor is None:
        messagebox.showwarning("Not Connected", "Connect to the database first.")
        return

    log("Seeding data...")
    set_status("Seeding data...")

    # 1) STAFF
    staff_rows = [
        (1, "Alice Johnson"),
        (2, "Bob Martinez"),
        (3, "Carol Singh"),
        (4, "David Chen"),
        (5, "Emma Brown"),
        (6, "Frank Miller"),
        (7, "Grace Park"),
        (8, "Hannah Scott"),
        (9, "Ian Wright"),
        (10, "Julia Roberts"),
    ]
    cursor.executemany("INSERT INTO Staff (StaffID, StaffName) VALUES (:1, :2)", staff_rows)

    # 2) AUTHORS
    author_rows = [
        (1, "George Orwell"),
        (2, "Jane Austen"),
        (3, "J.K. Rowling"),
        (4, "J.R.R. Tolkien"),
        (5, "Agatha Christie"),
        (6, "Stephen King"),
        (7, "Isaac Asimov"),
        (8, "Yuval Noah Harari"),
        (9, "Malcolm Gladwell"),
        (10, "Neil Gaiman"),
    ]
    cursor.executemany("INSERT INTO Author (AuthorID, AuthorName) VALUES (:1, :2)", author_rows)

    # 3) ADDRESS
    address_rows = [
        (1, "123 King St", "Toronto", "ON", "M5H 1A1"),
        (2, "456 Queen St", "Toronto", "ON", "M5V 2B2"),
        (3, "789 Dundas St", "Toronto", "ON", "M5T 1G4"),
        (4, "12 Bloor St", "Toronto", "ON", "M4W 1A8"),
        (5, "34 Spadina Ave", "Toronto", "ON", "M5V 2J4"),
        (6, "56 Yonge St", "Toronto", "ON", "M5E 1G5"),
        (7, "78 Bay St", "Toronto", "ON", "M5J 2N8"),
        (8, "90 College St", "Toronto", "ON", "M5G 1L5"),
        (9, "101 Front St", "Toronto", "ON", "M5J 2X4"),
        (10, "202 King St", "Toronto", "ON", "M5H 3T4"),
    ]
    cursor.executemany(
        """
        INSERT INTO Address (AddressID, Street, City, Province, PostalCode)
        VALUES (:1, :2, :3, :4, :5)
        """,
        address_rows,
    )

    # 4) CUSTOMERS (each linked to an AddressID)
    customer_rows = [
        (1001, "John", "Doe", "4165550001", 1),
        (1002, "Jane", "Smith", "4165550002", 2),
        (1003, "Michael", "Brown", "4165550003", 3),
        (1004, "Sarah", "Lee", "4165550004", 4),
        (1005, "Daniel", "Kim", "4165550005", 5),
        (1006, "Emily", "Wilson", "4165550006", 6),
        (1007, "Kevin", "Nguyen", "4165550007", 7),
        (1008, "Olivia", "Patel", "4165550008", 8),
        (1009, "Liam", "Garcia", "4165550009", 9),
        (1010, "Sophia", "Lopez", "4165550010", 10),
    ]
    cursor.executemany(
        """
        INSERT INTO Customer (CustomerID, FirstName, LastName, PhoneNumber, AddressID)
        VALUES (:1, :2, :3, :4, :5)
        """,
        customer_rows,
    )

    # 5) BOOK RECORDS (physical books – Book with DRMType + Binding)
    book_items = [
        # (RecordID, ItemID, Title, Genre, PubDate, StaffID, AuthorID, DRMType, Binding, TotalStock)
        (1, 101, "1984", "Dystopian", "1949-06-08", 1, 1, "PhysicalCopy", "Paperback", 4),
        (2, 102, "Animal Farm", "Political Satire", "1945-08-17", 1, 1, "PhysicalCopy", "Paperback", 3),
        (3, 103, "Pride and Prejudice", "Romance", "1813-01-28", 2, 2, "PhysicalCopy", "Hardcover", 3),
        (4, 104, "Harry Potter and the Philosopher's Stone", "Fantasy", "1997-06-26", 3, 3, "PhysicalCopy", "Hardcover", 5),
        (5, 105, "Harry Potter and the Chamber of Secrets", "Fantasy", "1998-07-02", 3, 3, "PhysicalCopy", "Paperback", 4),
        (6, 106, "The Hobbit", "Fantasy", "1937-09-21", 4, 4, "PhysicalCopy", "Hardcover", 3),
        (7, 107, "The Fellowship of the Ring", "Fantasy", "1954-07-29", 4, 4, "PhysicalCopy", "Hardcover", 2),
        (8, 108, "Murder on the Orient Express", "Mystery", "1934-01-01", 5, 5, "PhysicalCopy", "Paperback", 3),
        (9, 109, "The Shining", "Horror", "1977-01-28", 6, 6, "PhysicalCopy", "Paperback", 2),
        (10, 110, "IT", "Horror", "1986-09-15", 6, 6, "PhysicalCopy", "Paperback", 2),
        (11, 111, "Foundation", "Science Fiction", "1951-06-01", 7, 7, "PhysicalCopy", "Paperback", 3),
        (12, 112, "I, Robot", "Science Fiction", "1950-12-02", 7, 7, "PhysicalCopy", "Paperback", 3),
        (13, 113, "Sapiens", "Non-Fiction", "2011-01-01", 2, 8, "PhysicalCopy", "Paperback", 4),
        (14, 114, "Homo Deus", "Non-Fiction", "2015-01-01", 2, 8, "PhysicalCopy", "Paperback", 3),
        (15, 115, "Outliers", "Non-Fiction", "2008-11-18", 9, 9, "PhysicalCopy", "Paperback", 2),
        (16, 116, "The Tipping Point", "Non-Fiction", "2000-03-01", 9, 9, "PhysicalCopy", "Paperback", 2),
        (17, 117, "American Gods", "Fantasy", "2001-06-19", 10, 10, "PhysicalCopy", "Paperback", 3),
        (18, 118, "Coraline", "Fantasy", "2002-08-02", 10, 10, "PhysicalCopy", "Paperback", 3),
    ]

    for (
        record_id,
        item_id,
        title,
        genre,
        pub_date,
        staff_id,
        author_id,
        drm_type,
        binding,
        total_stock,
    ) in book_items:
        cursor.execute(
            """
            INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
            VALUES (:record_id, :title, :genre, TO_DATE(:pub_date, 'YYYY-MM-DD'), :staff_id)
            """,
            {
                "record_id": record_id,
                "title": title,
                "genre": genre,
                "pub_date": pub_date,
                "staff_id": staff_id,
            },
        )

        cursor.execute(
            """
            INSERT INTO RecordAuthor (RecordID, AuthorID)
            VALUES (:record_id, :author_id)
            """,
            {"record_id": record_id, "author_id": author_id},
        )

        cursor.execute(
            """
            INSERT INTO LibraryInventory (ItemID, RecordID, TotalStock)
            VALUES (:item_id, :record_id, :total_stock)
            """,
            {
                "item_id": item_id,
                "record_id": record_id,
                "total_stock": total_stock,
            },
        )

        cursor.execute(
            """
            INSERT INTO Book (RecordID, DRMType, Binding)
            VALUES (:record_id, :drm_type, :binding)
            """,
            {
                "record_id": record_id,
                "drm_type": drm_type,
                "binding": binding,
            },
        )

    # 6) DVD RECORDS
    dvd_items = [
        # (RecordID, ItemID, Title, Genre, PubDate, StaffID, AuthorID, RunTime, Rating, TotalStock)
        (19, 119, "Inception", "Sci-Fi Movie", "2010-07-16", 4, 10, 148, "PG-13", 5),
        (20, 120, "The Matrix", "Sci-Fi Movie", "1999-03-31", 4, 7, 136, "R", 5),
    ]

    for (
        record_id,
        item_id,
        title,
        genre,
        pub_date,
        staff_id,
        author_id,
        runtime,
        rating,
        total_stock,
    ) in dvd_items:
        cursor.execute(
            """
            INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
            VALUES (:record_id, :title, :genre, TO_DATE(:pub_date, 'YYYY-MM-DD'), :staff_id)
            """,
            {
                "record_id": record_id,
                "title": title,
                "genre": genre,
                "pub_date": pub_date,
                "staff_id": staff_id,
            },
        )

        cursor.execute(
            """
            INSERT INTO RecordAuthor (RecordID, AuthorID)
            VALUES (:record_id, :author_id)
            """,
            {"record_id": record_id, "author_id": author_id},
        )

        cursor.execute(
            """
            INSERT INTO LibraryInventory (ItemID, RecordID, TotalStock)
            VALUES (:item_id, :record_id, :total_stock)
            """,
            {
                "item_id": item_id,
                "record_id": record_id,
                "total_stock": total_stock,
            },
        )

        cursor.execute(
            """
            INSERT INTO DVD (RecordID, RunTime, PGRating)
            VALUES (:record_id, :runtime, :rating)
            """,
            {
                "record_id": record_id,
                "runtime": runtime,
                "rating": rating,
            },
        )

    # 7) EBOOK RECORDS (purely digital; good for exploring EBook + subtype)
    ebook_items = [
        # (RecordID, ItemID, Title, Genre, PubDate, StaffID, AuthorID, DRMType, FileFormat, TotalStock)
        (21, 201, "Digital Fortress", "Thriller", "1998-02-01", 1, 6, "AdobeDRM", "EPUB", 50),
        (22, 202, "The Pragmatic Programmer", "Technology", "1999-10-30", 2, 7, "Watermark", "PDF", 50),
    ]

    for (
        record_id,
        item_id,
        title,
        genre,
        pub_date,
        staff_id,
        author_id,
        drm_type,
        file_format,
        total_stock,
    ) in ebook_items:
        cursor.execute(
            """
            INSERT INTO Record (RecordID, Title, Genre, DateOfPublication, CatalogedBy)
            VALUES (:record_id, :title, :genre, TO_DATE(:pub_date, 'YYYY-MM-DD'), :staff_id)
            """,
            {
                "record_id": record_id,
                "title": title,
                "genre": genre,
                "pub_date": pub_date,
                "staff_id": staff_id,
            },
        )

        cursor.execute(
            """
            INSERT INTO RecordAuthor (RecordID, AuthorID)
            VALUES (:record_id, :author_id)
            """,
            {"record_id": record_id, "author_id": author_id},
        )

        cursor.execute(
            """
            INSERT INTO LibraryInventory (ItemID, RecordID, TotalStock)
            VALUES (:item_id, :record_id, :total_stock)
            """,
            {
                "item_id": item_id,
                "record_id": record_id,
                "total_stock": total_stock,
            },
        )

        cursor.execute(
            """
            INSERT INTO EBook (RecordID, DRMType, FileFormat)
            VALUES (:record_id, :drm_type, :file_format)
            """,
            {
                "record_id": record_id,
                "drm_type": drm_type,
                "file_format": file_format,
            },
        )

    # 8) LOANS
    loan_rows = [
        (1, 1001, 101, 1, "2025-11-01", "2025-11-15", "Y"),
        (2, 1002, 104, 2, "2025-11-10", "2025-11-24", "N"),
        (3, 1003, 119, 3, "2025-11-12", "2025-11-26", "N"),
        (4, 1004, 120, 4, "2025-11-05", "2025-11-19", "Y"),
        (5, 1005, 113, 5, "2025-11-08", "2025-11-22", "N"),
        (6, 1006, 114, 1, "2025-11-03", "2025-11-17", "Y"),
        (7, 1007, 115, 2, "2025-11-09", "2025-11-23", "N"),
        (8, 1008, 116, 3, "2025-11-11", "2025-11-25", "N"),
        (9, 1009, 117, 4, "2025-11-02", "2025-11-16", "Y"),
        (10, 1010, 118, 5, "2025-11-04", "2025-11-18", "Y"),
        (11, 1001, 104, 1, "2025-11-13", "2025-11-27", "N"),
        (12, 1002, 105, 2, "2025-11-14", "2025-11-28", "N"),
        (13, 1003, 106, 3, "2025-11-06", "2025-11-20", "Y"),
        (14, 1004, 107, 4, "2025-11-07", "2025-11-21", "N"),
        (15, 1005, 108, 5, "2025-11-15", "2025-11-29", "N"),
    ]
    cursor.executemany(
        """
        INSERT INTO Loans (loanId, customerId, itemId, staffId, loanDate, dueDate, overdue)
        VALUES (:1, :2, :3, :4,
                TO_DATE(:5, 'YYYY-MM-DD'),
                TO_DATE(:6, 'YYYY-MM-DD'),
                :7)
        """,
        loan_rows,
    )

    connection.commit()
    set_status("Seed data inserted")
    log("Seed data inserted.")



# METADATA & QUERY HELPERS

def get_table_metadata(table_name):
    """
    Returns list of (column_name, data_type) for a table/view.
    """
    if cursor is None:
        raise RuntimeError("Not connected")

    cursor.execute(
        """
        SELECT column_name, data_type
        FROM user_tab_columns
        WHERE table_name = :t
        ORDER BY column_id
        """,
        {"t": table_name.upper()},
    )
    return cursor.fetchall()  # [(name, type), ...]


def run_query(sql, params=None):
    if params is None:
        params = {}
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    return cols, rows



# BROWSE TAB: LOAD / ADD / EDIT / DELETE / SEARCH

def load_table():
    global current_table, current_columns
    if cursor is None:
        messagebox.showwarning("Not Connected", "Connect to the database first.")
        return

    table = table_var.get().strip()
    if not table:
        messagebox.showwarning("No Table Selected", "Choose a table or view.")
        return

    try:
        sql = f"SELECT * FROM {table}"
        cols, rows = run_query(sql)
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Error", str(e))
        log(f"Error loading table {table}: {e}")
        return

    current_table = table
    current_columns = cols

    # Clear tree
    for col in tree["columns"]:
        tree.heading(col, text="")
        tree.column(col, width=0)
    tree.delete(*tree.get_children())

    tree["columns"] = cols
    tree["show"] = "headings"

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    for row in rows:
        tree.insert("", "end", values=row)

    set_status(f"Loaded {table}")
    log(f"Loaded table/view: {table}")


def add_row():
    if cursor is None or current_table is None:
        messagebox.showwarning("No Table Loaded", "Load a table first.")
        return

    if current_table.upper() == "RECORDAVAILABLESTOCK":
        messagebox.showinfo("Read-Only", "This view is read-only.")
        return

    metadata = get_table_metadata(current_table)

    form = tk.Toplevel(root)
    form.title(f"Add row to {current_table}")
    form.geometry("400x500")

    entries = {}
    for idx, (col, col_type) in enumerate(metadata):
        lbl = tk.Label(form, text=f"{col} ({col_type})")
        lbl.grid(row=idx, column=0, sticky="w", padx=8, pady=4)
        ent = tk.Entry(form, width=30)
        ent.grid(row=idx, column=1, padx=8, pady=4)
        entries[col] = ent

    def on_save():
        values_expr = []
        binds = {}
        for col, col_type in metadata:
            v = entries[col].get().strip()
            if v == "":
                v = None
            bind_name = col.lower()
            binds[bind_name] = v

            if col_type.upper() == "DATE":
                values_expr.append(f"TO_DATE(:{bind_name}, 'YYYY-MM-DD')")
            else:
                values_expr.append(f":{bind_name}")

        col_list = ", ".join(col for col, _ in metadata)
        val_list = ", ".join(values_expr)
        sql = f"INSERT INTO {current_table} ({col_list}) VALUES ({val_list})"

        try:
            cursor.execute(sql, binds)
            connection.commit()
            log(f"Inserted row into {current_table}")
            form.destroy()
            load_table()
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Insert Error", str(e))
            log("Insert error: " + str(e))

    btn = tk.Button(form, text="Save", command=on_save)
    btn.grid(row=len(metadata), column=0, columnspan=2, pady=10)


def edit_row():
    if cursor is None or current_table is None:
        messagebox.showwarning("No Table Loaded", "Load a table first.")
        return

    if current_table.upper() == "RECORDAVAILABLESTOCK":
        messagebox.showinfo("Read-Only", "This view is read-only.")
        return

    selected = tree.focus()
    if not selected:
        messagebox.showwarning("No Row Selected", "Select a row to edit.")
        return

    values = tree.item(selected, "values")
    metadata = get_table_metadata(current_table)

    form = tk.Toplevel(root)
    form.title(f"Edit row in {current_table}")
    form.geometry("400x500")

    entries = {}
    pk_col, pk_type = metadata[0]
    pk_value_original = values[0]

    for idx, (col, col_type) in enumerate(metadata):
        lbl = tk.Label(form, text=f"{col} ({col_type})")
        lbl.grid(row=idx, column=0, sticky="w", padx=8, pady=4)
        ent = tk.Entry(form, width=30)
        ent.grid(row=idx, column=1, padx=8, pady=4)
        ent.insert(0, values[idx] if values[idx] is not None else "")
        if idx == 0:
            ent.config(state="disabled")  # PK immutable
        entries[col] = ent

    def on_save():
        set_clauses = []
        binds = {}

        # pk binding
        pk_bind = pk_col.lower() + "_pk"
        pk_val = pk_value_original
        binds[pk_bind] = pk_val

        for idx, (col, col_type) in enumerate(metadata):
            if idx == 0:
                continue
            bind_name = col.lower()
            v = entries[col].get().strip()
            if v == "":
                v = None
            binds[bind_name] = v

            if col_type.upper() == "DATE":
                set_clauses.append(f"{col} = TO_DATE(:{bind_name}, 'YYYY-MM-DD')")
            else:
                set_clauses.append(f"{col} = :{bind_name}")

        set_sql = ", ".join(set_clauses)

        if pk_type.upper() == "DATE":
            where_expr = f"{pk_col} = TO_DATE(:{pk_bind}, 'YYYY-MM-DD')"
        else:
            where_expr = f"{pk_col} = :{pk_bind}"

        sql = f"UPDATE {current_table} SET {set_sql} WHERE {where_expr}"

        try:
            cursor.execute(sql, binds)
            connection.commit()
            log(f"Updated row in {current_table}")
            form.destroy()
            load_table()
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Update Error", str(e))
            log("Update error: " + str(e))

    btn = tk.Button(form, text="Save", command=on_save)
    btn.grid(row=len(metadata), column=0, columnspan=2, pady=10)


def delete_row():
    if cursor is None or current_table is None:
        messagebox.showwarning("No Table Loaded", "Load a table first.")
        return

    if current_table.upper() == "RECORDAVAILABLESTOCK":
        messagebox.showinfo("Read-Only", "This view is read-only.")
        return

    selected = tree.focus()
    if not selected:
        messagebox.showwarning("No Row Selected", "Select a row to delete.")
        return

    if not messagebox.askyesno("Confirm Delete", "Delete selected row?"):
        return

    values = tree.item(selected, "values")
    metadata = get_table_metadata(current_table)
    pk_col, pk_type = metadata[0]
    pk_val = values[0]

    pk_bind = pk_col.lower() + "_pk"
    binds = {pk_bind: pk_val}

    if pk_type.upper() == "DATE":
        where_expr = f"{pk_col} = TO_DATE(:{pk_bind}, 'YYYY-MM-DD')"
    else:
        where_expr = f"{pk_col} = :{pk_bind}"

    sql = f"DELETE FROM {current_table} WHERE {where_expr}"

    try:
        cursor.execute(sql, binds)
        connection.commit()
        log(f"Deleted row from {current_table}")
        load_table()
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Delete Error", str(e))
        log("Delete error: " + str(e))


def search_table():
    if cursor is None or current_table is None:
        messagebox.showwarning("No Table Loaded", "Load a table first.")
        return

    term = search_var.get().strip()
    if not term:
        messagebox.showinfo("No Search Term", "Enter a search term.")
        return

    metadata = get_table_metadata(current_table)
    text_cols = [col for col, t in metadata if "CHAR" in t.upper() or "CLOB" in t.upper()]

    if not text_cols:
        messagebox.showinfo("No Text Columns", "No textual columns to search in this table.")
        return

    conditions = [f"LOWER({col}) LIKE :term" for col in text_cols]
    where_sql = " OR ".join(conditions)
    sql = f"SELECT * FROM {current_table} WHERE {where_sql}"

    try:
        cols, rows = run_query(sql, {"term": "%" + term.lower() + "%"})
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Search Error", str(e))
        log("Search error: " + str(e))
        return

    global current_columns
    current_columns = cols

    tree.delete(*tree.get_children())
    tree["columns"] = cols
    tree["show"] = "headings"

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    for row in rows:
        tree.insert("", "end", values=row)

    set_status(f"Search in {current_table}: {len(rows)} rows")
    log(f"Search '{term}' in {current_table}: {len(rows)} row(s) found.")



# SQL CONSOLE TAB

def execute_sql_console():
    if cursor is None:
        messagebox.showwarning("Not Connected", "Connect to the database first.")
        return

    sql = sql_text.get("1.0", "end").strip()
    if not sql:
        messagebox.showinfo("No SQL", "Enter a SQL statement.")
        return

    try:
        cursor.execute(sql)
        if sql.lower().startswith("select"):
            rows = cursor.fetchall()
            cols = [d[0] for d in cursor.description]

            console_tree.delete(*console_tree.get_children())
            console_tree["columns"] = cols
            console_tree["show"] = "headings"

            for col in cols:
                console_tree.heading(col, text=col)
                console_tree.column(col, width=120, anchor="w")

            for row in rows:
                console_tree.insert("", "end", values=row)

            set_status("SQL executed (SELECT)")
            log("SQL console: SELECT executed.")
        else:
            connection.commit()
            console_tree.delete(*console_tree.get_children())
            console_tree["columns"] = []
            console_tree["show"] = ""
            set_status("SQL executed (non-SELECT)")
            log("SQL console: non-SELECT executed.")
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("SQL Error", str(e))
        log("SQL console error: " + str(e))


# BUILD GUI
def build_gui():
    global root, status_var, log_text
    global table_var, tree, search_var
    global sql_text, console_tree

    root = tk.Tk()
    root.title("Library DBMS – Oracle GUI")
    root.geometry("1100x700")

    status_var = tk.StringVar(value="Not connected")
    status_label = tk.Label(root, textvariable=status_var, anchor="w", relief="sunken")
    status_label.pack(fill="x")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # TAB 1: SCHEMA
    schema_frame = ttk.Frame(notebook)
    notebook.add(schema_frame, text="Schema")

    create_btn = ttk.Button(schema_frame, text="Create Tables & View", command=create_tables)
    create_btn.pack(pady=10)

    drop_btn = ttk.Button(schema_frame, text="Drop Tables & View", command=drop_tables)
    drop_btn.pack(pady=5)

    seed_btn = ttk.Button(schema_frame, text="Seed Database", command=seed_data)
    seed_btn.pack(pady=5)

    info_lbl = tk.Label(
        schema_frame,
        text="Actions above operate on the Library schema.\n"
             "Dates in forms should use YYYY-MM-DD for DATE columns.",
        justify="left",
    )
    info_lbl.pack(pady=20)

    # TAB 2: BROWSE
    browse_frame = ttk.Frame(notebook)
    notebook.add(browse_frame, text="Browse & Edit")

    top_browse = ttk.Frame(browse_frame)
    top_browse.pack(fill="x", padx=5, pady=5)

    tk.Label(top_browse, text="Table / View:").pack(side="left")
    table_var = tk.StringVar()
    table_combo = ttk.Combobox(top_browse, textvariable=table_var, values=TABLE_NAMES, width=25)
    table_combo.pack(side="left", padx=5)
    table_combo.set("RECORDAVAILABLESTOCK")

    load_btn = ttk.Button(top_browse, text="Load", command=load_table)
    load_btn.pack(side="left", padx=5)

    # Search controls
    tk.Label(top_browse, text="Search:").pack(side="left", padx=(20, 0))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(top_browse, textvariable=search_var, width=25)
    search_entry.pack(side="left", padx=5)
    search_btn = ttk.Button(top_browse, text="Go", command=search_table)
    search_btn.pack(side="left")

    # Treeview
    tree_frame = ttk.Frame(browse_frame)
    tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

    tree = ttk.Treeview(tree_frame)
    tree.pack(side="left", fill="both", expand=True)

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    vsb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=vsb.set)

    # Row action buttons
    btn_frame = ttk.Frame(browse_frame)
    btn_frame.pack(fill="x", padx=5, pady=5)

    add_btn = ttk.Button(btn_frame, text="Add Row", command=add_row)
    add_btn.pack(side="left", padx=5)

    edit_btn = ttk.Button(btn_frame, text="Edit Row", command=edit_row)
    edit_btn.pack(side="left", padx=5)

    delete_btn = ttk.Button(btn_frame, text="Delete Row", command=delete_row)
    delete_btn.pack(side="left", padx=5)

    refresh_btn = ttk.Button(btn_frame, text="Refresh", command=load_table)
    refresh_btn.pack(side="left", padx=5)

    # TAB 3: SQL CONSOLE
    console_frame = ttk.Frame(notebook)
    notebook.add(console_frame, text="SQL Console")

    upper_console = ttk.Frame(console_frame)
    upper_console.pack(fill="both", expand=True, padx=5, pady=5)

    sql_text = tk.Text(upper_console, height=6)
    sql_text.pack(fill="x", padx=5, pady=5)

    exec_btn = ttk.Button(upper_console, text="Execute SQL", command=execute_sql_console)
    exec_btn.pack(pady=5)

    result_frame = ttk.Frame(console_frame)
    result_frame.pack(fill="both", expand=True, padx=5, pady=5)

    console_tree = ttk.Treeview(result_frame)
    console_tree.pack(side="left", fill="both", expand=True)

    vsb2 = ttk.Scrollbar(result_frame, orient="vertical", command=console_tree.yview)
    vsb2.pack(side="right", fill="y")
    console_tree.configure(yscrollcommand=vsb2.set)

    # BOTTOM LOG PANEL
    log_frame = ttk.Frame(root)
    log_frame.pack(fill="both", expand=False)

    log_label = tk.Label(log_frame, text="Log:")
    log_label.pack(anchor="w")

    log_text = tk.Text(log_frame, height=8, state="disabled")
    log_text.pack(fill="both", expand=True)

    return root


# MAIN

if __name__ == "__main__":
    root = build_gui()
    # Show login dialog immediately; app closes if user cancels before connecting
    show_login_dialog(root)
    try:
        root.mainloop()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
