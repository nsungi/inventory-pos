from django.urls import path
#from django.conf.urls import url
from . import views
 

app_name = 'inventory'

urlpatterns = [
    path('', views.StockListView.as_view(), name='inventory'),
    path('new', views.StockCreateView.as_view(), name='new-stock'),
    path('stock/<pk>/edit', views.StockUpdateView.as_view(), name='edit-stock'),
    path('stock/<pk>/delete', views.StockDeleteView.as_view(), name='delete-stock'),
    path('report/', views.InventoryReportView.as_view(), name='inventory-report'),
    path('report/general/', views.GeneralFinancialReportView.as_view(), name='general-financial-report'),
    path('report/daily/', views.DailyFinancialReportView.as_view(), name='daily-financial-report'),
    
    path('guide', views.UserGuideView.as_view(), name='guide'),
     
]



 