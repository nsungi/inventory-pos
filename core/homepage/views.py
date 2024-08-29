from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.db.models import Sum
from django.views.generic import View
from inventory.models import Stock
from transaction.models import SaleBill, PurchaseBill, Expense 
from django.views.generic import FormView, TemplateView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import PasswordResetRequestForm, CustomSetPasswordForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Product, Customer, Note
from .forms import ProductForm, CustomerForm, NoteForm


  
class HomeView(View):
    template_name = "home.html"

    def get(self, request):
        # For stock data
        labels = []
        data = []
        stockqueryset = Stock.objects.filter(is_deleted=False).order_by('-quantity')
        for item in stockqueryset:
            labels.append(item.name)
            data.append(item.quantity)
        
        # For sales data
        today = now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)
        
        sales = SaleBill.objects.filter(time__range=(start_of_day, end_of_day))
        total_sales = sales.aggregate(total=Sum('salebillno__totalprice'))['total'] or 0
        
        # Calculate total purchases
        purchases = PurchaseBill.objects.filter(time__range=(start_of_day, end_of_day))
        total_purchases = purchases.aggregate(total=Sum('purchasebillno__totalprice'))['total'] or 0
        
        # Calculate total expenses
        expenses = Expense.objects.filter(date__range=(start_of_day, end_of_day))
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

        # Calculate daily profit
        daily_profit = total_sales - (total_purchases + total_expenses)

        # For recent sales and purchases
        recent_sales = SaleBill.objects.order_by('-time')[:3]
        recent_purchases = PurchaseBill.objects.order_by('-time')[:3]
        recent_expenses = Expense.objects.order_by('-date')[:3]
        
        context = {
            'labels': labels,
            'data': data,
            'sales': recent_sales,
            'purchases': recent_purchases,
            'expenses': recent_expenses,
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'total_expenses': total_expenses,
            'daily_profit': daily_profit,  # Add daily profit to context
            'current_date': today.strftime('%Y-%m-%d'),  # Format date for display
        }
        
        return render(request, self.template_name, context)


class AboutView(View):
    template_name = "user_guide.html"
    
  
class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product-list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product-list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'products/product_delete.html'
    success_url = reverse_lazy('product-list')




class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer-list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer-list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_delete.html'
    success_url = reverse_lazy('customer-list')



class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'

class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'

class NoteCreateView(CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('note-list')

class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('note-list')

class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'notes/note_delete.html'
    success_url = reverse_lazy('note-list')
  
  
  

class PasswordResetRequestView(FormView):
    template_name = 'registration/password_reset_form.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        reset_url = f"http://{get_current_site(self.request).domain}{url}"
        message = render_to_string('registration/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        send_mail('Password Reset Request', message, 'no-reply@yourdomain.com', [user.email])
        return super().form_valid(form)
    
    

class PasswordResetDoneView(TemplateView):
    template_name = 'registration/password_reset_done.html'
    
    
    

class PasswordResetConfirmView(FormView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        uidb64 = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
        if default_token_generator.check_token(user, token):
            kwargs['user'] = user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)



class PasswordResetCompleteView(TemplateView):
    template_name = 'registration/password_reset_complete.html'





class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'registration/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your password was successfully updated!')
        return super().form_valid(form)



class PasswordChangeDoneView(TemplateView):
    template_name = 'registration/password_change_done.html'
