import sqlite3
from tkinter import *

import current
import product

Black = "#222831"
Space = "#393E46"
Grey = "#EEEEEE"
Teal = "#00ADB5"

database_permission_names = ['edit_user', 'checkout', 'Edit_items', 'View_log', 'AddRemove_employees',
                             'View_Employees_permissions', 'AddRemove_discounts']


class NumberedButton:
    def __init__(self, root, number, command, total_columns):
        self.button = Button(root, text="Select", font=("Arial", 16, "bold"), background=Teal, foreground=Black,
                             command=lambda: command(self.number))
        self.number = number
        if number > 0:
            self.button.grid(row=self.number, column=total_columns)


class Table:

    def __init__(self, root, total_rows, total_columns, lst, parent=None):
        self.parent = parent
        self.result = None
        self.lst = lst
        # code for creating table
        for i in range(total_rows):
            for j in range(total_columns):
                self.e = Entry(root, width=15, fg='blue',
                               font=('Arial', 16, 'bold'))
                self.e.grid(row=i, column=j)
                self.e.insert(END, lst[i][j])
            button = NumberedButton(root, i, self.set_result, total_columns)

    def set_result(self, i):
        self.result = self.lst[i]
        if self.parent:
            self.parent.destroy()


class SearchBox:
    def __init__(self, target, fields, text="", search_text="", condition=None):
        self.result = None
        self.fields = fields
        self.search_target = target
        self.condition = condition

        self.window = Tk()

        self.window.title("Search")
        self.label = Label(self.window, text=text, font=("Arial", 18, "bold"))
        self.label.grid(row=0, column=0)
        self.entry = Entry(self.window, width=50, font=("Arial", 18, "bold"), background=Grey, foreground=Space)
        self.entry.grid(column=0, row=1, pady=10, padx=10)
        self.entry.insert(END, search_text)
        self.entry.bind('<Return>', self.retrieve)
        self.button = Button(self.window, text='Search', command=self.retrieve)
        self.entered = ''
        self.button.grid(column=0, row=2, pady=10, padx=10)
        self.results = [()]
        if len(search_text) > 0: self.retrieve()
        self.window.mainloop()
        if self.results == [()] or len(list(self.results)) == 0:
            # #print("empty")
            return
        self.window = Tk()
        self.window.geometry("600x600")
        frame = Frame(self.window)
        frame.pack(fill=BOTH, expand=1)
        can = Canvas(frame)
        hbar = Scrollbar(frame, orient=HORIZONTAL, command=can.xview)
        hbar.pack(side=BOTTOM, fill=X)
        can.pack(side=LEFT, fill=BOTH, expand=1)
        vbar = Scrollbar(frame, orient=VERTICAL, command=can.yview)
        vbar.pack(side=RIGHT, fill=Y)
        can.config(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        can.bind('<Configure>', lambda e: can.config(scrollregion=can.bbox("all")))
        frame2 = Frame(can)
        can.create_window((0, 0), window=frame2, anchor='nw')

        if fields != '*':
            lst = [tuple(field.strip() for field in self.fields.split(','))]
        else:
            db = sqlite3.connect("data.db")
            cursor = db.cursor()
            x = cursor.execute(f"PRAGMA table_info({self.search_target});")
            lst = [tuple(a[1] for a in list(x))]
            db.commit()
        # #print(lst)
        lst.extend(list(self.results))
        table = Table(frame2, len(lst), len(lst[1]), lst, self.window)
        self.window.mainloop()
        self.result = table.result

    def retrieve(self, event=None):
        self.entered = self.entry.get()
        if self.entry.get().isnumeric():
            if int(self.entry.get()) == 0:
                self.window.destroy()
                return
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        if self.condition:
            self.results = cursor.execute(
                f"select {self.fields} from {self.search_target} where {self.condition}").fetchall()
        else:
            if self.entry.get().isnumeric():
                if int(self.entry.get()) == 0:
                    self.window.destroy()
                    db.commit()
                    return
                self.results = cursor.execute(
                    f"select {self.fields} from {self.search_target} where id= '{int(self.entry.get())}'").fetchall()
            else:
                self.results = cursor.execute(
                    f"select {self.fields} from {self.search_target} where name like '%{self.entry.get()}%'").fetchall()
        if len(list(self.results)) == 0:
            not_found = Label(text="لا نتائج", foreground="Red", background=Black)
            not_found.grid(row=3, column=0)
        else:
            db.commit()
            self.window.destroy()


class LoginInterface:
    def __init__(self):
        self.window = Tk()
        self.window.title("Login")
        self.window.config(background=Black)
        self.window.config(padx=10, pady=10)
        self.login_label = Label(text="Login", font=("Arial", 36, "bold"), foreground=Grey, background=Black)
        self.login_label.grid(row=0, column=0, pady=10, sticky="W")
        self.name_label = Label(text="Name", font=24, padx=10, foreground=Grey, background=Black)
        self.name_label.grid(row=1, column=0, sticky="W")
        self.name = Entry(width=50, font=("Arial", 18, "bold"), background=Grey, foreground=Space)
        self.name.grid(row=2, column=0, padx=30, pady=10, sticky="W")
        self.password_label = Label(text="Password", font=24, foreground=Grey, background=Black)
        self.password_label.grid(row=3, column=0, sticky="W", padx=10)
        self.password = Entry(show="*", width=50, font=("Arial", 18, "bold"), background=Grey, foreground=Space)
        self.password.grid(row=4, column=0, padx=30, pady=10, sticky="W")
        self.login_button = Button(text="Login", font=("Arial", 16, "bold"), background=Teal, foreground=Black,
                                   command=self.validate_login)
        self.login_button.grid(row=5, column=0, sticky="W", padx=30, pady=20)
        self.window.bind('<Return>', self.validate_login)
        self.window.mainloop()

    def validate_login(self, event=None):
        if self.name.get() == 'admin' and self.password.get() == 'admin':
            self.window.destroy()
            current.employee = current.super_employee
            current.gui = MainWindow(current.employee)
            return
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        try:
            if self.name.get().isnumeric():
                user = cursor.execute(f"select * from employee where id= '{int(self.name.get())}'").fetchone()
            else:
                user = cursor.execute(f"select * from employee where name= '{self.name.get()}'").fetchone()
            password = user[2]
        except TypeError:
            not_found = Label(text="User not found", foreground="Red", background=Black)
            not_found.grid(row=6, column=0)
        else:
            if password == current.encrypt_password(current.encrypt_password(self.password.get())):
                i = 0
                current.employee = product.Employee(user[1])
                current.employee.id = user[0]
                for permission in current.employee.permissions:
                    current.employee.permissions[permission] = bool(user[i + 3])
                    i += 1
                self.window.destroy()
                db.commit()
                current.gui = MainWindow(current.employee)
            else:
                not_found = Label(text="Wrong Password", foreground="Red", background=Black)
                not_found.grid(row=6, column=0)


def placeholder():
    pass


class MainWindow:
    def __init__(self, employee):
        self.permissions_functions = {
            "تعديل مستخدم": self.edit_user,
            "بيع": self.checkout,
            "تعديل/إضافة منتج": self.edit_items,
            "السجل": self.view_log,
            "إضافة مستخدم": self.add_employees,
            "إضافة عميل": self.add_customer,
            "تعديل عميل": self.edit_customer
        }
        self.window = Tk()
        self.window.title("Main Window")
        self.employee = employee
        self.initialize_window(employee)
        self.window.mainloop()

    def initialize_window(self, employee):
        self.window.config(background=Black)
        welcome_label = Label(self.window, text=f"مرحباً {employee.name}", font=("Arial", 24, "bold"), foreground=Grey,
                              background=Black)
        welcome_label.grid(row=0, column=0, pady=10)
        # window.config(padx=20, pady=20)
        i = 1
        for key, value in self.permissions_functions.items():
            if value:
                button = Button(self.window, text=key, font=("Arial", 16, "bold"), background=Teal, foreground=Black,
                                command=value)
                button.grid(row=i, column=0, padx=10, pady=10)
                i += 1
        logout_button = Button(self.window, text="خروج", font=("Arial", 16, "bold"), background=Teal,
                               foreground=Black, command=self.logout)
        logout_button.grid(row=i, column=0, padx=10, pady=10)

    def edit_user(self):
        self.window.destroy()
        if current.employee.name != 'mohamed.fareed2001':
            db = sqlite3.connect("data.db")
            cursor = db.cursor()
            is_permitted = cursor.execute(f"Select edit_user from employee where id = {current.employee.id}").fetchone()
            db.commit()
        else:
            is_permitted = [1]
        if is_permitted[0] == 0:
            print(f"illegal{is_permitted} - {current.employee.id}")
        else:
            current.gui = SearchBox('employee', 'id, name')
            if current.gui.result:
                # #print(current.gui.result)
                db = sqlite3.connect("data.db")
                cursor = db.cursor()
                emp = list(cursor.execute(f"Select * from employee where id = {current.gui.result[0]}").fetchone())
                db.commit()
                # #print(emp)
                employee = product.Employee(emp[1])
                employee.id = emp[0]
                employee.retrieve_permissions()
                current.gui = EditUser(employee)
                current.gui = MainWindow(current.employee)

    def checkout(self):
        self.window.destroy()
        current.gui = SearchBox('customer', 'id, name', "Enter customer name, 0 for None")
        customer = None
        if current.gui.result:
            customer = product.Customer(current.gui.result[1])
            customer.id = current.gui.result[0]
        current.gui = CheckoutInterface(current.employee, customer)

    def logout(self):
        self.window.destroy()
        current.employee = None
        current.gui = LoginInterface()

    def edit_items(self):
        self.window.destroy()
        box = SearchBox('item', '*', text='اكتب رقم أو اسم المنتج، 0 للإضافة')
        result = box.result
        new = True
        if result:
            item = product.Item(result[0], result[1], result[2], result[4], result[3], result[5])
            new = False
        else:
            item = None
        current.gui = EditItem(item, new)
        current.gui = MainWindow(current.employee)

    def view_log(self):
        self.window.destroy()
        window = Tk()
        var = StringVar()
        window.config(padx=10, pady=10, background=Black)
        button1 = Button(window, text="بائع", font=("Arial", 16, "bold"), background=Teal, foreground=Black,
                         command=lambda: var.set("employee"))
        button2 = Button(window, text="عميل", font=("Arial", 16, "bold"), background=Teal, foreground=Black,
                         command=lambda: var.set("customer"))
        button1.grid(row=0, column=0, padx=20)
        button2.grid(row=0, column=1, padx=20)
        button3 = Button(window, text="خروج", font=("Arial", 16, "bold"), background=Teal, foreground=Black,
                         command=lambda: var.set("exit"))
        button3.grid(row=1, column=0, padx=20, pady=20, columnspan=2)
        window.wait_variable(var)
        window.destroy()
        if var.get() not in {'employee', 'customer'}:
            current.gui = MainWindow(current.employee)
            return
        window = SearchBox(var.get(), 'id, name')
        if window.result:
            res = window.result
            if not res: return
            #print(res)
            search_id = res[0]
            window = SearchBox('receipt', '*', search_text=str(search_id), condition=f"{var.get()}_id = {search_id}")
            # window.retrieve()
            res = window.result
            if not res:
                current.gui = MainWindow(current.employee)
                return
            #print(res)
            rec_id = res[0]
            emp_name = res[1]
            cus_name = res[2]
            date = res[3]
            receipt = product.Receipt(emp_name, customer=cus_name)
            receipt.id = rec_id
            receipt.time = date
            db = sqlite3.connect("data.db")
            c = db.cursor()
            lst = c.execute(
                f"Select item_id, quantity from receipt_contains_item where  receipt_id = {receipt.id}").fetchall()
            # #print(lst)
            for item in lst:
                it = c.execute(f"select * from item where id = {item[0]}").fetchone()
                #print(f"{type(it[0])} {type(it[1])} {type(it[2])} {type(it[4])} {type(it[3])} {type(it[5])} ")
                ite = product.Item(it[0], it[1], it[2], it[4], it[3], it[5])
                receipt.add_element(product.ReceiptElement(ite, item[1]))
            db.commit()
            #print("Committed")
            current.gui = Refund(receipt)
        current.gui = MainWindow(current.employee)

    def add_employees(self):
        self.window.destroy()
        current.gui = AddEmployee()
        current.gui = MainWindow(current.employee)

    def add_customer(self):
        self.window.destroy()
        current.gui = EditCustomer()
        current.gui = MainWindow(current.employee)

    def edit_customer(self):
        self.window.destroy()
        current.gui = SearchBox('customer', '*', text='اكتب اسم أو رقم الزبون')
        res = current.gui.result
        customer = product.Customer(res[1], res[2], res[3])
        current.gui = EditCustomer(customer)
        current.gui = MainWindow(current.employee)


f = False


class EditUser:
    def __init__(self, employee):
        self.employee = employee
        self.window = Tk()
        self.window.title(f"Edit {employee.name}")
        self.window.config(background=Black)
        self.window.config(padx=10, pady=10)
        self.name_label = Label(self.window, text="الاسم: ", font=("Arial", 16,), foreground=Grey, background=Black)
        self.name_entry = Entry(self.window, font=("Arial", 16,))
        self.name_entry.insert(END, employee.name)
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10)
        self.password_label = Label(self.window, text="تغيير كلمة المرور: ", font=("Arial", 16,), foreground=Grey,
                                    background=Black)
        self.password_entry = Entry(self.window, show="*", font=("Arial", 16,))
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        self.repassword_label = Label(self.window, text="إعادة كتابة كلمة المرور: ", font=("Arial", 16,),
                                      foreground=Grey,
                                      background=Black)
        self.repassword_entry = Entry(self.window, show="*", font=("Arial", 16,))
        self.repassword_label.grid(row=2, column=0, padx=10, pady=10)
        self.repassword_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=10)
        self.permission_label = Label(text='الصلاحيات', font=("Arial", 24, "bold"), foreground=Space, background=Grey)
        self.permission_label.grid(row=3, column=0, columnspan=3, pady=10, padx=10)
        self.allowed_label = Label(text='مسموح', font=("Arial", 16,), foreground=Grey, background=Black)
        self.allowed_label.grid(row=4, column=1)
        self.disallowed_label = Label(text='غير مسموح', font=("Arial", 16,), foreground=Grey, background=Black)
        self.disallowed_label.grid(row=4, column=2)

        self.radio_states = []
        for value in employee.permissions.values():
            var = IntVar()
            var.set(value)
            self.radio_states.append(var)

        for i in range(len(employee.permissions)):
            new_label = Label(text=list(employee.permissions.keys())[i], foreground=Grey, background=Black,
                              font=("Arial", 16,))
            new_label.grid(row=5 + i, column=0)
            # rad_butt = Radiobutton(value=int(list(employee.permissions.values())[i] == 1), variable=radio_states[i])
            rad_butt = Radiobutton(value=1, variable=self.radio_states[i], foreground=Space, background=Black,
                                   font=("Arial", 16,))
            # rad_butt2 = Radiobutton(value=int(list(employee.permissions.values())[i] == 0), variable=radio_states[i])
            rad_butt2 = Radiobutton(value=0, variable=self.radio_states[i], foreground=Space, background=Black,
                                    font=("Arial", 16,))
            rad_butt.grid(row=5 + i, column=1)
            rad_butt2.grid(row=5 + i, column=2)
        self.submit = Button(text="حفظ التغييرات", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                             command=self.submit)
        self.submit.grid(row=5 + len(employee.permissions), column=0, columnspan=3, padx=30, pady=20)
        self.window.mainloop()

    def submit(self):
        def f_true():
            window.destroy()
            # #print("F true")
            db = sqlite3.connect("data.db")
            cursor = db.cursor()
            if len(self.name_entry.get()) > 0:
                cursor.execute(f"update employee set name = '{self.name_entry.get()}' where id = {self.employee.id}")
            db.commit()
            if len(self.password_entry.get()) > 0:
                if self.password_entry.get() == self.repassword_entry.get():
                    current.set_password(self.employee.id, self.password_entry.get())
                else:
                    not_matched = Label(self.window, text="كلمة المرور غير متطابقة", foreground="Red", background=Black,
                                        font=("Arial", 24))
                    not_matched.grid(row=len(self.employee.permissions) + 2, column=0, columnspan=3)
            db = sqlite3.connect("data.db")
            cursor = db.cursor()
            for i in range(len(self.radio_states)):
                cursor.execute(
                    f"update employee set {database_permission_names[i]} = {self.radio_states[i].get()} where id = {self.employee.id}")
            self.window.destroy()
            db.commit()

        window = Toplevel()
        label = Label(window, text=f"هل تريد الاستمرار؟", font=("Arial", 24, "bold"), foreground=Grey,
                      background=Black)
        label.grid(row=0, column=0, columnspan=2)
        b1 = Button(window, text="Yes", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                    command=f_true)
        b2 = Button(window, text="No", font=("Arial", 24, "bold"), background="Red", foreground=Black,
                    command=window.destroy)
        b1.grid(row=1, column=0)
        b2.grid(row=1, column=1)


