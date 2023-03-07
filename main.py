from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout

app = Flask(__name__)
with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # pozwala nam zrobić ustawienia w bazie danych
    db = SQLAlchemy(app) # dołączamy naszą aplikację do db

# Tablica:
# id  title  price   isActive
# 1   some    100     True
# 2   some2   200     False
# 3   some3   40      True

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True) # zapisujemy tutaj tylko liczbę
    # primery_key=True oznacza, że przy dodawaniu nowego zapisu będzie automatycznie aktualizować się
    title = db.Column(db.String(100), nullable=False) # (100) można umieścić maksymanlnie 100 znaków. nullable=False - oznacza, że pole nie może być pustym.
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    # text = db.Column(db.Text, nullable=False)# Text nie ogranicza nas w liczbie znaków, niż jak to robi "String", które ma maks 250.

    def __repr__(self):
        return self.title
    # [krakow, aloha, privet, aaaa, uhu, Pracownik restauracji, Pracownik restauracji, wroclaw]

# Tworzenie pliku shop.db
# >>>Otwieramy terminal
# >>>python
# >>> from main import app,db
# >>> app.app_context().push()
# >>> db.create_all()
# >>> exit()
    

@app.route('/') 
# Декораторы @ — это, по сути, "обёртки", которые дают нам возможность изменить поведение функции, не изменяя её код. 
# Отслеживанием главной страницы будет дорога ('/').
def home_page():
    items = Item.query.order_by(Item.price).all() # Item.price - będzie sortowanie po cenie
    return render_template('sklep.html', data=items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)
    api = Api(merchant_id=1396424,
          secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "PLN",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)
    

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
         title_in_form = request.form['title']
         price_in_form = request.form['price']
         item = Item(title=title_in_form, price=price_in_form)
         try:
             db.session.add(item)
             db.session.commit()
             return redirect('/')#  wysyłamy na główną stronę
         except:
             return "Błąd"
    else:
        return render_template('create.html')

if __name__ == "__main__":
    app.run(debug=True)