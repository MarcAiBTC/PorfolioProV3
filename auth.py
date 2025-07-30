"""
Enhanced Authentication Module - Minor Improvements
===================================================

Secure user authentication system for Portfolio Manager Pro with:
- PBKDF2-HMAC password hashing with salt (100,000 iterations)
- JSON-based user storage with atomic operations
- Input validation and sanitization
- Comprehensive logging for security events
- Rate limiting protection with configurable timeouts
- Enhanced session management

Security Features:
- Passwords hashed with PBKDF2-HMAC-SHA256
- Individual salt per user (16 bytes)
- 100,000 iterations for hash computation
- Base64 encoding for storage compatibility
- No plaintext password storage ever
- Account lockout after failed attempts

Minor enhancements for Portfolio Manager Pro v2.2.0:
- Better error messages and user feedback
- Enhanced logging for debugging
- Improved rate limiting configuration
- Better integration with Streamlit session state

Author: Enhanced by AI Assistant
"""

import os
import json
import hashlib
import base64
import secrets
import logging
import time
from typing import Dict, Tuple, Optional, Union
from typing import List
from datetime import datetime, timedelta

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration Constants - Enhanced for Portfolio Manager Pro
# ============================================================================

# Security parameters (production-ready)
PBKDF2_ITERATIONS = 100_000  # Industry standard for security
SALT_LENGTH = 16  # bytes (128 bits)
HASH_ALGORITHM = 'sha256'

# Rate limiting (configurable for different deployment scenarios)
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# File storage configuration
USER_DATA_DIR = os.path.join(os.path.dirname(__file__), "user_data")
USERS_FILE = os.path.join(USER_DATA_DIR, "users.json")
LOGIN_ATTEMPTS_FILE = os.path.join(USER_DATA_DIR, "login_attempts.json")

# Application metadata
APP_VERSION = "2.2.0"
CREATED_BY = "Portfolio Manager Pro"

# ============================================================================
# Directory and File Management
# ============================================================================

def _ensure_user_data_dir() -> None:
    """Ensure the user data directory exists with proper permissions."""
    try:
        os.makedirs(USER_DATA_DIR, mode=0o700, exist_ok=True)
        logger.debug(f"User data directory ensured: {USER_DATA_DIR}")
    except Exception as e:
        logger.error(f"Failed to create user data directory: {e}")
        raise

def _create_backup_if_needed(file_path: str) -> None:
    """Create a backup of the file before modifying it."""
    if os.path.exists(file_path):
        try:
            backup_path = f"{file_path}.backup_{int(time.time())}"
            with open(file_path, 'r', encoding='utf-8') as original:
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(original.read())
            logger.debug(f"Backup created: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup for {file_path}: {e}")

# ============================================================================
# User Data Operations - Enhanced
# ============================================================================

def load_users() -> Dict[str, Dict[str, str]]:
    """
    Load the user database from disk with enhanced error handling.
    
    Returns
    -------
    Dict[str, Dict[str, str]]
        Mapping of username to user credentials and metadata
    """
    _ensure_user_data_dir()
    
    if not os.path.isfile(USERS_FILE):
        logger.info("Users file does not exist - initializing empty user database")
        return {}
    
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validate the loaded data structure
        if not isinstance(data, dict):
            logger.error("Invalid users file format - not a dictionary")
            return {}
        
        # Validate each user record with enhanced checks
        valid_users = {}
        for username, user_data in data.items():
            if not isinstance(user_data, dict):
                logger.warning(f"Invalid user record format for {username} - skipping")
                continue
            
            # Check required fields
            required_fields = ['salt', 'hash']
            if all(field in user_data for field in required_fields):
                valid_users[username] = user_data
            else:
                logger.warning(f"Invalid user record for {username} - missing required fields")
        
        logger.info(f"Loaded {len(valid_users)} valid users from database")
        return valid_users
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in users file: {e}")
        # Create backup and return empty dict
        _create_backup_if_needed(USERS_FILE)
        return {}
    except Exception as e:
        logger.error(f"Error loading users file: {e}")
        return {}

