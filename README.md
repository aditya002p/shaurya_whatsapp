# FASTag WhatsApp Bot

A comprehensive WhatsApp bot backend for FASTag registration and activation, following the complete flow as specified in the botBackendFlow.txt file and integrating with Shauryapay APIs.

## Features

- **Complete FASTag Registration Flow**: Follows the exact conversation flow specified in botBackendFlow.txt
- **Shauryapay API Integration**: Full integration with all Shauryapay APIs as documented in shuarya_api.txt
- **Session Management**: Robust session handling for multi-step conversations
- **Input Validation**: Comprehensive validation for all user inputs
- **Document Upload**: Support for RC and vehicle image uploads
- **Agent Management**: Agent wallet and FASTag inventory management
- **RESTful API**: Complete REST API for external integrations

## Project Structure

```
fastag_whatsApp_bot/
├── config.py                 # Configuration settings
├── main.py                   # Main FastAPI application
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── models/                  # Database models
│   ├── __init__.py
│   ├── agent.py            # Agent model
│   ├── session.py          # Session model
│   ├── vehicle.py          # Vehicle model
│   └── fastag.py           # FASTag model
├── services/               # Business logic services
│   ├── __init__.py
│   ├── agent_service.py    # Agent operations
│   ├── session_service.py  # Session management
│   └── shauryapay_api.py   # Shauryapay API integration
├── routers/                # API route handlers
│   ├── agent_router.py     # Agent endpoints
│   ├── session_router.py   # Session endpoints
│   ├── vehicle_router.py   # Vehicle endpoints
│   └── fastag_router.py    # FASTag endpoints
└── utils/                  # Utility functions
    ├── __init__.py
    └── validators.py       # Input validation
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fastag_whatsApp_bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with the following variables:
   ```env
   SHAURYAPAY_API_KEY=your_shauryapay_api_key
   WHATSAPP_API_URL=your_whatsapp_api_url
   WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
   WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
   DATABASE_URL=sqlite:///./fastag_bot.db
   DEBUG=False
   SECRET_KEY=your_secret_key_here
   ```

4. **Initialize the database**:
   ```bash
   python -c "from models import *; from sqlalchemy import create_engine; engine = create_engine('sqlite:///./fastag_bot.db'); Base.metadata.create_all(engine)"
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Bot Flow

The bot follows this exact conversation flow:

1. **Welcome Message**: Shows agent info and asks for vehicle number
2. **Vehicle Details**: Collects vehicle number and engine number
3. **Mobile Verification**: Collects mobile number and sends OTP
4. **OTP Verification**: Validates OTP sent to user's mobile
5. **Personal Details**: Collects first name, last name, and date of birth
6. **ID Proof**: Selects ID proof type and collects ID number
7. **Plan Selection**: Chooses between 400 Plan and 500 Plan
8. **Wallet Creation**: Creates user wallet via Shauryapay API
9. **Document Upload**: Uploads RC Front, RC Back, Vehicle Front, Vehicle Side, and Tag Fixed images
10. **Serial Number**: Enters last 4 digits of serial number
11. **Barcode Selection**: Selects from available barcodes
12. **Vehicle Specifications**: Selects vehicle maker, model, and descriptor
13. **Confirmation**: Reviews all details and confirms
14. **Activation**: Activates FASTag and completes the process

## API Endpoints

### Agents
- `GET /agents/` - Get all agents
- `GET /agents/{agent_id}` - Get agent by ID
- `POST /agents/` - Create new agent
- `PUT /agents/{agent_id}` - Update agent
- `DELETE /agents/{agent_id}` - Delete agent
- `POST /agents/{agent_id}/decrement-fastags` - Decrement FASTags

### Sessions
- `GET /sessions/` - Get all sessions
- `GET /sessions/{session_id}` - Get session by ID
- `POST /sessions/` - Create new session
- `PUT /sessions/{session_id}` - Update session
- `PUT /sessions/{session_id}/state` - Update session state
- `POST /sessions/{session_id}/documents` - Add document
- `POST /sessions/{session_id}/complete` - Complete session
- `DELETE /sessions/{session_id}` - Delete session

