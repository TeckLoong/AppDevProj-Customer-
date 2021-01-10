from wtforms import Form, StringField, IntegerField, DecimalField, DateField, RadioField, SelectField, TextAreaField, validators, PasswordField

class CompanyForm(Form):
    company = SelectField("Delivery Company", [validators.DataRequired()], choices=[('','Select company'), ('SP','SingPost'), ('Qx', 'Qxpress'),('TQ','TaQbin'), ('UP', 'UParcel'),('LalaM','Lalamove'), ('GV', 'Gogovan')])

class StatusForm(Form):
    status = SelectField("", [validators.DataRequired()], choices=[("",'Select Status'), ('Awaiting Delivery','Awaiting Delivery'), ('Picked up by courier','Picked up by courier'), ('Delivered', 'Delivered')])

class ProductForm(Form):
    title = StringField(u'Title', [validators.Length(min=1, max=150), validators.DataRequired()])
    description = TextAreaField(u'Description', [validators.Length(min=1, max=1000), validators.Optional()])
    quantity = IntegerField(u'Quantity', [validators.DataRequired("Enter Integer only")])
    price = DecimalField(u'Price', [validators.DataRequired("Enter numbers only")], places=2)
    publisher = StringField(u'Publisher', [validators.Length(min=1, max=150), validators.DataRequired()])
    author = StringField(u'Author', [validators.Length(min=1, max=150), validators.DataRequired()])
    category = SelectField(u'Category', choices=[
        ('Graphic Novels', 'Graphic Novel'), ('Health', 'Health'), ('Technology', 'Technology'), 
        ('Cooking', 'Cooking'), ('History', 'History'), ('Fiction', 'Fiction'),
        ('Art', 'Art'), ('Science', 'Science'), ('Lifestyle', 'Lifestyle'), ('Sports', 'Sport')
        ])
    language = SelectField(u'Language', choices=[('English', 'English'), ('Chinese', 'Chinese'), ('German', 'German'),
        ('French', 'French'), ('Japanese', 'Japanese'), ('Korean', 'Korean'),])
    p_format = SelectField(u'Format', choices=[('Hardback', 'Hardback'), ('Paperback', 'Paperback')])
    pages = IntegerField(u'Pages', [validators.DataRequired("Enter Integer only")])

class OrderForm(Form):
    firstName = StringField(u'First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    lastName = StringField(u'Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    address1 = StringField(u'Address 1', [validators.Length(min=1, max=250), validators.DataRequired()])
    address2 = StringField(u'Address 2')
    country = SelectField(u'Country', [validators.DataRequired()], choices=[('Singapore', 'Singapore'),
        ('Malaysia', 'Malaysia'), ('Thailand', 'Thailand'), ('Vietnam', 'Vietnam'), ('Indonesia', 'Indonesia'),
        ('Australia', 'Australia'), ('New Zealand', 'New Zealand'), ('Cambodia', 'Cambodia')])
    state = StringField(u'State/Province', [validators.Length(min=1, max=150), validators.DataRequired()])
    city = StringField(u'City', [validators.Length(min=1, max=150), validators.DataRequired()])
    postcode = IntegerField(u'Postcode/Zip', [validators.DataRequired("Enter Integer only")])

class FAQForm(Form):
 firstName = StringField('Question', [validators.Length(min=1,max=150), validators.DataRequired()])
 lastName = StringField('Answer', [validators.Length(min=1,max=150), validators.DataRequired()])

class AddUserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=50), validators.DataRequired()])
    userEmail = StringField('Email', [validators.DataRequired()])
    userRole = SelectField('Role', choices=[("Admin", "Admin"), ("Seller", "Seller"), ("Support", "Support")])
    password = PasswordField('Password', [validators.Length(min=6, max=50), validators.DataRequired()])
    retypePassword = PasswordField('Retype Password', [validators.Length(min=6, max=50), validators.DataRequired()])

class UpdateUserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=50), validators.DataRequired()])
    userEmail = StringField('Email', [validators.DataRequired()])
    userRole = SelectField('Role', choices=[("Admin", "Admin"), ("Seller", "Seller"), ("Support", "Support")])

class RegisterUserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=50), validators.DataRequired()])
    userEmail = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6, max=50), validators.DataRequired()])

class LoginUserForm(Form):
    userEmail = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6, max=50), validators.DataRequired()])

