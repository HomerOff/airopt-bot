import json
import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `reg_time`) VALUES (?, ?)", (user_id, datetime.now()))

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def product_exists(self, product_name):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `products` WHERE `product_name` = ?",
                                         (product_name,)).fetchall()
            return bool(len(result))

    def set_user_cart(self, user_id, user_cart):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `user_cart` = ? WHERE `user_id` = ?",
                                       (json.dumps(user_cart), user_id,))

    def set_user_orders(self, user_id, user_orders):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `user_orders` = ? WHERE `user_id` = ?",
                                       (json.dumps(user_orders), user_id,))

    def set_product_new(self, product_category, product_name, product_description, product_price, product_media):
        with self.connection:
            if product_media:
                self.cursor.execute(
                    "INSERT INTO `products` (`product_category`, `product_name`, `product_description`, `product_price`, `product_media`) VALUES (?, ?, ?, ?, ?)",
                    (product_category, product_name, product_description, float(product_price),
                     json.dumps(product_media),))
            else:
                self.cursor.execute(
                    "INSERT INTO `products` (`product_category`, `product_name`, `product_description`, `product_price`) VALUES (?, ?, ?, ?)",
                    (product_category, product_name, product_description, float(product_price),))

    def get_order_order(self, order_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `order` FROM `orders` WHERE `order_id` = ?",
                (order_id,))
            order = None
            for row in result.fetchall():
                order = row[0]
            if order:
                return json.loads(order)
            else:
                return order

    def get_order_user_id(self, order_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `order_user_id` FROM `orders` WHERE `order_id` = ?",
                (order_id,))
            order_user_id = None
            for row in result.fetchall():
                order_user_id = row[0]
            return order_user_id

    def get_order_data(self, order_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `order` FROM `orders` WHERE `order_id` = ?",
                (order_id,))
            order = None
            for row in result.fetchall():
                order = row[0]
            if order:
                return json.loads(order)
            else:
                return order

    def set_order_status(self, order_id, order_status):
        with self.connection:
            return self.cursor.execute(
                "UPDATE `orders` SET `order_status` = ? WHERE `order_id` = ?",
                (order_status, order_id,))

    def set_user_data(self, user_id, user_name, user_number, user_address, user_comment):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `user_name` = ?,"
                                       "`user_number` = ?, `user_address` = ?, `user_comment` = ?"
                                       "WHERE `user_id` = ?",
                                       (user_name, user_number, user_address, user_comment, user_id,))

    def get_user_data(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `user_name`, `user_number`, `user_address`, `user_comment` FROM `users` WHERE `user_id` = ?",
                (user_id,))

            card = None
            for row in result.fetchall():
                card = row
            if '' in card[:-1]:
                return None
            else:
                return card

    def get_user_name(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `user_name` FROM `users` WHERE `user_id` = ?",
                (user_id,))

            user_name = None
            for row in result.fetchall():
                user_name = row[0]
            return user_name

    def get_users(self):
        with self.connection:
            result = self.cursor.execute("SELECT `user_id` FROM users").fetchall()
            return result

    def get_count_users(self):
        with self.connection:
            result = self.cursor.execute("SELECT COUNT(*) from 'users'").fetchall()
            return result[0][0]

    def get_user_cart(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `user_cart` FROM `users` WHERE `user_id` = ?",
                                         (user_id,))
            user_cart = None
            for row in result.fetchall():
                user_cart = row[0]
            if user_cart:
                return json.loads(user_cart)
            else:
                return user_cart

    def get_user_orders(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `user_orders` FROM `users` WHERE `user_id` = ?",
                                         (user_id,))
            user_orders = None
            for row in result.fetchall():
                user_orders = row[0]
            if user_orders:
                return json.loads(user_orders)
            else:
                return user_orders

    def get_products_category(self):
        with self.connection:
            result = self.cursor.execute("SELECT DISTINCT `product_category` FROM `products`")
            categories = []
            for row in result.fetchall():
                categories += row
            return categories

    def get_product_category(self, name):
        with self.connection:
            result = self.cursor.execute("SELECT `product_category` FROM `products` WHERE `product_name` = ?",
                                         (name,))
            category = None
            for row in result.fetchall():
                category = row[0]
            return category

    def get_product_description(self, name):
        with self.connection:
            result = self.cursor.execute("SELECT `product_description` FROM `products` WHERE `product_name` = ?",
                                         (name,))
            product_description = None
            for row in result.fetchall():
                product_description = row[0]
            return product_description

    def get_order_status(self, order_id):
        with self.connection:
            result = self.cursor.execute("SELECT `order_status` FROM `orders` WHERE `order_id` = ?",
                                         (order_id,))
            order_status = None
            for row in result.fetchall():
                order_status = row[0]
            return order_status

    def get_order_date(self, order_id):
        with self.connection:
            result = self.cursor.execute("SELECT `order_date` FROM `orders` WHERE `order_id` = ?",
                                         (order_id,))
            order_date = None
            for row in result.fetchall():
                order_date = row[0]
            return order_date

    def get_products_name(self, category, all_items=False):
        with self.connection:
            if all_items:
                result = self.cursor.execute(
                    "SELECT `product_name` FROM `products` WHERE `product_category` = ?",
                    (category,))
            else:
                result = self.cursor.execute(
                    "SELECT `product_name` FROM `products` WHERE `product_category` = ?",
                    (category,))
            name = []
            for row in result.fetchall():
                name += row
            name = [str(item) for item in name]
            return name

    def get_product_price(self, name):
        with self.connection:
            result = self.cursor.execute("SELECT `product_price` FROM `products` WHERE `product_name` = ?",
                                         (name,))
            price = None
            for row in result.fetchall():
                price = row[0]
            return price

    def get_product_media(self, name):
        with self.connection:
            result = self.cursor.execute("SELECT `product_media` FROM `products` WHERE `product_name` = ?",
                                         (name,))
            image = None
            for row in result.fetchall():
                image = row[0]
            if image:
                return json.loads(image)
            else:
                return None

    def get_other_media(self, name):
        with self.connection:
            result = self.cursor.execute("SELECT `other_media` FROM `other` WHERE `other_category` = ?",
                                         (name,))
            image = None
            for row in result.fetchall():
                image = row[0]
            if image:
                return json.loads(image)
            else:
                return None

    def get_product_card(self, name):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `product_description`, `product_price`, `product_count`, `product_media` FROM `products` WHERE `product_name` = ?",
                (name,))

            card = None
            for row in result.fetchall():
                card = row
            return card

    def set_product_category(self, name, product_category):
        with self.connection:
            return self.cursor.execute("UPDATE `products` SET `product_category` = ? WHERE `product_name` = ?",
                                       (product_category, name,))

    def set_product_name(self, name, product_name):
        with self.connection:
            return self.cursor.execute("UPDATE `products` SET `product_name` = ? WHERE `product_name` = ?",
                                       (product_name, name,))

    def set_product_description(self, name, product_description):
        with self.connection:
            return self.cursor.execute("UPDATE `products` SET `product_description` = ? WHERE `product_name` = ?",
                                       (product_description, name,))

    def set_product_price(self, name, product_price):
        with self.connection:
            return self.cursor.execute("UPDATE `products` SET `product_price` = ? WHERE `product_name` = ?",
                                       (product_price, name,))

    def set_product_media(self, name, product_media):
        with self.connection:
            return self.cursor.execute("UPDATE `products` SET `product_media` = ? WHERE `product_name` = ?",
                                       (json.dumps(product_media), name,))

    def set_other_media(self, category, other_media):
        with self.connection:
            return self.cursor.execute("UPDATE `other` SET `other_media` = ? WHERE `other_category` = ?",
                                       (json.dumps(other_media), category,))

    def del_product(self, name):
        with self.connection:
            return self.cursor.execute("DELETE FROM `products` WHERE `product_name` = ?", (name,))
