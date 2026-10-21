# ☕ Smart Café — Complete Real-World Café Management System

A production-grade, full-stack café website and operations management system engineered with **React + TypeScript + Vite**, **Tailwind CSS**, **Node.js + Express**, **SQLite / PostgreSQL**, **Socket.io**, **Google Gemini AI** , and **Secure Phone OTP Authentication**.

Built with three distinct customer experiences, tamper-proof QR table ordering, phone OTP verification across all checkout flows, an isolated and network-restricted admin panel with device authorization, live kitchen audio alerts, and an offline-capable admin Progressive Web App (PWA).

---

## 🌟 Three Customer Entry Flows & Experiences

### Flow A: Customer Scanning a Table QR Code (`/menu?table=T01&token=...`)
- **Tamper-Proof Scans**: Every physical table (T01–T10) has a cryptographically unique `qr_token` embedded in its QR code.
- **URL Tampering Protection**: If a customer changes `table=T01` to `table=T02` or strips the security token, the system detects the tamper attempt, displays a security warning banner, and prevents unauthorized orders from reaching the wrong table (HTTP 403).
- **Smooth Category Navigation**: Sticky horizontal category bar with auto-centering and vertical food item scroll-spy syncing.
- **Mandatory Phone OTP**: Before placing the dine-in order, the customer verifies their phone number via a 6-digit OTP modal.
- **Live Status Tracking**: Real-time Socket.io stepper (`Placed → Accepted → Preparing → Ready → Served`).

### Flow B: Online Ordering for Pickup & Delivery (`/order-online`)
- **Fulfillment Selection**: Toggle between Store Pickup (Takeaway) and Doorstep Delivery.
- **Delivery Details**: Address, landmark, and delivery rider instructions.
- **Automatic Delivery Fees**: Free delivery for orders above ₹500, flat ₹40 otherwise.
- **Mandatory Phone OTP**: Before confirming the order, the customer verifies their mobile number.
- **Distinct Admin Badges**: Orders arrive on the admin dashboard highlighted with distinct badges:
  - 🍽️ **Dine-In Table T01** (Emerald badge)
  - 🛍️ **Takeaway Pickup** (Blue badge)
  - 🛵 **Home Delivery** (Amber badge with delivery address)

### Flow C: Customer Table Reservation (`/reserve`)
- **Real-time Capacity Checking**: Visual booking interface displaying available time slots based on actual table capacities.
- **Atomic Double-Booking Prevention**: SQLite/PostgreSQL transaction atomically checks table capacity before saving.
- **Duplicate Booking Prevention**: Rejects duplicate bookings from the same phone number for the same time slot (HTTP 409).
- **Mandatory Phone OTP**: Phone number verified via OTP before the reservation is finalized.
- **Booking Reference Code**: Generates a unique tracking reference (e.g. `#RES-XXXXX-XX`) and displays booking status immediately on the admin dashboard.

---

## 🔐 Secure Phone OTP Verification Architecture

All customer checkout and reservation flows mandate server-verified mobile OTPs to eliminate fake orders, phantom bookings, and API bypass attacks.

### Security Guarantees:
1. **Server-Side Authorization**: Customers cannot bypass the OTP screen by calling `/api/orders` or `/api/reservations` directly. The backend requires a valid, signed JWT `otp_token` tied to the customer's phone number.
2. **Single-Use Consumption**: Once an order or reservation is created, the `otp_token` is atomically consumed. Replaying the same token fails immediately.
3. **Abuse & Brute-Force Protection**:
   - **60-Second Cooldown**: Prevents rapid SMS spamming (returns HTTP 429).
   - **Hourly Rate Limiting**: Maximum 5 OTP dispatches per hour per phone number.
   - **3-Attempt Lockout**: Each OTP allows a maximum of 3 failed attempts before the session is permanently locked.
   - **5-Minute Expiry**: Unused codes automatically expire after 5 minutes.
   - **Bcrypt Hashing**: OTP codes are hashed with bcrypt in the database; plaintext codes are never stored.
4. **Idempotency Protection**: Order submissions support `idempotency_key` to prevent duplicate billing if the customer clicks the confirmation button multiple times.

