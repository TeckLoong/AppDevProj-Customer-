import os, os.path
from flask import Flask, session, abort, flash, render_template, request, redirect, url_for
from Forms import *
import shelve, Models, datetime
from werkzeug.utils import secure_filename
from uuid import uuid4
from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser
from flask_socketio import SocketIO, emit
from functools import wraps

# pip install Flask
# pip install wtforms
# pip install Whoosh
# pip install flask-socketio

UPLOAD_FOLDER = './static/images/product_imgs'
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}
PRODUCT_IMAGE_PATH = 'images/product_imgs/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['SECRET_KEY'] = "4tiuerhvdf-g2gfdsgergEWwefWh6jIt-TyjtyhrtgWerfw23"
socketio = SocketIO(app)

@app.errorhandler(404)
def error_404(error):
    return render_template("error.html", message="This page does not exist.", sessionName=sessionName())

@app.errorhandler(401)
def error_401(error):
    return render_template("error.html", message="Unauthorised access!", sessionName=sessionName())

def login_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'username' in session:
            return func(*args, **kwargs)
        else:
            return render_template("error.html", message="You need to login to do this.")
    return wrap

def privilege_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if session['user_role'] != "Admin":
            return render_template("error.html",
                message="Error 401. You don't have the privilege to access this!", sessionName=sessionName())
        else:
            return func(*args, **kwargs)
    return wrap

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(product):
    file = request.files['image']
    if file and allowed_file(file.filename):
        img_name = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
        img_path = PRODUCT_IMAGE_PATH + img_name
        product.set_img(img_path)
        print('File successfully uploaded')

# reads db["Inventory"] from shelve and returns object
def read_shelve_inventory():
    db = shelve.open('database.db', 'r')
    inventory = db["Inventory"]
    db.close()
    return inventory

def createIndex(p_id, p_title, p_tags):
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    try:
        ix = index.open_dir("indexdir")
    except:
        schema = Schema(id=ID(stored=True), title=TEXT(stored=True), tags=TEXT(stored=True))
        ix = index.create_in("indexdir", schema)

    writer = ix.writer()
    writer.add_document(id=p_id, title=p_title, tags=p_tags)
    writer.commit()
    print("index created")

# returns search result
def searchIndex(searchKeyword, field):
    ix = index.open_dir("indexdir")
    query = QueryParser(field, ix.schema).parse(searchKeyword)

    products = []
    with ix.searcher() as s:
        results = s.search(query, limit=None)
        for result in results:
            products.append({'id': result['id'],'title': result['title'], 'tags': result['tags']})
    return products

def showIndex(searchResults):
    resultList = []
    for i in searchResults:
        print(i)
        resultList.append(read_shelve_inventory().get_product(i.get("id")))
    return resultList

def sessionName():
    if 'username' in session:
        return session['username']
    else:
        return ''

@app.route('/')
def home():
    productList = []
    custDict = {}
    db = shelve.open('database.db', 'r')
    custDict = db['Users']
    db.close()



    isUserExist = False
    for key in custDict:
        if custDict.get(key).get_email() == email and custDict.get(key).get_password() == password:
            session['username'] = custDict.get(key).get_name()
            session['user_role'] = custDict.get(key).get_role()
            isUserExist = True

            break
    print(custDict.get(key).get_email(), custDict.get(key).get_password())
    try:
        productDict = read_shelve_inventory().get_all_products()
        for key in productDict:
            productList.append(productDict.get(key))
    except:
        pass
    return render_template("home.html", productList=productList, sessionName=sessionName())

@app.route('/search/title')
def searchTitle():
    keyword = "" if request.args.get('keyword') is None else request.args.get('keyword')
    searchResults = searchIndex(keyword, "title")

    return render_template("search.html", resultList=showIndex(searchResults), sessionName=sessionName())

@app.route('/search/tags')
def searchTags():
    keyword = ' '.join([request.args.get('category'), request.args.get('language'), request.args.get('format')])
    print(keyword)
    searchResults = searchIndex(keyword, "tags")

    return render_template("search.html", resultList=showIndex(searchResults), sessionName=sessionName())