### Vehicles
- `GET /vehicles/` - Get all vehicles
- `GET /vehicles/{vehicle_id}` - Get vehicle by ID
- `GET /vehicles/by-number/{vehicle_number}` - Get vehicle by number
- `POST /vehicles/` - Create new vehicle
- `PUT /vehicles/{vehicle_id}` - Update vehicle
- `DELETE /vehicles/{vehicle_id}` - Delete vehicle
- `GET /vehicles/manufacturers` - Get vehicle manufacturers
- `GET /vehicles/manufacturers/{manufacturer}/models` - Get vehicle models
- `GET /vehicles/descriptors` - Get vehicle descriptors

### FASTags
- `GET /fastags/` - Get all FASTags
- `GET /fastags/{fastag_id}` - Get FASTag by ID
- `GET /fastags/by-tag/{tag_number}` - Get FASTag by tag number
- `POST /fastags/` - Create new FASTag
- `PUT /fastags/{fastag_id}` - Update FASTag
- `POST /fastags/{fastag_id}/activate` - Activate FASTag
- `POST /fastags/{fastag_id}/deactivate` - Deactivate FASTag
- `POST /fastags/{fastag_id}/recharge` - Recharge FASTag
- `GET /fastags/{fastag_id}/transactions` - Get transaction history
- `DELETE /fastags/{fastag_id}` - Delete FASTag

### WhatsApp Webhook
- `POST /webhook` - WhatsApp message webhook

## Shauryapay API Integration

The bot integrates with all Shauryapay APIs as documented in shuarya_api.txt:

1. **Generate OTP by Vehicle** (`/generate_otp_by_vehicle`)
2. **Validate OTP** (`/validate_otp_bajaj`)
3. **Update Customer Details** (`/update_customer_details`)
4. **Upload Document** (`/uploadDocument`)
5. **Update Vehicle Details** (`/update_vehicle_details`)

## Configuration

The application uses a centralized configuration system in `config.py`:

- **API Configuration**: Shauryapay and WhatsApp API settings
- **Database Configuration**: Database connection settings
- **Vehicle Data**: Manufacturers, models, and descriptors
- **Session States**: All possible conversation states
- **ID Proof Types**: Supported ID proof types
- **Plans**: Available FASTag plans

## Validation

The application includes comprehensive input validation:

- Vehicle number format validation
- Mobile number validation
- OTP format validation
- Date of birth validation
- ID proof number validation
- Serial number validation

## Error Handling

The application includes robust error handling:

- API error handling with proper HTTP status codes
- Input validation with user-friendly error messages
- Session state validation
- Database error handling

## Development

### Adding New Features

1. **New API Endpoints**: Add routes in the appropriate router file
2. **New Models**: Create models in the `models/` directory
3. **New Services**: Add business logic in the `services/` directory
4. **New Validators**: Add validation logic in `utils/validators.py`

### Testing

The application can be tested using:

1. **API Testing**: Use the Swagger UI at `/docs`
2. **Webhook Testing**: Send POST requests to `/webhook`
3. **Unit Testing**: Add test files in a `tests/` directory

## Deployment

### Production Deployment

1. **Environment Variables**: Set all required environment variables
2. **Database**: Use a production database (PostgreSQL, MySQL)
3. **Web Server**: Use Gunicorn or uWSGI with a reverse proxy
4. **SSL**: Configure SSL certificates for HTTPS
5. **Monitoring**: Set up application monitoring and logging

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

# Interakt Integration Guide for FASTag WhatsApp Bot

## Overview
This guide explains how to integrate your FASTag WhatsApp bot with Interakt's no-code platform.

## Prerequisites
- ✅ FastAPI backend running on `http://localhost:8000`
- ✅ All dependencies installed
- ✅ Database configured
- ✅ Shauryapay API credentials configured

## Interakt Workflow Setup

### 1. Initial Setup in Interakt
1. **Create New Workflow** in Interakt
2. **Set Trigger**: WhatsApp message received
3. **Add Webhook**: Point to your backend endpoint

### 2. Webhook Configuration
**URL**: `http://your-domain.com/webhook`
**Method**: POST
**Content-Type**: application/json

### 3. Workflow Steps

#### Step 1: Agent Mobile Number Collection
- **Message**: "Please enter your registered mobile number to continue."
- **Variable**: Store user input as `agent_mobile`
- **Webhook**: POST to `/agents/start`
- **Body**:
```json
{
    "mobile_number": "{{agent_mobile}}"
}
```

#### Step 2: Agent OTP Verification
- **Message**: "OTP sent to your mobile. Please enter the 4-digit OTP."
- **Variable**: Store user input as `agent_otp`
- **Webhook**: POST to `/agents/verify_otp`
- **Body**:
```json
{
    "mobile_number": "{{agent_mobile}}",
    "otp": "{{agent_otp}}"
}
```