### Supported SMS Providers (`OTP_PROVIDER` in `server/.env`):
- **`mock` (Default Dev Mode)**: Prints the 6-digit verification code to the backend terminal and provides an instant 1-click test button in the UI for effortless local testing.
- **`2factor`**: Production SMS gateway for Indian mobile numbers (+91).

---

## 🛡️ Dedicated Admin Panel & Network Restrictions

The administrative dashboard (`/admin`) is completely isolated from customer pages and protected by multi-layered security controls.

### 1. Role-Based Access Control (RBAC)
- **Café Manager (`admin`)**: Complete operational control (menu, pricing, table layout, security audit logs, settings).
- **Kitchen / Floor Staff (`staff`)**: Live orders queue, order prep statuses, and counter cash settlements.

### 2. Workstation Network Restriction (`ADMIN_ALLOWED_IPS`)
- Admins can restrict access to specific static IP addresses, subnets, or CIDR blocks:
  ```ini
  ADMIN_ALLOWED_IPS=127.0.0.1, ::1, 192.168.1.0/24, 100.64.0.0/10
  ```
- Unauthorized IP addresses are blocked with HTTP 403 Forbidden.

### 3. Workstation Device Authorization Key (`ADMIN_DEVICE_KEY`)
- An optional hardware/workstation secret key configured in the `.env` file and passed via the `x-admin-device-key` header.
- Terminal workstations can store this key locally in Admin Settings to unlock administrative access.

### 4. VPN Setup Guide (Tailscale / WireGuard)
For remote café owners managing multiple outlets securely without exposing admin ports to the public internet:
1. Install **Tailscale** on the café server: `curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up`
2. Install Tailscale on the manager's laptop or mobile phone.
3. Add the Tailscale CGNAT subnet to `ADMIN_ALLOWED_IPS`:
   ```ini
   ADMIN_ALLOWED_IPS=127.0.0.1, ::1, 100.64.0.0/10
   ```
4. Only devices connected to your private Tailnet can access `/admin`.

### 5. Administrative Audit Logging (`admin_audit_logs`)
- Every administrative action is automatically logged with timestamp, admin ID, name, action type, IP address, and details.
- Viewable in real-time under **Admin Settings → Security & Audit Logs**.

### 6. Live Web Audio Chimes
- When new orders arrive, the admin dashboard plays a gentle Web Audio chime alert.
- Staff can toggle audio notifications on or off using the sound toggle button in the dashboard header.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Canvas Confetti |
| **Backend** | Node.js (v20+), Express, TypeScript (`tsx`) |
| **Database** | SQLite via `better-sqlite3` (Zero-config, WAL mode, foreign keys enabled) / PostgreSQL compatible |
| **Real-time** | Socket.io bi-directional event broadcaster |
| **AI Assistant** | Google Gemini API (`@google/generative-ai`) with database-grounded system prompts |
| **Payments** | Razorpay Node.js SDK with server HMAC-SHA256 signature verification |
| **Phone OTP** | Multi-provider service (Mock/Dev, 2factor ) with single-use JWT verification |
| **QR Engine** | Dynamic vector SVG & PNG QR generation with cryptographic table tokens |
| **Offline PWA** | Service Worker + IndexedDB action queue with automatic background reconciliation |

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Node.js (v18 or v20+)
- npm (v9+)
- Python 3.10+ (for integration test suite)

### 2. Setup Dependencies
```bash
# Install root, backend, and frontend packages
npm install
cd server && npm install
cd ../client && npm install
cd ..
```

### 3. Configure Environment
Copy the example environment files:
```bash
cp server/.env.example server/.env
```
*(The default configuration uses `OTP_PROVIDER=mock` and `ADMIN_ALLOWED_IPS=127.0.0.1, ::1`, enabling instant local testing).*

### 4. Start the Application
Run both backend (`http://localhost:5000`) and frontend (`http://localhost:5173`) concurrently:
```bash
npm run dev
```

Or run each service individually:
```bash
# Terminal 1: Backend API & Socket.io server
npm run dev:server

# Terminal 2: Vite React frontend
npm run dev:client
```

Open **`http://localhost:5173`** in your browser.

---

