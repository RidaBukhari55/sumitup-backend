import re
import traceback
import secrets
import time
from database import users_collection
from models.User import User
from services.email_service import email_service

# Temporary storage for reset tokens (in production, use Redis or database)
reset_tokens = {}


# ===============================
# Password validation (INLINE)
# ===============================
def _is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


# ===============================
# MANUAL REGISTRATION
# ===============================
def register_user(data):
    try:
        if users_collection.find_one({"email": data["email"]}):
            return {"error": "USER_ALREADY_EXISTS"}

        if not _is_valid_password(data["password"]):
            return {"error": "WEAK_PASSWORD"}

        user = User(
            full_name=data.get("full_name", ""),
            email=data["email"],
            password=data["password"],
            role=data.get("role", "learner"),
            provider="local"
        )

        result = users_collection.insert_one(user.to_dict())
        print(f" User inserted with ID: {result.inserted_id}")
        return {"success": True}
    except Exception as e:
        print(f" Registration error: {str(e)}")
        print(traceback.format_exc())
        return {"error": f"REGISTRATION_FAILED: {str(e)}"}


# ===============================
# GOOGLE REGISTRATION / LOGIN
# ===============================
def register_with_google(data):
    user = users_collection.find_one({"email": data["email"]})

    # Existing Google or local user → login
    if user:
        return {
            "success": True,
            "role": user["role"],
            "is_new": False
        }

    # New Google user
    user = User(
        full_name=data.get("full_name", ""),
        email=data["email"],
        password=None,
        role="learner",
        provider="google"
    )

    users_collection.insert_one(user.to_dict())

    return {
        "success": True,
        "role": "learner",
        "is_new": True
    }


# ===============================
# LOGIN (LOCAL)
# ===============================
def login_user(email, password):
    user = users_collection.find_one({"email": email})

    if not user:
        return {"error": "USER_NOT_FOUND"}

    if user["provider"] != "local":
        return {"error": "GOOGLE_ACCOUNT"}

    if user["password"] != password:
        return {"error": "INVALID_PASSWORD"}

    return {
        "success": True,
        "role": user["role"]
    }


# ===============================  
# FORGOT PASSWORD
# ===============================
def forgot_password(email):
    try:
        user = users_collection.find_one({"email": email})
        
        if not user:
            return {"error": "USER_NOT_FOUND"}
        
        if user["provider"] != "local":
            return {"error": "GOOGLE_ACCOUNT"}
        
        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        expiry_time = time.time() + 3600  # 1 hour expiry
        
        # Store token temporarily (in production, use Redis/database)
        reset_tokens[reset_token] = {
            "email": email,
            "expiry": expiry_time
        }
        
        # Send password reset email
        email_sent = email_service.send_password_reset_email(email, reset_token)
        
        if not email_sent:
            # Clean up token if email failed
            del reset_tokens[reset_token]
            return {"error": "EMAIL_SEND_FAILED"}
        
        print(f"✅ Password reset email sent to {email}")
        return {
            "success": True,
            "message": "Password reset email sent successfully",
            "expires_in": "1 hour"
        }
    except Exception as e:
        print(f"❌ Forgot password error: {str(e)}")
        print(traceback.format_exc())
        return {"error": f"FORGOT_PASSWORD_FAILED: {str(e)}"}


# ===============================
# RESET PASSWORD
# ===============================
def reset_password(token, new_password):
    try:
        # Check if token exists and is valid
        if token not in reset_tokens:
            return {"error": "INVALID_TOKEN"}
        
        token_data = reset_tokens[token]
        
        # Check if token has expired
        if time.time() > token_data["expiry"]:
            del reset_tokens[token]  # Clean up expired token
            return {"error": "EXPIRED_TOKEN"}
        
        # Validate new password
        if not _is_valid_password(new_password):
            return {"error": "WEAK_PASSWORD"}
        
        email = token_data["email"]
        
        # Update password in database
        result = users_collection.update_one(
            {"email": email},
            {"$set": {"password": new_password}}
        )
        
        if result.modified_count == 0:
            return {"error": "UPDATE_FAILED"}
        
        # Clean up used token
        del reset_tokens[token]
        
        print(f"✅ Password reset successful for {email}")
        return {"success": True}
        
    except Exception as e:
        print(f"❌ Reset password error: {str(e)}")
        print(traceback.format_exc())
        return {"error": f"RESET_PASSWORD_FAILED: {str(e)}"}
