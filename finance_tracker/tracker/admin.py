from django.contrib import admin
from . models import Category, Transaction, MonthlyBudget

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(MonthlyBudget)