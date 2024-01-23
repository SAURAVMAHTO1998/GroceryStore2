import time
import tasks
from celery.result import AsyncResult
from worker import celery_app
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
import redis
from datetime import datetime, timedelta
import threading
import re

app = Flask(__name__)

ACCESS_EXPIRES = timedelta(minutes=30)  #Configures the expiration time for access tokens.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///groceryDB.sqlite"
app.config["SECRET_KEY"] = "grocerystore"
app.config["JWT_SECRET_KEY"] = "grocerystore"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES

jwt = JWTManager(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, origins=["http://localhost:8081"])

rhost = "localhost"
rport = 6379
rdb = 0
redis_client = redis.StrictRedis(
    host=rhost, port=rport, db=rdb, decode_responses=True)

cel_app = celery_app

class User(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'email': self.email,
            'name': self.name,
        }

    def __repr__(self):
        return f"User(email='{self.email}', name='{self.name}', password='{self.password}')"


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'name': self.name,
        }

    def __repr__(self):
        return f"Category(category_id='{self.category_id}', name='{self.name}')"


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    image_src = db.Column(db.String(100),nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'category.category_id'), nullable=False)
    price = db.Column(db.Integer, default=250, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'imagePath': self.image_src,
            'category_id': self.category_id,
            'price': self.price,
            'stock': self.stock,
        }

    def __repr__(self):
        return f"Product(product_id={self.product_id}, name='{self.name}', " \
               f"image_src='{self.image_src}', category_id={self.category_id}, " \
               f"price={self.price}, stock={self.stock})"


class CustomerCart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer,nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    purchase_time = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'cart_id': self.cart_id,
            'user_email': self.user_email,
            'product_id': self.product_id,
            'category_id':self.category_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'purchase_time': self.purchase_time.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __repr__(self):
        return f"CustomerCart(cart_id={self.cart_id}, user_email='{self.user_email}', " \
               f"product_id={self.product_id},category_id={self.category_id}, quantity={self.quantity}, " \
               f"total_price={self.total_price}, purchase_time={self.purchase_time})"



# Association Table for the many-to-many relationship between Order and Product
order_product_association = db.Table('order_product_association',
    db.Column('order_id', db.Integer, db.ForeignKey('order.order_id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.product_id'))
)

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(50), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_time = db.Column(db.DateTime, nullable=False)
    
    # Define the many-to-many relationship with the Product model
    products = db.relationship('Product', secondary=order_product_association, backref='orders')

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_email': self.user_email,
            'total_price': self.total_price,
            'order_time': self.order_time.strftime('%Y-%m-%d %H:%M:%S'),
            'products': [product.to_dict() for product in self.products]
        }

    def __repr__(self):
        return f"Order(order_id={self.order_id}, user_email='{self.user_email}', " \
               f"total_price={self.total_price}, order_time={self.order_time})"


with app.app_context():
    db.create_all()

"""
    Functions
"""


def validateLogin(name, password):
    if not name:
        raise Exception("Email not provided!")

    if not password:
        raise Exception("Password not provided!")

    check_user = User.query.filter_by(email=name).first()
    if not check_user:
        raise Exception("Name not registered!")

    if not bcrypt.check_password_hash(check_user.password, password):
        raise Exception("Invalid password!")

    # if admin and bool(check_user.admin) == False:
    #     raise Exception("Do not have admin privileges!")

    return check_user.admin

def check_admin(current_user):
    try:
        user = User.query.filter_by(email=current_user).first()
        if not user or not user.admin:
            raise Exception("User does not have admin privileges!")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

"""
    Celery Jobs
"""


def email_job():
    while True:
        print("New Email Job Loop!")
        with app.app_context():
            users = User.query.all()
            for user in users:
                last_purchase = CustomerCart.query.filter_by(user_email=user.email).order_by(
                    CustomerCart.purchase_time.desc()).first()
                if last_purchase is None:
                    tasks.email_task.delay(user.to_dict(), None)
                else:
                    tasks.email_task.delay(
                        user.to_dict(), last_purchase.purchase_time)
        time.sleep(60*10)


