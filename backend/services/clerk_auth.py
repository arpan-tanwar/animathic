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
        self.token_refresh_threshold = 600  # 10 minutes before expiration (increased from 5)
        self.max_token_age = 7200  # 2 hours maximum token age (increased from 1 hour)
        self.long_running_token_extension = 3600  # 1 hour extension for long-running operations
        
        # Cache for JWKS to avoid repeated fetches
        self._jwks_cache = {}
        self._jwks_cache_time = 0
        self._jwks_cache_ttl = 3600  # 1 hour cache TTL
        
        # Token validation cache for performance
        self._token_cache = {}
        self._token_cache_ttl = 300  # 5 minutes cache TTL
        
        # Long-running operation tracking
        self._long_running_operations = {}
        
        logger.info(f"ClerkAuthService initialized - Primary Issuer: {self.clerk_issuer}, Fallback: {self.clerk_issuer_fallback}")
        logger.info(f"Development mode: {self.dev_mode}, Allow dev tokens: {self.allow_dev_tokens}")
        logger.info(f"Token refresh threshold: {self.token_refresh_threshold}s, Max token age: {self.max_token_age}s")
        logger.info(f"Long-running token extension: {self.long_running_token_extension}s")
    
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
    
    def _can_extend_token_lifetime(self, exp: int, iat: int) -> bool:
        """Check if token lifetime can be extended for long-running operations"""
        current_time = int(time.time())
        time_until_expiry = exp - current_time
        token_age = current_time - iat
        
        # Can extend if token is not too old and has reasonable time left
        # Simplified logic: extend if token is not too old and has less than 30 minutes left
        return (token_age < self.max_token_age and 
                time_until_expiry > 0 and 
                time_until_expiry < 1800)  # 30 minutes
    
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
                
                if not jwks:
                # Fallback to secret key if available
                if self.clerk_secret_key:
                    logger.warning("JWKS fetch failed, using secret key fallback")
                    jwks = {"keys": [{"kid": "fallback", "secret": self.clerk_secret_key}]}
                else:
                    raise HTTPException(status_code=500, detail="Failed to fetch JWKS and no fallback available")
            
            # Cache the JWKS
            self._jwks_cache = jwks
            self._jwks_cache_time = current_time
            return jwks
    
    def _get_cached_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get cached token information if available and valid"""
        current_time = time.time()
        if token in self._token_cache:
            cache_entry = self._token_cache[token]
            if current_time - cache_entry['cache_time'] < self._token_cache_ttl:
                return cache_entry['token_info']
            else:
                # Remove expired cache entry
                del self._token_cache[token]
        return None
    
    def _cache_token_info(self, token: str, token_info: Dict[str, Any]):
        """Cache token information for performance"""
        self._token_cache[token] = {
            'token_info': token_info,
            'cache_time': time.time()
        }
    
    def register_long_running_operation(self, user_id: str, operation_id: str, token_exp: int):
        """Register a long-running operation for token lifetime extension"""
        self._long_running_operations[operation_id] = {
            'user_id': user_id,
            'token_exp': token_exp,
            'registered_at': time.time(),
            'extended': False
        }
        logger.info(f"Registered long-running operation {operation_id} for user {user_id}")
    
    def unregister_long_running_operation(self, operation_id: str):
        """Unregister a long-running operation"""
        if operation_id in self._long_running_operations:
            del self._long_running_operations[operation_id]
            logger.info(f"Unregistered long-running operation {operation_id}")
    
    def is_long_running_operation(self, operation_id: str) -> bool:
        """Check if an operation is registered as long-running"""
        return operation_id in self._long_running_operations
    
    async def verify_jwt_token(self, token: str, allow_extended_lifetime: bool = False) -> Dict[str, Any]:
        """Verify JWT token with enhanced error handling and lifetime extension"""
        try:
            # Check token cache first
            cached_info = self._get_cached_token_info(token)
            if cached_info:
                logger.debug("Using cached token information")
                return cached_info
            
            # Decode token without verification to check expiration
            try:
                unverified_payload = jwt.decode(token, options={"verify_signature": False})
                exp = unverified_payload.get('exp')
                iat = unverified_payload.get('iat')
                
                if exp:
                    current_time = int(time.time())
                    time_until_expiry = exp - current_time
                    
                    # Check if token is expired
                    if time_until_expiry <= 0:
                        logger.warning(f"JWT token has expired. Expired {abs(time_until_expiry)} seconds ago")
                        
                        # For long-running operations, check if we can extend the token
                        if allow_extended_lifetime and self._can_extend_token_lifetime(exp, iat):
                            logger.info(f"Token expired but extended for long-running operation")
                            # Don't raise exception, continue with extended lifetime
                            # Update the expiration time for the extended token
                            exp = exp + 3600  # Extend by 1 hour
                            unverified_payload['_extended_lifetime'] = True
                            unverified_payload['_original_exp'] = exp - 3600
                            unverified_payload['_extended_exp'] = exp
                        else:
                            raise HTTPException(
                                status_code=401,
                                detail={
                                    "error": "Token has expired",
                                    "requires_refresh": True,
                                    "message": "Your session has expired. Please refresh your authentication.",
                                    "expired_at": exp,
                                    "current_time": current_time,
                                    "expired_seconds_ago": abs(time_until_expiry)
                                }
                            )
                    
                    # Check if token is too old
                    if iat and self._is_token_too_old(iat):
                        logger.warning(f"JWT token is too old. Age: {current_time - iat} seconds")
                        raise HTTPException(
                            status_code=401,
                            detail={
                                "error": "Token is too old",
                                "requires_refresh": True,
                                "message": "Your session is too old. Please refresh your authentication.",
                                "issued_at": iat,
                                "current_time": current_time,
                                "token_age": current_time - iat
                            }
                        )
                    
                    # Check if token needs refresh soon
                    needs_refresh_soon = self._is_token_expiring_soon(exp)
                    
                    # Check if we can extend token lifetime for long-running operations
                    can_extend = allow_extended_lifetime and self._can_extend_token_lifetime(exp, iat)
                    
                    if can_extend:
                        logger.info(f"Token extended for long-running operation. Current expiry: {exp}, extended by 1 hour")
                        # Add extended lifetime flag
                        unverified_payload['_extended_lifetime'] = True
                        unverified_payload['_original_exp'] = exp
                        unverified_payload['_extended_exp'] = exp + 3600  # Extend by 1 hour
                    
                    if needs_refresh_soon:
                        logger.warning(f"JWT token will expire soon in {time_until_expiry} seconds")
                        unverified_payload['_warn_refresh_soon'] = True
                    
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
                    "needs_refresh_soon": payload.get('_warn_refresh_soon', False),
                    "can_extend_lifetime": payload.get('_extended_lifetime', False),
                    "extended_expiry": payload.get('_extended_exp')
                }
                
                # Cache the token information
                self._cache_token_info(token, token_info)
                
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
                        "needs_refresh_soon": payload.get('_warn_refresh_soon', False),
                        "can_extend_lifetime": payload.get('_extended_lifetime', False),
                        "extended_expiry": payload.get('_extended_exp')
                    }
                    
                    # Cache the token information
                    self._cache_token_info(token, token_info)
                    
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
                token_info['refresh_recommended'] = True
                token_info['refresh_message'] = "Your session will expire soon. Consider refreshing your authentication."
            
            return token_info
            
        except HTTPException as e:
            if e.detail and isinstance(e.detail, dict) and e.detail.get('requires_refresh'):
                return {
                    "authenticated": False,
                    "requires_refresh": True,
                    "error": e.detail.get('error', 'Authentication expired'),
                    "message": e.detail.get('message', 'Please refresh your authentication.'),
                    "expired_at": e.detail.get('expired_at'),
                    "current_time": e.detail.get('current_time')
                }
            else:
                raise
    
    def get_token_lifetime_info(self, token_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about token lifetime and refresh recommendations"""
        current_time = int(time.time())
        exp = token_info.get('expires_at')
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
        """Main authentication method with enhanced error handling"""
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
        
        # Development mode bypass
        if self.dev_mode and len(token) < 50:
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
        # Use the enhanced token verification with extended lifetime support
        token_info = await clerk_auth.verify_jwt_token(token, allow_extended_lifetime=True)
        
        # Check if token needs refresh soon
        if token_info.get('_warn_refresh_soon'):
            logger.warning(f"Token for user {token_info.get('user_id')} will expire soon - long-running process may fail")
            # Don't fail the request, but add a warning
            token_info['_warn_refresh_soon'] = True
            token_info['_refresh_warning'] = "Your session will expire soon. Consider refreshing before starting long operations."
        
        # Check if token lifetime was extended
        if token_info.get('_extended_lifetime'):
            logger.info(f"Token lifetime extended for long-running operation. Extended expiry: {token_info.get('_extended_exp')}")
            token_info['_lifetime_extended'] = True
            token_info['_extended_expiry'] = token_info.get('_extended_exp')
        
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
