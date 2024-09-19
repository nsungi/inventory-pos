from django import forms
from .models import Stock


class StockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):  # Used to set CSS classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['quantity_in_stock'].widget.attrs.update({'class': 'textinput form-control', 'min': '0'})
        self.fields['price'].widget.attrs.update({'class': 'textinput form-control', 'step': '0.01'})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})

    class Meta:
        model = Stock
        fields = ['name', 'quantity_in_stock', 'price', 'image']   