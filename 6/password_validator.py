"""
Password Validator - validates password strength requirements.
"""


class PasswordValidator:
    """Validator for password strength requirements."""
    
    MIN_LENGTH = 8
    SPECIAL_CHARS = "!@#$%^&*"
    
    def validate(self, password):
        """
        Validate password meets all requirements.
        
        Args:
            password: Password string to validate
            
        Returns:
            bool: True if password is valid, False otherwise
        """
        if password is None:
            return False
        
        if not self._check_length(password):
            return False
        
        if not self._check_no_spaces(password):
            return False
        
        if not self._check_uppercase(password):
            return False
        
        if not self._check_lowercase(password):
            return False
        
        if not self._check_digit(password):
            return False
        
        if not self._check_special_char(password):
            return False
        
        return True
    
    def _check_length(self, password):
        """Check minimum length requirement."""
        return len(password) >= self.MIN_LENGTH
    
    def _check_no_spaces(self, password):
        """Check password has no spaces."""
        return " " not in password
    
    def _check_uppercase(self, password):
        """Check at least one uppercase letter."""
        return any(c.isupper() for c in password)
    
    def _check_lowercase(self, password):
        """Check at least one lowercase letter."""
        return any(c.islower() for c in password)
    
    def _check_digit(self, password):
        """Check at least one digit."""
        return any(c.isdigit() for c in password)
    
    def _check_special_char(self, password):
        """Check at least one special character."""
        return any(c in self.SPECIAL_CHARS for c in password)
    
    def get_validation_errors(self, password):
        """
        Get list of validation errors.
        
        Args:
            password: Password string to validate
            
        Returns:
            list: List of error messages
        """
        errors = []
        
        if password is None:
            errors.append("Password cannot be None")
            return errors
        
        if not self._check_length(password):
            errors.append("Password must be at least {} characters".format(self.MIN_LENGTH))
        
        if not self._check_no_spaces(password):
            errors.append("Password must not contain spaces")
        
        if not self._check_uppercase(password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not self._check_lowercase(password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not self._check_digit(password):
            errors.append("Password must contain at least one digit")
        
        if not self._check_special_char(password):
            errors.append("Password must contain at least one special character: {}".format(self.SPECIAL_CHARS))
        
        return errors