#### Step 3: Agent Options
- **Message**: "Hi {{agent_name}} 👋,\n💼Your Wallet Balance: ₹{{wallet_balance}}, 🏷️ FASTags Left: {{fastags_left}}"
- **Buttons**: 
  - "Assign a FASTag"
  - "Replace a FASTag"

#### Step 4: Vehicle Number Collection
- **Message**: "Let's get your FASTag in just a few steps. 🚗\nPlease enter your Vehicle Number (e.g., MH12AB1234)"
- **Variable**: Store as `vehicle_number`
- **Webhook**: POST to `/fastags/assign/vehicle_number`
- **Body**:
```json
{
    "session_id": "{{session_id}}",
    "vehicle_number": "{{vehicle_number}}"
}
```

#### Step 5: Engine Number Collection
- **Message**: "Got it ✅Share the last 5 digits of engine no."
- **Variable**: Store as `engine_number`
- **Webhook**: POST to `/fastags/assign/engine_number`

#### Step 6: User Mobile Number
- **Message**: "Now send user's 10-digit Mobile Number:"
- **Variable**: Store as `user_mobile`
- **Webhook**: POST to `/fastags/assign/user_mobile`

#### Step 7: User OTP Verification
- **Message**: "Sending OTP to your {{user_mobile}} 🔐\nPlease type the 6-digit OTP\n🔁 Didn't get the OTP? Reply Resend"
- **Variable**: Store as `user_otp`
- **Webhook**: POST to `/fastags/assign/user_otp`

#### Step 8: User Information Collection
- **First Name**: "Share your FirstName"
- **Last Name**: "Share your LastName"  
- **DOB**: "Share your DOB (DD-MM-YYYY)/(Date-Month-Year)"
- **Webhook**: POST to `/fastags/assign/user_info`

#### Step 9: ID Proof Selection
- **Message**: "Thanks {{user_name}} 🙌\nChoose your ID Proof type:\n1. PAN\n2. Passport no - ask for expiry date\n3. Driving License - expiry date\n4. Voter Id"
- **Dropdown**: ID proof options
- **Webhook**: POST to `/fastags/assign/id_proof`

#### Step 10: Plan Selection
- **Message**: "Select your Plan:\n400 Plan\n500 Plan\nSat/Sun - limited offer no other offers"
- **Webhook**: POST to `/fastags/assign/plan`

#### Step 11: Document Upload
- **RC Front**: "Now please send the following 5 images one by one:\n📄 RC Front"
- **RC Back**: "📄 RC Back"
- **Vehicle Front**: "📸 Vehicle Front"
- **Vehicle Side**: "📸 Vehicle Side"
- **Tag Fixed**: "📸 Tag Fixed (If available)"
- **Webhook**: POST to `/fastags/assign/upload_image`

#### Step 12: Serial Number
- **Message**: "✅ All images received!\nEnter Last 4 digits of Serial Number(Barcode)"
- **Webhook**: POST to `/fastags/assign/serial_number`

#### Step 13: Barcode Selection
- **Message**: "Available Barcodes:\n{{barcode_list}}"
- **Webhook**: POST to `/fastags/assign/barcode`

#### Step 14: Vehicle Details
- **Maker**: "Who is your Vehicle Maker?\n{{maker_list}}"
- **Model**: "What is your Vehicle Model?\n{{model_list}}"
- **Descriptor**: "What is your Vehicle Descriptor\n{{descriptor_list}}"
- **Webhook**: POST to respective endpoints

#### Step 15: Confirmation
- **Message**: "Checkout Details & edit if required\nVehicle no - {{vehicle_number}}\nPhone no - {{user_mobile}}\nLast 5 digits of engine no - {{engine_number}}\nAadhar No - {{id_proof_number}}\nPlan - {{plan}}\nVehicle Maker - {{maker}}\nVehicle Model - {{model}}\nVehicle Descriptor - {{descriptor}}\nConfirm if entered details are correct with Yes or No?"
- **Buttons**: "Yes", "No"
- **Webhook**: POST to `/fastags/assign/confirm`