## 🔑 Demo & Test Credentials

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Café Manager (Admin)** | `admin@smartcafe.com` | `admin123` | Full control over Menu, Tables, Orders, Security Logs, Settings |
| **Floor / Kitchen Staff** | `staff@smartcafe.com` | `staff123` | Table statuses, Order prep stages, Cash billing |

*The admin login page (`/admin/login`) includes 1-click credential switcher buttons for testing.*

---

## 🧪 Automated System Integration Tests (12 Scenarios)

The project includes an automated integration test suite validating all 12 operational scenarios:

```bash
python server/scripts/test_complete_system.py
```

### Verified Test Scenarios:
1. **Scenario 1**: Table QR scan with `qr_token` & OTP verification -> order placed & received by admin.
2. **Scenario 2**: Online order (Pickup / Delivery) with OTP -> received by admin with distinct badges.
3. **Scenario 3**: Direct order placement without OTP token -> rejected with HTTP 400.
4. **Scenario 4**: Table reservation with OTP -> received by admin dashboard.
5. **Scenario 5**: Conflicting table reservation / capacity exceeded -> rejected with HTTP 409 conflict.
6. **Scenario 6**: Admin order status transitions (`placed → accepted → preparing → ready → served`) & strict transition validation.
7. **Scenario 7**: Database persistence across queries and state verification.
8. **Scenario 8**: Protected admin APIs without auth token / unauthorized network -> rejected with HTTP 401/403.
9. **Scenario 9**: Duplicate order submission with same `idempotency_key` -> returns existing order without creating duplicates.
10. **Scenario 10**: Invalid OTP, 60-second cooldown limit, and 3-attempt lockout enforcement.
11. **Scenario 11**: Table token tampering (e.g. changing T01 to T02 with mismatching token) -> rejected with HTTP 403.
12. **Scenario 12**: Admin menu item update -> reflected immediately on customer menu API.

---

## 🖨️ Table QR Code Physical Deployment Workflow

1. Log in to the Admin Dashboard and navigate to **Live Tables** (`/admin/tables`).
2. Set the **Target Base URL** to your deployed public domain (e.g., `https://smartcafe.in`).
3. Click **Get QR** on any table (T01 through T10).
4. Download the high-resolution vector/PNG QR code or click **Print Table Flyer**.
5. Each QR code is uniquely configured with its table ID and secret security token:
   ```
   https://smartcafe.in/menu?table=T01&token=tblsec_t01_...
   ```
6. When scanned by guests, the mobile menu verifies the table instantly, locking the cart and order to that physical table.

---

## 📁 Final Project Directory Structure

