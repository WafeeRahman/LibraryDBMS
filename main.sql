/* ============================================================
   LIBRARY DBMS – FINAL TABLE DEFINITIONS (BCNF / 3NF)
   Order: Staff, Author, Customer, Record, RecordAuthor,
          LibraryInventory, Book/EBook/DVD, Loans, Views
   ============================================================ */

------------------------------------------------------------
-- 1) STAFF
------------------------------------------------------------
CREATE TABLE Staff (
  StaffID   INT PRIMARY KEY,
  StaffName VARCHAR2(100) NOT NULL
);

------------------------------------------------------------
-- 2) AUTHOR
------------------------------------------------------------
CREATE TABLE Author (
  AuthorID   INT PRIMARY KEY,
  AuthorName VARCHAR2(100) NOT NULL
);

------------------------------------------------------------
-- 3) CUSTOMER
------------------------------------------------------------
CREATE TABLE Customer (
   CustomerID  NUMBER(9)  PRIMARY KEY,
   FirstName   VARCHAR2(50) NOT NULL,
   LastName    VARCHAR2(50) NOT NULL,
   PhoneNumber VARCHAR2(10),
   Address     VARCHAR2(254)
);

------------------------------------------------------------
-- 4) RECORD  (normalized: no AvailableStock, no Author column)
------------------------------------------------------------
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

------------------------------------------------------------
-- 5) RECORDAUTHOR  (M:N between Record and Author)
------------------------------------------------------------
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

------------------------------------------------------------
-- 6) LIBRARY INVENTORY
--    One inventory row per RecordID (ItemID identifies it).
------------------------------------------------------------
CREATE TABLE LibraryInventory (
    ItemID     INT PRIMARY KEY,
    RecordID   INT NOT NULL,
    TotalStock INT DEFAULT 1,
    CONSTRAINT fk_LI_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
    -- Uncomment if you want to enforce 1:1 between Record and Inventory:
    -- ,CONSTRAINT uq_LI_Record UNIQUE (RecordID)
);

------------------------------------------------------------
-- 7) BOOK  (subtype of Record)
------------------------------------------------------------
CREATE TABLE Book (
    RecordID INT PRIMARY KEY,
    ISBN     VARCHAR2(20),
    Binding  VARCHAR2(50),
    CONSTRAINT fk_Book_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);

------------------------------------------------------------
-- 8) EBOOK  (subtype of Record)
------------------------------------------------------------
CREATE TABLE EBook (
    RecordID   INT PRIMARY KEY,
    DRMType    VARCHAR2(50),
    FileFormat VARCHAR2(20),
    CONSTRAINT fk_EBook_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);

------------------------------------------------------------
-- 9) DVD  (subtype of Record)
------------------------------------------------------------
CREATE TABLE DVD (
    RecordID INT PRIMARY KEY,
    RunTime  INT,
    PGRating VARCHAR2(10),
    CONSTRAINT fk_DVD_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);

------------------------------------------------------------
-- 10) LOANS
------------------------------------------------------------
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

------------------------------------------------------------
-- 11) VIEW – RecordAvailableStock
--      Assumption: every row in LOANS is a currently-out copy.
--      AvailableStock = TotalStock - number of loans for that item.
------------------------------------------------------------
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
