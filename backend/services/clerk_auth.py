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
import time
import asyncio
from datetime import datetime, timedelta

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
        
        # Development mode - bypass authentication for testing
        self.dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        
        # Token refresh settings
        self.token_refresh_threshold = 300  # 5 minutes before expiration
        self.max_token_age = 3600  # 1 hour maximum token age
        
        # Cache for JWKS to avoid repeated fetches
        self._jwks_cache = {}
        self._jwks_cache_time = 0
        self._jwks_cache_ttl = 3600  # 1 hour cache TTL
        
        logger.info(f"ClerkAuthService initialized - Primary Issuer: {self.clerk_issuer}, Fallback: {self.clerk_issuer_fallback}")
        logger.info(f"Development mode: {self.dev_mode}, Allow dev tokens: {self.allow_dev_tokens}")
        logger.info(f"Token refresh threshold: {self.token_refresh_threshold}s, Max token age: {self.max_token_age}s")
    
    def _is_token_expiring_soon(self, exp: int) -> bool:
        """Check if token is expiring soon (within refresh threshold)"""
        current_time = int(time.time())
        time_until_expiry = exp - current_time
        return time_until_expiry <= self.token_refresh_threshold
    
    
    def _is_token_too_old(self, iat: int) -> bool:
        """Check if token is too old (beyond max age)"""
        current_time = int(time.time())
        token_age = current_time - iat
        return token_age > self.max_token_age
    
    async def _fetch_jwks_with_cache(self) -> Dict[str, Any]:
        """Fetch JWKS with caching to avoid repeated requests"""
        current_time = time.time()
        
        # Check if cache is still valid
        if (self._jwks_cache and 
            current_time - self._jwks_cache_time < self._jwks_cache_ttl):
            logger.debug("Using cached JWKS")
            return self._jwks_cache
        
        logger.debug("Fetching fresh JWKS from Clerk...")
        
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
                    logger.debug(f"Trying JWKS endpoint: {url}")
                    response = await client.get(url, timeout=10.0)
                    if response.status_code == 200:
                        jwks = response.json()
                        logger.info(f"Successfully retrieved JWKS from: {url}")
                        break
                    else:
                        logger.debug(f"Failed to fetch from {url}: {response.status_code}")
                except Exception as e:
                    logger.debug(f"Error fetching from {url}: {e}")
                    continue
            
            if not jwks:
                # Fallback: Try using the Clerk secret key to fetch JWKS
                logger.debug("Public JWKS endpoints failed, trying with secret key...")
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
            
            # Cache the JWKS
            self._jwks_cache = jwks
            self._jwks_cache_time = current_time
            logger.debug(f"Cached JWKS with {len(jwks.get('keys', []))} keys")
            
            return jwks
    
    async def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token from Clerk with enhanced expiration handling"""
        try:
            # Reduced logging for cleaner workflow visibility
            logger.debug(f"Starting JWT token verification for token: {token[:20]}...")
            
            # First, try to decode without verification to get header and check expiration
            try:
                unverified_payload = jwt.decode(token, options={"verify_signature": False})
                logger.debug(f"JWT unverified payload: {unverified_payload}")
                
                # Check if token is expired
                exp = unverified_payload.get('exp')
                iat = unverified_payload.get('iat', 0)
                
                if exp:
                    current_time = int(time.time())
                    time_until_expiry = exp - current_time
                    
                    if current_time > exp:
                        logger.warning(f"JWT token has expired. Exp: {exp}, Current: {current_time}, Expired {abs(time_until_expiry)} seconds ago")
                        raise HTTPException(
                            status_code=401, 
                            detail={
                                "error": "Token has expired",
                                "expired_at": exp,
                                "current_time": current_time,
                                "expired_seconds_ago": abs(time_until_expiry),
                                "requires_refresh": True,
                                "message": "Your session has expired. Please refresh your authentication."
                            }
                        )
                    elif self._is_token_expiring_soon(exp):
                        logger.warning(f"JWT token expiring soon. Exp: {exp}, Current: {current_time}, Expires in {time_until_expiry} seconds")
                        # Don't fail here, but warn that refresh is needed soon
                        unverified_payload['_warn_refresh_soon'] = True
                    else:
                        logger.debug(f"Token is valid for {time_until_expiry} more seconds")
                
                # Check if token is too old
                if iat and self._is_token_too_old(iat):
                    logger.warning(f"JWT token is too old. IAT: {iat}, Current: {current_time}, Age: {current_time - iat} seconds")
                    raise HTTPException(
                        status_code=401,
                        detail={
                            "error": "Token is too old",
                            "issued_at": iat,
                            "current_time": current_time,
                            "token_age_seconds": current_time - iat,
                            "requires_refresh": True,
                            "message": "Your session is too old. Please refresh your authentication."
                        }
                    )
                        
            except jwt.ExpiredSignatureError:
                logger.warning("JWT token has expired (caught by PyJWT)")
                raise HTTPException(
                    status_code=401, 
                    detail={
                        "error": "Token has expired",
                        "requires_refresh": True,
                        "message": "Your session has expired. Please refresh your authentication."
                    }
                )
            except Exception as e:
                logger.debug(f"Error checking token expiration: {e}")
                # Continue with verification even if expiration check fails
            
            unverified_header = jwt.get_unverified_header(token)
            key_id = unverified_header.get('kid')
            
            logger.debug(f"JWT header: {unverified_header}")
            logger.debug(f"Key ID: {key_id}")
            
            if not key_id:
                raise HTTPException(status_code=401, detail="Invalid token format - missing key ID")
            
            # Fetch public keys from Clerk (with caching)
            jwks = await self._fetch_jwks_with_cache()
            logger.debug(f"Retrieved {len(jwks.get('keys', []))} public keys from Clerk")
            
            public_key = None
            
            # Find the matching public key
            for key in jwks.get('keys', []):
                if key.get('kid') == key_id:
                    try:
                        logger.debug(f"Found matching public key for kid: {key_id}")
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
                        logger.debug(f"Failed to convert JWK to PEM: {e}")
                        continue
            
            if not public_key:
                raise HTTPException(status_code=401, detail="Public key not found for token")
            
            # Try to verify with primary issuer first
            try:
                logger.debug(f"Verifying JWT with primary issuer: {self.clerk_issuer}")
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    issuer=self.clerk_issuer,
                    options={"verify_aud": False}  # Don't verify audience for Clerk
                )
                
                # Check if we need to warn about upcoming expiration
                if payload.get('_warn_refresh_soon'):
                    logger.info(f"JWT token verified successfully but will expire soon - user should refresh")
                else:
                    logger.info(f"JWT token verified successfully for user: {payload.get('sub')}")
                
                logger.debug(f"JWT payload: {payload}")
                
                # Add token metadata for better error handling
                token_info = {
                    "user_id": payload.get('sub'),
                    "email": payload.get('email'),
                    "authenticated": True,
                    "payload": payload,
                    "expires_at": payload.get('exp'),
                    "issued_at": payload.get('iat'),
                    "needs_refresh_soon": payload.get('_warn_refresh_soon', False)
                }
                
                return token_info
                
            except jwt.InvalidIssuerError:
                logger.debug(f"Primary issuer failed, trying fallback: {self.clerk_issuer_fallback}")
                # Try with fallback issuer
                try:
                    payload = jwt.decode(
                        token,
                        public_key,
                        algorithms=['RS256'],
                        issuer=self.clerk_issuer_fallback,
                        options={"verify_aud": False}  # Don't verify audience for Clerk
                    )
                    
                    # Check if we need to warn about upcoming expiration
                    if payload.get('_warn_refresh_soon'):
                        logger.info(f"JWT token verified successfully with fallback but will expire soon - user should refresh")
                    else:
                        logger.info(f"JWT token verified successfully with fallback issuer for user: {payload.get('sub')}")
                    
                    logger.debug(f"JWT payload: {payload}")
                    
                    # Add token metadata for better error handling
                    token_info = {
                        "user_id": payload.get('sub'),
                        "email": payload.get('email'),
                        "authenticated": True,
                        "payload": payload,
                        "expires_at": payload.get('exp'),
                        "issued_at": payload.get('iat'),
                        "needs_refresh_soon": payload.get('_warn_refresh_soon', False)
                    }
                    
                    return token_info
                    
                except jwt.InvalidIssuerError:
                    logger.warning(f"Both primary and fallback issuers failed. Expected: {self.clerk_issuer} or {self.clerk_issuer_fallback}")
                    raise HTTPException(status_code=401, detail="Invalid token issuer")
                except jwt.ExpiredSignatureError:
                    logger.warning(f"JWT token has expired")
                    raise HTTPException(
                        status_code=401, 
                        detail={
                            "error": "Token has expired",
                            "requires_refresh": True,
                            "message": "Your session has expired. Please refresh your authentication."
                        }
                    )
                except jwt.InvalidTokenError as e:
                    logger.debug(f"Invalid JWT token: {e}")
                    raise HTTPException(status_code=401, detail="Invalid token")
                    
            except jwt.ExpiredSignatureError:
                logger.warning(f"JWT token has expired")
                raise HTTPException(
                    status_code=401, 
                    detail={
                        "error": "Token has expired",
                        "requires_refresh": True,
                        "message": "Your session has expired. Please refresh your authentication."
                    }
                )
            except jwt.InvalidTokenError as e:
                logger.debug(f"Invalid JWT token: {e}")
                raise HTTPException(status_code=401, detail="Invalid token")
                
        except jwt.InvalidTokenError as e:
            logger.debug(f"Invalid JWT token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during JWT verification: {e}")
            raise HTTPException(status_code=500, detail="Internal authentication error")
    
    async def refresh_token_if_needed(self, token: str) -> Dict[str, Any]:
        """Check if token needs refresh and provide guidance"""
        try:
            # Verify the current token
            token_info = await self.verify_jwt_token(token)
            
            # Check if refresh is needed soon
            if token_info.get('needs_refresh_soon'):
                logger.info(f"Token for user {token_info.get('user_id')} will expire soon - refresh recommended")
                token_info['refresh_recommended'] = True
                token_info['refresh_message'] = "Your session will expire soon. Consider refreshing your authentication."
            
            return token_info
            
        except HTTPException as e:
            if e.detail and isinstance(e.detail, dict) and e.detail.get('requires_refresh'):
                # Token needs refresh
                logger.warning(f"Token refresh required: {e.detail.get('message', 'Authentication expired')}")
                return {
                    "authenticated": False,
                    "requires_refresh": True,
                    "error": e.detail.get('error', 'Authentication expired'),
                    "message": e.detail.get('message', 'Please refresh your authentication.'),
                    "expired_at": e.detail.get('expired_at'),
                    "current_time": e.detail.get('current_time')
                }
            else:
                # Other authentication error
                raise
    
    def get_token_lifetime_info(self, token_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about token lifetime and refresh recommendations"""
        current_time = int(time.time())
        exp = token_info.get('expires_at')
        iat = token_info.get('issued_at')
        
        if not exp:
            return {"status": "unknown", "message": "Token expiration time unknown"}
        
        time_until_expiry = exp - current_time
        
        if time_until_expiry <= 0:
            return {
                "status": "expired",
                "message": "Token has expired",
                "expired_seconds_ago": abs(time_until_expiry),
                "requires_refresh": True
            }
        elif time_until_expiry <= self.token_refresh_threshold:
            return {
                "status": "expiring_soon",
                "message": f"Token expires in {time_until_expiry} seconds",
                "time_until_expiry": time_until_expiry,
                "refresh_recommended": True
            }
        else:
            return {
                "status": "valid",
                "message": f"Token valid for {time_until_expiry} more seconds",
                "time_until_expiry": time_until_expiry,
                "refresh_recommended": False
            }
    
    async def require_auth(self, authorization: str = Header(None)) -> Dict[str, Any]:
        """Dependency for requiring authentication on endpoints"""
        if not self.enabled:
            logger.debug("Authentication disabled - allowing unauthenticated access")
            return {"user_id": "anonymous", "authenticated": False}
        
        # Development mode - bypass authentication for testing
        if self.dev_mode:
            logger.debug("Development mode enabled - bypassing authentication")
            return {"user_id": "dev_user", "authenticated": True, "dev_mode": True}
        
        if not authorization:
            logger.debug("No authorization header provided")
            raise HTTPException(
                status_code=401, 
                detail={
                    "error": "Authorization header required",
                    "requires_refresh": False
                }
            )
        
        if not authorization.startswith("Bearer "):
            logger.debug(f"Invalid authorization format: {authorization[:20]}...")
            raise HTTPException(
                status_code=401, 
                detail={
                    "error": "Invalid authorization format",
                    "requires_refresh": False
                }
            )
        
        token = authorization.replace("Bearer ", "")
        logger.debug(f"Processing token: {token[:20]}...")
        
        # For development/testing, allow simplified tokens
        if self.allow_dev_tokens and len(token) > 10:
            try:
                # Simple token validation for development
                user_id = "user_" + token[:8]
                logger.debug(f"Development token accepted for user: {user_id}")
                return {"user_id": user_id, "authenticated": True}
            except Exception as e:
                logger.debug(f"Development token validation failed: {e}")
                raise HTTPException(
                    status_code=401, 
                    detail={
                        "error": "Invalid development token",
                        "requires_refresh": False
                    }
                )
        
        # For production, verify JWT token
        try:
            logger.debug("Starting JWT verification...")
            result = await self.verify_jwt_token(token)
            logger.debug(f"JWT verification successful: {result}")
            return result
            
        except HTTPException as e:
            # Re-raise HTTP exceptions as-is
            logger.debug(f"JWT verification failed with HTTP exception: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=401, 
                detail={
                    "error": "Token verification failed",
                    "requires_refresh": False
                }
            )

