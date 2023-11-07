from django.urls import path
from . import views

#install hotel_app urls
app_name ='hotel_app'
urlpatterns = [
    path('reservation',views.reservation_document, name='reservation'),
    path('reservationinfo',views.reservation_information, name='reservationinfo'),
    path( 'successful-submit', views.successfulSubmit, name='successful-submit' ),

    path('extend-room',views.room_reservation_extention , name='room_reservation_extention'),
    path('checkout',views.room_checkout , name ='checkout'),
    path('getcheckoutinfo',views.get_checkout_info , name ='getcheckoutinfo'),
    path('cash',views.hotel_cash , name='hotel_cash'),
    path('cash/payment',views.cash_payment , name='cash_payment'),
]