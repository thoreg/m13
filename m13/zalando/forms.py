from django import forms


class PriceToolForm(forms.Form):
    z_factor = forms.DecimalField(label='Z factor')