# Global instance
clerk_auth = ClerkAuthService()

# Dependency for FastAPI endpoints
async def require_authentication(authorization: str = Header(None)) -> Dict[str, Any]:
    """FastAPI dependency for requiring authentication"""
    return await clerk_auth.require_auth(authorization)

# Dependency for long-running processes (with enhanced token handling)
async def require_authentication_long_running(authorization: str = Header(None)) -> Dict[str, Any]:
    """FastAPI dependency for long-running processes with enhanced token validation"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Authorization header required",
                "requires_refresh": False,
                "message": "Please provide your authentication token."
            }
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Invalid authorization format",
                "requires_refresh": False,
                "message": "Please provide a valid Bearer token."
            }
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Use the enhanced token verification with refresh guidance
        token_info = await clerk_auth.verify_jwt_token(token)
        
        # Check if token needs refresh soon
        if token_info.get('needs_refresh_soon'):
            logger.warning(f"Token for user {token_info.get('user_id')} will expire soon - long-running process may fail")
            # Don't fail the request, but add a warning
            token_info['_warn_refresh_soon'] = True
            token_info['_refresh_warning'] = "Your session will expire soon. Consider refreshing before starting long operations."
        
        return token_info
        
    except HTTPException as e:
        if e.detail and isinstance(e.detail, dict) and e.detail.get('requires_refresh'):
            # Token needs refresh - provide clear guidance
            logger.warning(f"Long-running process blocked due to expired token: {e.detail.get('message')}")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication expired",
                    "requires_refresh": True,
                    "message": "Your session has expired. Please refresh your authentication before starting long operations.",
                    "expired_at": e.detail.get('expired_at'),
                    "current_time": e.detail.get('current_time'),
                    "expired_seconds_ago": e.detail.get('expired_seconds_ago'),
                    "long_running_process": True
                }
            )
        else:
            # Other authentication error
            raise

# Dependency for optional authentication
async def optional_authentication(authorization: str = Header(None)) -> Dict[str, Any]:
    """FastAPI dependency for optional authentication"""
    if not authorization:
        return {"user_id": "anonymous", "authenticated": False}
    return await clerk_auth.require_auth(authorization)