# font=("Arial", 16,), foreground=Grey,background=Black
f = True


class CheckoutInterface:
    def __init__(self, employee, customer):
        self.employee = employee
        self.customer = customer
        self.items = []
        self.window = Tk()

        self.window.title("Checkout")
        self.window.config(background=Black)
        self.window.config(padx=10, pady=10)
        frame1 = Frame(self.window, highlightthickness=1, highlightcolor=Grey, background=Black)
        frame1.grid(row=0, column=0, padx=10, pady=10)
        if customer:
            l1 = Label(frame1, text=f"اسم العميل: {customer.name}\t", font=("Arial", 16,), foreground=Grey,
                       background=Black)
            l1.grid(row=0, column=0, padx=10, pady=10)
        l2 = Label(frame1, text=f"اسم البائع: {employee.name}", font=("Arial", 16,), foreground=Grey, background=Black)
        l2.grid(row=0, column=2, padx=10, pady=10)

        frame2 = Frame(self.window, highlightthickness=1, highlightcolor=Grey, background=Black)
        frame2.grid(row=1, column=0, padx=10, pady=10)
        l3 = Label(frame2, text=f"رقم أو اسم المنتج: ", font=("Arial", 16,), foreground=Grey, background=Black)
        l3.grid(row=0, column=0, padx=10, pady=10)
        self.e1 = Entry(frame2, font=("Arial", 16,), foreground=Space, background=Grey)
        self.e1.grid(row=0, column=1, padx=10, pady=10)
        b1 = Button(frame2, text="Add", font=("Arial", 14, "bold"), background=Teal, foreground=Black,
                    command=self.add_element)
        b1.grid(row=0, column=2, padx=10, pady=10)
        self.frame3 = Frame(self.window, highlightthickness=1, highlightcolor=Grey, background=Black)
        self.frame3.grid(row=2, column=0)
        self.not_found = Label(self.frame3, text="غير موجود", foreground="Red", background=Black)
        l4 = Label(self.frame3, text="الاسم", font=("Arial", 14,), foreground=Grey, background=Black)
        l5 = Label(self.frame3, text="السعر", font=("Arial", 14,), foreground=Grey, background=Black)
        l6 = Label(self.frame3, text="الكمية", font=("Arial", 14,), foreground=Grey, background=Black)
        l7 = Label(self.frame3, text="الاجمالي", font=("Arial", 14,), foreground=Grey, background=Black)
        l4.grid(row=1, column=0, pady=10, padx=10)
        l5.grid(row=1, column=1, pady=10, padx=10)
        l6.grid(row=1, column=2, pady=10, padx=10)
        l7.grid(row=1, column=3, pady=10, padx=10)
        self.total = StringVar()
        self.total.set("0")
        l8 = Label(self.window, text="اجمالي السعر: ", font=("Arial", 16,), foreground=Grey, background=Black)
        l8.grid(row=3, column=0, pady=10, padx=10)
        l9 = Label(self.window, textvariable=self.total, font=("Arial", 16,), foreground=Grey, background=Black)
        l9.grid(row=3, column=1, pady=10, padx=10)
        self.submit = Button(text="حفظ", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                             command=self.submit)
        self.submit.grid(row=4, column=0, columnspan=3)
        self.window.mainloop()

    def add_element(self):
        self.not_found.destroy()
        self.not_found = Label(self.frame3, text="غير موجود", foreground="Red", background=Space)
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        if self.e1.get().isnumeric():
            item_data = cursor.execute(f"Select * from item where id = {int(self.e1.get())}").fetchone()
        else:
            it = list(cursor.execute(f"select * from item where name like '%{self.e1.get()}%'").fetchall())
            x = cursor.execute("PRAGMA table_info(item);")
            lst = [tuple(a[1] for a in list(x))]
            lst.extend(it)
            # #print(lst[1][0])
            n_window = Toplevel(self.window)

            # Paste
            n_window.geometry("800x600")
            frame = Frame(n_window)
            frame.pack(fill=BOTH, expand=1)
            can = Canvas(frame)
            hbar = Scrollbar(frame, orient=HORIZONTAL, command=can.xview)
            hbar.pack(side=BOTTOM, fill=X)
            can.pack(side=LEFT, fill=BOTH, expand=1)
            vbar = Scrollbar(frame, orient=VERTICAL, command=can.yview)
            vbar.pack(side=RIGHT, fill=Y)
            can.config(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
            can.bind('<Configure>', lambda e: can.config(scrollregion=can.bbox("all")))
            frame2 = Frame(can)
            can.create_window((0, 0), window=frame2, anchor='nw')
            table = Table(frame2, len(lst), len(lst[1]), lst, n_window)
            n_window.wait_window(n_window)
            item_data = table.result
        if not item_data:
            self.not_found.grid(row=0, column=0, columnspan=4)
        else:
            item = product.Item(item_data[0], item_data[1], item_data[2], item_data[4], item_data[3], item_data[5])
            item_field = ItemData(self.frame3, item, self)
            item_field.frame.grid(row=len(self.items) + 2, column=0, columnspan=4, padx=10, pady=10)
            self.items.append(item_field)
        db.commit()
        self.calculate_total()
        self.e1.delete(0, END)

    def calculate_total(self):
        x = 0
        for item_data in self.items:
            item_data.update_total_price()
            x += float(item_data.total_price.get())
        self.total.set(str(x))

    def update(self):
        x = 0
        for item_data in self.items:
            x += float(item_data.total_price.get())
        self.total.set(str(x))

    def submit(self):
        global f
        f = True
        window = None

        def f_false():
            if window:
                window.destroy()
            global f
            f = False

        receipt = product.Receipt(current.employee, customer=self.customer)
        # #print(receipt.id)
        db = sqlite3.connect("data.db")
        c = db.cursor()
        for item_data in self.items:
            receipt.add_element(product.ReceiptElement(item_data.item, int(item_data.quantity.get())))
        insufficient = [f'{element.item.name} أقل من الكمية الموجودة, يوجد فقط {element.item.left} is available' for
                        element in receipt.items if element.item.left < element.quantity]
        if len(insufficient) > 0:
            window = Toplevel(self.window)
            window.config(background=Black)
            for i in insufficient:
                label = Label(window, text=i, font=("Arial", 16,), foreground=Grey, background=Black)
                label.pack()
            b1 = Button(window, text="استمرار", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                        command=window.destroy)
            b1.pack(pady=10, side="left")
            b2 = Button(window, text="الغاء", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                        command=f_false)
            b2.pack(pady=10, side="right")

            window.wait_window(window)
        if not f:
            return
        for element in receipt.items:
            c.execute(
                f"update item set  quantity = {max(element.item.left - element.quantity, 0)} where id = {element.item.id}")
            c.execute(
                f"Insert into receipt_contains_item values ({receipt.id}, {element.item.id}, {int(element.quantity)})")
        receipt.hard_print()
        c.execute(
            f"Insert into receipt(employee_id, customer_id, date) VALUES ({receipt.seller.id}, {receipt.customer.id}, '{receipt.time}')")
        db.commit()
        self.window.destroy()
        current.gui = MainWindow(current.employee)


class ItemData:
    def __init__(self, root, item, par):
        self.parent = par
        self.frame = Frame(root, background=Space)
        self.item = item
        self.chosen_quantity = StringVar()
        self.chosen_quantity.set("1")
        self.total_price = StringVar()
        name = Label(self.frame, text=item.name, font=("Arial", 14,), foreground=Grey, background=Black)
        name.grid(row=0, column=0, pady=10, padx=10)
        price = Label(self.frame, text=item.price, font=("Arial", 14,), foreground=Grey, background=Black)
        price.grid(row=0, column=1, pady=10, padx=10)
        self.quantity = Spinbox(self.frame, from_=0, to=10000, width=10, textvariable=self.chosen_quantity,
                                command=self.update_total_price)
        self.quantity.grid(row=0, column=2, pady=10, padx=10)
        x = int(self.quantity.get()) * (item.price - item.discount)
        self.total_price.set(str(x))
        total = Label(self.frame, textvariable=self.total_price, font=("Arial", 14,), foreground=Grey, background=Black)
        total.grid(row=0, column=3, pady=10, padx=10)

    def update_total_price(self):
        x = int(self.quantity.get()) * (self.item.price - self.item.discount)
        self.total_price.set(str(x))
        self.parent.update()


class EditItem:
    def __init__(self, item, new=False):
        self.window = Tk()
        self.item = item
        self.window.config(background=Black, pady=10, padx=10)
        self.e = []
        self.new = new
        frame = Frame(self.window, background=Black)
        frame.pack()

        r1 = Frame(frame, background=Black)
        r1.pack()
        l1 = Label(r1, text="الرقم:", background=Black, font=("Arial", 16,), foreground=Grey)
        l1.pack(side="left")
        v1 = StringVar()
        if not new:
            v1.set(str(item.id))
        if not new:
            e1 = Entry(r1, textvariable=v1, state='disabled')
        else:
            e1 = Entry(r1, textvariable=v1)
        e1.pack(side="right")
        self.e.append(e1)

        r2 = Frame(frame, background=Black)
        r2.pack()
        l2 = Label(r2, text="الاسم:", background=Black, font=("Arial", 16,), foreground=Grey)
        l2.pack(side="left")
        v2 = StringVar()
        if not new:
            v2.set(str(item.name))
        e2 = Entry(r2, textvariable=v2)
        e2.pack(side="right")
        self.e.append(e2)

        r3 = Frame(frame, background=Black)
        r3.pack()
        l3 = Label(r3, text="السعر:", background=Black, font=("Arial", 16,), foreground=Grey)
        l3.pack(side="left")
        v3 = StringVar()
        if not new:
            v3.set(str(item.price))
        e3 = Entry(r3, textvariable=v3)
        e3.pack(side="right")
        self.e.append(e3)

        r4 = Frame(frame, background=Black)
        r4.pack()
        l4 = Label(r4, text="النوع:", background=Black, font=("Arial", 16,), foreground=Grey)
        l4.pack(side="left")
        v4 = StringVar()
        if not new:
            v4.set(str(item.category))
        e4 = Entry(r4, textvariable=v4)
        e4.pack(side="right")
        self.e.append(e4)

        r5 = Frame(frame, background=Black)
        r5.pack()
        l5 = Label(r5, text="الكمية الموجودة:", background=Black, font=("Arial", 16,), foreground=Grey)
        l5.pack(side="left")
        v5 = StringVar()
        if not new:
            v5.set(str(item.left))
        e5 = Entry(r5, textvariable=v5)
        e5.pack(side="right")
        self.e.append(e5)

        r6 = Frame(frame, background=Black)
        r6.pack()
        l6 = Label(r6, text="خصومات:", background=Black, font=("Arial", 16,), foreground=Grey)
        l6.pack(side="left")
        v6 = StringVar()
        if not new:
            v6.set(str(item.discount))
        e6 = Entry(r6, textvariable=v6)
        e6.insert(END, "0")
        e6.pack(side="right")
        self.e.append(e6)

        self.submit = Button(text="Submit Changes", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                             command=self.submit)
        self.submit.pack(side="bottom")

    def submit(self):
        db = sqlite3.connect("data.db")
        c = db.cursor()
        e = self.e
        if self.new:
            c.execute(
                f"INSERT INTO item values ({int(e[0].get())},"
                f"'{(e[1].get())}', {float(e[2].get())},"
                f"'{(e[3].get())}', {int(e[4].get())}, {float(e[5].get())}"
                f")"
            )
        else:
            c.execute(f"UPDATE item"
                      f" SET name = '{(e[1].get())}',"
                      f" price = {float(e[2].get())},"
                      f" category = '{e[3].get()}',"
                      f" quantity = {int(e[4].get())},"
                      f" discount = {float(e[5].get())}"
                      f" WHERE id={self.item.id}")
        db.commit()
        self.window.destroy()


class AddEmployee:
    def __init__(self):
        self.employee = product.Employee('placeholder', None)
        #print(self.employee.permissions)
        self.window = Tk()
        self.window.title(f"Add")
        self.window.config(background=Black)
        self.window.config(padx=10, pady=10)
        self.name_label = Label(self.window, text="الاسم: ", font=("Arial", 16,), foreground=Grey, background=Black)
        self.name_entry = Entry(self.window, font=("Arial", 16,))
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10)
        self.password_label = Label(self.window, text="كلمة المرور: ", font=("Arial", 16,), foreground=Grey,
                                    background=Black)
        self.password_entry = Entry(self.window, show="*", font=("Arial", 16,))
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        self.repassword_label = Label(self.window, text="أعد كتابة كلمة المرور: ", font=("Arial", 16,), foreground=Grey,
                                      background=Black)
        self.repassword_entry = Entry(self.window, show="*", font=("Arial", 16,))
        self.repassword_label.grid(row=2, column=0, padx=10, pady=10)
        self.repassword_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=10)
        self.permission_label = Label(text='الصلاجيات', font=("Arial", 24, "bold"), foreground=Space, background=Grey)
        self.permission_label.grid(row=3, column=0, columnspan=3, pady=10, padx=10)
        self.allowed_label = Label(text='سماح', font=("Arial", 16,), foreground=Grey, background=Black)
        self.allowed_label.grid(row=4, column=1)
        self.disallowed_label = Label(text='منع', font=("Arial", 16,), foreground=Grey, background=Black)
        self.disallowed_label.grid(row=4, column=2)

        self.radio_states = []
        for value in self.employee.permissions.values():
            var = IntVar()
            var.set(value)
            self.radio_states.append(var)

        for i in range(len(self.employee.permissions)):
            new_label = Label(text=list(self.employee.permissions.keys())[i], foreground=Grey, background=Black,
                              font=("Arial", 16,))
            new_label.grid(row=5 + i, column=0)
            # rad_butt = Radiobutton(value=int(list(employee.permissions.values())[i] == 1), variable=radio_states[i])
            rad_butt = Radiobutton(value=1, variable=self.radio_states[i], foreground=Space, background=Black,
                                   font=("Arial", 16,))
            # rad_butt2 = Radiobutton(value=int(list(employee.permissions.values())[i] == 0), variable=radio_states[i])
            rad_butt2 = Radiobutton(value=0, variable=self.radio_states[i], foreground=Space, background=Black,
                                    font=("Arial", 16,))
            rad_butt.grid(row=5 + i, column=1)
            rad_butt2.grid(row=5 + i, column=2)
        self.submit = Button(text="حفظ", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                             command=self.submit)
        self.submit.grid(row=5 + len(self.employee.permissions), column=0, columnspan=3, padx=30, pady=20)
        self.window.mainloop()

    def submit(self):
        def f_true():
            window.destroy()
            # #print("F true")
            db = sqlite3.connect("data.db")
            cursor = db.cursor()
            if len(self.name_entry.get()) > 0:
                cursor.execute(f"Insert into employee(name, password) VALUES ('{self.name_entry.get()}', ' ')")
            db.commit()
            if len(self.password_entry.get()) > 0:
                if self.password_entry.get() == self.repassword_entry.get():
                    current.set_password(self.employee.id, self.password_entry.get())
                else:
                    not_matched = Label(self.window, text="كلمة المرور غير متطابقة", foreground="Red", background=Black,
                                        font=("Arial", 24))
                    not_matched.grid(row=len(self.employee.permissions) + 2, column=0, columnspan=3)
            db = sqlite3.connect("data.db")
            cursor = db.cursor()
            for i in range(len(self.radio_states)):
                cursor.execute(
                    f"update employee set {database_permission_names[i]} = {self.radio_states[i].get()} where id = {self.employee.id}")
            self.window.destroy()
            db.commit()

        window = Toplevel()
        label = Label(window, text=f"هل تريد الاستمرار؟", font=("Arial", 24, "bold"), foreground=Grey,
                      background=Black)
        label.grid(row=0, column=0, columnspan=2)
        b1 = Button(window, text="نعم", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                    command=f_true)
        b2 = Button(window, text="لا", font=("Arial", 24, "bold"), background="Red", foreground=Black,
                    command=window.destroy)
        b1.grid(row=1, column=0)
        b2.grid(row=1, column=1)


