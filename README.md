# 🚗 CarVRuuum

CarVRuuum is a web platform for buying and selling used cars.  
Users can publish vehicles, explore listings, save favorites, and contact sellers directly via WhatsApp.

The platform is built with **Django** and focuses on simplicity, speed, and a modern UI.

---

# Features

## User Accounts
- User registration and login
- Profile with phone number and city
- Manage personal listings
- View favorite vehicles

## Vehicle Listings
- Publish vehicles with details
- Upload **1 to 10 images per car**
- View detailed car pages
- Contact the seller via **WhatsApp**

## Search and Filters
Users can explore the catalog with:

- Keyword search (make or model)
- City filter
- Maximum price filter
- Autocomplete suggestions for brands and cities

## Favorites
Users can:
- Add cars to favorites
- Remove cars from favorites
- Access saved vehicles quickly

---

# Tech Stack

**Backend**
- Python
- Django

**Frontend**
- HTML
- TailwindCSS
- Django Templates

**Database**
- SQLite (development)

**Media Handling**
- Pillow (for car images)

---

# Project Structure

```
CARVRUUUM/
│
├── cars/                # Car marketplace app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│
├── account/             # Authentication and templates
│   ├── templates/
│   │   └── account/
│
├── media/               # Uploaded car images
│
├── static/              # Static assets
│
├── manage.py
├── requirements.txt
└── README.md
```

---

# Installation

## 1. Clone the repository

```
git clone https://github.com/yourusername/carvruuum.git
cd carvruuum
```

---

## 2. Create virtual environment

```
python3 -m venv venv
```

Activate it:

**Mac / Linux**

```
source venv/bin/activate
```

**Windows**

```
venv\Scripts\activate
```

---

## 3. Install dependencies

```
pip install -r requirements.txt
```

---

## 4. Apply migrations

```
python manage.py migrate
```

---

## 5. Run the server

```
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000
```

Car catalog:

```
http://127.0.0.1:8000/cars/
```

---

# Image Upload

Each vehicle listing supports:

- Minimum: **1 image**
- Maximum: **10 images**

Images are stored in:

```
media/cars/
```

---

# WhatsApp Integration

Each car listing includes a **Contact via WhatsApp** button.

The message automatically includes:
- Car title
- Link to the listing

The phone number is taken from the seller's **profile**.

---

# Future Improvements

- Email verification
- Chat between buyer and seller
- Vehicle comparison
- Payment integration
- Admin moderation tools

---

# Author

**Santiago Villamizar**
**Leidy Gallo Vargas**
**Simon Estebanano Castro**
**Marbin Yessid Rivera Ciro**  

Systems Engineering