"""Password hashing utilities using bcrypt."""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    BCrypt has a maximum password length of 72 bytes.
    For passwords longer than 72 bytes, bcrypt will raise an error.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash the password
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds is a good security/performance balance
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)