#### Step 16: Success Message
- **Message**: "🎉 Success! Your FASTag has been Activated ✅\n\nCustomer Name: {{customer_name}}\nVehicle No: {{vehicle_number}}\nBarcode No: {{barcode}}\n\n📦 Your FASTag will be shipped shortly!\nNeed help? Visit Bajaj App Link\n\n💼 Wallet Balance: ₹{{wallet_balance}}\n🏷️ FASTags Left: {{fastags_left}}\nLet's continue with the next one. 🚗"

## API Endpoints for Interakt

### Core Endpoints
1. **Agent Verification**
   - `POST /agents/start` - Start agent verification
   - `POST /agents/verify_otp` - Verify agent OTP

2. **Session Management**
   - `POST /sessions/` - Create session
   - `GET /sessions/{session_id}` - Get session details

3. **FASTag Assignment Flow**
   - `POST /fastags/assign/vehicle_number`
   - `POST /fastags/assign/engine_number`
   - `POST /fastags/assign/user_mobile`
   - `POST /fastags/assign/user_otp`
   - `POST /fastags/assign/user_info`
   - `POST /fastags/assign/id_proof`
   - `POST /fastags/assign/plan`
   - `POST /fastags/assign/upload_image`
   - `POST /fastags/assign/serial_number`
   - `POST /fastags/assign/barcode`
   - `POST /fastags/assign/vehicle_maker`
   - `POST /fastags/assign/vehicle_model`
   - `POST /fastags/assign/vehicle_descriptor`
   - `POST /fastags/assign/confirm`

4. **Data Lookup Endpoints**
   - `GET /vehicles/manufacturers` - Get vehicle manufacturers
   - `GET /vehicles/manufacturers/{maker}/models` - Get vehicle models
   - `GET /vehicles/descriptors` - Get vehicle descriptors

## Response Format for Interakt

### Success Response
```json
{
    "status": "success",
    "message": "Bot response message",
    "session_id": "session_123",
    "options": ["Option 1", "Option 2"],
    "data": {
        "key": "value"
    }
}
```

### Error Response
```json
{
    "status": "error",
    "message": "Error message",
    "session_id": "session_123"
}
```

## Environment Variables for Production

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/fastag_db

# Shauryapay API
SHAURYAPAY_BASE_URL=https://shauryapay.com
SHAURYAPAY_API_KEY=your_api_key

# SMS Configuration
SMS_USER=your_sms_user
SMS_PASS=your_sms_pass
SMS_SENDER=SHYPAY
SMS_URL=http://bhashsms.com/api/sendmsg.php

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Testing the Integration

### 1. Local Testing
```bash
# Start the server
python main.py

# Test endpoints
curl -X POST http://localhost:8000/agents/start \
  -H "Content-Type: application/json" \
  -d '{"mobile_number": "9876543210"}'
```

### 2. Interakt Testing
1. **Set up webhook URL** in Interakt
2. **Test each step** with sample data
3. **Verify responses** match expected format
4. **Check error handling** with invalid inputs

## Common Issues and Solutions

### 1. Webhook Timeout
- **Issue**: Interakt webhook times out
- **Solution**: Ensure your server responds within 10 seconds

### 2. Session Management
- **Issue**: Session lost between steps
- **Solution**: Always pass session_id in webhook responses

### 3. Image Upload
- **Issue**: Images not uploading correctly
- **Solution**: Use base64 encoding for images

### 4. OTP Verification
- **Issue**: OTP validation failing
- **Solution**: Check SMS configuration and API credentials

## Production Deployment

### 1. Server Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="your_db_url"
export SHAURYAPAY_API_KEY="your_api_key"

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. SSL Certificate
- **Required**: HTTPS for production webhooks
- **Setup**: Use Let's Encrypt or your SSL provider

### 3. Database Migration
```bash
# Run database migrations
alembic upgrade head
```

### 4. Monitoring
- **Logs**: Monitor application logs
- **Health Check**: Set up health check endpoint
- **Error Tracking**: Implement error tracking (Sentry)

## Support and Maintenance

### 1. Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 2. Error Handling
```python
try:
    # Your code
except Exception as e:
    logger.error(f"Error: {str(e)}")
    return {"status": "error", "message": "Internal server error"}
```

### 3. Health Check Endpoint
```python
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

## Conclusion

Your codebase is now ready for Interakt integration! The key improvements made:

1. ✅ **Added agent verification flow**
2. ✅ **Fixed session management**
3. ✅ **Corrected API responses**
4. ✅ **Added proper error handling**
5. ✅ **Created comprehensive documentation**

Follow this guide to set up your Interakt workflow and test the integration thoroughly before going live. 


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
