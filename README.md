# 🎯 Spin & Win Game - Python Backend API

This is a Django-based backend project for a **Spin & Win** game app. It includes features like user registration, quizzes, predictions, OTP verification, wallet and payment integrations, and spinning/scratching rewards.

---

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

---

## 🔗 API Endpoints

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

---

## 🧰 Tech Stack

- Python 3.10+
- Django 4+
- Django REST Framework
- PostgreSQL
- Docker + Docker Compose
- Gunicorn (for production serving)

---

## 🐳 Dockerized Setup

### 1. 📦 Clone & Configure

```bash
git clone https://github.com/your-username/spin-and-win-backend.git
cd spin-and-win-backend