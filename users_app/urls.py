from django.shortcuts import redirect
from django.urls import path

from users_app import views

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about_view, name='about'),
    path('index/', views.index, name='index'),
    path('faq/', views.faq, name='faq'),
    path('settings_rules/', views.settings_rules, name='settings_rules'),
    path('settings_rules/delete/<int:rule_id>/', views.delete_rule, name='delete_rule'),
    path('settings_service/', views.settings_service, name='settings_service'),
    path('settings_service/delete/<int:key_id>/', views.delete_service, name='delete_service'),
    path('webhook/<str:token>/', views.get_webhook, name='webhook'),
    path('delete_number_service/<int:id>/', views.delete_number_service, name='delete_number_service')

]
