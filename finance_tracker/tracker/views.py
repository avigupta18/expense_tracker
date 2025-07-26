from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from .models import Transaction
from .forms import TransactionForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView , ListView
from .models import MonthlyBudget
from .forms import MonthlyBudgetForm
from django.shortcuts import get_object_or_404
import datetime
import csv
from django.http import HttpResponse
from django.views import View
from calendar import monthrange
from django.utils.timezone import now

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get selected month from query params or default to current month
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')

        today = now().date()
        if month and year:
            selected_month = datetime.date(int(year), int(month), 1)
        else:
            selected_month = today.replace(day=1)

        # Filter transactions by selected month
        end_day = monthrange(selected_month.year, selected_month.month)[1]
        start_date = selected_month
        end_date = selected_month.replace(day=end_day)

        month_transactions = Transaction.objects.filter(user=user, date__range=(start_date, end_date))
        recent_transactions=Transaction.objects.filter(user=user).order_by('-date')[:5]
        transactions = Transaction.objects.filter(user=user, date__range=(start_date, end_date))
        income = transactions.filter(category__is_income=True).aggregate(total=Sum('amount'))['total'] or 0
        expense = transactions.filter(category__is_income=False).aggregate(total=Sum('amount'))['total'] or 0

        # Get the matching monthly budget
        budget = MonthlyBudget.objects.filter(user=user, month=selected_month).first()

        context.update({
            'selected_month': selected_month,
            'transactions': month_transactions ,
            'recent_transactions': recent_transactions,
            'total_income': income,
            'total_expense': expense,
            'balance': income - expense,
            'monthly_budget': budget,
            'budget_remaining': budget.amount - expense if budget else None,
            'over_budget': expense > budget.amount if budget else False,
            'months': ['01','02','03','04','05','06','07','08','09','10','11','12'],
            'years': [year for year in range(today.year - 1, today.year + 3)],
        })

        return context


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'tracker/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'tracker/transaction_form.html'
    success_url = reverse_lazy('transactions')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'tracker/transaction_form.html'
    success_url = reverse_lazy('transactions')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'tracker/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = MonthlyBudget
    form_class = MonthlyBudgetForm
    template_name = 'tracker/budget_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = MonthlyBudget
    form_class = MonthlyBudgetForm
    template_name = 'tracker/budget_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return MonthlyBudget.objects.filter(user=self.request.user)
    

class ExportCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Filter user's transactions
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Category', 'Amount', 'Description', 'Type'])

        for txn in transactions:
            writer.writerow([
                txn.date,
                txn.category.name,
                txn.amount,
                txn.description,
                'Income' if txn.category.is_income else 'Expense'
            ])

        return response


