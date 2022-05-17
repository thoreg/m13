from django import forms

from .models import TransactionFileUpload


class PriceToolForm(forms.Form):
    """Form to set the PriceFactor which is used to pimp the prices for Z."""
    z_factor = forms.DecimalField(label='Z factor', decimal_places=2)


class UploadFileForm(forms.ModelForm):
    """Upload Form for Finance CSV Files."""
    original_csv = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = TransactionFileUpload
        fields = ['original_csv']
