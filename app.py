from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Дані для Telegram
TELEGRAM_BOT_TOKEN = '8335298638:AAGctNiOZVyWtbH_hXmz2jedO_lv50YufA0'
TELEGRAM_CHAT_ID = '1938781744'

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            old_price REAL,
            image TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            # Сережки (50 грн)
            ('Сережки «Перлинний бантик»', 'Сережки', 50.0, None, 'earrings_bows.jpg', 'Ніжні сережки у вигляді акуратних бантиків з перлин. Доступні в будь-яких кольорах на ваш вибір'),
            ('Класичні перлинні сережки', 'Сережки', 50.0, None, 'earrings_classic.jpg', 'Елегантні сережки з перлинними намистинами для щоденного образу. Доступні в будь-яких кольорах на ваш вибір'),
            ('Сережки «Перлинні шпильки»', 'Сережки', 50.0, None, 'earrings_pins.jpg', 'Витончені сережки-підвіски ручної роботи. Доступні в будь-яких кольорах на ваш вибір'),
            ('Фіолетові перлинні сережки', 'Сережки', 50.0, None, 'earrings_purple.jpg', 'Яскраві та оригінальні сережки з акцентом. Доступні в будь-яких кольорах на ваш вибір'),
            ('Сережки з перлинною стрічкою', 'Сережки', 50.0, None, 'earrings_ribbon.jpg', 'Романтичні сережки ручної роботи. Доступні в будь-яких кольорах на ваш вибір'),
            ('Сережки «Серця»', 'Сережки', 50.0, None, '5269689310875690636.jpg', 'Милі сережки у формі сердечок. Доступні в будь-яких кольорах на ваш вибір'),
            ('Сережки «Зірочки»', 'Сережки', 50.0, None, '5271941110689374157.jpg', 'Стильні золотисті сережки-зірочки. Доступні в будь-яких кольорах на ваш вибір'),
            
            # Брелоки (60 грн)
            ('Брелок «Перлинний бант»', 'Брелоки', 60.0, None, 'keychain_bow.jpg', 'Стильний брелок із перлин у формі бантика для ключів чи сумочки. Доступний в будь-яких кольорах на ваш вибір'),
            ('Брелок «Ніжність»', 'Брелоки', 60.0, None, 'keychain_ribbon.jpg', 'Елегантний брелок з перлинами та атласною стрічкою. Доступний в будь-яких кольорах на ваш вибір'),
            
            # Браслети (30 грн)
            ('Браслет із резинок', 'Аксесуари', 30.0, None, '5269689310875690472.jpg', 'Яскраві та зручні браслети ручної роботи з резинок. Доступні в будь-яких кольорах на ваш вибір'),
            
            # Кільця (40 грн за шт)
            ('Кільце ручної роботи', 'Аксесуари', 40.0, None, '5271941110689374155.jpg', 'Стильне мінімалістичне кільце. Доступне в будь-яких кольорах на ваш вибір'),

            # Сумки (240–300 грн)
            ('В’язана сумка', 'Сумки', 240.0, None, '5269689310875690236.jpg', 'М’яка та стильна в’язана сумка ручної роботи з плюшевої пряжі. Доступна в будь-яких кольорах на ваш вибір'),
            ('В’язана сумка з ланцюжком', 'Сумки', 300.0, None, '5269689310875690243.jpg', 'Елегантна в’язана сумка, прикрашена стильним ланцюжком. Доступна в будь-яких кольорах на ваш вибір'),
            ('В’язана сумка зі зіркою та бантом', 'Сумки', 300.0, None, '5269689310875690247.jpg', 'Оригінальна сумочка ручної роботи з декором зірки та банта. Доступна в будь-яких кольорах на ваш вибір'),

            # Аксесуари
            ('Повязка на голову', 'Аксесуари', 140.0, None, '5271941110689374152.jpg', 'М’яка і затишна пухнаста повязка. Доступна в будь-яких кольорах на ваш вибір'),
            ('Мітенки', 'Аксесуари', 170.0, None, '5271941110689374153.jpg', 'Теплі та милі в’язані мітенки ручної роботи. Доступні в будь-яких кольорах на ваш вибір'),

            # Подарункові бокси
            ('Маленький подарунковий бокс', 'Бокси', 120.0, None, '5269689310875690589.jpg', 'Містить 3-6 чудових подарунків-сюрпризів. Доступний у будь-яких кольорах та наповненні'),
            ('Стандартний подарунковий бокс', 'Бокси', 250.0, None, '5269689310875690589.jpg', 'Містить 7-10 чудових подарунків-сюрпризів. Доступний у будь-яких кольорах та наповненні'),
            ('Великий подарунковий бокс', 'Бокси', 330.0, None, '5269689310875690589.jpg', 'Містить 10-14 чудових подарунків-сюрпризів. Доступний у будь-яких кольорах та наповненні'),
            ('XXL подарунковий бокс', 'Бокси', 400.0, None, '5269689310875690589.jpg', 'Великий набір з 15-20 подарунків. Доступний у будь-яких кольорах та наповненні'),

            # Кросівки (Акційні пропозиції)
            ('Кросівки Slazenger', 'Акційні пропозиції', 999.0, 1500.0, '5269689310875690593.jpg', 'Стильні та зручні фірмові кросівки білого кольору з рожевими акцентами. Розмір: 34 (акційна пропозиція)')
        ]
        cursor.executemany('INSERT INTO products (title, category, price, old_price, image, description) VALUES (?, ?, ?, ?, ?, ?)', sample_products)
        conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    selected_category = request.args.get('category')
    
    categories = [row['category'] for row in conn.execute('SELECT DISTINCT category FROM products').fetchall()]
    
    if selected_category:
        products = conn.execute('SELECT * FROM products WHERE category = ?', (selected_category,)).fetchall()
    else:
        products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template('index.html', products=products, categories=categories, selected_category=selected_category, cart_count=cart_count)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if not product:
        return "Товар не найден", 404
    
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template('product_detail.html', product=product, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    conn = get_db_connection()
    cart_items = []
    total_price = 0
    
    for prod_id, qty in cart.items():
        product = conn.execute('SELECT * FROM products WHERE id = ?', (prod_id,)).fetchone()
        if product:
            item_total = product['price'] * qty
            total_price += item_total
            cart_items.append({
                'product': product,
                'qty': qty,
                'item_total': item_total
            })
    conn.close()
    
    cart_count = sum(cart.values())
    return render_template('cart.html', cart_items=cart_items, total_price=total_price, cart_count=cart_count)

@app.route('/update_cart/<int:product_id>/<action>', methods=['POST'])
def update_cart(product_id, action):
    cart = session.get('cart', {})
    prod_id_str = str(product_id)
    if prod_id_str in cart:
        if action == 'increase':
            cart[prod_id_str] += 1
        elif action == 'decrease':
            cart[prod_id_str] -= 1
            if cart[prod_id_str] <= 0:
                del cart[prod_id_str]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/order', methods=['GET', 'POST'])
def order():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart'))
        
    conn = get_db_connection()
    cart_items = []
    total_price = 0
    
    for prod_id, qty in cart.items():
        product = conn.execute('SELECT * FROM products WHERE id = ?', (prod_id,)).fetchone()
        if product:
            item_total = product['price'] * qty
            total_price += item_total
            cart_items.append({
                'product': product,
                'qty': qty,
                'item_total': item_total
            })
    conn.close()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        location = request.form.get('location')
        meeting_date = request.form.get('meeting_date')
        meeting_time = request.form.get('meeting_time')
        payment = request.form.get('payment')
        
        message = f"🛍 <b>Нове замовлення!</b>\n\n" \
                  f"👤 <b>Ім'я:</b> {full_name}\n" \
                  f"📞 <b>Телефон:</b> {phone}\n" \
                  f"📍 <b>Місце зустрічі:</b> {location}\n" \
                  f"📅 <b>Дата:</b> {meeting_date} о {meeting_time}\n" \
                  f"💳 <b>Оплата:</b> {'Картка' if payment == 'card' else 'Готівка'}\n\n" \
                  f"📦 <b>Товари:</b>\n"
                  
        for item in cart_items:
            message += f"— {item['product']['title']} (×{item['qty']}) — {item['item_total']} грн.\n"
            
        message += f"\n💰 <b>Загальна сума:</b> {total_price} грн."
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Помилка відправки в Telegram: {e}")
            
        session.pop('cart', None)
        
        return render_template('order_success.html', 
                               full_name=full_name, 
                               phone=phone, 
                               total_price=total_price, 
                               payment=payment)

    cart_count = sum(cart.values())
    return render_template('order.html', cart_items=cart_items, total_price=total_price, cart_count=cart_count)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)