
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from .models import *
from django.http.response import HttpResponse , Http404 , HttpResponseRedirect , JsonResponse 
from django.utils import timezone
import json
# Create your views here.

def reservation_document(request):
  
    Room_objects = Room.objects.filter( reservation_status = False )
    context = {
        'room_objects' : Room_objects
    }
    return render(request , 'hotel_app/hotel-reservation-usr-document.htm' , context)

def reservation_information(request):
    customer_objects = Customer_info.objects.order_by('-first_name')[:5] # 0__0 ?
    croom_id = request.POST['roomchoice'] 
    room_spec = Room.objects.get( id = croom_id )

    context = {
        'room_spec' : room_spec
    }
    return render(request , 'hotel_app/hotel-reservation-usr-information.htm' , context)

def successfulSubmit( request ) : 
    startdate = datetime.datetime.strptime(request.POST[ 'startdate' ] ,'%Y-%m-%d').date()
    if startdate and startdate < datetime.date.today():
        return HttpResponse('bad reservation date [you select date in past]')

    customer_info = Customer_info(
        first_name = request.POST[ 'customer_firstname' ],
        last_name = request.POST[ 'customer_lastname' ],
        phone =  request.POST[ 'customer_phone' ],
        national_code = request.POST[ 'cutomer_nationalcode' ],
        birth_day = request.POST[ 'customer_birthdate' ] if request.POST[ 'customer_birthdate' ] else datetime.date.today(),
        usr_email = request.POST[ 'customer_email' ]
    )

    customer_info.save()

    final_roomchoice = request.POST[ 'final_roomchoice' ]
    room = Room.objects.get( id = final_roomchoice )
    room.reserveRoom()

    dependents_number = request.POST[ 'dependents_number' ]
    if dependents_number :
        for i in range( int(dependents_number) ) :
            dependent_info = Dependent_info( 
                first_name = request.POST[ 'dependent_number_' + str( i ) + '_firstname' ],
                last_name = request.POST[ 'dependent_number_' + str( i ) + '_lastname' ],
                national_code = request.POST[ 'dependent_number_' + str( i ) + '_nationalcode' ],
                dependent_customer_fk = customer_info
            )
            dependent_info.save()

    reservation_range = request.POST[ 'reservation_range' ]
    finishdate = startdate + datetime.timedelta(int(reservation_range))
    # finishdate += reservation_range #complete this  fin date
    reservation = Reservation(
        start_date = startdate,
        finish_date = finishdate,
        reservation_room_fk = room,
        reservation_customer_fk = customer_info,
        reservation_status = 'active'
    )
    
    reservation.save()
    
    context ={'msg':'Successful Submit','detail':'Your Reservation has been submitted','rsv_id':reservation.id}
    return render( request , 'hotel_app/successful-submit.htm' , context)


def room_reservation_extention(request):
    if request.method == 'GET':
        expired_Reservation_obj = Reservation.objects.filter(reservation_status='active',finish_date__lte = datetime.date.today())

        return render(request ,'hotel_app/hotel-room-reserve-extention.htm',{'expired_reservations':expired_Reservation_obj , 'today_date':datetime.date.today()})

    elif request.method == 'POST':
        try:
            rsv_id = request.POST['expired_reservation_item_id']
            nday_to_extend = request.POST['nday_to_extend']

            rsv_obj = Reservation.objects.get(id = rsv_id , reservation_status='active')
            if int(nday_to_extend) <= rsv_obj.max_day_extend() :
                rsv_obj.finish_date = rsv_obj.finish_date + datetime.timedelta(int(nday_to_extend))
                rsv_obj.save()

                context ={'msg':'Successful Reservation extention',
                          'detail':'Your Reservation has been extend'}
                return render( request , 'hotel_app/successful-submit.htm' , context)
            else:
                return HttpResponse('bad parameter for extend reservation')                

        except:
            return HttpResponse('bad parameter for extend reservation')

def room_checkout(request):
    if request.method == 'GET':
        return render(request , 'hotel_app/hotel-room-checkout.htm')

    elif request.method == 'POST':
        try:
            checkout_code = request.POST['searchbox']
            if checkout_code:
                rsv_obj = Reservation.objects.get(id=checkout_code,reservation_status='checkout')
                rsv_obj.reservation_status = 'fin'
                rsv_obj.save()
                room_obj = rsv_obj.reservation_room_fk
                room_obj.reservation_status = False
                room_obj.save()

                context ={'msg':'Successful checkout',
                          'detail':'customer checkout finished'}
                return render( request , 'hotel_app/successful-submit.htm' , context)
            else:
                return HttpResponse('bad checkout code')
        except:
            return HttpResponse('bad checkout code')
        
def get_checkout_info(request):
    if request.method == 'POST':
        checkout_code = request.POST['checkout_code']
        if checkout_code and checkout_code.isnumeric():
            try:
                checkout_obj = Payment.objects.get(payment_reservation_fk = checkout_code)
                result = {"payment_date":str(checkout_obj.payment_date) , "payment_status":str(checkout_obj.payment_status),
                          "payment_amount":str(checkout_obj.payment_amount),"reservation_fin_date":str(checkout_obj.payment_reservation_fk.finish_date),
                          "customer_fname":str(checkout_obj.payment_reservation_fk.reservation_customer_fk.first_name),
                          "customer_lname":str(checkout_obj.payment_reservation_fk.reservation_customer_fk.last_name)}
                return  HttpResponse(json.dumps(result))
            except:
                return HttpResponseBadRequest()
        else:
            return HttpResponseBadRequest()

    

def hotel_cash(request):
    if request.method == 'GET':

        #get reservation list with active status
        try:
            resrvation_obj = Reservation.objects.filter(reservation_status ='active')
          
            context_dict={'active_reservations':resrvation_obj , 'today_date':timezone.now()}
            return render(request , 'hotel_app/hotel-cash.htm',context_dict)
        except:
            return HttpResponse('bad form selection')
            
    elif request.method == 'POST':
        reservation_id = request.POST['reservation_item_id']
        resrvation_obj = Reservation.objects.get(id=reservation_id , reservation_status ='active')
        if reservation_id :
            return render(request , 'hotel_app/hotel-cash-payment.htm',{'r_id':reservation_id , 'total_cost':resrvation_obj.calc_cost()})
        else :
            return HttpResponse('bad reservation selection')
        

def cash_payment(request):
    if request.method == 'POST':
        rsv_id = request.POST['resrvation_id']
        try:
            #update resrvation
            resrvation_obj = Reservation.objects.get(id=rsv_id , reservation_status ='active')
            resrvation_obj.reservation_status = 'checkout'
            resrvation_obj.save()
            
            #upadate payment
            payment_obj = Payment(payment_reservation_fk = resrvation_obj,payment_date = datetime.date.today(),
                                    payment_status = 'succecfull', payment_amount = resrvation_obj.calc_cost())
            payment_obj.save()

            context ={'msg':'Payment Successful','detail':'Successful checkout '}
            return render( request , 'hotel_app/successful-submit.htm' , context)
        except:
            return HttpResponse('bad request parameter')
    else:
        return HttpResponse('bad request parameter')
    

