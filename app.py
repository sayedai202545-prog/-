import sqlite3
from datetime import datetime

DB_NAME = "crm_inventory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            company TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
        """
    )

    conn.commit()
    conn.close()


def add_product():
    name = input("اسم الصنف: ").strip()
    sku = input("كود الصنف (SKU): ").strip()
    unit_price = float(input("سعر الوحدة: ").strip())
    quantity = int(input("الكمية الحالية: ").strip())

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO products(name, sku, unit_price, quantity, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, sku, unit_price, quantity, datetime.now().isoformat()),
        )
        conn.commit()
        print("✅ تم إضافة الصنف بنجاح")
    except sqlite3.IntegrityError:
        print("❌ كود الصنف موجود بالفعل")
    finally:
        conn.close()


def list_products():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name, sku, unit_price, quantity FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("لا توجد أصناف حالياً.")
        return

    print("\n--- قائمة الأصناف ---")
    for row in rows:
        print(f"ID: {row[0]} | الاسم: {row[1]} | SKU: {row[2]} | السعر: {row[3]} | الكمية: {row[4]}")


def add_customer():
    full_name = input("اسم العميل: ").strip()
    phone = input("رقم الهاتف: ").strip()
    email = input("الإيميل: ").strip()
    company = input("الشركة (اختياري): ").strip()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO customers(full_name, phone, email, company, created_at) VALUES (?, ?, ?, ?, ?)",
        (full_name, phone, email, company, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    print("✅ تم إضافة العميل بنجاح")


def list_customers():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, phone, email, company FROM customers ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("لا يوجد عملاء حالياً.")
        return

    print("\n--- قائمة العملاء ---")
    for row in rows:
        print(f"ID: {row[0]} | الاسم: {row[1]} | الهاتف: {row[2]} | الإيميل: {row[3]} | الشركة: {row[4]}")


def create_order():
    customer_id = int(input("ID العميل: ").strip())
    product_id = int(input("ID الصنف: ").strip())
    quantity = int(input("الكمية المطلوبة: ").strip())

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT unit_price, quantity, name FROM products WHERE id = ?", (product_id,))
    product = cur.fetchone()

    if not product:
        print("❌ الصنف غير موجود")
        conn.close()
        return

    unit_price, stock_qty, product_name = product
    if quantity > stock_qty:
        print(f"❌ الكمية غير كافية. المتاح: {stock_qty}")
        conn.close()
        return

    total = unit_price * quantity

    cur.execute(
        "INSERT INTO orders(customer_id, product_id, quantity, total, created_at) VALUES (?, ?, ?, ?, ?)",
        (customer_id, product_id, quantity, total, datetime.now().isoformat()),
    )
    cur.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))

    conn.commit()
    conn.close()

    print(f"✅ تم إنشاء طلب بنجاح للصنف '{product_name}' بقيمة {total}")


def list_orders():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT o.id, c.full_name, p.name, o.quantity, o.total, o.created_at
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        JOIN products p ON p.id = o.product_id
        ORDER BY o.id DESC
        """
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("لا توجد طلبات حالياً.")
        return

    print("\n--- قائمة الطلبات ---")
    for row in rows:
        print(
            f"طلب #{row[0]} | العميل: {row[1]} | الصنف: {row[2]} | الكمية: {row[3]} | الإجمالي: {row[4]} | التاريخ: {row[5]}"
        )


def main_menu():
    init_db()

    menu = {
        "1": ("إضافة صنف للمخزون", add_product),
        "2": ("عرض الأصناف", list_products),
        "3": ("إضافة عميل CRM", add_customer),
        "4": ("عرض العملاء", list_customers),
        "5": ("إنشاء طلب بيع", create_order),
        "6": ("عرض الطلبات", list_orders),
        "0": ("خروج", None),
    }

    while True:
        print("\n===== نظام المخزون + CRM =====")
        for key, (label, _) in menu.items():
            print(f"{key}. {label}")

        choice = input("اختر عملية: ").strip()

        if choice == "0":
            print("👋 شكراً لاستخدام النظام")
            break

        action = menu.get(choice)
        if not action:
            print("❌ اختيار غير صحيح")
            continue

        try:
            action[1]()
        except ValueError:
            print("❌ تأكد من إدخال أرقام صحيحة في الحقول الرقمية")
        except sqlite3.IntegrityError as e:
            print(f"❌ خطأ في قاعدة البيانات: {e}")


if __name__ == "__main__":
    main_menu()
