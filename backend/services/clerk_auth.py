"""
Clerk Authentication Service for Animathic Backend
Handles user authentication and authorization using Clerk
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException, Header
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
import jwt
from dotenv import load_dotenv
import base64

load_dotenv()

logger = logging.getLogger(__name__)

class ClerkAuthService:
    def __init__(self):
        self.enabled = True
        # Use custom Clerk domain, but also accept standard Clerk domain as fallback
        self.clerk_issuer = "https://clerk.animathic.com"
        self.clerk_issuer_fallback = "https://clerk.dev"  # Standard Clerk domain as fallback
        # Audience should be the frontend domain or can be None for Clerk
        self.clerk_audience = None
        
        # Store Clerk secret key for fallback JWKS fetch
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
        
        # For development/testing, allow simplified tokens
        self.allow_dev_tokens = os.getenv("ENVIRONMENT", "production") != "production"
        
        logger.info(f"ClerkAuthService initialized - Primary Issuer: {self.clerk_issuer}, Fallback: {self.clerk_issuer_fallback}, Audience: {self.clerk_audience}")
    
    async def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token from Clerk"""
        try:
            logger.info(f"Starting JWT token verification for token: {token[:20]}...")
            
            # First, try to decode without verification to get header
            unverified_header = jwt.get_unverified_header(token)
            key_id = unverified_header.get('kid')
            
            logger.info(f"JWT header: {unverified_header}")
            logger.info(f"Key ID: {key_id}")
            
            if not key_id:
                raise HTTPException(status_code=401, detail="Invalid token format - missing key ID")
            
            # Fetch public keys from Clerk
            logger.info("Fetching public keys from Clerk...")
            async with httpx.AsyncClient() as client:
                # Try multiple JWKS endpoints - Clerk might have different public endpoints
                jwks_urls = [
                    "https://clerk.animathic.com/.well-known/jwks.json",
                    "https://clerk.dev/.well-known/jwks.json",
                    "https://api.clerk.dev/v1/jwks"
                ]
                
                jwks = None
                for url in jwks_urls:
                    try:
                        logger.info(f"Trying JWKS endpoint: {url}")
                        response = await client.get(url, timeout=10.0)
                        if response.status_code == 200:
                            jwks = response.json()
                            logger.info(f"Successfully retrieved JWKS from: {url}")
                            break
                        else:
                            logger.warning(f"Failed to fetch from {url}: {response.status_code}")
                    except Exception as e:
                        logger.warning(f"Error fetching from {url}: {e}")
                        continue
                
                if not jwks:
                    # Fallback: Try using the Clerk secret key to fetch JWKS
                    logger.info("Public JWKS endpoints failed, trying with secret key...")
                    try:
                        if hasattr(self, 'clerk_secret_key') and self.clerk_secret_key:
                            headers = {
                                "Authorization": f"Bearer {self.clerk_secret_key}",
                                "Content-Type": "application/json"
                            }
                            response = await client.get(
                                "https://api.clerk.dev/v1/jwks",
                                headers=headers,
                                timeout=10.0
                            )
                            if response.status_code == 200:
                                jwks = response.json()
                                logger.info("Successfully retrieved JWKS using secret key")
                            else:
                                logger.error(f"Failed to fetch JWKS with secret key: {response.status_code}")
                        else:
                            logger.error("No Clerk secret key available for fallback")
                    except Exception as e:
                        logger.error(f"Error in fallback JWKS fetch: {e}")
                
                if not jwks:
                    logger.error("Failed to fetch JWKS from all endpoints and fallback methods")
                    raise HTTPException(status_code=500, detail="Failed to fetch public keys from Clerk")
                
                logger.info(f"Retrieved {len(jwks.get('keys', []))} public keys from Clerk")
                
                public_key = None
                
                # Find the matching public key
                for key in jwks.get('keys', []):
                    if key.get('kid') == key_id:
                        try:
                            logger.info(f"Found matching public key for kid: {key_id}")
                            # Convert JWK to PEM format
                            n = int.from_bytes(
                                base64.urlsafe_b64decode(key['n'] + '=='), 
                                'big'
                            )
                            e = int.from_bytes(
                                base64.urlsafe_b64decode(key['e'] + '=='), 
                                'big'
                            )
                            
                            public_numbers = RSAPublicNumbers(e, n)
                            public_key = public_numbers.public_key()
                            break
                        except Exception as e:
                            logger.warning(f"Failed to convert JWK to PEM: {e}")
                            continue
                
                if not public_key:
                    raise HTTPException(status_code=401, detail="Public key not found for token")
                
                # Try to verify with primary issuer first
                try:
                    logger.info(f"Verifying JWT with primary issuer: {self.clerk_issuer}")
                    payload = jwt.decode(
                        token,
                        public_key,
                        algorithms=['RS256'],
                        issuer=self.clerk_issuer,
                        options={"verify_aud": False}  # Don't verify audience for Clerk
                    )
                    
                    logger.info(f"JWT token verified successfully with primary issuer for user: {payload.get('sub')}")
                    logger.info(f"JWT payload: {payload}")
                    
                    return {
                        "user_id": payload.get('sub'),
                        "email": payload.get('email'),
                        "authenticated": True,
                        "payload": payload
                    }
                    
                except jwt.InvalidIssuerError:
                    logger.info(f"Primary issuer failed, trying fallback: {self.clerk_issuer_fallback}")
                    # Try with fallback issuer
                    try:
                        payload = jwt.decode(
                            token,
                            public_key,
                            algorithms=['RS256'],
                            issuer=self.clerk_issuer_fallback,
                            options={"verify_aud": False}  # Don't verify audience for Clerk
                        )
                        
                        logger.info(f"JWT token verified successfully with fallback issuer for user: {payload.get('sub')}")
                        logger.info(f"JWT payload: {payload}")
                        
                        return {
                            "user_id": payload.get('sub'),
                            "email": payload.get('email'),
                            "authenticated": True,
                            "payload": payload
                        }
                        
                    except jwt.InvalidIssuerError:
                        logger.warning(f"Both primary and fallback issuers failed. Expected: {self.clerk_issuer} or {self.clerk_issuer_fallback}, Got: {payload.get('iss') if 'payload' in locals() else 'unknown'}")
                        raise HTTPException(status_code=401, detail="Invalid token issuer")
                    except jwt.ExpiredSignatureError:
                        logger.warning(f"JWT token has expired")
                        raise HTTPException(status_code=401, detail="Token has expired")
                    except jwt.InvalidTokenError as e:
                        logger.warning(f"Invalid JWT token: {e}")
                        raise HTTPException(status_code=401, detail="Invalid token")
                        
                except jwt.ExpiredSignatureError:
                    logger.warning(f"JWT token has expired")
                    raise HTTPException(status_code=401, detail="Token has expired")
                except jwt.InvalidTokenError as e:
                    logger.warning(f"Invalid JWT token: {e}")
                    raise HTTPException(status_code=401, detail="Invalid token")
                    
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Error verifying JWT: {e}")
            raise HTTPException(status_code=500, detail="Token verification failed")
    
    async def require_auth(self, authorization: str = Header(None)) -> Dict[str, Any]:
        """Dependency for requiring authentication on endpoints"""
        if not self.enabled:
            logger.warning("Authentication disabled - allowing unauthenticated access")
            return {"user_id": "anonymous", "authenticated": False}
        
        if not authorization:
            logger.warning("No authorization header provided")
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        if not authorization.startswith("Bearer "):
            logger.warning(f"Invalid authorization format: {authorization[:20]}...")
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization.replace("Bearer ", "")
        logger.info(f"Processing token: {token[:20]}...")
        
        # For development/testing, allow simplified tokens
        if self.allow_dev_tokens and len(token) > 10:
            try:
                # Simple token validation for development
                user_id = "user_" + token[:8]
                logger.info(f"Development token accepted for user: {user_id}")
                return {"user_id": user_id, "authenticated": True}
            except Exception as e:
                logger.warning(f"Development token validation failed: {e}")
                raise HTTPException(status_code=401, detail="Invalid development token")
        
        # For production, verify JWT token
        try:
            logger.info("Starting JWT verification...")
            result = await self.verify_jwt_token(token)
            logger.info(f"JWT verification successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(status_code=401, detail="Token verification failed")

# Global instance
clerk_auth = ClerkAuthService()

# Dependency for FastAPI endpoints
async def require_authentication(authorization: str = Header(None)) -> Dict[str, Any]:
    """FastAPI dependency for requiring authentication"""
    return await clerk_auth.require_auth(authorization)

# Dependency for optional authentication
async def optional_authentication(authorization: str = Header(None)) -> Dict[str, Any]:
    """FastAPI dependency for optional authentication"""
    if not authorization:
        return {"user_id": "anonymous", "authenticated": False}
    return await clerk_auth.require_auth(authorization)
