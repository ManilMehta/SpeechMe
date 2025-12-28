from fastapi import HTTPException, Header
from typing import Optional
from supabase import create_client
import os

def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify the JWT token using Supabase and extract user ID
    """
    print(f"🔐 Auth header received: {authorization[:50] if authorization else 'None'}...")
    
    if not authorization:
        print("❌ No authorization header")
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        
        if len(parts) != 2:
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        scheme, token = parts
        
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        print(f"🔐 Verifying token with Supabase...")
        
        # Create Supabase client with anon key
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")  # Use anon key, not service key
        )
        
        # Verify the token by getting the user
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            print("❌ Invalid token - no user found")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user_response.user.id
        
        print(f"✅ Auth successful! User ID: {user_id}")
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")