import pytz
from django import forms


class SearchCriteriaForm(forms.Form):
    COUNTRY_CHOICES = tuple(((code.lower(), name) for code, name in pytz.country_names.items()))

    language = forms.CharField(max_length=256, required=False)
    ignore_forks = forms.NullBooleanField(required=False)
    last_update = forms.DateField(required=False)
    project_title = forms.CharField(max_length=256, required=False)
    country_codes = forms.MultipleChoiceField(required=False, choices=COUNTRY_CHOICES)
    stars_lower_bound = forms.IntegerField(required=False)
    stars_upper_bound = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=True)
