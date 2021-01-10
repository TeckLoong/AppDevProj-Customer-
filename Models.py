class Inventory:
    def __init__(self):
        self.__productDict = {}
        self.__totalSales = 0

    def set_product(self, key, product):
        self.__productDict[key] = product
    def set_total_sales(self, sales):
        self.__totalSales += sales

    def get_all_products(self):
        return self.__productDict
    def get_product(self, key):
        return self.__productDict[key]
    def get_total_sales(self):
        return self.__totalSales


class Product:
    def __init__(self, p_id, p_name, p_desc, p_qty, p_price, p_details):
        self.__p_id = p_id
        self.__p_name = p_name
        self.__p_desc = p_desc
        self.__p_qty = p_qty
        self.__p_price = p_price
        self.__p_details = p_details # array [publisher, author, category, language, format, pages]
        self.__p_img = ""

    def set_id(self, p_id):
        self.__p_id = p_id
    def set_name(self, p_name):
        self.__p_name = p_name
    def set_desc(self, p_desc):
        self.__p_desc = p_desc
    def set_qty(self, p_qty):
        self.__p_qty = p_qty
    def set_price(self, p_price):
        self.__p_price = p_price
    def set_details(self, p_details):
        self.__p_details = p_details
    def set_img(self, p_img):
        self.__p_img = p_img

    def get_id(self):
        return self.__p_id
    def get_name(self):
        return self.__p_name
    def get_desc(self):
        return self.__p_desc
    def get_qty(self):
        return self.__p_qty
    def get_price(self):
        return self.__p_price
    def get_details(self):
        return self.__p_details
    def get_img(self):
        return self.__p_img

class CartItem:
    def __init__(self, id, img, name, price):
        self.__id = id
        self.__img = img
        self.__name = name
        self.__qty = 0
        self.__price = price
    
    def set_id(self, id):
        self.__id = id
    def set_img(self, img):
        self.__img = img
    def set_name(self, name):
        self.__name = name
    def set_qty(self, qty):
        self.__qty = qty
    def add_qty(self, qty):
        self.__qty += qty
    def set_price(self, price):
        self.__price = price

    def get_id(self):
        return self.__id
    def get_img(self):
        return self.__img
    def get_name(self):
        return self.__name
    def get_qty(self):
        return self.__qty
    def get_price(self):
        return self.__price

class UserOrder:
    def __init__(self):
        self.__orderDict = {}

    def set_order(self, key, order):
        self.__orderDict[key] = order

    def get_all_orders(self):
        return self.__orderDict
    def get_order(self, key):
        return self.__orderDict[key]

class Order:
    def __init__(self, orderID, firstName, lastName, address1, address2,
                country, postcode, state, city, orderDate, orderItems):
        self.__orderID = orderID
        self.__firstName = firstName
        self.__lastName = lastName
        self.__address1 = address1
        self.__address2 = address2
        self.__country = country
        self.__postcode = postcode
        self.__state = state
        self.__city = city
        self.__orderDate = orderDate
        self.__orderItems = orderItems

    def set_orderID(self, o_id):
        self.__orderID = o_id
    def set_firstName(self, name):
        self.__firstName = name
    def set_lastName(self, name):
        self.__lastName = name
    def set_address1(self, address):
        self.__address1 = address
    def set_address2(self, address):
        self.__address2 = address
    def set_country(self, country):
        self.__country = country
    def set_postcode(self, postcode):
        self.__postcode = postcode
    def set_state(self, state):
        self.__state = state
    def set_city(self, city):
        self.__city = city
    def set_date(self, date):
        self.__orderDate = date
    def set_items(self, items):
        self.__orderItems = items

    def get_orderID(self):
        return self.__orderID
    def get_firstName(self):
        return self.__firstName
    def get_lastName(self):
        return self.__lastName
    def get_address1(self):
        return self.__address1
    def get_address2(self):
        return self.__address2
    def get_country(self):
        return self.__country
    def get_postcode(self):
        return self.__postcode
    def get_state(self):
        return self.__state
    def get_city(self):
        return self.__city
    def get_date(self):
        return self.__orderDate
    def get_items(self):
        return self.__orderItems

class Delivery:
    def __init__(self, orderID, status, address, 
                country, postcode, state, city):
        self.__orderID = orderID
        self.__status = status
        self.__address = address # array [address1, address2]
        self.__country = country
        self.__postcode = postcode
        self.__state = state
        self.__city = city
        self.__companyName = ""

    def get_orderID(self):
        return self.__orderID

    def set_orderID(self, orderID):
        self.__orderID = orderID

    def get_status(self):
        return self.__status

    def set_status(self, status):
        self.__status = status

    def get_address(self):
        return self.__address

    def set_address(self, address):
        self.__address = address
    
    def get_country(self):
        return self.__country

    def set_country(self, country):
        self.__country = country

    def get_postcode(self):
        return self.__postcode

    def set_postcode(self, postcode):
        self.__postcode = postcode

    def get_state(self):
        return self.__state

    def set_state(self, state):
        self.__state = state

    def get_city(self):
        return self.__city
    
    def set_city(self, city):
        self.__city = city

    def get_company_name(self):
        return self.__companyName

    def set_company_name(self, companyName):
        self.__companyName = companyName

class FAQ:
    countID= 0

    def __init__(self, firstName, lastName ):
        FAQ.countID +=1
        self.__FAQID = FAQ.countID
        self.__firstName = firstName
        self.__lastName = lastName

    def get_FAQID(self):
        return self.__FAQID

    def get_firstName(self):
        return self.__firstName

    def get_lastName(self):
        return self.__lastName

    def set_FAQID(self, faqID):
        self.__FAQIDID = faqID

    def set_firstName(self, firstName):
        self.__firstName = firstName

    def set_lastName(self, lastName):
        self.__lastName = lastName

class User:
    def __init__(self, name, u_id, email, password):
        self.__name = name
        self.__u_id = u_id
        self.__email = email
        self.__role = ""
        self.__password = password

    def set_name(self, name):
        self.__name = name

    def set_id(self, u_id):
        self.__u_id = u_id

    def set_email(self, email):
        self.__email = email

    def set_role(self, role):
        self.__role = role

    def set_password(self, password):
        self.__password = password

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__u_id

    def get_email(self):
        return self.__email

    def get_role(self):
        return self.__role

    def get_password(self):
        return self.__password