@app.route('/product/start=<int:start>&view=<int:view>')
def viewPagination(start, view):
    productList = []
    try:
        productDict = read_shelve_inventory().get_all_products()
        for key in productDict:
            productList.append(productDict.get(key))
    except:
        pass
    count = len(productList)
    prevPage = ''
    nextPage = ''

    # make prev url
    if not(start == 1):
        start_copy = start - view
        prevPage = "/product/start=%d&view=%d" % (start_copy, view)

    # make next url
    if not(start + view > count):
        start_copy = start + view
        nextPage = "/product/start=%d&view=%d" % (start_copy, view)

    pagination = productList[(start - 1):(start - 1 + view)]
    return render_template("home.html", productList=pagination, nextPage=nextPage, prevPage=prevPage, sessionName=sessionName())


@app.route('/product/<name>/<id>')
def viewProduct(id, name):
    return render_template("viewProduct.html", product=read_shelve_inventory().get_product(id), sessionName=sessionName())


@app.route('/inventory')
@login_required
@privilege_required
def inventory():
    productDict = {}
    try:
        productDict = read_shelve_inventory().get_all_products()
    except:
        pass
    return render_template("inventory.html", productDict=productDict, sessionName=sessionName())


@app.route('/add-item', methods=['GET', 'POST'])
@login_required
@privilege_required
def addProduct():
    addProduct = ProductForm(request.form)
    if request.method == 'POST' and addProduct.validate():
        db = shelve.open('database.db', 'c')
        try:
            inventory = db["Inventory"]
        except:
            print("Unable to read Inventory from database.db.")
            print("Creating new Inventory...")
            inventory = Models.Inventory()

        productIndex = str(uuid4())
        productDetails = [addProduct.publisher.data, addProduct.author.data, addProduct.category.data,
                            addProduct.language.data, addProduct.p_format.data, addProduct.pages.data]
        product = Models.Product(productIndex, addProduct.title.data, addProduct.description.data,
        addProduct.quantity.data, addProduct.price.data, productDetails)
        upload_image(product)
        createIndex(productIndex, addProduct.title.data,
                    ' '.join([addProduct.category.data, addProduct.language.data, addProduct.p_format.data]))


        inventory.set_product(productIndex, product)
        db["Inventory"] = inventory
        db.close()

        return redirect(url_for('inventory'))
    return render_template("addProduct.html", form=addProduct, sessionName=sessionName())


@app.route('/edit-item/<id>/', methods=["GET", "POST"])
@login_required
@privilege_required
def updateProduct(id):
    updateProduct = ProductForm(request.form)
    if request.method == "POST" and updateProduct.validate():
        db = shelve.open('database.db', 'w')
        inventory = db["Inventory"]

        product = inventory.get_product(id)
        productDetails = [updateProduct.publisher.data, updateProduct.author.data, updateProduct.category.data,
                            updateProduct.language.data, updateProduct.p_format.data, updateProduct.pages.data]
        product.set_name(updateProduct.title.data)
        product.set_desc(updateProduct.description.data)
        product.set_qty(updateProduct.quantity.data)
        product.set_price(updateProduct.price.data)
        product.set_details(productDetails)
        upload_image(product)

        inventory.set_product(id, product)
        db["Inventory"] = inventory
        db.close()

        return redirect(url_for('inventory'))
    else:
        product = read_shelve_inventory().get_product(id)
        productDetails = product.get_details()
        updateProduct.title.data = product.get_name()
        updateProduct.description.data = product.get_desc()
        updateProduct.quantity.data = product.get_qty()
        updateProduct.price.data = product.get_price()
        updateProduct.publisher.data = productDetails[0]
        updateProduct.author.data = productDetails[1]
        updateProduct.category.data = productDetails[2]
        updateProduct.language.data = productDetails[3]
        updateProduct.p_format.data = productDetails[4]
        updateProduct.pages.data = productDetails[5]

        return render_template("updateProduct.html", form=updateProduct, sessionName=sessionName())

@app.route('/deleteProduct/<id>', methods=['POST'])
@login_required
@privilege_required
def deleteProduct(id):
    db = shelve.open('database.db', 'w')
    inventory = db["Inventory"]
    inventory.get_all_products().pop(id)
    db["Inventory"] = inventory
    db.close()

    return redirect(url_for('inventory'))


@app.route('/addCart/<id>', methods=['POST', 'GET'])
def addCart(id):
    cartDict = {}
    db = shelve.open('database.db', 'w')
    item = db["Inventory"].get_product(id)
    try:
        cartDict = db["Cart"]
        cart = cartDict[id]
    except:
        cart = Models.CartItem(item.get_id(), item.get_img(),
                        item.get_name(), item.get_price())
    cart.add_qty(1)
    cartDict[id] = cart
    db["Cart"] = cartDict
    db.close()

    return redirect(url_for('home'))

