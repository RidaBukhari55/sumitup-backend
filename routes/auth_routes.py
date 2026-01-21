from fastapi import APIRouter, HTTPException, Request
from controllers.auth_controller import (
    register_user,
    login_user,
    register_with_google,
    forgot_password,
    reset_password
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ===============================
# REGISTER (MANUAL)
# ===============================
@router.post("/register")
async def register(request: Request):
    data = await request.json()
    result = register_user(data)

    if "error" in result:
        if result["error"] == "USER_ALREADY_EXISTS":
            raise HTTPException(400, "User already exists")
        if result["error"] == "WEAK_PASSWORD":
            raise HTTPException(
                400,
                "Password must be at least 8 characters and contain letters and numbers"
            )
        # Catch any database or other errors
        raise HTTPException(500, result["error"])

    return {"message": "Registration successful"}


# ===============================
# REGISTER WITH GOOGLE (ALT FLOW)
# ===============================
@router.post("/register/google")
async def register_google(request: Request):
    data = await request.json()
    result = register_with_google(data)

    redirect_to = (
        "/admin/dashboard"
        if result["role"] == "admin"
        else "/uploadVideo"
    )

    return {
        "message": "Google authentication successful",
        "is_new_user": result["is_new"],
        "redirect_to": redirect_to
    }


# ===============================
# LOGIN
# ===============================
@router.post("/login")
async def login(request: Request):
    data = await request.json()
    result = login_user(data["email"], data["password"])

    if "error" in result:
        if result["error"] == "USER_NOT_FOUND":
            raise HTTPException(404, "User not found")
        if result["error"] == "INVALID_PASSWORD":
            raise HTTPException(401, "Invalid credentials")
        if result["error"] == "GOOGLE_ACCOUNT":
            raise HTTPException(
                400,
                "This account was created using Google Sign-In"
            )

    redirect_to = (
        "/admin/dashboard"
        if result["role"] == "admin"
        else "/uploadVideo"
    )

    return {
        "message": "Login successful",
        "redirect_to": redirect_to
    }


# ===============================
# FORGOT PASSWORD
# ===============================
@router.post("/forgot-password")
async def forgot_pass(request: Request):
    data = await request.json()
    result = forgot_password(data["email"])

    if "error" in result:
        if result["error"] == "USER_NOT_FOUND":
            raise HTTPException(404, "User not found")
        if result["error"] == "GOOGLE_ACCOUNT":
            raise HTTPException(400, "This account uses Google Sign-In")
        if result["error"] == "EMAIL_SEND_FAILED":
            raise HTTPException(500, "Failed to send password reset email. Please try again.")
        raise HTTPException(500, result["error"])

    return {
        "message": "Password reset email sent successfully",
        "expires_in": result["expires_in"]
    }


# ===============================
# RESET PASSWORD
# ===============================
@router.post("/reset-password")
async def reset_pass(request: Request):
    data = await request.json()
    result = reset_password(data["token"], data["new_password"])

    if "error" in result:
        if result["error"] == "INVALID_TOKEN":
            raise HTTPException(400, "Invalid or expired reset token")
        if result["error"] == "EXPIRED_TOKEN":
            raise HTTPException(400, "Reset token has expired")
        if result["error"] == "WEAK_PASSWORD":
            raise HTTPException(400, "Password must be at least 8 characters and contain letters and numbers")
        raise HTTPException(500, result["error"])

    return {"message": "Password reset successful"}
