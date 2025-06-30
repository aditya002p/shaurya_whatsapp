# FASTag WhatsApp Bot API Endpoints

This document describes the production-ready API endpoints for the FASTag WhatsApp Bot, covering Agent Authentication, Issuance, and Replacement flows.  
**All flows require agent authentication first.**

---

## 1. Agent Authentication Flow

### 1.1. Verify Agent Mobile and Send OTP

**POST** `/agents/verify-mobile`

**Request:**
```json
{
  "mobile_number": "9876543210"
}
```

**Response (Success):**
```json
{
  "message": "OTP sent successfully.",
  "agent_id": 123
}
```

**Response (Failure):**
```json
{
  "detail": "Invalid mobile number format."
}
```
or
```json
{
  "detail": "Agent not found. Please use a registered mobile number."
}
```

---

### 1.2. Verify OTP and Get Agent Details

**POST** `/agents/verify-otp`

**Request:**
```json
{
  "mobile_number": "9876543210",
  "otp": "1234"
}
```

**Response (Success):**
```json
{
  "message": "Hi John 👋",
  "session_id": "SESSION123",
  "agent_id": 123,
  "agent_name": "John Doe",
  "wallet_balance": 5000,
  "fastags_left": 10
}
```

**Response (Failure):**
```json
{
  "detail": "Invalid OTP. Please try again."
}
```
or
```json
{
  "detail": "Could not retrieve agent details after OTP verification."
}
```

---

## 2. FASTag Issuance Flow

> **Note:** All endpoints below require a valid `session_id` from agent authentication.

### 2.1. Start Assignment

**POST** `/fastags/assign/start`

**Request:**
```json
{
  "session_id": "SESSION123"
}
```

**Response:**
```json
{
  "message": "Let's get your FASTag in just a few steps. 🚗 Please enter your Vehicle Number (e.g., MH12AB1234)."
}
```

---

### 2.2. Submit Vehicle and Engine Number

**POST** `/fastags/assign/vehicle-details`

**Request:**
```json
{
  "session_id": "SESSION123",
  "vehicle_number": "MH12AB1234",
  "engine_number": "12345"
}
```

**Response:**
```json
{
  "message": "Now, please send the user's 10-digit Mobile Number."
}
```

---

### 2.3. Submit User Mobile and Send OTP

**POST** `/fastags/assign/user-mobile`

**Request:**
```json
{
  "session_id": "SESSION123",
  "user_mobile": "9876543210"
}
```

**Response:**
```json
{
  "message": "Sending OTP to 9876543210 🔐 Please type the 6-digit OTP."
}
```

---

### 2.4. Verify User OTP

**POST** `/fastags/assign/verify-otp`

**Request:**
```json
{
  "session_id": "SESSION123",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "OTP verified! Please provide the user's details, starting with their First Name."
}
```

---

### 2.5. Submit User's Personal Information

**POST** `/fastags/assign/user-info`

**Request:**
```json
{
  "session_id": "SESSION123",
  "first_name": "John",
  "last_name": "Doe",
  "dob": "01-01-1990"
}
```

**Response:**
```json
{
  "message": "Thanks, John! Choose the ID proof type:\n1. PAN\n2. Passport\n3. Driving License\n4. Voter ID"
}
```

---

### 2.6. Submit User's ID Proof

**POST** `/fastags/assign/id-proof`

**Request:**
```json
{
  "session_id": "SESSION123",
  "id_type": "1",
  "id_number": "ABCDE1234F",
  "expiry_date": "31-12-2030"
}
```

**Response:**
```json
{
  "message": "Great! Now, select a plan."
}
```

---

### 2.7. Select Plan

**POST** `/fastags/assign/plan`

**Request:**
```json
{
  "session_id": "SESSION123",
  "plan_id": "PLAN123"
}
```

**Response:**
```json
{
  "message": "Please select a plan:\n1. ₹500 - Standard Plan\n2. ₹1000 - Premium Plan\n...",
  "plans": [
    {"id": "PLAN123", "amount": 500, "description": "Standard Plan"},
    {"id": "PLAN456", "amount": 1000, "description": "Premium Plan"}
  ]
}
```

---

### 2.8. Upload Document/Image

**POST** `/fastags/assign/upload-image`

**Request:**
```json
{
  "session_id": "SESSION123",
  "image_type": "rc_front",
  "image_base64": "<base64-encoded-image>"
}
```

**Response:**
```json
{
  "message": "Image received. Please upload the next image or type 'done' if all images are uploaded."
}
```

---

### 2.9. All Images Uploaded

**POST** `/fastags/assign/images-done`

**Request:**
```json
{
  "session_id": "SESSION123"
}
```

**Response:**
```json
{
  "message": "Available Barcodes:\nBARCODE1\nBARCODE2\n...",
  "barcodes": [
    {"barcode": "BARCODE1"},
    {"barcode": "BARCODE2"}
  ]
}
```

---

### 2.10. Select Barcode

