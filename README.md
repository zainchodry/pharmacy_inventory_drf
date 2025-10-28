# 💊 Pharmacy Inventory System (Django REST Framework)

A complete backend system built with **Django REST Framework (DRF)** for managing pharmacy operations such as **user authentication**, **inventory management**, **supplier tracking**, and **sales control**.

## 🚀 Features

### 🧍 Accounts App
- JWT-based authentication (login/logout/register)
- Role-based users (Admin, Pharmacist, Staff)
- User management APIs

### 📦 Inventory App
- Product management (name, batch, expiry, quantity)
- Supplier management
- Stock in/out tracking
- Automatic low-stock alert system
- Category-wise product grouping

## 🛠️ Tech Stack
- **Python 3.8+**
- **Django 4.x**
- **Django REST Framework**
- **SimpleJWT**
- **SQLite3 / PostgreSQL**
- **drf-yasg** for API documentation

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/zainchodry/pharmacy_inventory_drf.git
cd pharmacy_inventory_drf
```

### 2️⃣ Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # For Linux / Mac
venv\Scripts\activate      # For Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

## 🧩 Project Structure

```
pharmacy_drf/
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
│
├── inventory/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── filters.py
│
├── pharmacy_drf/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── manage.py
```

## 🔐 Authentication Setup (JWT)

This project uses **SimpleJWT** for secure token-based authentication.

### Endpoints
| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/token/` | POST | Obtain access and refresh token |
| `/api/token/refresh/` | POST | Refresh the access token |
| `/api/accounts/register/` | POST | Register new user |
| `/api/accounts/login/` | POST | Login and get JWT tokens |

## ⚙️ DRF and JWT Configuration

Add this to your `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

## 🧪 Run the Project

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Server will start at:
```
http://127.0.0.1:8000/
```

## 📘 API Endpoints

### 🔹 Accounts
| URL | Method | Description |
|------|---------|-------------|
| `/api/accounts/register/` | POST | Register a new user |
| `/api/accounts/login/` | POST | User login |
| `/api/token/` | POST | Get JWT access and refresh tokens |
| `/api/token/refresh/` | POST | Refresh token |

### 🔹 Inventory
| URL | Method | Description |
|------|---------|-------------|
| `/api/inventory/products/` | GET | List all products |
| `/api/inventory/products/` | POST | Create new product |
| `/api/inventory/products/<id>/` | PUT | Update product |
| `/api/inventory/products/<id>/` | DELETE | Delete product |
| `/api/inventory/suppliers/` | GET | List all suppliers |
| `/api/inventory/stock/` | GET | View stock details |

## 🧾 Example .env File

Create a `.env` file in your project root:
```
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_NAME=pharmacy_db
DATABASE_USER=postgres
DATABASE_PASSWORD=1234
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

## 🧰 Superuser (Admin) Setup

To create a superuser:
```bash
python manage.py createsuperuser
```

Then login at:
```
http://127.0.0.1:8000/admin/
```

## 🧑‍💻 API Documentation

After running the server:
```
http://127.0.0.1:8000/swagger/
```
or
```
http://127.0.0.1:8000/redoc/
```

## 🏁 Future Enhancements
- Sales Management App (Invoices, Customers)
- Stock Alerts via Email
- Daily/Monthly Reports
- Dashboard for analytics

## 👨‍💻 Author
**Zain Choudry (enigmatix)**  
Backend Developer — Django / DRF / Odoo / Automation  
📧 Email: razzaqzain546@gmail.com
🌐 GitHub: [https://github.com/zainchodry](https://github.com/zainchodry)