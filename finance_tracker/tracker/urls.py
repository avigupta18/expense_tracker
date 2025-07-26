from django.urls import path
from . import views
from .views import DashboardView
from .views import (
    DashboardView,
    TransactionListView, TransactionCreateView,
    TransactionUpdateView, TransactionDeleteView ,
    BudgetCreateView, BudgetUpdateView,
)
from .views import ExportCSVView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('transactions/add/', TransactionCreateView.as_view(), name='add_transaction'),
    path('transactions/<int:pk>/edit/', TransactionUpdateView.as_view(), name='edit_transaction'),
    path('transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name='delete_transaction'),
    path('budget/add/', BudgetCreateView.as_view(), name='add_budget'),
    path('budget/<int:pk>/edit/',BudgetUpdateView.as_view(),name='edit_budget'),
    path('transactions/export/',ExportCSVView.as_view(),name='export_csv')
]