def user_monthly_report_job():
    while True:
        print("New User Monthly Report Job Loop!")
        with app.app_context():
            now = datetime.datetime.now()
            if now.day == 13:
                users = User.query.all()
                for user in users:

                    start_date = datetime.datetime(now.year, now.month, 1)
                    if now.month == 12:
                        end_date = datetime.datetime(now.year + 1, 1, 1)
                    else:
                        end_date = datetime.datetime(
                            now.year, now.month + 1, 1)

                    monthly_purchase = CustomerCart.query.filter_by(user_email=user.email).filter(
                        CustomerCart.purchase_time >= start_date,
                        CustomerCart.purchase_time < end_date).all()

                    if len(monthly_purchase) > 0:
                        res = []
                        for  product in monthly_purchase:
                            product = Product.query.filter_by(
                                product_id=customercart.product_id).first()
                            customercart_dict = dict()
                            customercart_dict.update({"product_name": product.name})
                            customercart_dict.update(
                                {"purchase_time": customercart.purchase_time.strftime('%d %B, %Y')})
                            res.append(customercart_dict)

                        tasks.monthly_report.delay(
                            user.to_dict(), res, now.strftime('%B'), now.strftime('%Y'))
        time.sleep(60*10)




"""
    User Endpoints
"""

@app.route('/', methods=['GET'])
def index():
    return "Madras Grocery  API"



"""
    User Authentication Endpoints
"""

@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        # source = request.json.get('source', False)

        source=validateLogin(email, password)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    access_token = create_access_token(identity=email)
    print("source ")
    print(source)
    # if source:
    #     return jsonify(access_token=access_token, admin=True), 200
    # return jsonify(access_token=access_token), 200
    return jsonify(access_token=access_token, admin=source), 200

@app.route('/signup', methods=['POST'])
def signup():
    try:
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        name = request.json.get('name', None)

        if not email:
            raise Exception("Email not provided!")

        if not bool(re.fullmatch(r'^[\w.]+@[\w.]+[.]+[\w.]+', email)):
            raise Exception("Invalid email address!")

        if not password:
            raise Exception("Password not provided!")
        
        if len(password) < 8:
            raise Exception("Your password must be at least 8 characters!")

        if not name:
            raise Exception("Name not provided!")
        
        check_user = User.query.filter_by(email=email).first()

        if check_user:
            raise Exception("Email is already in use!")
        
        has_uppercase = False
        has_lowercase = False
        has_digit = False
        has_special = False
        allowed_Schars = ['!', '@', '#', '$', '%']

        for char in password:
            if char.isupper():
                has_uppercase = True
            elif char.islower():
                has_lowercase = True
            elif char.isdigit():
                has_digit = True
            elif char in allowed_Schars:
                has_special = True
        if not (has_uppercase and has_lowercase and has_digit and has_special):
            raise Exception(
                "Invalid Password! Your password must contain a capital letter/ number/ special character.")

        password = bcrypt.generate_password_hash(password)
        
        # ... (previous signup validation code)

        if request.json.get('adminkey', None) == "adminKey":
            new_user = User(email=email, name=name, password=password, admin=True)
        else:
            new_user = User(email=email, name=name, password=password)

        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "User Registered!"}), 200



@app.route('/addtocart', methods=['POST'])
@jwt_required()
def add_to_cart():
    try:
        current_user = get_jwt_identity()
        user_data = User.query.filter_by(email=current_user).first()
        
        product_id = request.json.get('product_id', None)
        quantity = int(request.json.get('quantity', 0))

        # Retrieve the product from the database
        product = Product.query.filter_by(product_id=product_id).first()

        # Check if the product exists
        if not product:
            raise Exception("Product not found!")
        product_price = float(product.price)
        total_price = quantity * product_price

        category_id=product.category_id

        if not category_id or not product_id or not quantity:
            raise Exception("Incomplete information for adding to cart!")

        if not user_data:
            raise Exception("User not found!")

        new_cart = CustomerCart(user_email=current_user,
                                category_id=category_id, product_id=product_id,quantity=quantity,
                                 total_price=total_price, purchase_time=datetime.now())

        db.session.add(new_cart)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "item added to cart!"}), 200

