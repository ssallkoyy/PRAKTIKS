"""
Unit tests for PasswordValidator using TDD approach.
Demonstrates Red -> Green -> Refactor cycle.
"""
import unittest
from password_validator import PasswordValidator


class TestPasswordValidatorTDD(unittest.TestCase):
    """
    TDD Test suite showing step-by-step development.
    Each test method represents one TDD cycle.
    """
    
    def setUp(self):
        self.validator = PasswordValidator()
    
    # ===== TDD STEP 1: Minimum Length =====
    def test_step1_password_minimum_length(self):
        """
        TDD Step 1: Password must be at least 8 characters
        Red: Test fails (no implementation)
        Green: Add length check
        """
        self.assertFalse(self.validator.validate("1234567"))  # 7 chars - too short
        self.assertTrue(self.validator.validate("12345678"))  # 8 chars - minimum
    
    # ===== TDD STEP 2: Uppercase Letter =====
    def test_step2_password_requires_uppercase(self):
        """
        TDD Step 2: Must have at least one uppercase letter
        Red: Test fails (no uppercase check)
        Green: Add uppercase validation
        """
        self.assertFalse(self.validator.validate("password123!"))  # all lowercase
        self.assertTrue(self.validator.validate("Password123!"))   # has uppercase
    
    # ===== TDD STEP 3: Digit =====
    def test_step3_password_requires_digit(self):
        """
        TDD Step 3: Must have at least one digit
        Red: Test fails (no digit check)
        Green: Add digit validation
        """
        self.assertFalse(self.validator.validate("Password!"))     # no digits
        self.assertTrue(self.validator.validate("Password123!"))   # has digits
    
    # ===== TDD STEP 4: Special Character =====
    def test_step4_password_requires_special_char(self):
        """
        TDD Step 4: Must have at least one special character
        Red: Test fails (no special char check)
        Green: Add special char validation
        """
        self.assertFalse(self.validator.validate("Password123"))   # no special chars
        self.assertTrue(self.validator.validate("Password123!"))   # has !
    
    # ===== TDD STEP 5: No Spaces =====
    def test_step5_password_no_spaces(self):
        """
        TDD Step 5: Must not contain spaces
        Red: Test fails (no space check)
        Green: Add space validation
        """
        self.assertFalse(self.validator.validate("Pass word123!")) # has space
        self.assertTrue(self.validator.validate("Password123!"))   # no spaces
    
    # ===== TDD STEP 6: Lowercase Letter =====
    def test_step6_password_requires_lowercase(self):
        """
        TDD Step 6: Must have at least one lowercase letter
        Red: Test fails (no lowercase check)
        Green: Add lowercase validation
        """
        self.assertFalse(self.validator.validate("PASSWORD123!"))  # all uppercase
        self.assertTrue(self.validator.validate("Password123!"))   # has lowercase
    
    # ===== TDD STEP 7: None Value =====
    def test_step7_password_none_value(self):
        """
        TDD Step 7: Handle None value
        Red: Test fails (crashes on None)
        Green: Add None check
        """
        self.assertFalse(self.validator.validate(None))
    
    # ===== TDD STEP 8: Empty String =====
    def test_step8_password_empty_string(self):
        """
        TDD Step 8: Handle empty string
        Red: Test fails
        Green: Empty string fails length check
        """
        self.assertFalse(self.validator.validate(""))
    
    # ===== TDD STEP 9: Complete Valid Password =====
    def test_step9_complete_valid_password(self):
        """
        TDD Step 9: Test complete valid password
        Green: All requirements met
        """
        self.assertTrue(self.validator.validate("MyP@ssw0rd"))
        self.assertTrue(self.validator.validate("Secure123!"))
        self.assertTrue(self.validator.validate("Str0ng#Pass"))
    
    # ===== TDD STEP 10: Validation Errors =====
    def test_step10_get_validation_errors(self):
        """
        TDD Step 10: Get detailed validation errors
        Red: Method doesn't exist
        Green: Implement get_validation_errors()
        """
        errors = self.validator.get_validation_errors("weak")
        self.assertIn("Password must be at least 8 characters", errors)
        self.assertIn("Password must contain at least one uppercase letter", errors)
        self.assertIn("Password must contain at least one digit", errors)
        self.assertIn("Password must contain at least one special character", errors)
    
    def test_step10_get_validation_errors_empty_for_valid(self):
        """
        TDD Step 10: Valid password should have no errors
        """
        errors = self.validator.get_validation_errors("MyP@ssw0rd")
        self.assertEqual(len(errors), 0)
    
    def test_step10_get_validation_errors_none(self):
        """
        TDD Step 10: None password should return error
        """
        errors = self.validator.get_validation_errors(None)
        self.assertIn("Password cannot be None", errors)
    
    # ===== TDD STEP 11: Edge Cases =====
    def test_step11_password_exactly_minimum_length(self):
        """
        TDD Step 11: Password with exactly 8 characters
        """
        self.assertTrue(self.validator.validate("Pass123!"))
    
    def test_step11_password_very_long(self):
        """
        TDD Step 11: Very long password should work
        """
        long_password = "A" * 100 + "b1!"
        self.assertTrue(self.validator.validate(long_password))
    
    def test_step11_password_only_special_chars(self):
        """
        TDD Step 11: Password with only special chars should fail
        """
        self.assertFalse(self.validator.validate("!!!!!!!!"))
    
    def test_step11_password_only_digits(self):
        """
        TDD Step 11: Password with only digits should fail
        """
        self.assertFalse(self.validator.validate("12345678"))


class TestPasswordValidatorEdgeCases(unittest.TestCase):
    """Additional edge case tests for complete coverage."""
    
    def setUp(self):
        self.validator = PasswordValidator()
    
    def test_password_with_unicode(self):
        """Test password with unicode characters"""
        # Unicode chars are not in SPECIAL_CHARS, so should fail
        self.assertFalse(self.validator.validate("Пароль123!"))
    
    def test_password_with_tab(self):
        """Test password with tab character"""
        # Tab is not a space, but password should still work if other requirements met
        self.assertTrue(self.validator.validate("Pass\tword1!"))
    
    def test_password_with_newline(self):
        """Test password with newline"""
        self.assertTrue(self.validator.validate("Pass\nword1!"))
    
    def test_password_all_special_chars_from_set(self):
        """Test password with all special characters from the set"""
        self.assertTrue(self.validator.validate("Aa1!@#$%^&*"))
    
    def test_password_missing_one_requirement(self):
        """Test passwords missing exactly one requirement"""
        # Missing uppercase
        self.assertFalse(self.validator.validate("password123!"))
        # Missing lowercase
        self.assertFalse(self.validator.validate("PASSWORD123!"))
        # Missing digit
        self.assertFalse(self.validator.validate("Password!!!"))
        # Missing special char
        self.assertFalse(self.validator.validate("Password123"))


def run_tests():
    """Run all tests and display results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordValidatorTDD))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordValidatorEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TDD TEST SUMMARY")
    print("=" * 70)
    print("Tests run: {}".format(result.testsRun))
    print("Failures: {}".format(len(result.failures)))
    print("Errors: {}".format(len(result.errors)))
    print("Success: {}".format(result.wasSuccessful()))
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