@app.route('/showCart', methods=["POST", "GET"])
def showCart():
    cartList = []
    db = shelve.open('database.db', 'r')
    try:
        cartDict = db["Cart"]
        for k in cartDict:
            cartList.append(cartDict.get(k))
    except:
        pass
    db.close()
    return render_template("showCart.html", cartList=cartList, sessionName=sessionName())

@app.route('/updateCart/<id>', methods=["POST", "GET"])
def updateCart(id):
    qty = int(request.args.get('qty'))
    db = shelve.open('database.db', 'w')
    itemDict = db["Cart"]
    itemDict.get(id).set_qty(qty)
    db["Cart"] = itemDict
    db.close()
    return redirect(url_for("showCart"))

@app.route('/deleteCart/<id>', methods=["POST"])
def deleteCart(id):
    db = shelve.open('database.db', 'w')
    itemDict = db["Cart"]
    itemDict.pop(id)
    db["Cart"] = itemDict
    db.close()

    return redirect(url_for("showCart"))

@app.route('/checkout', methods=["POST", "GET"])
@login_required
def checkout():
    checkoutForm = OrderForm(request.form)
    if request.method == "POST" and checkoutForm.validate():
        db = shelve.open('database.db', 'w')
        orderDict = {}
        userID = "66fiddling99"
        orderID = str(uuid4())
        itemDict = db["Cart"]
        try:
            orderDict = db["Orders"]

            userOrder = orderDict[userID]
        except:
            userOrder = Models.UserOrder()
            orderDict[userID] = userOrder

        order = Models.Order(orderID, checkoutForm.firstName.data, checkoutForm.lastName.data,
                checkoutForm.address1.data, checkoutForm.address2.data, checkoutForm.country.data,
                checkoutForm.postcode.data,checkoutForm.state.data, checkoutForm.city.data,
                str(datetime.date.today()), itemDict)

        userOrder.set_order(orderID, order)
        orderDict[userID] = userOrder
        itemDict = {}
        db["Cart"] = itemDict
        db["Orders"] = orderDict

        # create delivery object
        deliveryDict = {}
        try:
            deliveryDict = db["DeliveryDict"]
        except:
            pass
        delivery = Models.Delivery(orderID, "Awaiting Delivery", [order.get_address1(), order.get_address2()],
                            order.get_country(), order.get_postcode(), order.get_state(),
                            order.get_city())
        deliveryDict[orderID] = delivery
        db["DeliveryDict"] = deliveryDict
        db.close()

        return redirect(url_for("home"))
    return render_template("checkout.html", form=checkoutForm, sessionName=sessionName())

@app.route('/order')
@login_required
def userOrder():
    orderList = []
    userID = "66fiddling99"

    db = shelve.open('database.db', 'r')
    try:
        orderDict = db["Orders"]
        userOrder = orderDict[userID].get_all_orders()
        for k in userOrder:
            orderList.append(userOrder.get(k))
    except:
        pass
    db.close()
    return render_template("userOrder.html", orderList=orderList, sessionName=sessionName())

@app.route('/order/<id>')
@login_required
def viewOrder(id):
    userID = "66fiddling99"

    db = shelve.open('database.db', 'r')
    orderDict = db["Orders"]

    db.close()
    userOrder = orderDict[userID].get_order(id)
    productDict = orderDict[userID].get_order(id).get_items()

    return render_template("viewOrder.html", order=userOrder, productDict=productDict, sessionName=sessionName())

# Delivery
@app.route('/delivery-seller')
@login_required
@privilege_required
def retrieveSellerDelivery():
    status = StatusForm(request.form)

    deliveryDict = {}

    db = shelve.open("database.db", "r")
    deliveryDict = db["DeliveryDict"]
    db.close()
    deliveryList = []

    for key in deliveryDict:
        delivery = deliveryDict.get(key)
        deliveryList.append(delivery)

    return render_template('deliverySellerView.html', deliveryList=deliveryList, count=len(deliveryList), form=status, sessionName=sessionName())

@app.route('/delivery-customer')
@login_required
def retrieveCustomerDelivery():

    deliveryDict = {}
    db = shelve.open("database.db", "r")
    deliveryDict = db["DeliveryDict"]
    db.close()

    deliveryList = []
    for key in deliveryDict:
        delivery = deliveryDict.get(key)
        deliveryList.append(delivery)

    return render_template('deliveryCustView.html', deliveryList=deliveryList, count=len(deliveryList), sessionName=sessionName())

