import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATA_DIR = 'data'

# Осигуряване, че директорията съществува
os.makedirs(DATA_DIR, exist_ok=True)

# Файлове
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
CARTS_FILE = os.path.join(DATA_DIR, 'carts.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')


# Инициализация на файлове с празни списъци
def init_files():
    for file in [USERS_FILE, PRODUCTS_FILE, CARTS_FILE, ORDERS_FILE]:
        if not os.path.exists(file):
            with open(file, 'w', encoding='utf-8') as f:
                json.dump([], f)


# Помощни функции за четене/запис
def read_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_data(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ------ ПОТРЕБИТЕЛИ ------
def get_all_users():
    return read_data(USERS_FILE)


def save_user(username, password, email):
    users = get_all_users()
    user_id = len(users) + 1
    users.append({
        'id': user_id,
        'username': username,
        'password': generate_password_hash(password),
        'email': email,
        'created_at': datetime.now().isoformat()
    })
    write_data(USERS_FILE, users)
    return user_id


def find_user_by_username(username):
    users = get_all_users()
    for user in users:
        if user['username'] == username:
            return user
    return None


def verify_user(username, password):
    user = find_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None


# ------ ПРОДУКТИ ------
def get_all_products():
    products = read_data(PRODUCTS_FILE)
    if not products:  # Добавяне на примерни продукти
        products = [
            {'id': 1, 'name': 'Розов хидратиращ крем', 'price': 32.99, 'category': 'Кремове', 'image_url': '',
             'description': 'Нежен крем с роза и хиалуронова киселина за дълбока хидратация'},
            {'id': 2, 'name': 'Лавандулов серум', 'price': 45.50, 'category': 'Серуми', 'image_url': '',
             'description': 'Успокояващ серум с лавандула и витамин Е'},
            {'id': 3, 'name': 'Ексфолиращ скраб със захар', 'price': 24.99, 'category': 'Ексфолианти', 'image_url': '',
             'description': 'Нежен скраб със захар и кокосово масло'},
            {'id': 4, 'name': 'Комплект "Розова мечта"', 'price': 89.99, 'category': 'Сетове', 'image_url': '',
             'description': 'Пълен сет: крем, серум и тоник за перфектна грижа'},
            {'id': 5, 'name': 'Витамин С осветляваща маска', 'price': 28.50, 'category': 'Маски', 'image_url': '',
             'description': 'Осветляваща маска с витамин С и екстракт от портокал'},
            {'id': 6, 'name': 'Черен чай anti-aging концентрат', 'price': 55.00, 'category': 'Серуми', 'image_url': '',
             'description': 'Антивъзрастов серум с черен чай и пептиди'},
            {'id': 7, 'name': 'Захарна полировка за лице', 'price': 29.99, 'category': 'Ексфолианти', 'image_url': '',
             'description': 'Нежна ексфолираща полировка с фини захарни кристали'},
        ]
        write_data(PRODUCTS_FILE, products)
    return products


def get_product_by_id(product_id):
    products = get_all_products()
    for product in products:
        if product['id'] == product_id:
            return product
    return None


# ------ КОЛИЧКА ------
def get_cart(user_id):
    carts = read_data(CARTS_FILE)
    for cart in carts:
        if cart['user_id'] == user_id:
            return cart
    return None


def add_to_cart(user_id, product_id, quantity=1):
    carts = read_data(CARTS_FILE)
    cart = get_cart(user_id)

    if not cart:
        cart = {'user_id': user_id, 'items': []}
        carts.append(cart)

    for item in cart['items']:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            write_data(CARTS_FILE, carts)
            return True

    cart['items'].append({'product_id': product_id, 'quantity': quantity})
    write_data(CARTS_FILE, carts)
    return True


def remove_from_cart(user_id, product_id):
    carts = read_data(CARTS_FILE)
    cart = get_cart(user_id)
    if cart:
        cart['items'] = [item for item in cart['items'] if item['product_id'] != product_id]
        write_data(CARTS_FILE, carts)
        return True
    return False


def update_cart_item(user_id, product_id, quantity):
    if quantity <= 0:
        return remove_from_cart(user_id, product_id)

    carts = read_data(CARTS_FILE)
    cart = get_cart(user_id)
    if cart:
        for item in cart['items']:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                write_data(CARTS_FILE, carts)
                return True
    return False


def clear_cart(user_id):
    carts = read_data(CARTS_FILE)
    carts = [cart for cart in carts if cart['user_id'] != user_id]
    write_data(CARTS_FILE, carts)
    return True


# ------ ПОРЪЧКИ ------
def create_order(user_id, total_amount, items):
    orders = read_data(ORDERS_FILE)
    order_id = len(orders) + 1
    order = {
        'id': order_id,
        'user_id': user_id,
        'total': total_amount,
        'items': items,
        'date': datetime.now().isoformat(),
        'status': 'pending'
    }
    orders.append(order)
    write_data(ORDERS_FILE, orders)
    return order_id


def get_user_orders(user_id):
    orders = read_data(ORDERS_FILE)
    return [order for order in orders if order['user_id'] == user_id]


# Инициализация
init_files()