@app.route('/cart/get', methods=['GET'])
@jwt_required()
def get_cart_items():
    try:
        current_user = get_jwt_identity()
        user_data = User.query.filter_by(email=current_user).first()

        if not user_data:
            raise Exception("User not found!")

        cart_items = db.session.query(CustomerCart, Product, Category).filter(
            CustomerCart.user_email == current_user).filter(CustomerCart.product_id == Product.product_id).filter(CustomerCart.category_id == Category.category_id).all()

        cart_data = []

        for cart, product, category in cart_items:
            item = {
                "cart_id":cart.cart_id,
                "product_name": product.name,
                "product_id":product.product_id,
                "category_name": category.name,
                "quantity": cart.quantity,
                "price":cart.total_price,
            }
            cart_data.append(item)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(cart_items=cart_data), 200

@app.route('/cart/delete_all', methods=['POST'])
@jwt_required()
def delete_all_cart_items():
    try:
        current_user_email = get_jwt_identity()
        user_data = User.query.filter_by(email=current_user_email).first()

        if not user_data:
            raise Exception("User not found!")

        # Delete all cart items for the current user
        CustomerCart.query.filter_by(user_email=current_user_email).delete()

        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='All cart items deleted!'), 200

@app.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    redis_client.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify(msg='Successfully logged out'), 200

@app.route('/search', methods=['GET'])
def search_products():
    try:
        query = request.args.get('query', None)

        if not query:
            raise Exception("Search query not provided!")

        # Perform a case-insensitive search in product names
        products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
        search_results = [product.to_dict() for product in products]

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(search_results=search_results), 200



"""
    Admin Endpoints
"""

# User Management

@app.route('/admin/user/get', methods=['GET'])
@jwt_required()
def admin_get_users():
    current_user = get_jwt_identity()
    check_admin(current_user)

    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return jsonify(users=user_list), 200


@app.route('/user/create', methods=['POST'])
@jwt_required()
def admin_create_user():
    current_user = get_jwt_identity()
    check_admin(current_user)

    email = request.json.get('email', None)
    name = request.json.get('name', None)
    password = request.json.get('password', None)
    admin_status = request.json.get('admin', False)

    try:
        if not email or not name or not password:
            raise Exception("Incomplete user information!")
        password = bcrypt.generate_password_hash(password)
        new_user = User(email=email, name=name, password=password, admin=admin_status)
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='User Created!'), 200


# Category Management

@app.route('/category/get', methods=['GET'])
@jwt_required()
def admin_get_categories():
    current_user = get_jwt_identity()
    check_admin(current_user)

    categories = Category.query.all()
    category_list = [category.to_dict() for category in categories]
    return jsonify(categories=category_list), 200


@app.route('/category/create', methods=['POST'])
@jwt_required()
def admin_create_category():
    current_user = get_jwt_identity()
    check_admin(current_user)

    name = request.json.get('name', None)

    try:
        if not name:
            raise Exception("Category Name not provided!")

        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='Category Created!'), 200


# Product Management

@app.route('/product/get', methods=['GET'])
@jwt_required()
def admin_get_products():
    current_user = get_jwt_identity()
    check_admin(current_user)

    products = Product.query.all()
    product_list = [product.to_dict() for product in products]
    return jsonify(products=product_list), 200


@app.route('/product/create', methods=['POST'])
@jwt_required()
def admin_create_product():
    current_user = get_jwt_identity()
    check_admin(current_user)

    name = request.json.get('name', None)
    image_src = request.json.get('image_src', None)
    category_id = request.json.get('category_id', None)
    price = request.json.get('price', 250)
    stock = request.json.get('stock', 0)

    try:
        if not name or not category_id:
            raise Exception("Incomplete product information!")

        new_product = Product(name=name, image_src=image_src, category_id=category_id, price=price, stock=stock)
        db.session.add(new_product)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='Product Created!'), 200

@app.route('/category/delete', methods=['POST'])
@jwt_required()
def category_delete():
    category_id = request.json.get('category_id', None)

    try:
        if not category_id:
            raise Exception("Category ID not provided!")

        category = Category.query.filter_by(category_id=category_id).first()
        if not category:
            raise Exception("Venue not found!")

        Product.query.filter_by(category_id=category_id).delete()

        db.session.delete(category)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='Category Deleted!'), 200

