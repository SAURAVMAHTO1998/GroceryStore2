# pyright: reportMissingImports=false, reportMissingModuleSource=false
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///groceryDB.sqlite"
db = SQLAlchemy(app)

class User(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"User(email='{self.email}', name='{self.name}', password='{self.password}', language='{self.language}')"


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Category(category_id={self.category_id}, name='{self.name}')"


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    manufacture_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    rate_per_unit = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False)  # e.g., 'Rs/Kg', 'Rs/Litre'
    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id), nullable=False)

    def __repr__(self):
        return f"Product(product_id={self.product_id}, name='{self.name}', " \
               f"manufacture_date={self.manufacture_date}, expiry_date={self.expiry_date}, " \
               f"rate_per_unit={self.rate_per_unit}, unit='{self.unit}', category_id={self.category_id})"


class CustomerCart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(50), db.ForeignKey(User.email), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.product_id), nullable=False)
    purchase_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"CustomerCart(cart_id={self.cart_id}, user_email='{self.user_email}', " \
               f"category_id={self.category_id}, product_id={self.product_id}, " \
               f"purchase_time={self.purchase_time})"


with app.app_context():
    db.create_all()
