from django import forms


class LoginForm(forms.Form):
    email = forms.CharField(label="Ten dang nhap hoac email", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "admin hoac name@example.com"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))


class RegisterForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    is_publisher = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    certificate = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "demo-cert.pdf"}))


class CategoryForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))


class AuthorForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    biography = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))
    publisher = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-select"}))


class BookForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    isbn = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}))
    language = forms.ChoiceField(choices=[("English", "English"), ("Arabic", "Arabic")], widget=forms.Select(attrs={"class": "form-select"}))
    no_of_page = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}))
    year_of_publication = forms.DateField(widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    total_number_of_book = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}))
    category = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-select"}))
    author_id = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-select"}))
    publisher_id = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-select"}))
    front_img = forms.URLField(required=False, widget=forms.URLInput(attrs={"class": "form-control"}))
    back_img = forms.URLField(required=False, widget=forms.URLInput(attrs={"class": "form-control"}))


class AddToCartForm(forms.Form):
    book_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={"class": "form-control", "style": "max-width: 90px;"}))


class CheckoutForm(forms.Form):
    country = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    city = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    street = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    card_number = forms.CharField(initial="4242424242424242", widget=forms.TextInput(attrs={"class": "form-control"}))