@app.route("/accept-delivery/<id>/", methods=["GET", "POST"])
@login_required
@privilege_required
def acceptDelivery(id):
    form = CompanyForm(request.form)
    if request.method == "POST" and form.validate():
        deliveryDict = {}
        db = shelve.open("database.db", "w")
        deliveryDict = db["DeliveryDict"]

        delivery = deliveryDict.get(id)
        delivery.set_company_name(form.company.data)
        delivery.set_status("Picked up by courier")

        deliveryDict[id] = delivery
        db["DeliveryDict"] = deliveryDict
        db.close()

        return redirect(url_for('retrieveSellerDelivery'))
    return render_template("acceptDelivery.html", form=form, sessionName=sessionName())

@app.route("/update-delivery/<id>/", methods=["GET", "POST"])
@login_required
@privilege_required
def updateDelivery(id):
    statusForm = StatusForm(request.form)
    if request.method == "POST" and statusForm.validate():
        deliveryDict = {}
        db = shelve.open("database.db", "w")
        deliveryDict = db["DeliveryDict"]

        delivery = deliveryDict.get(id)
        delivery.set_status(statusForm.status.data)

        db['DeliveryDict'] = deliveryDict
        db.close()

        return redirect(url_for('retrieveSellerDelivery'))
    else:
        deliveryDict = {}
        db = shelve.open("database.db", "r")
        deliveryDict = db["DeliveryDict"]
        db.close()

        delivery = deliveryDict.get(id)
        statusForm.status.data = delivery.get_status()

        return render_template("deliverySellerView.html", form=statusForm, sessionName=sessionName())

@app.route("/delete-delivery/<id>", methods=["POST"])
@login_required
@privilege_required
def deleteDelivery(id):
    orderDict = {}
    db = shelve.open("database.db", "w")
    orderDict = db["DeliveryDict"]

    # Removing the order
    orderDict.pop(id)
    db["DeliveryDict"] = orderDict
    db.close()

    return redirect(url_for('retrieveSellerDelivery'))


# FAQ
@app.route('/createFAQ', methods=['GET', 'POST'])
@login_required
@privilege_required
def createfaq():
    createfaqForm = FAQForm(request.form)
    if request.method == 'POST' and createfaqForm.validate():
        faqDict = {}
        db = shelve.open('database.db', 'c')
        try:
            faqDict = db['FAQID']
        except:
            print("Error in retrieving Questions from database.db.")
        faq = Models.FAQ(createfaqForm.firstName.data,createfaqForm.lastName.data)
        faqDict[faq.get_FAQID()] = faq
        db['FAQID'] = faqDict

        return redirect(url_for('retrievefaq'))
    return render_template('createFAQ.html', form=createfaqForm, sessionName=sessionName())


@app.route('/retrievefaq')
@login_required
@privilege_required
def retrievefaq():
    faqDict = {}
    db = shelve.open('database.db', 'r')
    faqDict = db['FAQID']
    db.close()

    faqList = []
    for key in faqDict:
        faq = faqDict.get(key)
        faqList.append(faq)

    return render_template('retrieveFAQ.html',faqList=faqList, count=len(faqList), sessionName=sessionName())

@app.route('/DisplayQ')
def DisplayQ():

    faqDict = {}
    db = shelve.open('database.db', 'r')
    faqDict = db['FAQID']
    db.close()

    faqList = []
    for key in faqDict:
        faq = faqDict.get(key)
        faqList.append(faq)
    return render_template('DisplayQ.html',faqList=faqList, count=len(faqList), sessionName=sessionName())


@app.route('/updatefaq/<int:id>/', methods=['GET', 'POST'])
@login_required
@privilege_required
def updatefaq(id):
    updatefaqform = FAQForm(request.form)
    if request.method == 'POST' and updatefaqform.validate():
        faqDict = {}
        db = shelve.open('database.db', 'w')
        faqDict = db['FAQID']
        faq = faqDict.get(id)
        faq.set_firstName(updatefaqform.firstName.data)
        faq.set_lastName(updatefaqform.lastName.data)
        db['FAQID'] = faqDict
        db.close()
        return redirect(url_for('retrievefaq'))
    else:
        faqDict = {}
        db = shelve.open('database.db', 'r')
        faqDict = db['FAQID']
        db.close()
        faq = faqDict.get(id)
        updatefaqform.firstName.data = faq.get_firstName()
        updatefaqform.lastName.data = faq.get_lastName()
        return render_template('updateFAQ.html',form=updatefaqform, sessionName=sessionName())