class Refund:
    def __init__(self, receipt):
        self.receipt = receipt
        self.window = Tk()
        self.window.config(background=Black)
        frame = Frame(self.window)
        frame.config(background=Space)
        self.str_vars = []
        for element in receipt.items:
            row = Frame(frame, background=Space)
            label = Label(row, text=element.item.name, font=("Arial", 16,), background=Space, foreground=Grey)
            label.grid(row=0, column=0, padx=10)
            var = StringVar()
            var.set(str(element.quantity))
            box = Spinbox(row, from_=0, to=element.quantity, width=10, textvariable=var)
            box.grid(row=0, column=1, padx=10)
            self.str_vars.append(var)
            row.pack(pady=10)
        frame.pack()
        self.submit = Button(text="حفظ التغييرات", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                             command=self.submit)
        self.submit.pack()
        self.window.mainloop()

    def submit(self):
        db = sqlite3.connect("data.db")
        c = db.cursor()
        for i in range(len(self.str_vars)):
            if int(self.str_vars[i].get()) != self.receipt.items[i].quantity:
                if int(self.str_vars[i].get()) == 0:
                    c.execute(
                        f"DELETE FROM receipt_contains_item "
                        f"where receipt_id={self.receipt.id} "
                        f"AND item_id={self.receipt.items[i].item.id}"
                    )
                else:
                    c.execute(
                        f"UPDATE receipt_contains_item "
                        f"SET quantity = {int(self.str_vars[i].get())} "
                        f"where receipt_id={self.receipt.id} "
                        f"AND item_id={self.receipt.items[i].item.id}"
                    )
        db.commit()
        self.window.destroy()