def save_users(users: Dict[str, Dict[str, str]]) -> bool:
    """
    Save the user database to disk with atomic operations and validation.
    
    Parameters
    ----------
    users : Dict[str, Dict[str, str]]
        User database to save
        
    Returns
    -------
    bool
        True if save was successful, False otherwise
    """
    _ensure_user_data_dir()
    
    # Enhanced input validation
    if not isinstance(users, dict):
        logger.error("Invalid users data - not a dictionary")
        return False
    
    # Validate user records
    for username, user_data in users.items():
        if not isinstance(user_data, dict):
            logger.error(f"Invalid user data for {username}")
            return False
        
        required_fields = ['salt', 'hash']
        if not all(field in user_data for field in required_fields):
            logger.error(f"Missing required fields for user {username}")
            return False
    
    try:
        # Create backup of existing file
        _create_backup_if_needed(USERS_FILE)
        
        # Add metadata to the save
        save_data = {
            'metadata': {
                'version': APP_VERSION,
                'last_updated': datetime.now().isoformat(),
                'created_by': CREATED_BY,
                'user_count': len(users)
            },
            'users': users
        }
        
        # Write to temporary file first (atomic operation)
        temp_file = f"{USERS_FILE}.tmp"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        # Atomic rename (on most systems)
        if os.name == 'nt':  # Windows
            if os.path.exists(USERS_FILE):
                os.remove(USERS_FILE)
        os.rename(temp_file, USERS_FILE)
        
        # Set restrictive permissions
        os.chmod(USERS_FILE, 0o600)
        
        logger.info(f"Successfully saved {len(users)} users to database")
        return True
        
    except Exception as e:
        logger.error(f"Error saving users file: {e}")
        # Clean up temp file if it exists
        try:
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
        return False

def load_users_from_file() -> Dict[str, Dict[str, str]]:
    """
    Load users with metadata handling (backward compatibility).
    
    Returns
    -------
    Dict[str, Dict[str, str]]
        User data without metadata
    """
    try:
        data = load_users()
        
        # Check if this is the new format with metadata
        if 'metadata' in data and 'users' in data:
            logger.debug(f"Loading users from new format (version: {data['metadata'].get('version', 'unknown')})")
            return data['users']
        else:
            # Old format - return as is
            logger.debug("Loading users from legacy format")
            return data
            
    except Exception as e:
        logger.error(f"Error loading users from file: {e}")
        return {}

# ============================================================================
# Password Hashing and Verification - Production Ready
# ============================================================================

def _hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
    """
    Hash a password using PBKDF2-HMAC with SHA-256 (production-grade security).
    
    Parameters
    ----------
    password : str
        Plain text password to hash
    salt : bytes, optional
        Cryptographic salt. If None, generates a new one.
        
    Returns
    -------
    Tuple[str, str]
        Base64-encoded salt and hash
        
    Raises
    ------
    ValueError
        If password is empty or invalid
    """
    # Enhanced input validation
    if not password:
        raise ValueError("Password cannot be empty")
    
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    
    if len(password) > 256:  # Reasonable upper limit
        raise ValueError("Password is too long (max 256 characters)")
    
    try:
        # Generate cryptographically secure salt if not provided
        if salt is None:
            salt = secrets.token_bytes(SALT_LENGTH)
        
        # Validate salt length
        if len(salt) != SALT_LENGTH:
            raise ValueError(f"Salt must be {SALT_LENGTH} bytes long")
        
        # Hash the password with PBKDF2-HMAC-SHA256
        key = hashlib.pbkdf2_hmac(
            HASH_ALGORITHM,
            password.encode('utf-8'),
            salt,
            PBKDF2_ITERATIONS
        )
        
        # Encode for storage
        b64_salt = base64.b64encode(salt).decode('utf-8')
        b64_hash = base64.b64encode(key).decode('utf-8')
        
        logger.debug("Password hashed successfully with PBKDF2-HMAC-SHA256")
        return b64_salt, b64_hash
        
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

def _verify_password(password: str, stored_salt: str, stored_hash: str) -> bool:
    """
    Verify a password against stored hash and salt using constant-time comparison.
    
    Parameters
    ----------
    password : str
        Plain text password to verify
    stored_salt : str
        Base64-encoded salt from storage
    stored_hash : str
        Base64-encoded hash from storage
        
    Returns
    -------
    bool
        True if password matches, False otherwise
    """
    try:
        # Input validation
        if not all([password, stored_salt, stored_hash]):
            return False
        
        # Decode stored values
        salt = base64.b64decode(stored_salt)
        expected_hash = stored_hash
        
        # Hash the provided password with the stored salt
        _, computed_hash = _hash_password(password, salt)
        
        # Constant-time comparison to prevent timing attacks
        return secrets.compare_digest(computed_hash, expected_hash)
        
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

# ============================================================================
# Rate Limiting and Security - Enhanced
# ============================================================================