@app.route('/deleteFAQ/<int:id>', methods=['POST'])
@login_required
@privilege_required
def deletefaq(id):
    faqDict = {}
    db = shelve.open('database.db', 'w')
    faqDict = db['FAQID']
    faqDict.pop(id)
    db['FAQID'] = faqDict
    db.close()
    return redirect(url_for('retrievefaq'))

# User
@app.route('/register', methods=['GET', 'POST'])
def register():
    registerUserForm = RegisterUserForm(request.form)
    if request.method == 'POST' and registerUserForm.validate():
        custDict = {}
        db = shelve.open('database.db', 'c')

        try:
            custDict = db['Users']
        except:
            print("Error in retrieving Users from database.db.")

        userID = str(uuid4())
        user = Models.User(registerUserForm.username.data, userID,
        registerUserForm.userEmail.data, registerUserForm.password.data)
        user.set_role("Customer")
        print(user.get_id(), user.get_name(), user.get_email(), user.get_password())
        custDict[user.get_id()] = user
        db['Users'] = custDict
        db.close()
        return render_template('alert.html')
    return render_template('register.html', form=registerUserForm, sessionName=sessionName())

@app.route('/login', methods=['GET', 'POST'])
def login():
    loginUser = LoginUserForm(request.form)
    if request.method == 'POST' and loginUser.validate():
        custDict = {}
        db = shelve.open('database.db', 'r')
        custDict = db['Users']
        db.close()

        email = loginUser.userEmail.data
        password = loginUser.password.data

        session['username'] = 'Name'
        session['user_role'] = 'Admin'
        isUserExist = True

        if isUserExist:
            return redirect(url_for('home'))
        else:
            return render_template('notsignup.html', sessionName=sessionName())

    return render_template('login.html', form=loginUser, sessionName=sessionName())

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('user_role', None)
    return redirect(url_for('home'))

@app.route('/adduser', methods=['GET', 'POST'])
@login_required
@privilege_required
def addUser():
    createUserForm = AddUserForm(request.form)
    if request.method == 'POST' and createUserForm.validate():
        usersDict = {}
        db = shelve.open('database.db', 'c')
        try:
            usersDict = db['Users']
        except:
            print("Error in retrieving Users from database.db.")

        userID = str(uuid4())
        user = Models.User(createUserForm.username.data, userID,
        createUserForm.userEmail.data, createUserForm.password.data)
        user.set_role(createUserForm.userRole.data)
        usersDict[user.get_id()] = user
        db['Users'] = usersDict
        db.close()

        return redirect(url_for('manageUser'))
    return render_template('addUser.html', form=createUserForm, sessionName=sessionName())

@app.route('/retrieveusers')
@login_required
@privilege_required
def manageUser():
    usersDict = {}
    db = shelve.open('database.db', 'r')
    usersDict = db['Users']
    db.close()

    usersList = []
    for key in usersDict:
        user = usersDict.get(key)
        usersList.append(user)
    return render_template('manageUser.html', usersList=usersList, count=len(usersList), sessionName=sessionName())

@app.route('/updateUser/<id>/', methods=['GET', 'POST'])
@login_required
@privilege_required
def updateUser(id):
    userForm = UpdateUserForm(request.form)
    if request.method == 'POST' and userForm.validate():
        print("it works")
        usersDict = {}
        db = shelve.open('database.db', 'w')
        usersDict = db['Users']

        user = usersDict.get(id)
        user.set_name(userForm.username.data)
        user.set_email(userForm.userEmail.data)
        user.set_role(userForm.userRole.data)

        db['Users'] = usersDict
        db.close()

        return redirect(url_for('manageUser'))

    else:
        usersDict = {}
        db = shelve.open('database.db', 'w')
        usersDict = db['Users']
        db.close()

        user = usersDict.get(id)
        userForm.username.data = user.get_name()
        userForm.userEmail.data = user.get_email()
        userForm.userRole.data = user.get_role()

        return render_template('updateUser.html', form=userForm, sessionName=sessionName())

@app.route('/deleteUser/<id>', methods=['POST'])
@login_required
@privilege_required
def deleteUser(id):
    usersDict = {}
    db = shelve.open('database.db','w')
    usersDict = db['Users']

    usersDict.pop(id)

    db['Users'] = usersDict
    db.close()

    return redirect(url_for('manageUser'))

@app.route('/ChatApp')
def ChatApp():
    return render_template('/ChatApp.html')

def messageRecived():
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageRecived)

if __name__ == "__main__":
    app.run(debug=True)
    socketio.run(app)
