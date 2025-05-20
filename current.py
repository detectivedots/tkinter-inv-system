import sqlite3
import product

global employee
global gui


def init():
    global employee
    global gui
    employee = None
    gui = None


def set_password(id, new_password):
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    new_password = encrypt_password(new_password)
    cursor.execute(f"update employee set  password = '{encrypt_password(new_password)}' where id = {id}")
    db.commit()


def encrypt_password(password):
    epass = ''
    for letter in password:
        x = ord(str(letter))
        x *= 5
        x += 3
        x %= 1114111
        epass += chr(x)
    return epass


super_permissions = {
    "Edit a user": True,
    "Checkout": True,
    "Edit items": True,
    "View log": True,
    "Add/Remove employees": True,
    "View Employees permissions": True,
    "Add/Remove discounts": True
}

super_employee = product.Employee('mohamed.fareed2001', super_permissions)
super_employee.id = 0