class EditCustomer:
    def __init__(self, customer=None):
        self.new = False if customer else True
        self.customer = product.Customer('placeholder')
        if customer:
            self.customer = customer
        self.window = Tk()
        self.window.title(f"Add")
        self.window.config(background=Black)
        self.window.config(padx=10, pady=10)
        self.name_label = Label(self.window, text="الاسم: ", font=("Arial", 16,), foreground=Grey, background=Black)
        self.name_entry = Entry(self.window, font=("Arial", 16,))
        self.mobile_label = Label(self.window, text="الهاتف: ", font=("Arial", 16,), foreground=Grey, background=Black)
        self.mobile_entry = Entry(self.window, font=("Arial", 16,))
        self.address_label = Label(self.window, text="العنوان: ", font=("Arial", 16,), foreground=Grey,
                                   background=Black)
        self.address_entry = Entry(self.window, font=("Arial", 16,))
        self.mobile_label.grid(row=1, column=0, padx=10, pady=10)
        self.mobile_entry.grid(row=1, column=1, padx=10, pady=10)
        if customer:
            self.name_entry.insert(END, customer.name)
            self.mobile_entry.insert(END, customer.mobile)
            self.address_entry.insert(END, customer.address)
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.address_label.grid(row=2, column=0, padx=10, pady=10)
        self.address_entry.grid(row=2, column=1, padx=10, pady=10)
        self.submit = Button(text="حفظ", font=("Arial", 24, "bold"), background=Teal, foreground=Black,
                             command=self.submit)
        self.submit.grid(row=3, column=0, columnspan=3, padx=30, pady=20)
        self.window.mainloop()

    def submit(self):
        db = sqlite3.connect("data.db")
        c = db.cursor()
        if self.new:
            c.execute(
                f"INSERT INTO customer(name, mobile, address) VALUES ("
                f"'{self.name_entry.get()}', '{self.mobile_entry.get()}', "
                f"'{self.address_entry.get()}'"
                f")"
            )
        else:
            c.execute(
                f"UPDATE customer "
                f"SET name = '{self.name_entry.get()}', "
                f"address= '{self.address_entry.get()}', "
                f"mobile= '{self.mobile_entry.get()}' "
                f"WHERE id = {self.customer.id}"
            )
        self.window.destroy()
        db.commit()
