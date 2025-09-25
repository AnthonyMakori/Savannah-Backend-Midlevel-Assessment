# Anthony Store – Django REST API  
**Enterprise-grade backend for Savannah Informatics Backend Role Assessment**

---

## 🚀 Overview  
A robust Django REST service powering **Anthony Store**.  
Features exhaustive testing, multi-environment deployment automation, and advanced business integrations.

---

## ✨ Features  
- User registration, login, logout endpoints  
- Token-based authentication (JWT)  
- Password change & reset flows  
- Profile management  
- OAuth2 / OpenID Connect support  
- Extended fields: `first_name`, `last_name`, `gender`, `age`, `date_of_birth`, `id_number`  
- Validated contact info & multiple addresses  
- Business customer support & classification  
- Customer preferences & loyalty points  
- Financial tracking  
- Product variants, attributes & types (simple, variable, grouped, digital)  
- Brand & SEO fields  
- Inventory tracking & low-stock alerts  
- Reviews, ratings & image galleries  
- Order processing with Africa’s Talking SMS and email notifications  
- Unlimited-depth hierarchy (materialized path)  
- Category attributes & business rules  
- SEO & display configurations  
- PostgreSQL (primary), MySQL (alternative), SQLite (dev)  
- Environment-based DB configs  


## 📦 Installation  

```bash
cp .env.example .env
docker-compose up -d
```

---

## 📝 Running Locally  

```bash
pip install -r requirements.txt
python manage.py makemigrations && python manage.py migrate
python scripts/setup_demo_data.py
python manage.py runserver
```

- **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)  
- **Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)  
- **API Root**: [http://localhost:8000/api/](http://localhost:8000/api/)  

**Admin login:** `admin` / `admin123`  
**Test user:** `customer1` / `customer123`

---

## 🔑 Authentication  
- Prefix: `/api/`  
- Header: `Authorization: Bearer <token>` (except auth routes)  

---

## 🔗 Auth Endpoints  

| Endpoint                | Method | Description          |
|-------------------------|:------:|----------------------|
| `/auth/register/`       | POST   | Register new user    |
| `/auth/login/`          | POST   | Obtain JWT tokens    |
| `/auth/logout/`         | POST   | Revoke token         |
| `/auth/profile/`        | GET/PUT| Retrieve/update profile |
| `/auth/change-password/`| POST   | Change password      |

**Sample Login:**

```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
  "username": "customer1",
  "password": "customer123"
}
```

Response:

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

---

## 🧑‍💼 Customers  

| Endpoint             | Method         | Description                 |
|----------------------|:--------------:|-----------------------------|
| `/customers/`        | GET/POST       | List or create customers    |
| `/customers/{id}/`   | GET/PUT/DELETE | Detail, update, delete      |
| `/customers/me/`     | GET            | Current user profile        |

---

## 📂 Categories  

| Endpoint                            | Method | Description                    |
|-------------------------------------|:------:|--------------------------------|
| `/categories/`                      | GET/POST| List or create categories       |
| `/categories/tree/`                 | GET    | Retrieve full hierarchy         |
| `/categories/{slug}/avg_price/`     | GET    | Average price in category       |

---

## 🛍️ Products  

| Endpoint           | Method         | Description             |
|--------------------|:--------------:|-------------------------|
| `/products/`       | GET/POST       | List or create products |
| `/products/{id}/`  | GET/PUT/DELETE | Retrieve/update/delete  |
| `/products/search/`| GET            | Search & filter         |

**Sample Create Product:**

```http
POST /api/products/
Content-Type: application/json
```

```json
{
  "name": "iPhone 15 Pro",
  "price": "999.99",
  "category": "electronics",
  "sku": "IPH15PRO001",
  "stock_quantity": 50
}
```

---

## 📝 Orders  

| Endpoint                 | Method         | Description                   |
|--------------------------|:--------------:|-------------------------------|
| `/orders/`               | GET/POST       | List or create orders         |
| `/orders/my_orders/`     | GET            | List current user orders      |
| `/orders/{id}/`          | GET/PUT        | Detail or update order status |

**Sample Create Order:**

```http
POST /api/orders/
Content-Type: application/json
```

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

---

## ✅ Testing  

Unit, integration, acceptance, performance and security tests:

```bash
python scripts/test_runner.py
pytest --cov=./
```

Coverage target: **80%+**

---

## 🐳 Docker & Deployment  

```bash
docker build -t anthony-store:latest .
docker-compose up -d
```

Push to registry:

```bash
docker tag anthony-store:latest your-registry/anthony-store:latest
docker push your-registry/anthony-store:latest
```

Helm deployment:

```bash
helm install anthony-store charts/anthony-store-chart
```

---

## 🔒 Security  

- Token-based auth, CORS, CSRF protection  
- Input validation & sanitization  
- SQL injection & XSS prevention  
- Rate limiting  
- Request logging & error tracking  
- Health check & metrics endpoints  

---

## 🤝 Contributing  

1. Fork & clone repo  
2. Create feature branch  
3. Commit & open PR  
4. CI will run tests & deploy previews  

---

## 📞 Contact  

- **Store**: Anthony Store  
- **Email**: [anthonymakori2@gmail.com](mailto:anthonymakori2@gmail.com)  
- **Phone/WhatsApp**: +254 707497200  

---

## 📄 License  
MIT © [Anthony Makori](https://github.com/AnthonyMakori)
