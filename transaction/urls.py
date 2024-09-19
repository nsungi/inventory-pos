from django.urls import path
#from django.conf.urls import url
from . import views

app_name = 'transaction'

urlpatterns = [
    path('suppliers/', views.SupplierListView.as_view(), name='suppliers-list'),
    path('suppliers/new', views.SupplierCreateView.as_view(), name='new-supplier'),
    path('suppliers/<pk>/edit', views.SupplierUpdateView.as_view(), name='edit-supplier'),
    path('suppliers/<pk>/delete', views.SupplierDeleteView.as_view(), name='delete-supplier'),
    path('suppliers/<name>', views.SupplierView.as_view(), name='supplier'),

    path('purchases/', views.PurchaseView.as_view(), name='purchases-list'), 
    #path('purchases/new', views.SelectSupplierView.as_view(), name='select-supplier'), 
    path('purchases/select/', views.SelectSupplierView.as_view(), name='select-supplier'),
    path('daily-purchases/', views.DailyPurchaseView.as_view(), name='daily-purchases'),
   # path('purchases/new/<pk>', views.PurchaseCreateView.as_view(), name='new-purchase'),  
    
    
    path('purchases/new/<int:pk>/', views.PurchaseCreateView.as_view(), name='new-purchase'),
 
    path('purchases/bill/<int:billno>/', views.PurchaseBillView.as_view(), name='purchase-bill'),
    
    path('purchases/<pk>/delete', views.PurchaseDeleteView.as_view(), name='delete-purchase'),
    
    path('sales/', views.SaleView.as_view(), name='sales-list'),
    path('new-sale/', views.SaleCreateView.as_view(), name='new-sale'),
    path('sales/<pk>/delete', views.SaleDeleteView.as_view(), name='delete-sale'),
    
    
    
    path('daily-sales/', views.DailySalesView.as_view(), name='daily_sales'),
    path('day-sales/', views.DaySalesView.as_view(), name='day_sales'),
    path('sales-report/', views.SalesReportView.as_view(), name='sales_report'),

    path("purchases/<billno>", views.PurchaseBillView.as_view(), name="purchase-bill"),
    path("sales/<billno>", views.SaleBillView.as_view(), name="sale-bill"),
    
    
    path('list/', views.ExpenseListView.as_view(), name='list'),
    path('create/', views.ExpenseCreateView.as_view(), name='create'),
    path('report/', views.ExpenseReportView.as_view(), name='report'),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/', views.ExpenseListView.as_view(), name='expenses'),

]

 
 