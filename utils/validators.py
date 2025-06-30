import re
from datetime import datetime
from typing import Optional

class Validators:
    def __init__(self):
        pass
    
    def validate_vehicle_number(self, vehicle_number: str) -> bool:
        """
        Validate vehicle number format (e.g., MH12AB1234)
        """
        if not vehicle_number:
            return False
        
        # Remove spaces and convert to uppercase
        vehicle_number = vehicle_number.strip().upper()
        
        # Pattern for Indian vehicle numbers: 2 letters + 2 digits + 2 letters + 4 digits
        pattern = r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$'
        
        return bool(re.match(pattern, vehicle_number))
    
    def validate_engine_number(self, engine_number: str) -> bool:
        """
        Validate engine number (last 5 digits)
        """
        if not engine_number:
            return False
        
        engine_number = engine_number.strip()
        
        # Should be exactly 5 digits
        return len(engine_number) == 5 and engine_number.isdigit()
    
    def validate_mobile_number(self, mobile_number: str) -> bool:
        """
        Validate 10-digit mobile number
        """
        if not mobile_number:
            return False
        
        mobile_number = mobile_number.strip()
        
        # Remove any non-digit characters
        mobile_number = re.sub(r'\D', '', mobile_number)
        
        # Should be exactly 10 digits and start with 6, 7, 8, or 9
        return (len(mobile_number) == 10 and 
                mobile_number.isdigit() and 
                mobile_number[0] in ['6', '7', '8', '9'])
    
    def validate_otp(self, otp: str) -> bool:
        """
        Validate 6-digit OTP
        """
        if not otp:
            return False
        
        otp = otp.strip()
        
        # Should be exactly 4 to 6 digits
        return len(otp) >= 4 and len(otp) <= 6 and otp.isdigit()
    
    def validate_dob(self, dob: str) -> bool:
        """
        Validate date of birth in various formats
        """
        if not dob:
            return False
        
        dob = dob.strip()
        
        # Try different date formats
        date_formats = [
            '%d-%m-%Y',    # DD-MM-YYYY
            '%d/%m/%Y',    # DD/MM/YYYY
            '%d %B %Y',    # DD Month YYYY
            '%d %b %Y',    # DD Mon YYYY
            '%Y-%m-%d',    # YYYY-MM-DD
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(dob, fmt)
                # Check if date is reasonable (not in future and not too old)
                current_year = datetime.now().year
                if 1900 <= parsed_date.year <= current_year:
                    return True
            except ValueError:
                continue
        
        return False
    
    def validate_aadhaar_number(self, aadhaar: str) -> bool:
        """
        Validate 12-digit Aadhaar number
        """
        if not aadhaar:
            return False
        
        aadhaar = re.sub(r'\D', '', aadhaar.strip())
        
        # Should be exactly 12 digits
        return len(aadhaar) == 12 and aadhaar.isdigit()
    
    def validate_pan_number(self, pan: str) -> bool:
        """
        Validate PAN number format
        """
        if not pan:
            return False
        
        pan = pan.strip().upper()
        
        # PAN format: 5 letters + 4 digits + 1 letter
        pattern = r'^[A-Z]{5}\d{4}[A-Z]{1}$'
        
        return bool(re.match(pattern, pan))
    
    def validate_passport_number(self, passport: str) -> bool:
        """
        Validate passport number format
        """
        if not passport:
            return False
        
        passport = passport.strip().upper()
        
        # Basic passport validation (can be enhanced based on specific requirements)
        # Usually starts with a letter and contains alphanumeric characters
        pattern = r'^[A-Z]\d{7}$'
        
        return bool(re.match(pattern, passport))
    
    def validate_driving_license(self, dl: str) -> bool:
        """
        Validate driving license number format
        """
        if not dl:
            return False
        
        dl = dl.strip().upper()
        
        # Basic DL validation (can be enhanced based on specific requirements)
        # Usually contains alphanumeric characters
        pattern = r'^[A-Z]{2}\d{2}\d{4}\d{7}$'
        
        return bool(re.match(pattern, dl))
    
    def validate_voter_id(self, voter_id: str) -> bool:
        """
        Validate voter ID number format
        """
        if not voter_id:
            return False
        
        voter_id = voter_id.strip().upper()
        
        # Basic voter ID validation (can be enhanced based on specific requirements)
        # Usually contains alphanumeric characters
        pattern = r'^[A-Z]{3}\d{7}$'
        
        return bool(re.match(pattern, voter_id))
    
    def validate_id_proof_number(self, id_type: str, id_number: str) -> bool:
        """
        Validate ID proof number based on type
        """
        if not id_number:
            return False
        
        id_number = id_number.strip()
        
        if id_type == "PAN":
            return self.validate_pan_number(id_number)
        elif id_type == "Passport":
            return self.validate_passport_number(id_number)
        elif id_type == "Driving License":
            return self.validate_driving_license(id_number)
        elif id_type == "Voter ID":
            return self.validate_voter_id(id_number)
        else:
            # For Aadhaar or other types, use Aadhaar validation
            return self.validate_aadhaar_number(id_number)
    
    def validate_serial_number(self, serial_number: str) -> bool:
        """
        Validate 4-digit serial number
        """
        if not serial_number:
            return False
        
        serial_number = serial_number.strip()
        
        # Should be exactly 4 digits
        return len(serial_number) == 4 and serial_number.isdigit()
    
    def validate_vehicle_maker(self, maker: str) -> bool:
        """
        Validate vehicle maker from allowed list
        """
        from config import Config
        
        if not maker:
            return False
        
        maker = maker.strip().upper()
        
        return maker in Config.VEHICLE_MANUFACTURERS
    
    def validate_vehicle_model(self, maker: str, model: str) -> bool:
        """
        Validate vehicle model for given maker
        """
        from config import Config
        
        if not model:
            return False
        
        model = model.strip().upper()
        maker = maker.strip().upper()
        
        # Get allowed models for the maker
        allowed_models = Config.VEHICLE_MODELS.get(maker, [])
        
        # If no specific models defined for maker, accept any non-empty string
        if not allowed_models:
            return len(model) > 0
        
        return model in allowed_models
    
    def validate_vehicle_descriptor(self, descriptor: str) -> bool:
        """
        Validate vehicle descriptor
        """
        from config import Config
        
        if not descriptor:
            return False
        
        descriptor = descriptor.strip()
        
        return descriptor in Config.VEHICLE_DESCRIPTORS
    
    def sanitize_input(self, input_text: str) -> str:
        """
        Sanitize user input to prevent injection attacks
        """
        if not input_text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_text.strip())
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized

    @staticmethod
    def validate_mobile(mobile: str) -> bool:
        return bool(re.match(r'^[6-9]\d{9}$', mobile))

    @staticmethod
    def validate_otp(otp: str) -> bool:
        return bool(re.match(r'^\d{4,6}$', otp))

    @staticmethod
    def validate_vehicle_number(vehicle_number: str) -> bool:
        return bool(re.match(r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$', vehicle_number.upper()))

    @staticmethod
    def validate_engine_number(engine_number: str) -> bool:
        return bool(re.match(r'^\d{5}$', engine_number))
