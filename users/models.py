import datetime
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth.models import AbstractUser,BaseUserManager

# Create your models here.
"""_Flexible _ and customizable way of handle user creation"""

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager for the creation of regular users
    """

    def create_user(self, username, email, password=None,**extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username.strip(),email=email,**extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    """
    Create and save a SuperUser with the given username, email and password ensuring
    access to Django admin interface
    """

    def create_superuser(self, username, email, password = None,**extra_fields):
        
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')
        
        return self.create_user(username, password, email, **extra_fields)
    

class CustomUser(AbstractUser):
    """
    You can add fields that you want in your form not included in AbstractUser
    e.g gender = models.CharField(max_length=10)
    """
    USER_TYPE_CHOICES=(
        ('patient','Patient'),
        ('doctor','Doctor'),
    )
    
    GENDER_MALE=0
    GENDER_FEMALE=1
    
    GENDER_CHOICES=(
        (GENDER_MALE,'Male'),
        (GENDER_FEMALE,'Female')
    )
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    user_type=models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    username=models.CharField(
        max_length=150,
        unique=True,
        help_text='Required 150 caracters or fewer.Letters, digits and spaces only.',
        validators=[],
        error_messages={'unique':'A user with that username already exists',
        },
        )
    
    email = models.EmailField(verbose_name='email',unique=True,help_text="The email field is required",
                              error_messages={'unique': 'A user with that email already exits'})
    
    birth_date = models.DateField(verbose_name='birthdate',help_text='Select your birth date')
    gender = models.IntegerField(verbose_name='gender', choices=GENDER_CHOICES, help_text='Select your gender')
     
    """_Role based authorization purposes_
    """
    def is_patient(self):
        return self.user_type =='patient'
    
    def is_doctor(self):
        return self.user_type == 'doctor'
    
    def greet(self):
        return {GENDER_MALE:'Welcome Mr.{self.username}', GENDER_FEMALE:'Welcome Ms.{self.username}'}[self.gender]
    
    def get_age(self):
        age=datetime.date.today()-self.birth_date
        return int((age).days/365.25)
        
    objects=CustomUserManager()

"""_Using Proxy Models for Handle the Complex User Data Model and enhance future mantainment and scalability_"""

class Patient(CustomUser):
    
    PATIENT_TYPE_CHOICES = (
        ('urgency', 'Urgency'),
        ('common', 'Common'),
    )
    
    patient_type = models.CharField(max_length=20, choices=PATIENT_TYPE_CHOICES)
    
# Temperature in degrees Celsius
    temperature = models.DecimalField(
                                    max_digits=5,
                                    decimal_places=2,
                                    validators=[MinValueValidator(36.5),MaxValueValidator(42.5)],
                                    verbose_name='Body temperature',
                                    help_text="Patient's body temperature in degrees Celsius",
                                    null=True,   # Allows the field to be null if temperature is unknown
                                    blank=True)  # Allows the field to be blank in forms 

# Pulse in beats per minute    
    pulse = models.IntegerField(
        validators=[MinValueValidator(40),MaxValueValidator(120)],
        verbose_name='Pulse Rate',
        help_text="Patient's pulse rate in beats per minute",
        null=True,  # Allows the field to be null if pulse is unknown
        blank=True) # Allows the field to be blank in forms 
    
 # Blood pressure in mmHg, typically recorded as systolic(HIGH)/diastolic(LOW)
    systolic_pressure = models.DecimalField(
        verbose_name="Systolic Blood Pressure",
        help_text="Patient's systolic blood pressure in mmHg",
        validators=[MinValueValidator(90),MaxValueValidator(140)],
        null=True,  # Allows the field to be null if blood pressure is unknown
        blank=True,  # Allows the field to be blank in forms
    )
    diastolic_pressure = models.DecimalField(
        verbose_name="Diastolic Blood Pressure",
        help_text="Patient's diastolic blood pressure in mmHg",
        validators=[MinValueValidator(60),MaxValueValidator(90)],
        null=True,  # Allows the field to be null if blood pressure is unknown
        blank=True,  # Allows the field to be blank in forms
    )   
    
    
    class Meta:
        proxy =True
    
class CommonPatient(Patient):

    diagnosis=models.TextField(verbose_name='diagnosis',help_text="Patient's medical diagnosis",null=True,blank=True)
    applied_analysis = models.BooleanField(verbose_name='analysis',help_text="Patient's analysis applied checking",null=True, blank=True)

class UrgencyPatient(Patient):
    
    main_syntom = models.CharField(max_length=255,verbose_name='Main synptom',help_text="Patient's main synptom")
    admitted = models.BooleanField(verbose_name='Admitted',help_text="Patient's admitted in the hospital",null=True, blank=True)

    def get_vitalsignals_summary(self):
        return Patient.objects.filter(temperature = self.temperature,pulse = self.pulse, systolic_pressure = self.systolic_pressure,diastolic_pressure = self.diastolic_pressure)
        
class Doctor(CustomUser):
    class Meta:
        proxy=True