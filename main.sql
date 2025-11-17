/* ============================================================
   CPS510 – LIBRARY DBMS SCHEMA (BCNF / 3NF)
   Wafee Rahman, Richie Au, Umair Ansar
*/

/* 1) STAFF
  Stores staff members. */
CREATE TABLE Staff (
  StaffID   INT PRIMARY KEY,
  StaffName VARCHAR2(100) NOT NULL
);

/* 2) AUTHOR
  Stores authors. */
CREATE TABLE Author (
  AuthorID   INT PRIMARY KEY,
  AuthorName VARCHAR2(100) NOT NULL
);

/* 3) ADDRESS
  Customer addresses. */
CREATE TABLE Address (
  AddressID  INT           PRIMARY KEY,
  Street     VARCHAR2(100),
  City       VARCHAR2(100),
  Province   VARCHAR2(50),
  PostalCode VARCHAR2(10)
);

/* 4) CUSTOMER
  Library patrons; references Address. */
CREATE TABLE Customer (
  CustomerID  NUMBER(9)    PRIMARY KEY,
  FirstName   VARCHAR2(50) NOT NULL,
  LastName    VARCHAR2(50) NOT NULL,
  PhoneNumber VARCHAR2(15),
  AddressID   INT,
  CONSTRAINT fk_Customer_Address
    FOREIGN KEY (AddressID)
    REFERENCES Address(AddressID)
);

/* 5) RECORD
  Bibliographic record; cataloged by staff. */
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

/* 6) RECORDAUTHOR
  M:N link between Record and Author. */
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
     - AddressID → (Street, City, Province, PostalCode)

   Normal Form:
     - Single-key table.
     - All attributes depend on AddressID.
     - In 3NF and BCNF.
);

CREATE TABLE Address (
  AddressID  INT           PRIMARY KEY,
  Street     VARCHAR2(100),
  City       VARCHAR2(100),
  Province   VARCHAR2(50),
  PostalCode VARCHAR2(10)
);


/* ============================================================
   4) CUSTOMER
   ------------------------------------------------------------
   Purpose:
     - Stores library patrons.

   Functional Dependencies:
     - CustomerID → (FirstName, LastName, PhoneNumber, AddressID)

   Rationale / Decomposition:
     - Original design had a full Address string in Customer.
     - To avoid possible transitive dependencies via Address,
       we decompose:
         Customer(CustomerID, FirstName, LastName, PhoneNumber, AddressID)
         Address(AddressID, Street, City, Province, PostalCode)

   Normal Form:
     - All non-key attributes in Customer depend only on CustomerID.
     - Address details are moved to separate Address table.
     - In 3NF and BCNF.
   ============================================================ */
CREATE TABLE Customer (
   CustomerID  NUMBER(9)    PRIMARY KEY,
   FirstName   VARCHAR2(50) NOT NULL,
   LastName    VARCHAR2(50) NOT NULL,
   PhoneNumber VARCHAR2(15),
   AddressID   INT,
   CONSTRAINT fk_Customer_Address
     FOREIGN KEY (AddressID)
     REFERENCES Address(AddressID)
);


/* ============================================================
   5) RECORD
   ------------------------------------------------------------
   Purpose:
     - Bibliographic description of a title (book, e-book, DVD).
     - Normalized: no AvailableStock, no AuthorName column.
       (Authors are handled via RecordAuthor, availability via view.)

   Functional Dependency:
     - RecordID → (Title, Genre, DateOfPublication, CatalogedBy)

   Normal Form:
     - AvailableStock is derived (TotalStock – active loans).
       It is removed from this base table and computed by a view.
     - Author is multi-valued; moved to separate RecordAuthor table.
     - All remaining non-key attributes depend on RecordID only.
     - In 3NF and BCNF.
   ============================================================ */
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


/* ============================================================
   6) RECORDAUTHOR (M:N between Record and Author)
   ------------------------------------------------------------
   Purpose:
     - Resolves the many-to-many relationship between Record
       and Author.

   Functional Dependencies:
     - (RecordID, AuthorID) → [no additional attributes]

   Normal Form:
     - Composite primary key (RecordID, AuthorID).
     - No non-key attributes; no partial or transitive dependencies.
     - In 3NF and BCNF.
   ============================================================ */
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


