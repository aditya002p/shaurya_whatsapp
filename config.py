import os
from typing import Dict, List

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fastag_bot.db")

    # Shauryapay API
    SHAURYAPAY_BASE_URL = os.getenv("SHAURYAPAY_BASE_URL", "https://shauryapay.com")
    SHAURYAPAY_API_KEY = os.getenv("SHAURYAPAY_API_KEY", "")
    AGGR_CHANNEL = os.getenv("AGGR_CHANNEL", "SHSK")
    OCP_APIM_SUBSCRIPTION_KEY = os.getenv("OCP_APIM_SUBSCRIPTION_KEY", "da0b62a0884b435488b72f1cb14f89e7")

    # SMS Configuration (bhashsms.com)
    SMS_USER = "ShauryaSoftrack"
    SMS_PASS = "123456"
    SMS_SENDER = "SHYPAY"
    SMS_URL = "http://bhashsms.com/api/sendmsg.php"
    SMS_PRIORITY = "ndnd"
    SMS_STYPE = "normal"

    # App
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # WhatsApp API Configuration (assuming you're using WhatsApp Business API)
    WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
    WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    
    # Vehicle Manufacturers and Models
    VEHICLE_MANUFACTURERS = {
        "MARUTI": "MARUTI",
        "TOYOTA": "TOYOTA", 
        "TATA": "TATA",
        "HYUNDAI": "HYUNDAI",
        "KIA MOTORS": "KIA MOTORS",
        "MAHINDRA & MAHINDRA": "MAHINDRA & MAHINDRA",
        "MAHINDRA RENAULT": "MAHINDRA RENAULT",
        "MAHINDRA REVA": "MAHINDRA REVA",
        "MAHINDRA SSANGYONG": "MAHINDRA SSANGYONG",
        "HONDA": "HONDA",
        "FOTON": "FOTON",
        "JAYEM AUTOMOTIVE": "JAYEM AUTOMOTIVE",
        "NISSAN MOTORS": "NISSAN MOTORS",
        "ASTON MARTIN": "ASTON MARTIN"
    }
    
    # Vehicle Models by Manufacturer
    VEHICLE_MODELS = {
        "TOYOTA": [
            "ALPHARD", "CAMRY", "COROLLA", "COROLLA ALTIS", "ETIOS", 
            "ETIOS CROSS", "ETIOS LIVA", "FORTUNER", "GLANZA", "INNOVA"
        ],
        "MARUTI": [
            "SWIFT", "DZIRE", "BALENO", "BREZZA", "ERTIGA", "S-CROSS"
        ],
        "HYUNDAI": [
            "I10", "I20", "VENUE", "CRETA", "VERNA", "ELANTRA"
        ],
        "TATA": [
            "TIAGO", "TIGOR", "NEXON", "HARRIER", "SAFARI", "PUNCH"
        ]
    }
    
    # Vehicle Descriptors
    VEHICLE_DESCRIPTORS = ["Petrol", "Diesel", "CNG", "Electric", "Hybrid"]
    
    # ID Proof Types
    ID_PROOF_TYPES = {
        "1": "PAN",
        "2": "Passport",
        "3": "Driving License", 
        "4": "Voter ID"
    }
    
    # Plans
    PLANS = {
        "400": "400 Plan",
        "500": "500 Plan"
    }
    
    # Image Types for Document Upload
    IMAGE_TYPES = [
        "RC_FRONT",
        "RC_BACK", 
        "VEHICLE_FRONT",
        "VEHICLE_SIDE",
        "TAG_FIXED"
    ]
    
    # Session States
    SESSION_STATES = {
        "INIT": "INIT",
        "AGENT_MOBILE": "AGENT_MOBILE",
        "AGENT_OTP": "AGENT_OTP", 
        "AGENT_VERIFIED": "AGENT_VERIFIED",
        "VEHICLE_NUMBER": "VEHICLE_NUMBER",
        "ENGINE_NUMBER": "ENGINE_NUMBER", 
        "MOBILE_NUMBER": "MOBILE_NUMBER",
        "OTP_SENT": "OTP_SENT",
        "OTP_VERIFIED": "OTP_VERIFIED",
        "FIRST_NAME": "FIRST_NAME",
        "LAST_NAME": "LAST_NAME",
        "DOB": "DOB",
        "ID_PROOF_TYPE": "ID_PROOF_TYPE",
        "ID_PROOF_NUMBER": "ID_PROOF_NUMBER",
        "PLAN_SELECTION": "PLAN_SELECTION",
        "WALLET_CREATED": "WALLET_CREATED",
        "RC_FRONT": "RC_FRONT",
        "RC_BACK": "RC_BACK",
        "VEHICLE_FRONT": "VEHICLE_FRONT",
        "VEHICLE_SIDE": "VEHICLE_SIDE",
        "TAG_FIXED": "TAG_FIXED",
        "SERIAL_NUMBER": "SERIAL_NUMBER",
        "BARCODE_SELECTION": "BARCODE_SELECTION",
        "VEHICLE_MAKER": "VEHICLE_MAKER",
        "VEHICLE_MODEL": "VEHICLE_MODEL",
        "VEHICLE_DESCRIPTOR": "VEHICLE_DESCRIPTOR",
        "CONFIRMATION": "CONFIRMATION",
        "COMPLETED": "COMPLETED",
        # Replace FASTag flow states
        "REPLACE_USER_MOBILE": "REPLACE_USER_MOBILE",
        "REPLACE_USER_OTP": "REPLACE_USER_OTP",
        "REPLACE_USER_VERIFIED": "REPLACE_USER_VERIFIED",
        "REPLACE_PLAN_SELECTION": "REPLACE_PLAN_SELECTION",
        "REPLACE_BARCODE_SELECTION": "REPLACE_BARCODE_SELECTION",
        "REPLACE_CONFIRMATION": "REPLACE_CONFIRMATION"
    }
