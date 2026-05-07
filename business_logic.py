import re
from data_access import *


class BusinessLogic:

    @staticmethod
    def validate_register(username, password, confirm_password, email):
        """Валидира данните за регистрация"""
        errors = []

        if len(username) < 3:
            errors.append("Потребителското име трябва да е поне 3 символа")

        if find_user_by_username(username):
            errors.append("Потребителското име вече съществува")

        if len(password) < 4:
            errors.append("Паролата трябва да е поне 4 символа")

        if password != confirm_password:
            errors.append("Паролите не съвпадат")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("Невалиден имейл адрес")

        return errors

    @staticmethod
    def calculate_cart_total(cart_items):
        """Пресмята общата стойност на количката"""
        total = 0
        if not cart_items:
            return 0.0
        for item in cart_items:
            product = get_product_by_id(item['product_id'])
            if product:
                total += product['price'] * item['quantity']
        return round(total, 2)

    @staticmethod
    def get_cart_with_details(user_id):
        """Връща количката с детайли за продуктите"""
        cart = get_cart(user_id)

        # Ако няма количка или количката е празна
        if not cart or not cart.get('items') or len(cart.get('items', [])) == 0:
            return {'items': [], 'total': 0}

        items_with_details = []
        for item in cart['items']:
            product = get_product_by_id(item['product_id'])
            if product:
                items_with_details.append({
                    'product_id': item['product_id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': item['quantity'],
                    'subtotal': round(product['price'] * item['quantity'], 2)
                })

        total = BusinessLogic.calculate_cart_total(cart['items'])
        return {'items': items_with_details, 'total': total}

    @staticmethod
    def checkout(user_id):
        """Формира поръчка от количката"""
        cart_details = BusinessLogic.get_cart_with_details(user_id)

        if not cart_details['items']:
            return None, "Количката е празна"

        # Създаване на поръчка
        order_items = [{'product_id': item['product_id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity']}
                       for item in cart_details['items']]

        order_id = create_order(user_id, cart_details['total'], order_items)

        # Изчистване на количката
        clear_cart(user_id)

        return order_id, "Поръчката е успешна!"

    @staticmethod
    def filter_products(category=None, search=None):
        """Филтрира продуктите"""
        products = get_all_products()

        if category and category != 'Всички':
            products = [p for p in products if p['category'] == category]

        if search:
            search_lower = search.lower()
            products = [p for p in products if search_lower in p['name'].lower() or
                        search_lower in p['description'].lower()]

        return products

    @staticmethod
    def get_categories():
        """Връща уникалните категории"""
        products = get_all_products()
        categories = list(set([p['category'] for p in products]))
        return ['Всички'] + categories