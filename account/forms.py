from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
import re


class CustomerRegistrationForm(forms.Form):
    """Customer Registration Form with comprehensive validation"""
    
    full_name = forms.CharField(
        max_length=100,
        min_length=2,
        required=True,
        error_messages={
            'required': 'Full name is required',
            'min_length': 'Name must be at least 2 characters long',
            'max_length': 'Name cannot exceed 100 characters'
        }
    )
    
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message="Enter a valid email address")],
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )
    
    phone = forms.CharField(
        max_length=15,  # allow input but regex enforces exactly 10 digits
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Enter a valid 10-digit phone number'
            )
        ],
        error_messages={
            'required': 'Phone number is required'
        }
    )
    
    password = forms.CharField(
        min_length=8,
        max_length=128,
        required=True,
        error_messages={
            'required': 'Password is required',
            'min_length': 'Password must be at least 8 characters long'
        }
    )
    
    confirm_password = forms.CharField(
        required=True,
        error_messages={
            'required': 'Please confirm your password'
        }
    )
    
    def clean_email(self):
        """Validate email uniqueness and format"""
        email = self.cleaned_data.get('email')
        
        if email:
            # Convert to lowercase for consistency
            email = email.lower().strip()
            
            # Check if email already exists
            if User.objects.filter(username=email).exists():
                raise ValidationError(
                    "🔴 This email is already registered. Please use a different email or try logging in.",
                    code='email_exists'
                )
            
        return email
    
    # Phone validation temporarily disabled until migration is run
    # def clean_phone(self):
    #     """Validate phone number uniqueness"""
    #     from .models import Profile
    #     
    #     phone = self.cleaned_data.get('phone')
    #     
    #     if phone:
    #         # Strip any spaces or special characters except +
    #         phone = phone.strip()
    #         
    #         # Check if phone already exists
    #         if Profile.objects.filter(phone=phone).exists():
    #             raise ValidationError(
    #                 "🔴 This phone number is already registered. Please use a different number.",
    #                 code='phone_exists'
    #             )
    #         
    #     return phone
    
    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password')
        
        if password:
            # Check for at least one uppercase letter
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter")
            
            # Check for at least one lowercase letter
            if not re.search(r'[a-z]', password):
                raise ValidationError("Password must contain at least one lowercase letter")
            
            # Check for at least one digit
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one number")
            
            # Check for at least one special character
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("Password must contain at least one special character (!@#$%^&*, etc.)")
        
        return password
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match")
        
        return cleaned_data


class ProviderRegistrationForm(forms.Form):
    """Provider Registration Form with comprehensive validation"""
    
    full_name = forms.CharField(
        max_length=100,
        min_length=2,
        required=True,
        error_messages={
            'required': 'Full name is required',
            'min_length': 'Name must be at least 2 characters long'
        }
    )
    
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message="Enter a valid email address")],
        error_messages={
            'required': 'Email is required'
        }
    )
    
    phone = forms.CharField(
        max_length=15,  # allow input but regex enforces exactly 10 digits
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Enter a valid 10-digit phone number'
            )
        ],
        error_messages={
            'required': 'Phone number is required'
        }
    )
    
    password = forms.CharField(
        min_length=8,
        max_length=128,
        required=True,
        error_messages={
            'required': 'Password is required',
            'min_length': 'Password must be at least 8 characters long'
        }
    )
    
    confirm_password = forms.CharField(
        required=True,
        error_messages={
            'required': 'Please confirm your password'
        }
    )
    
    experience = forms.CharField(
        max_length=500,
        required=True,
        error_messages={
            'required': 'Experience details are required'
        }
    )
    
    service_categories = forms.MultipleChoiceField(
        required=True,
        choices=[
            ("painting", "Painting"),
            ("plumbing", "Plumbing"),
            ("electrical", "Electrical"),
            ("cleaning", "Cleaning"),
            ("carpentry", "Carpentry"),
            ("ac_repair", "AC Repair"),
        ],
        error_messages={
            'required': 'Please select at least one service category'
        }
    )
    
    def clean_email(self):
        """Validate email uniqueness and format"""
        email = self.cleaned_data.get('email')
        
        if email:
            email = email.lower().strip()
            
            if User.objects.filter(username=email).exists():
                raise ValidationError(
                    "🔴 This email is already registered. Please use a different email or try logging in.",
                    code='email_exists'
                )
        
        return email
    
    # Phone validation temporarily disabled until migration is run
    # def clean_phone(self):
    #     """Validate phone number uniqueness"""
    #     from .models import Profile
    #     
    #     phone = self.cleaned_data.get('phone')
    #     
    #     if phone:
    #         # Strip any spaces or special characters except +
    #         phone = phone.strip()
    #         
    #         # Check if phone already exists
    #         if Profile.objects.filter(phone=phone).exists():
    #             raise ValidationError(
    #                 "🔴 This phone number is already registered. Please use a different number.",
    #                 code='phone_exists'
    #             )
    #         
    #     return phone
    
    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password')
        
        if password:
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter")
            
            if not re.search(r'[a-z]', password):
                raise ValidationError("Password must contain at least one lowercase letter")
            
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one number")
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("Password must contain at least one special character")
        
        return password
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match")
        
        return cleaned_data


class ProviderCertificateUploadForm(forms.Form):
    """Form for validating certificate uploads"""
    
    ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    certificates = forms.FileField(
        required=True,
        error_messages={
            'required': 'At least one certificate is required'
        }
    )
    
    def clean_certificates(self):
        """Validate certificate file"""
        certificate = self.cleaned_data.get('certificates')
        
        if certificate:
            # Check file size
            if certificate.size > self.MAX_FILE_SIZE:
                raise ValidationError(f"File size must not exceed 5MB. Your file is {certificate.size / (1024*1024):.2f}MB")
            
            # Check file extension
            file_extension = certificate.name.split('.')[-1].lower()
            if file_extension not in self.ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f"Only {', '.join(self.ALLOWED_EXTENSIONS)} files are allowed. You uploaded: {file_extension}"
                )
        
        return certificate


class LoginForm(forms.Form):
    """Login Form with validation"""
    
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message="Enter a valid email address")],
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )
    
    password = forms.CharField(
        required=True,
        min_length=1,
        error_messages={
            'required': 'Password is required'
        }
    )
    
    def clean_email(self):
        """Normalize email"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email
