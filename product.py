import copy
import os
import sqlite3
import tempfile
from datetime import datetime


class Item:
    def __init__(self, num, name, price, num_left, category=None, discount=0):
        self.id = num
        self.name = name
        self.price = price
        self.category = category
        self.left = num_left
        self.discount = discount


class Customer:
    def __init__(self, name, mobile="", address=""):
        db = sqlite3.connect("data.db")
        c = db.cursor()
        last_customer_id = c.execute("SELECT * FROM SQLITE_SEQUENCE WHERE name='customer'").fetchone()
        last_customer_id = last_customer_id[1] if last_customer_id else 0
        db.commit()
        self.id = last_customer_id + 1
        self.name = name
        self.mobile = mobile
        self.address = address


class ReceiptElement:
    def __init__(self, item, quantity=1):
        self.item = item
        self.quantity = quantity
        self.cost = item.price * quantity


class Receipt:
    def __init__(self, employee, receipt_elements=None, customer=None):
        db = sqlite3.connect("data.db")
        c = db.cursor()
        last_receipt_id = c.execute("SELECT * FROM SQLITE_SEQUENCE WHERE name='receipt'").fetchone()
        last_receipt_id = last_receipt_id[1] if last_receipt_id else 0
        db.commit()
        if receipt_elements is None:
            receipt_elements = []
        self.seller = employee
        self.items = receipt_elements
        if customer is None:
            self.customer = Customer("")
            self.customer.id = 0
        else:
            self.customer = customer
        self.total_cost = self.calculate_total_cost()
        self.id = last_receipt_id + 1
        self.time = datetime.now()

    def calculate_total_cost(self):
        total = 0
        for item in self.items:
            total += item.cost * item.quantity
        return total

    def add_element(self, element):
        if element.quantity == 0:
            return
        f = False
        for item in self.items:
            if item.item.id == element.item.id:
                item.quantity += element.quantity
                f = True
                break
        if not f:
            self.items.append(element)
        self.total_cost = self.calculate_total_cost()

    def remove_element(self, element):
        self.items.remove(element)
        self.total_cost = self.calculate_total_cost()

    def change_element_quantity(self, element):
        for item in self.items:
            if item.item == element.item:
                item.quantity = element.quantity
                return True
        return False

    def get_text(self):
        s = f"Seller: {self.seller.name}\t\tCustomer: {self.customer.name}\n" \
            f"Receipt ID= {self.id}, date={self.time.date()}, time={self.time.hour}:{self.time.minute}\n" \
            f"اسم\tسعر\tكمية\tاجمالي\n"
        # print(s)
        for element in self.items:
            s += f"{element.item.name}\t{element.item.price - element.item.discount}\t{element.quantity}\t{(element.item.price - element.item.discount) * element.quantity}\n"
        summ = 0
        for element in self.items:
            summ += (element.item.price - element.item.discount) * element.quantity
        s += f"{summ}\tالإجمالي:"
        return s

    def hard_print(self):
        s = self.get_text()
        filename = tempfile.mktemp(".txt").encode("utf-8")
        open(filename, "wb").write(s.encode("utf-8"))
        os.startfile(filename, "print")


DEFAULT_PERMISSIONS = {
    "Edit User": False,
    "Checkout": True,
    "Edit items": False,
    "View log": True,
    "Add/Remove employees": False,
    "View Employees permissions": False,
    "Add/Remove discounts": False
}


class Employee:
    def __init__(self, name, permissions=None):
        db = sqlite3.connect("data.db")
        c = db.cursor()
        last_seller_id = c.execute("SELECT * FROM SQLITE_SEQUENCE WHERE name='employee'").fetchone()
        last_seller_id = last_seller_id[1] if last_seller_id else 0
        db.commit()
        if permissions is None:
            permissions = copy.deepcopy(DEFAULT_PERMISSIONS)
        self.name = name
        self.id = last_seller_id + 1
        self.permissions = permissions

    def retrieve_permissions(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        permissions = list(cursor.execute(f"Select * from employee where id = {self.id}").fetchone())[3::]
        i = 0
        for key, value in self.permissions.items():
            self.permissions[key] = permissions[i]
            i += 1
