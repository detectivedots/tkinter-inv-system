import sqlite3
x = input()
if (x == '__init__'):
    db = sqlite3.connect('data.db')
    c = db.cursor()
    c.execute('''-- we don't know how to generate root <with-no-name> (class Root) :(
create table customer
(
    id      INTEGER
        primary key autoincrement,
    name    TEXT,
    mobile  TEXT,
    address TEXT
);

create table employee
(
    id                         INTEGER
        primary key autoincrement,
    name                       TEXT        not null,
    password                   varchar(64) not null,
    edit_user                  INTEGER default False,
    checkout                   INT     default TRUE,
    Edit_items                 INT     default False,
    View_log                   INT     default TRUE,
    AddRemove_employees        INT     default False,
    View_Employees_permissions INT     default False,
    AddRemove_discounts        INTEGER default 0
);

create table item
(
    id       INTEGER
        primary key,
    name     TEXT  not null,
    price    FLOAT not null,
    category TEXT,
    quantity INTEGER default 0,
    discount FLOAT   default 0
);

create table receipt
(
    id          INTEGER
        primary key autoincrement,
    employee_id INT
        references employee,
    customer_id INT
        references customer,
    date        DATETIME
);

create table receipt_contains_item
(
    receipt_id INTEGER
        references receipt,
    item_id    INTEGER
        references item,
    quantity   INTEGER,
    primary key (receipt_id, item_id)
);

''')
    db.commit()