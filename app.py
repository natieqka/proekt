from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from business_logic import BusinessLogic
from data_access import *
from ai_assistant import assistant

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production-12345'

# Инициализиране на примерни продукти при стартиране
get_all_products()


# ----- ДЕКОРАТОР ЗА ПРОВЕРКА НА ВХОД -----
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Моля, влезте в профила си', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


# ----- МАРШРУТИ -----
@app.route('/')
def index():
    products = get_all_products()[:4]
    return render_template('index.html', products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']

        errors = BusinessLogic.validate_register(username, password, confirm_password, email)

        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            user_id = save_user(username, password, email)
            session['user_id'] = user_id
            session['username'] = username
            flash('Регистрацията е успешна!', 'success')
            return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Добре дошли, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Грешно потребителско име или парола', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Излязохте успешно', 'info')
    return redirect(url_for('index'))


@app.route('/products')
def products():
    category = request.args.get('category', 'Всички')
    search = request.args.get('search', '')

    filtered_products = BusinessLogic.filter_products(category, search)
    categories = BusinessLogic.get_categories()

    return render_template('products.html',
                           products=filtered_products,
                           categories=categories,
                           current_category=category,
                           search=search)


@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    add_to_cart(session['user_id'], product_id, 1)
    flash('Продуктът беше добавен в количката!', 'success')
    return redirect(request.referrer or url_for('products'))


@app.route('/cart')
@login_required
def cart():
    cart_details = BusinessLogic.get_cart_with_details(session['user_id'])
    return render_template('cart.html', cart=cart_details)


@app.route('/update_cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    quantity = int(request.form['quantity'])
    update_cart_item(session['user_id'], product_id, quantity)
    flash('Количката беше обновена', 'info')
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    remove_from_cart(session['user_id'], product_id)
    flash('Продуктът беше премахнат', 'info')
    return redirect(url_for('cart'))


@app.route('/checkout')
@login_required
def checkout():
    order_id, message = BusinessLogic.checkout(session['user_id'])
    if order_id:
        flash(message, 'success')
        return redirect(url_for('orders'))
    else:
        flash(message, 'danger')
        return redirect(url_for('cart'))


@app.route('/orders')
@login_required
def orders():
    user_orders = get_user_orders(session['user_id'])
    return render_template('orders.html', orders=user_orders)


@app.route('/profile')
@login_required
def profile():
    user = find_user_by_username(session['username'])
    return render_template('profile.html', user=user)


# ----- AI АСИСТЕНТ -----
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({'error': 'Няма зададен въпрос'}), 400

        answer = assistant.get_response_sync(question)

        return jsonify({
            'question': question,
            'answer': answer,
            'success': True
        })
    except Exception as e:
        print(f"Грешка в chat API: {e}")
        return jsonify({
            'error': 'Възникна грешка, моля опитайте отново',
            'success': False
        }), 500


if __name__ == '__main__':
    app.run(debug=True)