from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View,
    CreateView, 
    UpdateView,
    TemplateView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Stock
from .forms import StockForm
from django_filters.views import FilterView
from .filters import StockFilter
from django.db.models import Sum
from transaction.models import SaleBill, PurchaseBill, Expense
from datetime import datetime, timedelta

  


class StockListView(FilterView):
    filterset_class = StockFilter
    queryset = Stock.objects.filter(is_deleted=False)
    template_name = 'inventory.html'
    paginate_by = 10


class StockCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Stock                                                                       # setting 'Stock' model as model
    form_class = StockForm                                                              # setting 'StockForm' form as form
    template_name = "edit_stock.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory/'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Stock has been created successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Stock'
        context["savebtn"] = 'Add to Inventory'
        return context       


class StockUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
    model = Stock                                                                       # setting 'Stock' model as model
    form_class = StockForm                                                              # setting 'StockForm' form as form
    template_name = "edit_stock.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory/'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Stock has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Stock'
        context["savebtn"] = 'Update Stock'
        context["delbtn"] = 'Delete Stock'
        return context


class StockDeleteView(View):                                                            # view class to delete stock
    template_name = "delete_stock.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Stock has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        return render(request, self.template_name, {'object' : stock})

    def post(self, request, pk):  
        stock = get_object_or_404(Stock, pk=pk)
        stock.is_deleted = True
        stock.save()                                               
        messages.success(request, self.success_message)
        return redirect('/inventory/')
    


class InventoryReportView(TemplateView):
    template_name = "inventory_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all non-deleted stocks
        stocks = Stock.objects.filter(is_deleted=False)
        
        # Prepare data for the bar chart
        labels = [stock.name for stock in stocks]
        data = [stock.quantity for stock in stocks]
        
        context['stocks'] = stocks
        context['total_quantity'] = stocks.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        context['labels'] = labels
        context['data'] = data
        
        return context



    
# Financial report

class DailyFinancialReportView(TemplateView):
    template_name = 'daily_financial_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()

        # Total Sales Revenue
        sales = SaleBill.objects.filter(time__date=today)
        total_sales = sales.aggregate(total=Sum('salebillno__totalprice'))['total'] or 0

        # Total Purchases
        purchases = PurchaseBill.objects.filter(time__date=today)
        total_purchases = purchases.aggregate(total=Sum('purchasebillno__totalprice'))['total'] or 0

        # Total Expenses
        expenses = Expense.objects.filter(date=today)
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

        # Total Inventory
        inventory = Stock.objects.filter(is_deleted=False)
        total_inventory = inventory.aggregate(total=Sum('quantity'))['total'] or 0

        # Profit Calculation
        profit = total_sales - total_purchases - total_expenses

        # Prepare data for the chart
        context['total_sales'] = total_sales
        context['total_purchases'] = total_purchases
        context['total_expenses'] = total_expenses
        context['total_inventory'] = total_inventory
        context['profit'] = profit
        context['report_date'] = today.strftime('%d %B %Y')

        return context



#General financial report
class GeneralFinancialReportView(TemplateView):
    template_name = 'general_financial_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=31)).replace(day=1)

        # Total Sales Revenue
        sales = SaleBill.objects.filter(time__range=(start_of_month, end_of_month))
        total_sales = sales.aggregate(total=Sum('salebillno__totalprice'))['total'] or 0

        # Total Purchases
        purchases = PurchaseBill.objects.filter(time__range=(start_of_month, end_of_month))
        total_purchases = purchases.aggregate(total=Sum('purchasebillno__totalprice'))['total'] or 0

        # Total Expenses
        expenses = Expense.objects.filter(date__range=(start_of_month, end_of_month))
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

        # Total Inventory
        inventory = Stock.objects.filter(is_deleted=False)
        total_inventory = inventory.aggregate(total=Sum('quantity'))['total'] or 0

        # Profit Calculation
        profit = total_sales - total_purchases - total_expenses

        # Prepare data for the chart
        context['total_sales'] = total_sales
        context['total_purchases'] = total_purchases
        context['total_expenses'] = total_expenses
        context['total_inventory'] = total_inventory
        context['profit'] = profit
        context['current_period'] = f"{start_of_month.strftime('%B %Y')}"

        return context
    


class UserGuideView(TemplateView):
    template_name = 'user_guide.html'

 