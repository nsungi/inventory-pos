from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View, 
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    DetailView
)

from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.views import View
import matplotlib.pyplot as plt
import pandas as pd
import json 
  
 
from .models import (
    PurchaseBill, 
    Supplier, 
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,  
    SaleItem,
    SaleBillDetails,
    Stock,
    Expense
)
from .forms import (
    SelectSupplierForm, 
    PurchaseItemFormset,
    PurchaseDetailsForm, 
    SupplierForm, 
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm,
    ExpenseForm
)


 

# shows a lists of all suppliers
class SupplierListView(ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    queryset = Supplier.objects.filter(is_deleted=False)
    paginate_by = 10

# used to add a new supplier
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transaction/suppliers'
    success_message = "Supplier has been created successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Supplier'
        context["savebtn"] = 'Add Supplier'
        return context     

# used to update a supplier's info
class SupplierUpdateView(SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transaction/suppliers'
    success_message = "Supplier details has been updated successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Supplier'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Supplier'
        return context



# used to delete a supplier
class SupplierDeleteView(View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "Supplier has been deleted successfully"

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object' : supplier})

    def post(self, request, pk):  
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.save()                                               
        messages.success(request, self.success_message)
        return redirect('transaction:suppliers-list')




# used to view a supplier's profile
class SupplierView(View):
    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier'  : supplierobj,
            'bills'     : bills
        }
        return render(request, 'suppliers/supplier.html', context)


# shows the list of bills of all purchases 
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10


# used to select the supplier
class SelectSupplierView(View):
    form_class = SelectSupplierForm
    template_name = 'purchases/select_supplier.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            supplier_id = form.cleaned_data.get("supplier").id  # Get the ID of the selected supplier
            return redirect(reverse('transaction:new-purchase', kwargs={'pk': supplier_id}))
        return render(request, self.template_name, {'form': form})

    
    
  
# Used to generate a bill object and save items
class PurchaseCreateView(View):
    template_name = 'purchases/new_purchase.html'

    def get(self, request, pk):
        formset = PurchaseItemFormset(request.GET or None)  # Renders an empty formset
        supplierobj = get_object_or_404(Supplier, pk=pk)    # Gets the supplier object
        context = {
            'formset': formset,
            'supplier': supplierobj,
        }                                                   # Sends the supplier and formset as context
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = PurchaseItemFormset(request.POST)         # Receives a POST method for the formset
        supplierobj = get_object_or_404(Supplier, pk=pk)    # Gets the supplier object
        if formset.is_valid():
            # Saves bill
            try:
                billobj = PurchaseBill(supplier=supplierobj)
                billobj.save()
            except Exception as exc:
                print('Exception error! ', exc)
                context = {
                    'formset': formset,
                    'supplier': supplierobj,
                }
                return render(request, self.template_name, context)

            try:
                # Create bill details object
                billdetailsobj = PurchaseBillDetails(billno=billobj)
                billdetailsobj.save()
            except Exception as exc:
                print('Exception error! ', exc)
                # Removing purchase transaction to keep transaction data clean
                billobj.delete()
                context = {
                    'formset': formset,
                    'supplier': supplierobj,
                }
                return render(request, self.template_name, context)

            # Save each individual form
            for form in formset:
                # Save the form as a new PurchaseItem object
                billitem = form.save(commit=False)
                billitem.billno = billobj  # Links the bill object to the items
                # Gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)  # Gets the item
                # Calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # Updates quantity in stock db
                stock.quantity += billitem.quantity  # Updates quantity
                billdetailsobj.total += billitem.totalprice
                # Saves bill item and stock
                stock.save()
                billitem.save()

            billdetailsobj.save()
            messages.success(request, "Purchased items have been registered successfully")
            return redirect('transaction:purchase-bill', billno=billobj.billno)
        # If the formset is not valid
        formset = PurchaseItemFormset(request.GET or None)
        context = {
            'formset': formset,
            'supplier': supplierobj
        }
        return render(request, self.template_name, context)
  
  


# used to delete a bill object
class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "purchases/delete_purchase.html"
    success_url = '/transaction/purchases'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Purchase bill has been deleted successfully")
        return super(PurchaseDeleteView, self).delete(*args, **kwargs)




# shows the list of bills of all sales 
class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10




# used to display the sale bill object
class SaleBillView(View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        context = {
            'bill': SaleBill.objects.get(billno=billno),
            'items': SaleItem.objects.filter(billno=billno),
            'billdetails': SaleBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = SaleBillDetails.objects.get(billno=billno)
            # Update fields
            billdetailsobj.eway = request.POST.get("eway")
            # Set other fields...
            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill': SaleBill.objects.get(billno=billno),
            'items': SaleItem.objects.filter(billno=billno),
            'billdetails': SaleBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)




# used to generate a bill object and save items
class SaleCreateView(View):                                                      
    template_name = 'sales/new_sale.html'

    def get(self, request):
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)                          # renders an empty formset
        stocks = Stock.objects.filter(is_deleted=False)
        context = {
            'form'      : form,
            'formset'   : formset,
            'stocks'    : stocks
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)                                 # recieves a post method for the formset
        if form.is_valid() and formset.is_valid():
            # saves bill
            try:
                billobj = form.save(commit=False)
                billobj.save()

            except Exception as exc:
                print('Exception error! ',exc)
                context = {
                    'form'      : form,
                    'formset'   : formset,
                }
                return render(request, self.template_name, context)
            
            try:
                # create bill details object
                billdetailsobj = SaleBillDetails(billno=billobj)
                billdetailsobj.save()

            except Exception as exc:
                print('Exception error! ',exc)
                # Removing purchase transaction to keep transaction data clean
                billobj.delete()
                context = {
                    'form'      : form,
                    'formset'   : formset,
                }
                return render(request, self.template_name, context)

            for form in formset:                                                # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj                                       # links the bill object to the items
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)      
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity -= billitem.quantity
                billdetailsobj.total += billitem.totalprice 
                # saves bill item and stock
                stock.save()
                billitem.save()

            billdetailsobj.save()
            messages.success(request, "Sold items have been registered successfully")
            #return redirect('sale-bill', billno=billobj.billno)
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        context = {
            'form'      : form,
            'formset'   : formset,
        }
        return render(request, self.template_name, context)






# used to delete a bill object
class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transaction/sales'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Sale bill has been deleted successfully")
        return super(SaleDeleteView, self).delete(*args, **kwargs)



class PurchaseBillView(View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        context = {
            'bill': get_object_or_404(PurchaseBill, billno=billno),
            'items': PurchaseItem.objects.filter(billno=billno),
            'billdetails': get_object_or_404(PurchaseBillDetails, billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            try:
                # Ensure `billno` is an integer
                billdetailsobj = get_object_or_404(PurchaseBillDetails, billno=billno)
                billdetailsobj.eway = request.POST.get("eway")
                billdetailsobj.veh = request.POST.get("veh")
                billdetailsobj.destination = request.POST.get("destination")
                billdetailsobj.po = request.POST.get("po")
                billdetailsobj.cgst = Decimal(request.POST.get("cgst", "0"))
                billdetailsobj.sgst = Decimal(request.POST.get("sgst", "0"))
                billdetailsobj.igst = Decimal(request.POST.get("igst", "0"))
                billdetailsobj.cess = Decimal(request.POST.get("cess", "0"))
                billdetailsobj.tcs = Decimal(request.POST.get("tcs", "0"))
                billdetailsobj.total = Decimal(request.POST.get("total", "0"))

                billdetailsobj.save()
                messages.success(request, "Bill details have been modified successfully")
            except ValueError as e:
                # Handle conversion errors
                messages.error(request, f"Error processing numbers: {e}")

        context = {
            'bill': get_object_or_404(PurchaseBill, billno=billno),
            'items': PurchaseItem.objects.filter(billno=billno),
            'billdetails': get_object_or_404(PurchaseBillDetails, billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)




#Daily Sales report

class DailySalesView(TemplateView):
    template_name = 'sales/daily_sales.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        sales = SaleBill.objects.filter(time__range=(start_of_day, end_of_day))
        total_sales = sales.aggregate(total=Sum('salebillno__totalprice'))['total']
        context['total_sales'] = total_sales if total_sales else 0
        
        # Add the current date to context
        context['current_date'] = today

        # Prepare data for the chart
        daily_sales = sales.values('time__date').annotate(total=Sum('salebillno__totalprice')).order_by('time__date')
        # Convert date objects to strings
        formatted_sales = [{'time__date': sale['time__date'].strftime('%Y-%m-%d'), 'total': sale['total']} for sale in daily_sales]
        context['sales_data'] = json.dumps(formatted_sales)
        
        return context





#Single day sales

class DaySalesView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        sales = SaleBill.objects.filter(time__range=(start_of_day, end_of_day))
        total_sales = sales.aggregate(total=Sum('salebillno__totalprice'))['total']
        context['total_sales'] = total_sales if total_sales else 0
        context['current_date'] = today.strftime('%Y-%m-%d')  # Format date for display
        return context


    
 #Sales report   

class SalesReportView(TemplateView):
    template_name = 'sales/sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()
        start_of_month = today.replace(day=1)
        end_of_month = today + timedelta(days=31)
        sales = SaleBill.objects.filter(time__range=(start_of_month, end_of_month))

        daily_sales = sales.values('time__date').annotate(total=Sum('salebillno__totalprice')).order_by('time__date')

        # Convert dates to strings
        formatted_sales = [
            {
                'time__date': sale['time__date'].strftime('%Y-%m-%d'),
                'total': sale['total']
            }
            for sale in daily_sales
        ]

        context['sales_data'] = json.dumps(formatted_sales)
        return context





#Daily puchase summary

class DailyPurchaseView(View):
    template_name = 'purchases/daily_purchase.html'

    def get(self, request):
        today = now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        # Get purchases for today
        purchases = PurchaseBill.objects.filter(time__range=(start_of_day, end_of_day))
        total_purchases = purchases.aggregate(total=Sum('purchasebillno__totalprice'))['total']
        total_purchases = total_purchases if total_purchases else 0

        # Prepare data for the bar chart
        labels = []
        data = []

        for purchase in purchases:
            labels.append(purchase.billno)
            data.append(purchase.get_total_price())

        context = {
            'total_purchases': total_purchases,
            'labels': labels,
            'data': data,
            'current_date': today.strftime('%Y-%m-%d')
        }
        return render(request, self.template_name, context)




#Expenses

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = '/transaction/list/'  # Redirect after successful creation

    def form_valid(self, form):
        return super().form_valid(form)



class ExpenseListView(ListView):
    model = Expense
    template_name = 'expenses/expenses_list.html'
    context_object_name = 'expenses'
    paginate_by = 10  # Number of items per page

    def get_queryset(self):
        """Optionally, filter by date range or other criteria."""
        return Expense.objects.all().order_by('-date')
    


class ExpenseDetailView(DetailView):
    model = Expense
    template_name = 'expenses/expense_detail.html'
    context_object_name = 'expense'



    
    
#Expense report

class ExpenseReportView(TemplateView):
    template_name = 'expenses/expense_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        # Aggregate total expenses
        total_expenses = Expense.objects.filter(date__range=(start_of_day, end_of_day)).aggregate(total=Sum('amount'))['total']
        
        # Convert Decimal to float
        total_expenses = float(total_expenses) if total_expenses else 0.0
        
        # Data for the chart
        expense_data = Expense.objects.filter(date__range=(start_of_day, end_of_day))
        categories = expense_data.values_list('category__name', flat=True).distinct()
        amounts = [expense_data.filter(category__name=cat).aggregate(total=Sum('amount'))['total'] for cat in categories]

        # Convert amounts from Decimal to float
        amounts = [float(amount) if amount else 0.0 for amount in amounts]

        context['total_expenses'] = total_expenses
        context['current_date'] = today.strftime('%Y-%m-%d')
        context['categories'] = json.dumps(list(categories))
        context['amounts'] = json.dumps(amounts)
        return context





#Profit

class ProfitReportView(TemplateView):
    template_name = 'expenses/profit_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        # Total Sales Revenue
        sales = SaleBill.objects.filter(time__range=(start_of_day, end_of_day))
        total_sales = sales.aggregate(total=Sum('salebillno__totalprice'))['total'] or 0

        # Cost of Goods Sold (COGS)
        purchases = PurchaseBill.objects.filter(time__range=(start_of_day, end_of_day))
        total_cogs = purchases.aggregate(total=Sum('purchasebillno__totalprice'))['total'] or 0

        # Total Expenses
        expenses = Expense.objects.filter(date__range=(start_of_day, end_of_day))
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

        # Profit Calculation
        profit = total_sales - total_cogs - total_expenses

        context['total_sales'] = total_sales
        context['total_cogs'] = total_cogs
        context['total_expenses'] = total_expenses
        context['profit'] = profit
        context['current_date'] = today.strftime('%Y-%m-%d')

        return context
