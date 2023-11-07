from django.db import models
import datetime
from django.core.validators import MaxValueValidator,MinValueValidator,MinLengthValidator

# Room 
class Room(models.Model):
    # room_id = models.AutoField(primary_key=True)
    num_bed = models.SmallIntegerField(validators=[MaxValueValidator(4) , MinValueValidator(1)])
    special_view_flag = models.BooleanField(default=False)
    max_num_person = models.SmallIntegerField(validators=[MaxValueValidator(10) , MinValueValidator(1)])
    cost_per_night = models.DecimalField(max_digits=6, decimal_places=2)

    reservation_status = models.BooleanField(default=False) # becarefull about this

    def reserveRoom( self ) :
        self.reservation_status = True
        self.save()
        return ''

    def __str__(self):
        return str(self.id)+' '+str(self.reservation_status)


# customer_info
class Customer_info(models.Model):
    # customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone = models.CharField(max_length=11 , validators=[MinLengthValidator(11)]) 
    national_code = models.CharField(max_length=10 , validators=[MinLengthValidator(10)]) 
    birth_day = models.DateField()
    usr_email = models.EmailField(max_length = 254)

    def __str__(self):
        return self.first_name+' '+self.last_name


# customer_Dependent_info
class Dependent_info( models.Model ) :
    dependent_id = models.AutoField( primary_key=True )
    first_name = models.CharField( max_length=20)
    last_name = models.CharField(max_length=20)
    national_code = models.CharField(max_length=10 , validators=[MinLengthValidator(10)]) 
    dependent_customer_fk = models.ForeignKey( Customer_info, on_delete=models.CASCADE )

    def __str__(self) :
        return str(self.dependent_id) +' '+str(self.dependent_customer_fk.id)

# reservation
class Reservation(models.Model):
    reserve_status_list = (('1','active') ,('2','checkout'),('3','fin'))

    start_date = models.DateField()
    finish_date = models.DateField()
    reservation_room_fk = models.ForeignKey(Room , on_delete=models.CASCADE)
    reservation_customer_fk = models.ForeignKey(Customer_info , on_delete=models.DO_NOTHING)
    reservation_status = models.CharField(max_length=1 , default= '1' , choices=reserve_status_list)
    
    def max_day_extend(self):
        resv_obj = Reservation.objects.filter(start_date__gt = self.finish_date ,reservation_status='active',
                                                reservation_room_fk = self.reservation_room_fk).order_by('start_date').first()
        if resv_obj:
            if (resv_obj.start_date - self.finish_date).days -1 > 10 :
                return 10
            else:
                return (resv_obj.start_date - self.finish_date).days -1
        else:
            return 10        
    def calc_cost(self):
        final_cost = ((datetime.date.today() - self.start_date).days)*float(self.reservation_room_fk.cost_per_night)*1.1

        if final_cost == 0.0:
            final_cost = float(self.reservation_room_fk.cost_per_night)*1.1

        if final_cost < 0 :
            final_cost = 0
        return final_cost
    def __str__(self):
        return str(self.id) + ' '+str(self.start_date)+' '+str(self.finish_date)+' '+self.reservation_status


# payment
class Payment(models.Model):
    payment_status_list =(('1','succecfull') , ('2','rejected'))

    payment_reservation_fk = models.ForeignKey(Reservation , on_delete=models.CASCADE)
    payment_date = models.DateField()
    payment_status = models.CharField(max_length=1 , default= '1' , choices=payment_status_list)
    payment_amount = models.DecimalField(max_digits=8, decimal_places=3)
    
    def __str__(self):
        return str(self.id) +' '+str(self.payment_reservation_fk.id)+' '+self.payment_status+' '+str(self.payment_amount)+'$'
# Create your models here.
