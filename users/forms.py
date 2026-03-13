from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    location = forms.CharField(max_length=255, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    farmer_id = forms.CharField(max_length=50, required=False, help_text="Required for farmers (Kissan-ID)")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'phone_number', 'location', 'farmer_id', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Password must be at least 8 characters long'
        self.fields['password2'].help_text = 'Enter the same password for verification'
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        farmer_id = cleaned_data.get('farmer_id')
        
        if role == 'farmer' and not farmer_id:
            raise forms.ValidationError("Farmer ID (Kissan-ID) is required for farmers")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.location = self.cleaned_data['location']
        user.role = self.cleaned_data['role']
        if self.cleaned_data.get('farmer_id'):
            user.farmer_id = self.cleaned_data['farmer_id']
        
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')


class FarmerSubscriptionForm(forms.Form):
    SUBSCRIPTION_CHOICES = [
        (100, '₹100 - 1 Month'),
        (250, '₹250 - 3 Months'),
        (500, '₹500 - 6 Months'),
        (900, '₹900 - 1 Year'),
    ]
    
    subscription_plan = forms.ChoiceField(choices=SUBSCRIPTION_CHOICES, widget=forms.RadioSelect())