def load_login_attempts() -> Dict[str, Dict[str, Union[int, str]]]:
    """Load login attempt tracking data with validation."""
    if not os.path.exists(LOGIN_ATTEMPTS_FILE):
        return {}
    
    try:
        with open(LOGIN_ATTEMPTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate data structure
        if not isinstance(data, dict):
            logger.warning("Invalid login attempts file format")
            return {}
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading login attempts: {e}")
        return {}

def save_login_attempts(attempts: Dict[str, Dict[str, Union[int, str]]]) -> None:
    """Save login attempt tracking data with error handling."""
    _ensure_user_data_dir()
    
    try:
        # Add metadata
        save_data = {
            'metadata': {
                'version': APP_VERSION,
                'last_updated': datetime.now().isoformat()
            },
            'attempts': attempts
        }
        
        with open(LOGIN_ATTEMPTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
        os.chmod(LOGIN_ATTEMPTS_FILE, 0o600)
        
    except Exception as e:
        logger.error(f"Error saving login attempts: {e}")

def is_account_locked(username: str) -> Tuple[bool, Optional[str]]:
    """
    Check if an account is temporarily locked due to failed attempts.
    
    Parameters
    ----------
    username : str
        Username to check
        
    Returns
    -------
    Tuple[bool, Optional[str]]
        (is_locked, time_remaining_str)
    """
    attempts_data = load_login_attempts()
    
    # Handle new file format
    if 'attempts' in attempts_data:
        attempts_data = attempts_data['attempts']
    
    user_attempts = attempts_data.get(username, {})
    
    if not user_attempts:
        return False, None
    
    try:
        failed_count = user_attempts.get('failed_count', 0)
        last_attempt_str = user_attempts.get('last_attempt', '')
        
        if failed_count < MAX_LOGIN_ATTEMPTS:
            return False, None
        
        if not last_attempt_str:
            return False, None
        
        # Parse last attempt time
        last_attempt = datetime.fromisoformat(last_attempt_str)
        lockout_duration = timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        time_since_attempt = datetime.now() - last_attempt
        
        # Check if lockout period has expired
        if time_since_attempt > lockout_duration:
            # Reset attempts count
            user_attempts['failed_count'] = 0
            attempts_data[username] = user_attempts
            save_login_attempts(attempts_data)
            return False, None
        
        # Calculate remaining lockout time
        remaining_time = lockout_duration - time_since_attempt
        remaining_minutes = int(remaining_time.total_seconds() // 60)
        
        return True, f"{remaining_minutes} minutes"
        
    except Exception as e:
        logger.error(f"Error checking account lock status: {e}")
        return False, None

def record_login_attempt(username: str, success: bool, details: str = "") -> None:
    """
    Record a login attempt for rate limiting with enhanced logging.
    
    Parameters
    ----------
    username : str
        Username that attempted login
    success : bool
        Whether the login was successful
    details : str, optional
        Additional details about the attempt
    """
    attempts_data = load_login_attempts()
    
    # Handle new file format
    if 'attempts' in attempts_data:
        attempts_data = attempts_data['attempts']
    
    if username not in attempts_data:
        attempts_data[username] = {
            'failed_count': 0, 
            'last_attempt': '',
            'first_attempt': datetime.now().isoformat(),
            'total_attempts': 0
        }
    
    user_attempts = attempts_data[username]
    user_attempts['last_attempt'] = datetime.now().isoformat()
    user_attempts['total_attempts'] = user_attempts.get('total_attempts', 0) + 1
    
    if success:
        user_attempts['failed_count'] = 0
        user_attempts['last_success'] = datetime.now().isoformat()
        logger.info(f"Successful login recorded for {username} {details}")
    else:
        user_attempts['failed_count'] = user_attempts.get('failed_count', 0) + 1
        logger.warning(f"Failed login attempt recorded for {username} (count: {user_attempts['failed_count']}) {details}")
        
        # Log potential security threat
        if user_attempts['failed_count'] >= MAX_LOGIN_ATTEMPTS:
            logger.warning(f"Account locked due to multiple failed attempts: {username}")
    
    attempts_data[username] = user_attempts
    save_login_attempts(attempts_data)

# ============================================================================
# Input Validation and Sanitization - Enhanced
# ============================================================================

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username according to enhanced security requirements.
    
    Parameters
    ----------
    username : str
        Username to validate
        
    Returns
    -------
    Tuple[bool, str]
        (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if not isinstance(username, str):
        return False, "Username must be a string"
    
    # Clean the username
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters long"
    
    # Enhanced character validation
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')
    if not all(c in allowed_chars for c in username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    # Cannot start or end with special characters
    if username.startswith(('_', '-')) or username.endswith(('_', '-')):
        return False, "Username cannot start or end with special characters"
    
    # Reserved usernames
    reserved = ['admin', 'root', 'system', 'test', 'user', 'guest', 'demo']
    if username.lower() in reserved:
        return False, "Username is reserved, please choose another"
    
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password according to enhanced security requirements.
    
    Parameters
    ----------
    password : str
        Password to validate
        
    Returns
    -------
    Tuple[bool, str]
        (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if not isinstance(password, str):
        return False, "Password must be a string"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 256:
        return False, "Password is too long (max 256 characters)"
    
    # Enhanced strength requirements
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    
    if not (has_letter and has_number):
        return False, "Password must contain at least one letter and one number"
    
    # Check for common weak passwords
    weak_passwords = ['password', '123456', 'password123', 'admin', 'qwerty']
    if password.lower() in weak_passwords:
        return False, "Password is too common, please choose a stronger password"
    
    return True, ""

def sanitize_username(username: str) -> str:
    """
    Sanitize username input with enhanced cleaning.
    
    Parameters
    ----------
    username : str
        Raw username input
        
    Returns
    -------
    str
        Sanitized username
    """
    if not isinstance(username, str):
        return ""
    
    # Strip whitespace and normalize case for consistency
    cleaned = username.strip().lower()
    
    # Remove any potentially dangerous characters
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789_-')
    cleaned = ''.join(c for c in cleaned if c in allowed_chars)
    
    # Ensure reasonable length
    return cleaned[:50]

# ============================================================================
# Public Authentication Functions - Enhanced
# ============================================================================

def register_user(username: str, password: str) -> bool:
    """
    Register a new user with comprehensive validation and enhanced metadata.
    
    Parameters
    ----------
    username : str
        Desired username
    password : str
        Plain text password
        
    Returns
    -------
    bool
        True if registration successful, False otherwise
    """
    try:
        # Sanitize input
        username_clean = sanitize_username(username)
        
        # Validate inputs with enhanced checks
        username_valid, username_error = validate_username(username_clean)
        if not username_valid:
            logger.warning(f"Registration failed - invalid username '{username_clean}': {username_error}")
            return False
        
        password_valid, password_error = validate_password(password)
        if not password_valid:
            logger.warning(f"Registration failed - invalid password for '{username_clean}': {password_error}")
            return False
        
        # Load existing users
        users = load_users_from_file()
        
        # Check if username already exists
        if username_clean in users:
            logger.warning(f"Registration failed - username already exists: {username_clean}")
            return False
        
        # Hash the password
        salt, hashed_password = _hash_password(password)
        
        # Create user record with enhanced metadata
        users[username_clean] = {
            'salt': salt,
            'hash': hashed_password,
            'created_at': datetime.now().isoformat(),
            'last_login': '',
            'login_count': 0,
            'app_version': APP_VERSION,
            'account_status': 'active',
            'password_changed_at': datetime.now().isoformat()
        }
        
        # Save to database
        if save_users(users):
            logger.info(f"New user registered successfully: {username_clean}")
            
            # Record successful registration
            record_login_attempt(username_clean, True, "(registration)")
            
            return True
        else:
            logger.error(f"Failed to save new user: {username_clean}")
            return False
        
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        return False

def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user with comprehensive security checks and enhanced logging.
    
    Parameters
    ----------
    username : str
        Username
    password : str
        Plain text password
        
    Returns
    -------
    bool
        True if authentication successful, False otherwise
    """
    try:
        # Sanitize input
        username_clean = sanitize_username(username)
        
        # Basic validation
        if not username_clean or not password:
            logger.warning("Authentication failed - empty username or password")
            record_login_attempt(username_clean or "unknown", False, "(empty credentials)")
            return False
        
        # Check if account is locked
        is_locked, remaining_time = is_account_locked(username_clean)
        if is_locked:
            logger.warning(f"Authentication failed - account locked: {username_clean} (remaining: {remaining_time})")
            return False
        
        # Load users database
        users = load_users_from_file()
        
        # Check if user exists
        if username_clean not in users:
            logger.warning(f"Authentication failed - user not found: {username_clean}")
            record_login_attempt(username_clean, False, "(user not found)")
            return False
        
        user_record = users[username_clean]
        
        # Validate user record structure
        required_fields = ['salt', 'hash']
        if not all(field in user_record for field in required_fields):
            logger.error(f"Authentication failed - invalid user record: {username_clean}")
            record_login_attempt(username_clean, False, "(corrupted record)")
            return False
        
        # Check account status
        if user_record.get('account_status') == 'disabled':
            logger.warning(f"Authentication failed - account disabled: {username_clean}")
            record_login_attempt(username_clean, False, "(account disabled)")
            return False
        
        # Verify password
        if _verify_password(password, user_record['salt'], user_record['hash']):
            # Update user metadata
            user_record['last_login'] = datetime.now().isoformat()
            user_record['login_count'] = user_record.get('login_count', 0) + 1
            user_record['last_app_version'] = APP_VERSION
            users[username_clean] = user_record
            save_users(users)
            
            # Record successful attempt
            record_login_attempt(username_clean, True, f"(login #{user_record['login_count']})")
            
            logger.info(f"Successful authentication: {username_clean}")
            return True
        else:
            logger.warning(f"Authentication failed - invalid password: {username_clean}")
            record_login_attempt(username_clean, False, "(invalid password)")
            return False
        
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        if username:
            record_login_attempt(sanitize_username(username), False, f"(error: {str(e)[:50]})")
        return False

# ============================================================================
# User Management Functions - Enhanced
# ============================================================================

def get_user_info(username: str) -> Optional[Dict[str, str]]:
    """
    Get user information (excluding sensitive data) with enhanced details.
    
    Parameters
    ----------
    username : str
        Username to query
        
    Returns
    -------
    Optional[Dict[str, str]]
        User info or None if not found
    """
    try:
        username_clean = sanitize_username(username)
        users = load_users_from_file()
        
        if username_clean not in users:
            return None
        
        user_record = users[username_clean]
        
        # Return enhanced non-sensitive information
        return {
            'username': username_clean,
            'created_at': user_record.get('created_at', ''),
            'last_login': user_record.get('last_login', ''),
            'login_count': str(user_record.get('login_count', 0)),
            'account_status': user_record.get('account_status', 'active'),
            'app_version': user_record.get('app_version', 'unknown'),
            'last_app_version': user_record.get('last_app_version', 'unknown')
        }
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return None

def change_password(username: str, old_password: str, new_password: str) -> bool:
    """
    Change user password with enhanced validation and security.
    
    Parameters
    ----------
    username : str
        Username
    old_password : str
        Current password
    new_password : str
        New password
        
    Returns
    -------
    bool
        True if password change successful, False otherwise
    """
    try:
        # First authenticate with old password
        if not authenticate_user(username, old_password):
            logger.warning(f"Password change failed - authentication failed: {username}")
            return False
        
        # Validate new password
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            logger.warning(f"Password change failed - invalid new password: {password_error}")
            return False
        
        # Check if new password is different from old password
        username_clean = sanitize_username(username)
        users = load_users_from_file()
        
        if username_clean not in users:
            return False
        
        # Verify new password is different
        user_record = users[username_clean]
        if _verify_password(new_password, user_record['salt'], user_record['hash']):
            logger.warning(f"Password change failed - new password same as old: {username_clean}")
            return False
        
        # Hash new password
        salt, hashed_password = _hash_password(new_password)
        
        # Update user record
        user_record['salt'] = salt
        user_record['hash'] = hashed_password
        user_record['password_changed_at'] = datetime.now().isoformat()
        user_record['password_change_count'] = user_record.get('password_change_count', 0) + 1
        
        users[username_clean] = user_record
        
        # Save changes
        if save_users(users):
            logger.info(f"Password changed successfully: {username_clean}")
            record_login_attempt(username_clean, True, "(password changed)")
            return True
        else:
            logger.error(f"Failed to save password change: {username_clean}")
            return False
        
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return False

# ============================================================================
# Utility Functions - Enhanced
# ============================================================================

def get_system_stats() -> Dict[str, Union[int, str]]:
    """
    Get enhanced system statistics.
    
    Returns
    -------
    Dict[str, Union[int, str]]
        System statistics
    """
    try:
        users = load_users_from_file()
        attempts_data = load_login_attempts()
        
        # Handle new file format
        if 'attempts' in attempts_data:
            attempts_data = attempts_data['attempts']
        
        locked_accounts = sum(1 for username in users.keys() if is_account_locked(username)[0])
        
        # Calculate additional stats
        total_logins = sum(user.get('login_count', 0) for user in users.values())
        active_users = sum(1 for user in users.values() if user.get('last_login'))
        
        return {
            'total_users': len(users),
            'active_users': active_users,
            'locked_accounts': locked_accounts,
            'total_logins': total_logins,
            'users_file_exists': os.path.exists(USERS_FILE),
            'app_version': APP_VERSION,
            'last_backup': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {'error': str(e)}

def cleanup_old_login_attempts(days_old: int = 30) -> int:
    """
    Clean up old login attempt records.
    
    Parameters
    ----------
    days_old : int, default 30
        Remove attempts older than this many days
        
    Returns
    -------
    int
        Number of records cleaned up
    """
    try:
        attempts_data = load_login_attempts()
        
        # Handle new file format
        if 'attempts' in attempts_data:
            attempts_data = attempts_data['attempts']
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        users_to_remove = []
        for username, user_attempts in attempts_data.items():
            try:
                last_attempt_str = user_attempts.get('last_attempt', '')
                if last_attempt_str:
                    last_attempt = datetime.fromisoformat(last_attempt_str)
                    if last_attempt < cutoff_date:
                        users_to_remove.append(username)
                else:
                    # Remove entries without timestamp
                    users_to_remove.append(username)
            except:
                # If we can't parse the date, remove it
                users_to_remove.append(username)
        
        for username in users_to_remove:
            del attempts_data[username]
        
        if users_to_remove:
            save_login_attempts(attempts_data)
            logger.info(f"Cleaned up {len(users_to_remove)} old login attempt records")
        
        return len(users_to_remove)
        
    except Exception as e:
        logger.error(f"Error cleaning up login attempts: {e}")
        return 0

def initialize_auth_module() -> bool:
    """
    Initialize the authentication module with enhanced setup.
    
    Returns
    -------
    bool
        True if initialization successful
    """
    try:
        _ensure_user_data_dir()
        
        # Clean up old data periodically
        cleanup_old_login_attempts()
        
        # Check file permissions
        for file_path in [USERS_FILE, LOGIN_ATTEMPTS_FILE]:
            if os.path.exists(file_path):
                # Ensure restrictive permissions
                os.chmod(file_path, 0o600)
        
        logger.info(f"Authentication module initialized successfully (v{APP_VERSION})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize authentication module: {e}")
        return False

# ============================================================================
# Portfolio Manager Pro Integration Functions
# ============================================================================

def get_user_portfolio_stats(username: str) -> Optional[Dict[str, Union[int, str]]]:
    """
    Get user statistics relevant to portfolio management.
    
    Parameters
    ----------
    username : str
        Username to query
        
    Returns
    -------
    Optional[Dict[str, Union[int, str]]]
        User portfolio statistics
    """
    try:
        user_info = get_user_info(username)
        if not user_info:
            return None
        
        # Additional portfolio-specific stats
        attempts_data = load_login_attempts()
        if 'attempts' in attempts_data:
            attempts_data = attempts_data['attempts']
        
        user_attempts = attempts_data.get(sanitize_username(username), {})
        
        return {
            'username': user_info['username'],
            'member_since': user_info.get('created_at', ''),
            'last_active': user_info.get('last_login', ''),
            'session_count': user_info.get('login_count', '0'),
            'account_status': user_info.get('account_status', 'active'),
            'security_score': calculate_security_score(user_info, user_attempts),
            'app_version': user_info.get('last_app_version', 'unknown')
        }
        
    except Exception as e:
        logger.error(f"Error getting user portfolio stats: {e}")
        return None

def calculate_security_score(user_info: Dict[str, str], user_attempts: Dict[str, Union[int, str]]) -> str:
    """
    Calculate a security score for the user based on various factors.
    
    Parameters
    ----------
    user_info : Dict[str, str]
        User information
    user_attempts : Dict[str, Union[int, str]]
        Login attempt data
        
    Returns
    -------
    str
        Security score (High, Medium, Low)
    """
    try:
        score = 0
        
        # Recent login activity (positive)
        last_login = user_info.get('last_login')
        if last_login:
            try:
                last_login_date = datetime.fromisoformat(last_login)
                days_since_login = (datetime.now() - last_login_date).days
                if days_since_login < 7:
                    score += 2
                elif days_since_login < 30:
                    score += 1
            except:
                pass
        
        # Regular usage (positive)
        login_count = int(user_info.get('login_count', 0))
        if login_count > 10:
            score += 2
        elif login_count > 3:
            score += 1
        
        # Recent failed attempts (negative)
        failed_count = user_attempts.get('failed_count', 0)
        if failed_count > 0:
            score -= failed_count
        
        # Account age (positive)
        created_at = user_info.get('created_at')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at)
                days_old = (datetime.now() - created_date).days
                if days_old > 30:
                    score += 1
            except:
                pass
        
        # Determine security level
        if score >= 4:
            return "High"
        elif score >= 1:
            return "Medium"
        else:
            return "Low"
            
    except Exception as e:
        logger.error(f"Error calculating security score: {e}")
        return "Unknown"

def is_user_session_valid(username: str, max_session_hours: int = 24) -> bool:
    """
    Check if a user session should still be considered valid.
    
    Parameters
    ----------
    username : str
        Username to check
    max_session_hours : int, default 24
        Maximum hours for session validity
        
    Returns
    -------
    bool
        True if session should be valid, False otherwise
    """
    try:
        user_info = get_user_info(username)
        if not user_info:
            return False
        
        last_login = user_info.get('last_login')
        if not last_login:
            return False
        
        last_login_date = datetime.fromisoformat(last_login)
        max_session_duration = timedelta(hours=max_session_hours)
        
        return (datetime.now() - last_login_date) <= max_session_duration
        
    except Exception as e:
        logger.error(f"Error checking session validity: {e}")
        return False

def get_authentication_status() -> Dict[str, Union[bool, str, int]]:
    """
    Get overall authentication system status.
    
    Returns
    -------
    Dict[str, Union[bool, str, int]]
        Authentication system status
    """
    try:
        stats = get_system_stats()
        
        return {
            'system_operational': True,
            'total_users': stats.get('total_users', 0),
            'active_users': stats.get('active_users', 0),
            'locked_accounts': stats.get('locked_accounts', 0),
            'version': APP_VERSION,
            'security_level': 'High',  # PBKDF2 with 100k iterations
            'encryption_method': 'PBKDF2-HMAC-SHA256',
            'last_maintenance': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting authentication status: {e}")
        return {
            'system_operational': False,
            'error': str(e)
        }

# ============================================================================
# Advanced Security Functions
# ============================================================================

def audit_user_activity(username: str, days_back: int = 30) -> Dict[str, Union[int, List[str]]]:
    """
    Audit user activity for security monitoring.
    
    Parameters
    ----------
    username : str
        Username to audit
    days_back : int, default 30
        Number of days to look back
        
    Returns
    -------
    Dict[str, Union[int, List[str]]]
        Audit results
    """
    try:
        username_clean = sanitize_username(username)
        
        # Get user info
        user_info = get_user_info(username_clean)
        if not user_info:
            return {'error': 'User not found'}
        
        # Get login attempts
        attempts_data = load_login_attempts()
        if 'attempts' in attempts_data:
            attempts_data = attempts_data['attempts']
        
        user_attempts = attempts_data.get(username_clean, {})
        
        # Calculate audit metrics
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        audit_results = {
            'username': username_clean,
            'audit_period_days': days_back,
            'total_login_attempts': user_attempts.get('total_attempts', 0),
            'failed_attempts': user_attempts.get('failed_count', 0),
            'account_created': user_info.get('created_at', ''),
            'last_login': user_info.get('last_login', ''),
            'login_count': int(user_info.get('login_count', 0)),
            'security_score': calculate_security_score(user_info, user_attempts),
            'account_status': user_info.get('account_status', 'active'),
            'suspicious_activity': []
        }
        
        # Check for suspicious patterns
        if user_attempts.get('failed_count', 0) > 3:
            audit_results['suspicious_activity'].append('Multiple recent failed login attempts')
        
        if user_info.get('account_status') != 'active':
            audit_results['suspicious_activity'].append('Account status is not active')
        
        return audit_results
        
    except Exception as e:
        logger.error(f"Error auditing user activity: {e}")
        return {'error': str(e)}

def export_security_logs(days_back: int = 7) -> Optional[str]:
    """
    Export security logs for analysis.
    
    Parameters
    ----------
    days_back : int, default 7
        Number of days of logs to export
        
    Returns
    -------
    Optional[str]
        JSON string of security logs or None if failed
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get all users and their recent activity
        users = load_users_from_file()
        attempts_data = load_login_attempts()
        
        if 'attempts' in attempts_data:
            attempts_data = attempts_data['attempts']
        
        security_log = {
            'export_date': datetime.now().isoformat(),
            'period_days': days_back,
            'app_version': APP_VERSION,
            'users': []
        }
        
        for username, user_data in users.items():
            user_attempts = attempts_data.get(username, {})
            
            user_log = {
                'username': username,
                'created_at': user_data.get('created_at', ''),
                'last_login': user_data.get('last_login', ''),
                'login_count': user_data.get('login_count', 0),
                'account_status': user_data.get('account_status', 'active'),
                'recent_failed_attempts': user_attempts.get('failed_count', 0),
                'total_attempts': user_attempts.get('total_attempts', 0)
            }
            
            security_log['users'].append(user_log)
        
        return json.dumps(security_log, indent=2)
        
    except Exception as e:
        logger.error(f"Error exporting security logs: {e}")
        return None

# ============================================================================
# Module Initialization and Cleanup
# ============================================================================

def perform_maintenance() -> Dict[str, Union[bool, int, str]]:
    """
    Perform routine maintenance on the authentication system.
    
    Returns
    -------
    Dict[str, Union[bool, int, str]]
        Maintenance results
    """
    try:
        results = {
            'maintenance_date': datetime.now().isoformat(),
            'success': True,
            'actions_performed': []
        }
        
        # Clean up old login attempts
        cleaned_attempts = cleanup_old_login_attempts(30)
        if cleaned_attempts > 0:
            results['actions_performed'].append(f"Cleaned {cleaned_attempts} old login attempts")
        
        # Backup user data
        try:
            _create_backup_if_needed(USERS_FILE)
            _create_backup_if_needed(LOGIN_ATTEMPTS_FILE)
            results['actions_performed'].append("Created backup files")
        except Exception as e:
            results['actions_performed'].append(f"Backup failed: {str(e)}")
        
        # Verify file permissions
        for file_path in [USERS_FILE, LOGIN_ATTEMPTS_FILE]:
            if os.path.exists(file_path):
                os.chmod(file_path, 0o600)
        results['actions_performed'].append("Verified file permissions")
        
        # Check system health
        stats = get_system_stats()
        results['system_stats'] = stats
        
        logger.info(f"Maintenance completed successfully: {len(results['actions_performed'])} actions")
        return results
        
    except Exception as e:
        logger.error(f"Maintenance failed: {e}")
        return {
            'maintenance_date': datetime.now().isoformat(),
            'success': False,
            'error': str(e)
        }

# Initialize on import (with enhanced setup)
if __name__ != "__main__":
    initialize_auth_module()

# ============================================================================
# Backward Compatibility & Legacy Support
# ============================================================================

# Maintain backward compatibility with existing Portfolio Manager Pro code
def list_users() -> List[str]:
    """
    List all registered usernames (admin function) - maintained for compatibility.
    
    Returns
    -------
    List[str]
        List of usernames
    """
    try:
        users = load_users_from_file()
        return list(users.keys())
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return []

def delete_user(username: str, password: str) -> bool:
    """
    Delete a user account with authentication - maintained for compatibility.
    
    Parameters
    ----------
    username : str
        Username to delete
    password : str
        Password for confirmation
        
    Returns
    -------
    bool
        True if deletion successful, False otherwise
    """
    try:
        # Authenticate first
        if not authenticate_user(username, password):
            logger.warning(f"User deletion failed - authentication failed: {username}")
            return False
        
        username_clean = sanitize_username(username)
        users = load_users_from_file()
        
        if username_clean not in users:
            return False
        
        # Remove user
        del users[username_clean]
        
        # Save changes
        if save_users(users):
            logger.info(f"User deleted successfully: {username_clean}")
            
            # Also clean up login attempts
            attempts_data = load_login_attempts()
            if 'attempts' in attempts_data:
                attempts_data = attempts_data['attempts']
                
            if username_clean in attempts_data:
                del attempts_data[username_clean]
                save_login_attempts(attempts_data)
            
            return True
        else:
            logger.error(f"Failed to save user deletion: {username_clean}")
            return False
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False

# ============================================================================
# Module Information
# ============================================================================

__version__ = APP_VERSION
__author__ = "Portfolio Manager Pro Team"
__license__ = "MIT"
__description__ = "Enhanced Authentication Module for Portfolio Manager Pro"

# Export public interface
__all__ = [
    'register_user',
    'authenticate_user', 
    'get_user_info',
    'change_password',
    'delete_user',
    'list_users',
    'get_system_stats',
    'is_account_locked',
    'get_user_portfolio_stats',
    'is_user_session_valid',
    'get_authentication_status',
    'perform_maintenance',
    'cleanup_old_login_attempts',
    'validate_username',
    'validate_password',
    'sanitize_username'
]