from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_zipcode(value):
    '''
    Ensures an entered zipcode is a valid 5-digit zipcode.

    Input:
        value: a string

    Raises ValidationError if not a zipcode.
    '''
    if not value.isdigit():
        raise ValidationError(
            _('%(value)s is not a valid 5-digit Zip Code.'),
            params={'value': value})

class FullEntryForm(forms.Form):
    '''
    Django form for organization information input. 

    Required fields:
        Keywords
        Name
    Optional fields:
        zipcode
        description
        size
    '''
    keywords = forms.CharField(label="Key Words", 
        max_length=500, 
        widget=forms.TextInput(attrs={'size': 65}), help_text = " ")
    name = forms.CharField(label='Organization Name', max_length=100, 
        widget=forms.TextInput(attrs={'size': 50}), help_text = " ")
    # zipcode cannot be an integer because of the possibility of leading zeros
    zipcode = forms.CharField(label="Zip Code", 
        min_length=5, max_length=5, required=False, 
        widget=forms.TextInput(attrs={'size': 10}), 
        validators = [validate_zipcode], help_text = " ")
    description = forms.CharField(label="Description or Mission Statement", 
        max_length=1000, required=False, 
        widget=forms.Textarea, help_text = " ")
    size = forms.ChoiceField(label="Size", required=False, 
        choices=[(None, 'select'), ('small', 'small'), 
        ('medium', 'medium'), ('large', 'large')])

