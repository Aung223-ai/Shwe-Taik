from django import forms

class SubCatForm(forms.Form):
    class Meta:
        fields = '__all__'