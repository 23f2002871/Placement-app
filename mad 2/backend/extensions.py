from flask_caching import Cache
from flask_mail import Mail

# Creating the objects here so they can be imported anywhere
cache = Cache()
mail = Mail()