from django import forms
from .models import Job , Article
from .models import ContactMessage
from django.core.exceptions import ValidationError


JOB_DESCRIPTION_TEMPLATE = """
<h2>Job Description</h2>
<p>....</p>

<h2>The Role</h2>
<p>...</p>

<p>...</p>

<h2>Requirements</h2>
<ul>
<li></li>
<li></li>
<li></li>
</ul>
"""

class JobAdminForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = '__all__'
        widgets = {
            'categories': forms.SelectMultiple(attrs={'id': 'id_categories'}),
            'subcategories': forms.SelectMultiple(attrs={'id': 'id_subcategories'}),
        }

    class Media:
        js = ('js/job_admin.js',)
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # new job
            self.fields['description'].initial = JOB_DESCRIPTION_TEMPLATE


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Message subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Type your message...'}),
        }