**POST** `/fastags/assign/barcode`

**Request:**
```json
{
  "session_id": "SESSION123",
  "barcode": "BARCODE1"
}
```

**Response:**
```json
{
  "message": "Who is your Vehicle Maker?\nMaker1\nMaker2\n...",
  "makers": ["Maker1", "Maker2"]
}
```

---

### 2.11. Select Vehicle Maker

**POST** `/fastags/assign/vehicle_maker`

**Request:**
```json
{
  "session_id": "SESSION123",
  "maker": "Maker1"
}
```

**Response:**
```json
{
  "message": "What is your Vehicle Model?\nModel1\nModel2\n...",
  "models": ["Model1", "Model2"]
}
```

---

### 2.12. Select Vehicle Model

**POST** `/fastags/assign/vehicle_model`

**Request:**
```json
{
  "session_id": "SESSION123",
  "model": "Model1"
}
```

**Response:**
```json
{
  "message": "What is your Vehicle Descriptor?\nDescriptor1\nDescriptor2\n...",
  "descriptors": ["Descriptor1", "Descriptor2"]
}
```

---

### 2.13. Select Vehicle Descriptor

**POST** `/fastags/assign/vehicle_descriptor`

**Request:**
```json
{
  "session_id": "SESSION123",
  "descriptor": "Descriptor1"
}
```

**Response:**
```json
{
  "message": "Checkout Details & edit if required\nVehicle no - ...\nPhone no - ...\n...Confirm if entered details are correct with Yes or No?"
}
```

---

### 2.14. Confirm All Details and Activate FASTag

**POST** `/fastags/assign/confirm`

**Request:**
```json
{
  "session_id": "SESSION123",
  "confirm": true
}
```

**Response:**
```json
{
  "message": "🎉 Success! Your FASTag has been Activated ✅\nCustomer Name: ...\nVehicle No: ...\nBarcode No: ...\n📦 Your FASTag will be shipped shortly!\n💼 Wallet Balance: ₹...\n🏷️ FASTags Left: ..."
}
```

---

## 3. FASTag Replacement Flow

> **Note:** All endpoints below require a valid `session_id` from agent authentication.

### 3.1. Start Replacement

**POST** `/fastags/replace/start`

**Request:**
```json
{
  "session_id": "SESSION123"
}
```

**Response:**
```json
{
  "message": "Now, please send the user's 10-digit Mobile Number."
}
```

---

### 3.2. Verify User Mobile for Replacement

**POST** `/fastags/replace/verify-mobile`

**Request:**
```json
{
  "session_id": "SESSION123",
  "user_mobile": "9876543210"
}
```

**Response:**
```json
{
  "message": "Sending OTP to 9876543210 🔐 Please type the 6-digit OTP."
}
```

---

### 3.3. Verify OTP for Replacement

**POST** `/fastags/replace/verify-otp`

**Request:**
```json
{
  "session_id": "SESSION123",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "Please select a plan:\n1. ₹500 - Standard Plan\n2. ₹1000 - Premium Plan\n...",
  "plans": [
    {"id": "PLAN123", "amount": 500, "description": "Standard Plan"},
    {"id": "PLAN456", "amount": 1000, "description": "Premium Plan"}
  ]
}
```

---

### 3.4. Select Plan for Replacement

**POST** `/fastags/replace/select-plan`

**Request:**
```json
{
  "session_id": "SESSION123",
  "plan_id": "PLAN123"
}
```

**Response:**
```json
{
  "message": "Please select a barcode:\nBARCODE1\nBARCODE2\n...",
  "barcodes": [
    {"id": "BARCODE1", "number": "BARCODE1"},
    {"id": "BARCODE2", "number": "BARCODE2"}
  ]
}
```

---

### 3.5. Select Barcode for Replacement

**POST** `/fastags/replace/select-barcode`

**Request:**
```json
{
  "session_id": "SESSION123",
  "barcode": "BARCODE1"
}
```

**Response:**
```json
{
  "message": "Please review the following details:\n\nCustomer Name: ...\nMobile: ...\nSelected Plan: ...\nNew Barcode: ...\n\nType 'confirm' to proceed or 'cancel' to start over.",
  "user_info": {
    "name": "John Doe",
    "mobile": "9876543210"
  }
}
```

---

### 3.6. Confirm FASTag Replacement

**POST** `/fastags/replace/confirm`

**Request:**
```json
{
  "session_id": "SESSION123",
  "confirm": true
}
```

**Response:**
```json
{
  "message": "🎉 Success! FASTag has been replaced successfully!\n\nCustomer Mobile: ...\nNew Barcode: ...\n💼 Wallet Balance: ₹...\n🏷️ FASTags Left: ..."
}
```

---

## Notes

- All endpoints require a valid `session_id` from agent authentication.
- All error responses follow the format:
  ```json
  {
    "detail": "Error message here."
  }
  ```
- All flows strictly follow the botBackendFlow.txt and shaurya_api.txt