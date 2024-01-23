# pyright: reportMissingImports=false, reportMissingModuleSource=false
# .\venv\Scripts\activate
# celery -A main:cel_app worker -l INFO -P gevent


# sudo service redis-server start
# redis-cli
from datetime import datetime, timedelta
from email.message import EmailMessage
import smtplib
import ssl
from worker import celery_app
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import csv

templates_path = os.path.join(os.path.dirname(__file__), "templates")

env = Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=select_autoescape()
)


email_body1 = """ Hey {},

We hope you've been enjoying shopping with us at GroceryMart! We value your patronage and want to ensure you never miss out on the best grocery deals.
We've noticed that it's been a while since your last purchase. Don't miss the chance to explore our latest products and offers. As a valued customer, we have an exclusive offer waiting for you:

🎉 Get a 10% discount on your next purchase! 🛒

Whether it's fresh produce, pantry essentials, or household items, we have a wide variety for you to choose from. Our high-quality products and excellent service await you.

Here's how to claim your discount:

1. Visit our website at http://localhost:8000/
2. Browse our selection of products and categories.
3. Add your preferred items to your cart.
4. Use the promo code: GROCERY10 at checkout.

This offer is valid for a limited time, so don't wait too long to place your order. Treat yourself to quality groceries and enjoy the convenience of online shopping.

Shop now: http://localhost:8000/products
Thank you for choosing GroceryMart. We look forward to serving you again soon!

Best regards,
The GroceryMart Team
"""

email_body2 = """ Hey {},

We're delighted to have you as a loyal customer at GroceryMart! You've recently made a purchase with us, and we're here to let you know that the savings continue.

🛍️ Explore our latest products and special offers! 🎁

Whether you're looking for fresh produce, pantry staples, or household necessities, we have everything you need. Our user-friendly platform and reliable delivery service are ready to provide you with another seamless shopping experience.

Visit our website today to discover the latest deals and add your favorite items to your cart. Enjoy the convenience of online grocery shopping!

Explore products: http://localhost:8000/products
Thank you for choosing GroceryMart. We can't wait to serve you again!

Best regards,
The GroceryMart Team
"""

@celery_app.task
def send_email(receiver_email, subject, message, html=None):
    try:
        email_sender = "grocerymart@gmail.com"  # Update with your grocery app email
        email_password = "your_email_password"  # Update with your email password

        em = EmailMessage()
        em['From'] = receiver_email
        em['To'] = email_sender
        em['Subject'] = subject

        if html:
            em.set_content("Please enable HTML to view this email.")
            em.add_alternative(html, subtype='html')
        else:
            em.set_content(message)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, receiver_email, em.as_string())
    except Exception as e:
        return str(e)

    return "Successfully sent email"

@celery_app.task
def grocery_email_task(user, last_purchase):
    if last_purchase:
        now = datetime.now()
        time_since_last_purchase = now - last_purchase
        if time_since_last_purchase <= timedelta(minutes=1):
            return "Active User"
        else:
            email_subject = f"🛒 Welcome Back to GroceryMart, {user['name']}!"
            res = send_email(user["email"], email_subject, email_body2.format(user["name"]))
            return res
    else:
        email_subject = f"🎉 Exclusive Offer: Enjoy 10% Off Your Next Purchase, {user['name']}!"
        res = send_email(user["email"], email_subject, email_body1.format(user["name"]))
        return res

@celery_app.task
def monthly_report(user, purchases, month, year):
    if purchases:
        email_subject = f"📅 Monthly Purchase Report - {user['name']}"
        template = env.get_template("purchase_report_template.html")
        html = template.render(month=month, year=year, purchases=purchases)
        res = send_email(user["email"], email_subject, None, html)
        return res
    return "No purchases found"

@celery_app.task
def export_csv(name, purchase_data):
    if purchase_data:
        filepath = "./exports/"+name+".csv"
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = purchase_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in purchase_data:
                writer.writerow(data)
        return "CSV Exported"
    return "No purchases found"

