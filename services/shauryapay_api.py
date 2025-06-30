import requests
import json
import base64
from typing import Dict, Any, Optional, List
from config import Config

class ShauryapayAPI:
    def __init__(self):
        self.base_url = Config.SHAURYAPAY_BASE_URL
        self.default_headers = {
            "Content-Type": "application/json",
            "aggr_channel": Config.AGGR_CHANNEL,
            "ocp-apim-subscription-key": Config.OCP_APIM_SUBSCRIPTION_KEY
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Generic request handler for all API calls."""
        url = f"{self.base_url}{endpoint}"
        headers = self.default_headers.copy()
        
        if "custom_headers" in kwargs:
            headers.update(kwargs.pop("custom_headers"))

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            return {"status": "error", "message": f"HTTP error occurred: {http_err}", "data": None}
        except requests.exceptions.RequestException as req_err:
            return {"status": "error", "message": f"Request error occurred: {req_err}", "data": None}
        except ValueError:
            return {"status": "error", "message": "Failed to decode JSON response", "data": None}

    def get_agent_by_mobile(self, mobile_number: str) -> Dict[str, Any]:
        """Get agent details by mobile number."""
        return self._make_request("GET", f"/api/agent/get_by_mobile/{mobile_number}")

    def get_agent_by_id(self, agent_id: int) -> Dict[str, Any]:
        """Get agent details by ID."""
        return self._make_request("GET", f"/api/agent/get_by_id/{agent_id}")

    def get_barcodes(self, agent_id: int) -> Dict[str, Any]:
        """Get available barcodes for an agent."""
        return self._make_request("GET", f"/api/agent/get_barcodes/{agent_id}")

    def generate_otp_by_vehicle(self, vehicle_number: str, agent_id: int, mobile_number: str, engine_no: str) -> Dict[str, Any]:
        """Generate OTP for vehicle verification."""
        payload = {
            "vehicle_number": vehicle_number,
            "agent_id": agent_id,
            "mobile_number": mobile_number,
            "isChassis": 0,
            "engineNo": engine_no,
            "chassisNo": ""
        }
        return self._make_request("POST", "/generate_otp_by_vehicle", json=payload)

    def validate_otp(self, request_id: str, session_id: str, agent_id: int, otp: str) -> Dict[str, Any]:
        """Validate OTP sent to the user's mobile."""
        payload = {
            "requestId": request_id,
            "sessionId": session_id,
            "agent_id": agent_id,
            "otp": otp
        }
        return self._make_request("POST", "/validate_otp_bajaj", json=payload)

    def update_customer_details(self, session_id: str, vehicle_number: str, name: str, last_name: str, dob: str, doc_type: str, doc_no: str, plan_id: str, expiry_date: str = "") -> Dict[str, Any]:
        """Update customer details after OTP verification."""
        payload = {
            "sessionId": session_id,
            "vehicle_number": vehicle_number,
            "name": name,
            "lastName": last_name,
            "dob": dob,
            "docType": doc_type,
            "docNo": doc_no,
            "expiryDate": expiry_date,
            "plan_id": plan_id
        }
        return self._make_request("POST", "/update_customer_details", json=payload)

    def upload_document(self, session_id: str, image_type: str, image_base64: str) -> Dict[str, Any]:
        """Upload document images (e.g., RC Front, RC Back)."""
        payload = {
            "sessionId": session_id,
            "imageType": image_type,
            "image": image_base64
        }
        return self._make_request("POST", "/uploadDocument", json=payload)

    def get_vehicle_makers(self, session_id: str, agent_id: int, vehicle_number: str) -> Dict[str, Any]:
        """Get a list of vehicle manufacturers."""
        payload = {
            "sessionId": session_id,
            "agent_id": str(agent_id),
            "vehicle_number": vehicle_number
        }
        return self._make_request("POST", "/vehicleMakerList", json=payload)

    def get_vehicle_descriptors(self) -> Dict[str, Any]:
        """Get a list of vehicle descriptors."""
        return self._make_request("GET", "/get_vehicleDescriptor")

    def get_vehicle_details(self, vehicle_number: str) -> Dict[str, Any]:
        """Get latest vehicle details."""
        return self._make_request("POST", "/get_single_vehicle_for_latest_Details", json={"vehicle_number": vehicle_number})

    def update_vehicle_details(self, session_id: str, vehicle_number: str, agent_id: int, serial_no: str, engine_no: str, chassis_no: str, vehicle_manuf: str, model: str, vehicle_colour: str, vehicle_type: str, vehicle_descriptor: str, state_of_registration: str) -> Dict[str, Any]:
        """Update vehicle details with all specifications."""
        payload = {
            "sessionId": session_id,
            "vehicle_number": vehicle_number,
            "agent_id": agent_id,
            "serialNo": serial_no,
            "engineNo": engine_no,
            "chassisNo": chassis_no,
            "vehicleManuf": vehicle_manuf,
            "model": model,
            "vehicleColour": vehicle_colour,
            "type": "4W",
            "vehicleType": vehicle_type,
            "vehicleDescriptor": vehicle_descriptor,
            "stateOfRegistration": state_of_registration
        }
        return self._make_request("POST", "/update_vehicle_details", json=payload)
    
    def activate_fastag(self, session_id: str, barcode: str) -> Dict[str, Any]:
        """
        Activate FASTag with selected barcode
        This would be the final step in the flow
        """
        # This is a placeholder - implement based on your backend requirements
        return {
            "status": "true",
            "message": "FASTag activated successfully",
            "data": {
                "tag_number": barcode,
                "activation_status": "success"
            }
        }

    def check_user_exists(self, mobile_number: str) -> bool:
        """Check if a user exists in the system."""
        response = self._make_request("GET", f"/users/check/{mobile_number}", params={})
        return response.get("exists", False)

    def generate_otp(self, mobile_number: str) -> Dict[str, Any]:
        """Generate OTP for user verification."""
        response = self._make_request("POST", "/users/otp/generate", json={
            "mobile_number": mobile_number
        })
        return {
            "success": response.get("status") == "success",
            "message": response.get("message", "OTP sent successfully")
        }

    def verify_otp(self, mobile_number: str, otp: str) -> Dict[str, Any]:
        """Verify OTP for user."""
        response = self._make_request("POST", "/users/otp/verify", json={
            "mobile_number": mobile_number,
            "otp": otp
        })
        return {
            "success": response.get("status") == "success",
            "message": response.get("message", "OTP verified successfully")
        }

    def get_available_plans(self) -> List[Dict[str, Any]]:
        """Get list of available FASTag plans."""
        response = self._make_request("GET", "/plans", params={})
        return response.get("plans", [])

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific plan."""
        response = self._make_request("GET", f"/plans/{plan_id}", params={})
        return response.get("plan")

    def get_available_barcodes(self) -> List[Dict[str, Any]]:
        """Get list of available barcodes."""
        response = self._make_request("GET", "/barcodes/available", params={})
        return response.get("barcodes", [])

    def get_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific barcode."""
        response = self._make_request("GET", f"/barcodes/{barcode}", params={})
        return response.get("barcode")

    def get_user_info(self, mobile_number: str) -> Optional[Dict[str, Any]]:
        """Get user information."""
        response = self._make_request("GET", f"/users/{mobile_number}", params={})
        return response.get("user")

    def process_replacement(self, user_mobile: str, new_barcode: str, plan_id: str) -> Dict[str, Any]:
        """Process FASTag replacement."""
        response = self._make_request("POST", "/fastag/replace", json={
            "user_mobile": user_mobile,
            "new_barcode": new_barcode,
            "plan_id": plan_id
        })
        return {
            "success": response.get("status") == "success",
            "message": response.get("message", "FASTag replaced successfully")
        }

    def extract_request_id(self, response: Dict[str, Any]) -> Optional[str]:
        """Extracts the request ID from the API response."""
        data = response.get("data")
        if isinstance(data, list) and data:
            return data[0].get("requestId")
        if isinstance(data, dict):
            return data.get("requestId")
        return None

    def extract_session_id(self, response: Dict[str, Any]) -> Optional[str]:
        """Extracts the session ID from the API response."""
        data = response.get("data")
        if isinstance(data, list) and data:
            return data[0].get("sessionId")
        if isinstance(data, dict):
            return data.get("sessionId")
        return None
