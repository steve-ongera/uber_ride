# RideKE — Uber-style Ride Booking App (Practice Project)

A simple ride-hailing app built to practice collaborating on one codebase
via GitHub. Backend is Django REST Framework, frontend is React (Vite).

## Tech Stack

**Backend:** Django 5 + Django REST Framework + JWT auth (simplejwt) + M-Pesa Daraja STK Push
**Frontend:** React (Vite) + React Router + Axios

## Data Model

4 core models in `api/models.py`:

| Model     | Purpose                                                              |
|-----------|-----------------------------------------------------------------------|
| `User`    | Custom user (extends `AbstractUser`) with a `role`: RIDER or DRIVER |
| `Vehicle` | A driver's registered vehicle (1-to-1 with a driver user)           |
| `Ride`    | A booking — pickup/dropoff, status lifecycle, fare                  |
| `Payment` | 1-to-1 with a Ride — M-Pesa or cash, tracks STK Push status          |

**Ride status flow:** `PENDING → ACCEPTED → ONGOING → COMPLETED` (or `CANCELLED` at any point before completion).

## Project Structure

```
uber-clone/
├── backend/
│   ├── manage.py
│   ├── core/                  # project-level settings & urls
│   │   ├── settings.py
│   │   └── urls.py            # main url — includes api.urls
│   └── api/
│       ├── models.py          # ✅ done
│       ├── serializers.py     # ✅ done
│       ├── views.py           # ⬜ next
│       ├── urls.py            # ⬜ next
│       └── permissions.py     # ⬜ next (IsRider / IsDriver)
│
└── frontend/
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── services/
        │   └── api.js          # ⬜ all axios endpoint calls live here
        ├── components/
        │   ├── Navbar.jsx
        │   └── Sidebar.jsx
        └── pages/
            ├── Login.jsx
            ├── Register.jsx
            ├── Home.jsx             # available rides / book a ride entry point
            ├── BookRide.jsx
            ├── SuccessfulPayment.jsx
            └── Profile.jsx
```

## Getting Started

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers requests python-decouple
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm create vite@latest . -- --template react
npm install axios react-router-dom
npm run dev
```

## Environment Variables (backend `.env`)
```
SECRET_KEY=
DEBUG=True
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=
MPESA_PASSKEY=
MPESA_CALLBACK_URL=
```

## Git Workflow (for the two of us)

1. `main` is always deployable — no direct commits.
2. Branch per feature: `feature/ride-booking`, `feature/mpesa-payment`, `feature/auth-frontend`.
3. Small, focused PRs — one person reviews before merge.
4. Pull `main` and rebase your branch before opening a PR, to keep conflicts small.
5. Suggested split: one person owns backend endpoints for a feature, the other wires up the matching frontend page — so `views.py` + `pages/X.jsx` land in the same PR where possible.

## Status

- [x] `models.py`
- [x] `serializers.py`
- [ ] `views.py`
- [ ] `api/urls.py` + main `urls.py`
- [ ] `settings.py`
- [ ] Frontend scaffold (`main.jsx`, `App.jsx`, `services/api.js`, components, pages)