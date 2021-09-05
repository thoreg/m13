from django import forms

from .models import PriceTool


class PriceToolForm(forms.Form):
    z_factor = forms.DecimalField(label='Z factor', decimal_places=2)
