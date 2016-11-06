from django import forms

class bookImgFileForm(forms.Form):
	book_image = forms.FileField(label='Select file', required=False)