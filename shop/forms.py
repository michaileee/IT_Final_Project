from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# 1. რეგისტრაციის პერსონალური ფორმა
class CustomRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ვთარგმნით ველების სახელებს
        self.fields['username'].label = "მომხმარებლის სახელი"
        self.fields['password1'].label = "პაროლი"
        self.fields['password2'].label = "გაიმეორეთ პაროლი"
        
        # ვასუფთავებთ ან ვთარგმნით ქვედა დამხმარე ტექსტებს
        self.fields['username'].help_text = "გამოიყენეთ მხოლოდ ასოები, ციფრები და @/./+/-/_ სიმბოლოები."
        self.fields['password1'].help_text = "პაროლი უნდა შეიცავდეს მინიმუმ 8 სიმბოლოს და არ უნდა იყოს ზედმეტად მარტივი."
        self.fields['password2'].help_text = ""

# 2. ავტორიზაციის (Login) პერსონალური ფორმა
class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ვთარგმნით შესვლის ველებსაც
        self.fields['username'].label = "მომხმარებლის სახელი"
        self.fields['password'].label = "პაროლი"