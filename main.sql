/* ============================================================
   CPS510 – LIBRARY DBMS SCHEMA (BCNF / 3NF)
   Wafee Rahman, Richie Au, Umair Ansar
*/


/* 1) STAFF
   Purpose:
     - Stores staff members who catalog records and process loans.

   Keys & Functional Dependencies:
     - PK: StaffID
     - FDs: StaffID → StaffName
   Normal Form:
     - Every non-key attribute (StaffName) depends only on key.
     - No transitive dependencies.
     - Relation is in 3NF and BCNF.
*/
CREATE TABLE Staff (
  StaffID   INT PRIMARY KEY,
  StaffName VARCHAR2(100) NOT NULL
);


/* 2) AUTHOR

   Purpose:
     - Stores authors that can be linked to 0..N records.

   Keys & Functional Dependencies:
     - PK: AuthorID
     - FDs: AuthorID → AuthorName
   Normal Form:
     - Single-key table, all attributes fully depend on the key.
     - Relation is in 3NF and BCNF.
*/
CREATE TABLE Author (
  AuthorID   INT PRIMARY KEY,
  AuthorName VARCHAR2(100) NOT NULL
);


/* 3) CUSTOMER
   
   Purpose:
     - Stores library patrons who borrow items.

   Keys & Functional Dependencies:
     - PK: CustomerID
     - FDs: CustomerID → (FirstName, LastName, PhoneNumber, Address)
   Normal Form:
     - All attributes directly describe the customer entity.
     - No partial or transitive dependencies.
     - Relation is in 3NF and BCNF. */
CREATE TABLE Customer (
   CustomerID  NUMBER(9)      PRIMARY KEY,
   FirstName   VARCHAR2(50)   NOT NULL,
   LastName    VARCHAR2(50)   NOT NULL,
   PhoneNumber VARCHAR2(10),
   Address     VARCHAR2(254)
);


/* 4) RECORD
  
   Purpose:
     - Logical / bibliographic record for a title (book, ebook, DVD).
     - Does NOT contain inventory-level attributes or author name
       (those are in LibraryInventory and RecordAuthor).

   Keys & Functional Dependencies:
     - PK: RecordID
     - FDs:
         RecordID → (Title, Genre, DateOfPublication, CatalogedBy)
   Normal Form:
     - "AvailableStock" and "AuthorName" deliberately removed to
       avoid non-key and multi-valued dependencies.
     - CatalogedBy is a foreign key, not a determinant.
     - All non-key attributes depend on the key, the whole key,
       and nothing but the key.
     - Relation is in 3NF and BCNF. */
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


/* 5) RECORDAUTHOR  (M:N between Record and Author)

   Purpose:
     - Resolves the many-to-many relationship between Record
       and Author by using a junction table.

   Keys & Functional Dependencies:
     - PK: (RecordID, AuthorID)
     - FDs:
         (RecordID, AuthorID) → [no additional attributes]
   Normal Form:
     - Every determinant is a candidate key (the composite PK).
     - No transitive or partial dependencies.
     - Relation is in 3NF and BCNF.
*/
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


/* 6) LIBRARY INVENTORY

   Purpose:
     - Physical inventory level for each bibliographic record.
     - One Inventory row per ItemID (copy group) referencing Record.

   Keys & Functional Dependencies:
     - PK: ItemID
     - FDs:
         ItemID → (RecordID, TotalStock)
   Normal Form:
     - TotalStock is an inventory-level attribute, not derived
       per loan; aggregation is done in the view.
     - Optionally enforce 1:1 between Record and LibraryInventory
       with a UNIQUE constraint on RecordID.
     - Relation is in 3NF and BCNF. */
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


/* 7) BOOK  (subtype of Record)
   
   Purpose:
     - Stores attributes specific to physical books
       (ISBN, Binding, etc.) for records that are books.

   Keys & Functional Dependencies:
     - PK/FK: RecordID (also FK to Record)
     - FDs: RecordID → (ISBN, Binding)
   Normal Form:
     - One-to-one with Record for book-type records.
     - All attributes depend on RecordID, which is a key.
     - Relation is in 3NF and BCNF. */
CREATE TABLE Book (
    RecordID INT PRIMARY KEY,
    ISBN     VARCHAR2(20),
    Binding  VARCHAR2(50),
    CONSTRAINT fk_Book_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);


/* 8) EBOOK  (subtype of Record)
   
   Purpose:
     - Stores attributes specific to electronic books (DRM, file type).

   Keys & Functional Dependencies:
     - PK/FK: RecordID
     - FDs: RecordID → (DRMType, FileFormat)
   Normal Form:
     - One-to-one with Record for ebook-type records.
     - All attributes depend on the key.
     - Relation is in 3NF and BCNF.
   */
CREATE TABLE EBook (
    RecordID   INT PRIMARY KEY,
    DRMType    VARCHAR2(50),
    FileFormat VARCHAR2(20),
    CONSTRAINT fk_EBook_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);


/* 9) DVD  (subtype of Record)
   
   Purpose:
     - Stores attributes specific to DVD/video records.

   Keys & Functional Dependencies:
     - PK/FK: RecordID
     - FDs: RecordID → (RunTime, PGRating)
   Normal Form:
     - One-to-one with Record for DVD-type records.
     - All attributes depend on the key.
     - Relation is in 3NF and BCNF.*/
CREATE TABLE DVD (
    RecordID INT PRIMARY KEY,
    RunTime  INT,
    PGRating VARCHAR2(10),
    CONSTRAINT fk_DVD_Record
        FOREIGN KEY (RecordID)
        REFERENCES Record(RecordID)
);


/*
   10) LOANS

   Purpose:
     - Tracks each loan transaction of a physical item to a customer.
     - Models business rules like "due date must be after loan date"
       and "overdue flag must be 'Y' or 'N'".

   Keys & Functional Dependencies:
     - PK: loanId
     - FDs:
         loanId → (customerId, itemId, staffId,
                   loanDate, dueDate, overdue)

   Constraints / Business Rules:
     - fkLoansCustomer: each loan references a valid Customer.
     - fkLoansItem: each loan references a valid LibraryInventory item.
     - fkLoansStaff: each loan is processed by a Staff member.
     - chkDueDate: dueDate > loanDate.
     - overdue ∈ {'Y','N'}.

   Normal Form:
     - No attribute depends on anything other than loanId.
     - No repeating groups or derived totals; aggregated "active loans"
       are computed in the view RecordAvailableStock.
     - Relation is in 3NF and BCNF.
  */
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


/* 
   11) VIEW – RecordAvailableStock (Advanced Report)

   Purpose:
     - Summarizes, for each Record + ItemID (inventory group):
         • Total copies (TotalStock)
         • Number of active loans
         • Computed AvailableStock = TotalStock - ActiveLoans
     - Assumption:
         Every row in LOANS represents a currently-out copy.
         (If your business rules differ, you could:
           - Add a returnDate field and filter out returned loans,
           - Or add a "status" column.)

   Logic:
     1. Start from Record (bibliographic data).
     2. Join to LibraryInventory to get TotalStock per ItemID.
     3. LEFT JOIN a derived table "al" that counts the number of
        loans per itemId (ActiveLoans).
     4. Compute AvailableStock with:
           GREATEST(TotalStock - NVL(ActiveLoans, 0), 0)
        to avoid negative values and handle NULLs.

   */
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