@app.route('/product/delete', methods=['POST'])
@jwt_required()
def product_delete():
    product_id = request.json.get('product_id', None)

    try:
        if not product_id:
            raise Exception("Product ID not provided!")

        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            raise Exception("Product not found!")

        db.session.delete(product)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='Product Deleted!'), 200

# # Update Category

@app.route('/category/update', methods=['POST'])
@jwt_required()
def admin_update_category():
    current_user = get_jwt_identity()
    check_admin(current_user)

    category_id = request.json.get('category_id', None)
    name = request.json.get('name', None)

    try:
        if not category_id:
            raise Exception("Category ID not provided!")
        if not name:
            raise Exception("Category Name not provided!")

        category = Category.query.filter_by(category_id=category_id).first()
        if not category:
            raise Exception("Category not found!")

        category.name = name
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='Category Updated!'), 200

@app.route('/cart/delete', methods=['POST'])
@jwt_required()
def cart_delete():
    current_user_email = get_jwt_identity()
    cart_id = request.json.get('cart_id', None)

    try:
        if not cart_id:
            raise Exception("Cart ID not provided!")

        cart_item = CustomerCart.query.filter_by(cart_id=cart_id, user_email=current_user_email).first()
        if not cart_item:
            raise Exception("Cart item not found or does not belong to the user!")

        db.session.delete(cart_item)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='Cart item deleted!'), 200

# # Update Product

@app.route('/product/update', methods=['POST'])
@jwt_required()
def admin_update_product():
    current_user = get_jwt_identity()
    check_admin(current_user)

    product_id = request.json.get('product_id', None)
    name = request.json.get('name', None)
    image_src = request.json.get('image_src', None)
    category_id = request.json.get('category_id', None)
    price = request.json.get('price', None)
    stock = request.json.get('stock', None)

    try:
        if not product_id:
            raise Exception("Product ID not provided!")
        if not name:
            raise Exception("Product Name not provided!")
    
        if not category_id:
            raise Exception("Category ID not provided!")

        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            raise Exception("Product not found!")

        product.name = name
        product.image_src = image_src
        product.category_id = category_id

        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock

        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='Product Updated!'), 200

@app.route('/order/create', methods=['POST'])
@jwt_required()
def create_order():
    try:
        current_user_email = get_jwt_identity()
        user_data = User.query.filter_by(email=current_user_email).first()

        if not user_data:
            raise Exception("User not found!")

        data = request.json
        product_ids = data.get('product_ids', [])
        
        # Retrieve products based on the provided product IDs
        products = Product.query.filter(Product.product_id.in_(product_ids)).all()

        if not products:
            raise Exception("No valid products provided!")

        # Calculate the total price based on the selected products
        total_price = sum(product.price for product in products)

        # Create a new order
        new_order = Order(
            user_email=current_user_email,
            total_price=total_price,
            order_time=datetime.now() 
        )

        # Associate products with the order
        new_order.products.extend(products)

        db.session.add(new_order)
        db.session.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(msg='Order created successfully!', order_id=new_order.order_id), 201

@app.route('/order/history', methods=['GET'])
@jwt_required()
def get_order_history():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            raise Exception("User not found!")

        orders = Order.query.filter_by(user_email=current_user).order_by(Order.order_time.desc()).all()

        order_data = []

        for order in orders:
            order_data.append(order.to_dict())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(orders=order_data), 200

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Convert the order_time to a string for JSON serialization
        order.order_time = order.order_time.strftime('%Y-%m-%d %H:%M:%S')

        # Convert products to a list of dictionaries for JSON serialization
        products = [{'product_id': product.product_id,
                     'name': product.name,
                     'quantity': 1,  # You might need to adjust this based on your actual data
                     'price': product.price} for product in order.products]

        order_dict = {
            'order_id': order.order_id,
            'user_email': order.user_email,
            'total_price': order.total_price,
            'order_time': order.order_time,
            'products': products,
        }

        return jsonify(order_dict), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    t1 = threading.Thread(target=email_job)
    t1.daemon = True
    t1.start()
    t2 = threading.Thread(target=user_monthly_report_job)
    t2.daemon = True
    t2.start()
    app.run(debug=True, port=5002)