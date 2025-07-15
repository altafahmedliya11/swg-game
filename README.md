# 🎯 Spin & Win Game - Python Backend API

This is a Django-based backend project for a **Spin & Win** game app. It includes features such as user registration, quizzes, predictions, OTP verification, wallet management, payment integrations, and spinning/scratching rewards.

## 🚀 Features

- ✅ User Registration and OTP Verification
- 🎮 Spin & Scratch Game Logic
- 🧠 Quiz and Prediction Updates
- 💰 Add, Reset, and Manage Coins
- 📱 User Profile and Last Login Tracking
- 💸 Payments and Transaction History
- 🔗 Dynamic Links for Promotions
- 🪙 Funds Management
- 🖼️ Banners API for App Display

## 🔗 API Endpoints

Here’s a list of all available routes (via DRF `router.register()`):

| Endpoint | View | Description |
|---------|------|-------------|
| `register/` | `UserRegistrationView` | Register a new user |
| `otp/verify/` | `VerifyOTPView` | Verify OTP for login/registration |
| `resetpassword/` | `ResetPassword` | Reset user password |
| `user/` | `LastLoginView` | Track last login info |
| `user/details/` | `UserDetailsView` | Get or update user details |
| `user/profile/` | `ProfileUpdate` | Update user profile |
| `coins/add/` | `UserDetailsView` | Add coins to user |
| `quiz/update/` | `QuizView` | Update quiz answer |
| `quiz/reset/` | `QuizResetView` | Reset quiz data |
| `pred/update/` | `PredView` | Update predictions |
| `spin-scratch/add/` | `SpinScratchUpdate` | Update spin/scratch result |
| `payment/` | `PaymentView` | Make a payment |
| `transactions/` | `TransactionView` | View user transactions |
| `dynamic/coins/` | `DynamicCoinsView` | Fetch dynamic coin data |
| `dynamic/links/` | `DynamicLinksView` | Fetch dynamic links (e.g., referrals) |
| `dynamic/funds/` | `CoinsPaymentView` | Funds management |
| `banners/` | `BannersView` | Retrieve promotional banners |

## 🧰 Tech Stack

- Python 3.10+
- Django 4+
- Django REST Framework
- SQLite / PostgreSQL
- JWT / Token Auth (assumed for OTP)

## ⚙️ Setup Instructions

```bash
# Clone the repo
git clone https://github.com/your-username/spin-and-win-backend.git
cd spin-and-win-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Migrate DB
python manage.py migrate

# Run server
python manage.py runserver