```
project/
├── client/                              # Frontend React + TypeScript Application
│   ├── public/
│   │   ├── favicon.svg                  # Coffee SVG favicon
│   │   ├── manifest.webmanifest         # PWA Manifest
│   │   └── sw.js                        # Service Worker for offline PWA
│   ├── src/
│   │   ├── components/
│   │   │   ├── CategoryBar.tsx          # Sticky horizontal scroll bar with scroll spy
│   │   │   ├── FoodCard.tsx             # Food item card with diet badges & controls
│   │   │   ├── CartDrawer.tsx           # Order slide-over drawer
│   │   │   ├── OTPVerificationModal.tsx # 6-digit phone OTP verification modal
│   │   │   ├── GeminiChatbot.tsx        # Floating Google Gemini AI assistant
│   │   │   ├── RazorpayModal.tsx        # Payment modal & HMAC signature verification
│   │   │   ├── ReviewModal.tsx          # Customer review submission dialog
│   │   │   ├── Navbar.tsx               # Header with table indicator & cart pill
│   │   │   └── Footer.tsx               # Ambiance, hours, and navigation links
│   │   ├── context/
│   │   │   ├── AuthContext.tsx          # Admin authentication state
│   │   │   └── CartContext.tsx          # Shopping cart & table tracking state
│   │   ├── lib/
│   │   │   ├── api.ts                   # Type-safe API client (OTP, Orders, Tables, Auth)
│   │   │   ├── socket.ts                # Socket.io real-time connection
│   │   │   └── offlineStore.ts          # IndexedDB queue & cache
│   │   ├── pages/
│   │   │   ├── HomePage.tsx             # Landing page with 3 customer entry points
│   │   │   ├── MenuPage.tsx             # Dine-in QR menu with category scrolling
│   │   │   ├── OrderOnlinePage.tsx      # Pickup & delivery ordering flow
│   │   │   ├── CheckoutPage.tsx         # Order review & OTP checkout
│   │   │   ├── OrderSuccessPage.tsx     # Live Socket.io order status tracker
│   │   │   ├── ReservePage.tsx          # Table reservation with real-time slot checking
│   │   │   ├── ReviewsPage.tsx          # Public customer review wall
│   │   │   ├── AboutPage.tsx            # Café history & coffee story
│   │   │   ├── ContactPage.tsx          # Map, hours, and inquiry form
│   │   │   └── admin/
│   │   │       ├── AdminLayout.tsx           # Protected admin layout & navigation
│   │   │       ├── AdminLoginPage.tsx        # Login screen with network & device status
│   │   │       ├── AdminDashboardPage.tsx    # Live KPIs & operations overview
│   │   │       ├── AdminTablesPage.tsx       # Table grid & QR flyer generator
│   │   │       ├── AdminOrdersPage.tsx       # Live orders feed with audio chimes & badges
│   │   │       ├── AdminMenuPage.tsx         # Menu CRUD & availability toggles
│   │   │       ├── AdminReservationsPage.tsx # Table reservation manager
│   │   │       ├── AdminPaymentsPage.tsx     # Payments, receipts & refunds
│   │   │       ├── AdminReviewsPage.tsx      # Review moderation
│   │   │       ├── AdminAnalyticsPage.tsx    # Revenue, sales & channel metrics
│   │   │       └── AdminSettingsPage.tsx     # Device keys, VPN guide & audit logs
│   │   ├── App.tsx                      # Application router & route guards
│   │   └── main.tsx                     # React DOM entrypoint
│   └── package.json
│
├── server/                              # Backend API & Real-time Server (Node + Express)
│   ├── data/
│   │   └── smartcafe.db                 # SQLite database file (WAL mode)
│   ├── src/
│   │   ├── config.ts                    # Server configuration & constants
│   │   ├── index.ts                     # Express & Socket.io server entrypoint
│   │   ├── db/
│   │   │   ├── index.ts                 # Database connection & non-destructive migrations
│   │   │   ├── schema.sql               # Full SQL schema
│   │   │   └── seed.ts                  # Seed data (42 items, 10 tables, admin accounts)
│   │   ├── middleware/
│   │   │   ├── auth.ts                  # JWT authentication & role-based checks
│   │   │   └── adminSecurity.ts         # IP allowlist, device authorization & audit logger
│   │   ├── routes/
│   │   │   ├── auth.ts                  # Login, security status & audit logs
│   │   │   ├── otp.ts                   # Phone OTP dispatch & verification
│   │   │   ├── menu.ts                  # Menu categories & items CRUD
│   │   │   ├── tables.ts                # Table occupancy & tamper-proof QR verification
│   │   │   ├── orders.ts                # Atomic order placement & strict status transitions
│   │   │   ├── reservations.ts          # Atomic capacity reservation & conflict prevention
│   │   │   ├── payments.ts              # Razorpay checkout & verification.
│   │   │   ├── reviews.ts               # Review submission & moderation
│   │   │   ├── analytics.ts             # Sales, revenue & channel analytics
│   │   │   └── chatbot.ts               # Gemini AI assistant with menu context
│   │   └── services/
│   │       ├── otp.ts                   # OTP generation, rate limits, hashing & dispatch
│   │       ├── socket.ts                # Socket.io event broadcaster
│   │       ├── gemini.ts                # Google Generative AI integration
│   │       ├── razorpay.ts              # Razorpay order creation & HMAC verification
│   │       └── qrcode.ts                # Table QR code generator
│   ├── scripts/
│   │   ├── test_complete_system.py      # Automated 12-scenario integration test suite
│   │   └── verify_schema.mjs            # Database schema verification script
│   ├── .env.example                     # Environment template with all options
│   ├── .env                             # Active local environment configuration
│   └── package.json
│
└── package.json                         # Root package scripts
```
