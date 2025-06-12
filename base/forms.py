from django import forms
from .models import Job

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # new job
            self.fields['description'].initial = JOB_DESCRIPTION_TEMPLATE
