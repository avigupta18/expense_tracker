from django import forms
from .models import Transaction
from .models import MonthlyBudget
from datetime import datetime

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('category', 'amount', 'description', 'date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class MonthlyBudgetForm(forms.ModelForm):
    # Use CharField so '2025-08' is accepted directly
    month = forms.CharField(
        label='Month',
        widget=forms.TextInput(attrs={'type': 'month'})
    )

    class Meta:
        model = MonthlyBudget
        fields = ['amount', 'month']

    def clean_month(self):
        month_str = self.cleaned_data['month']  # e.g. '2025-08'
        try:
            return datetime.strptime(month_str, '%Y-%m').date().replace(day=1)
        except (ValueError, TypeError):
            raise forms.ValidationError('Enter a valid month (YYYY-MM).')