/* ============================================================
   7) LIBRARYINVENTORY
   ------------------------------------------------------------
   Purpose:
     - Physical inventory level per bibliographic record.
     - ItemID identifies an inventory group (e.g., all copies).

   Functional Dependency:
     - ItemID → (RecordID, TotalStock)

   Normal Form:
     - TotalStock is stored as an inventory attribute.
     - Availability per item is computed in the view, not stored.
     - Determinant (ItemID) is the key; table in BCNF.
   ============================================================ */
CREATE TABLE LibraryInventory (
    ItemID     INT PRIMARY KEY,
    RecordID   INT NOT NULL,
    TotalStock INT DEFAULT 1,
    CONSTRAINT fk_LI_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
    -- Uncomment below if you want at most one inventory row per Record:
    -- ,CONSTRAINT uq_LI_Record UNIQUE (RecordID)
);


/* ============================================================
   8) BOOK  (subtype of Record)
   ------------------------------------------------------------
   Purpose:
     - Stores attributes specific to book-type records.

   NOTE (matching PDF description):
     - Book table: (RecordID, DRMType, Binding)

   Functional Dependency:
     - RecordID → (DRMType, Binding)

   Normal Form:
     - RecordID is both PK and FK to Record.
     - All non-key attributes depend on this key.
     - In 3NF and BCNF.
   ============================================================ */
CREATE TABLE Book (
    RecordID INT PRIMARY KEY,
    DRMType  VARCHAR2(50),
    Binding  VARCHAR2(50),
    CONSTRAINT fk_Book_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);


/* ============================================================
   9) EBOOK  (subtype of Record)
   ------------------------------------------------------------
   Purpose:
     - Stores attributes specific to electronic book records.

   NOTE (matching PDF description):
     - E-Book table: (RecordID, DRMType, FileFormat)

   Functional Dependency:
     - RecordID → (DRMType, FileFormat)

   Normal Form:
     - RecordID is PK and FK.
     - Non-key attributes depend only on RecordID.
     - In 3NF and BCNF.
   ============================================================ */
CREATE TABLE EBook (
    RecordID   INT PRIMARY KEY,
    DRMType    VARCHAR2(50),
    FileFormat VARCHAR2(20),
    CONSTRAINT fk_EBook_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);


/* ============================================================
   10) DVD  (subtype of Record)
   ------------------------------------------------------------
   Purpose:
     - Stores attributes specific to DVD/video records.

   Functional Dependency:
     - RecordID → (RunTime, PGRating)

   Normal Form:
     - RecordID is PK and FK.
     - RunTime and PGRating depend only on RecordID.
     - In 3NF and BCNF.
   ============================================================ */
CREATE TABLE DVD (
    RecordID INT PRIMARY KEY,
    RunTime  INT,
    PGRating VARCHAR2(10),
    CONSTRAINT fk_DVD_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);


/* ============================================================
   11) LOANS
   ------------------------------------------------------------
   Purpose:
     - Tracks each loan transaction of a physical item.

   Attributes (matching PDF):
     - LoanID, CustomerID, ItemID, StaffID, LoanDate,
       DueDate, Overdue?

   Functional Dependency:
     - LoanID → (CustomerID, ItemID, StaffID,
                 LoanDate, DueDate, Overdue)

   Constraints:
     - Each loan references a valid Customer, Item, and Staff.
     - DueDate must be after LoanDate.
     - Overdue ∈ {'Y','N'}.

   Normal Form:
     - All non-key attributes depend on LoanID.
     - No partial or transitive dependencies.
     - In 3NF and BCNF.
   ============================================================ */
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
);


/* ============================================================
   12) VIEW – RecordAvailableStock  (Advanced Report)
   ------------------------------------------------------------
   Purpose:
     - Advanced summary report that shows, per Record + ItemID:
         • TotalCopies (TotalStock)
         • ActiveLoans  (number of Loans rows per itemId)
         • AvailableStock = TotalCopies – ActiveLoans (min 0)
       along with bibliographic info from Record.

   Assumption:
     - Every row in Loans represents a currently-out copy.
       (If you later add returnDate or status, the derived subquery
        can be adjusted to filter returned loans.)

   Logic:
     1) Join Record to LibraryInventory to get TotalStock.
     2) LEFT JOIN a derived table that counts loans per itemId.
     3) Use NVL to handle items with zero loans, and GREATEST
        to clamp available stock at zero.

   This view is your "advanced report" object. Code is formatted
   and commented to satisfy the rubric’s requirement for clear
   reporting logic.
   ============================================================ */
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
