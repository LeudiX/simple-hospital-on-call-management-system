import datetime
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth.models import AbstractUser,BaseUserManager

# Course Notes
"""
This implementation follows best coding practices and SOLID principles:

1-Single Responsibility Principle (SRP): Each class has a single responsibility. The Patient class is responsible for managing vital signs, while the UrgencyPatient class is responsible for registering urgency patients.

2-Open-Closed Principle (OCP): The classes are open for extension (through inheritance) but closed for modification. The UrgencyPatient class extends the Patient class without modifying it.

3-Liskov Substitution Principle (LSP): The UrgencyPatient class can be used as a substitute for the Patient class without affecting the correctness of the program.

4-Interface Segregation Principle (ISP): The classes provide specific interfaces (get_vital_signs() and register()) that are relevant to their respective responsibilities.

5-Dependency Inversion Principle (DIP): The classes depend on abstractions (the Patient class) rather than concrete implementations.
"""


# Custom User Models.
"""_Flexible _ and customizable way of handle user creation"""

# CustomUserManager Class (inherits from BaseUserManager)
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
    
# CustomUser Class (inherits from Abstract User)
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
    
    def __str__(self):
        return f"Name: {self.first_name} {self.last_name} ({self.user_type})"
    
    def greet(self):
        return {GENDER_MALE:'Welcome Mr.{self.username}', GENDER_FEMALE:'Welcome Ms.{self.username}'}[self.gender]
    
    """Calculate the age of the patient in years."""
    def get_age(self):
        age=datetime.date.today()-self.birth_date 
        return int((age).days/365.25)
    
    """Check if the patient's age is within human standards (18-120 years)."""
    def is_age_valid(self):
        age = self.get_age()
        return 0<= age <=120
            
    objects=CustomUserManager()

"""_Using Multi-table Inheritance and Proxy Models for handle the complex User Data Model and enhance future mantainment and scalability_"""

# Patient Class(inherits from CustomUser)
class Patient(CustomUser):
    
    PATIENT_TYPE_CHOICES = (
        ('urgency', 'Urgency'),
        ('common', 'Common'),
    )
    
    patient_type = models.CharField(max_length=50, choices=PATIENT_TYPE_CHOICES)
    
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
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(90),MaxValueValidator(140)],
        null=True,  # Allows the field to be null if blood pressure is unknown
        blank=True,  # Allows the field to be blank in forms
    )
    diastolic_pressure = models.DecimalField(
        verbose_name="Diastolic Blood Pressure",
        help_text="Patient's diastolic blood pressure in mmHg",
         max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(60),MaxValueValidator(90)],
        null=True,  # Allows the field to be null if blood pressure is unknown
        blank=True,  # Allows the field to be blank in forms
    )
      
    """_The constructor of the Patient class initializes the vital sign fields_
    """
    def __init__(self,temperature,pulse,systolic_pressure,diastolic_pressure):
        self.temperature = temperature
        self.pulse = pulse
        self.systolic_pressure = systolic_pressure
        self.diastolic_pressure = diastolic_pressure
    
    """_Returns a summary of the patient's vital signs. This promotes encapsulation by providing a 
        clear interface to access the vital signs_
    """
    def get_vital_signs(self):
        # Returns a summary of the patient's vital signs
        return f"Temperature: {self.temperature}, Pulse: {self.pulse}, Blood Pressure: {self.systolic_pressure}/{self.diastolic_pressure}"
    
    def __str__(self):
        return f"Patient {self.first_name} {self.last_name} ({self.patient_type})"
    
    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        

# CommonPatient Class(inherits from Patient)    
class CommonPatient(Patient):

    NO=0
    YES=1
    
    ANALYSIS_CHOICES=(
        (NO,'No'),
        (YES,'Yes')
    )    
    
    diagnosis=models.CharField(max_length=255,verbose_name='diagnosis',help_text="Patient's medical diagnosis",null=True,blank=True)
    analysis_applied=models.IntegerField(verbose_name='Analysis applied', choices=ANALYSIS_CHOICES, help_text="Patient's required analysis?")
    
    class Meta:
        proxy:True
        
# UrgencyPatient Class (inherits from Patient)                
class UrgencyPatient(Patient):
    
    NO=0
    YES=1
    
    ADMISSION_CHOICES=(
        (NO,'No'),
        (YES,'Yes')
    ) 
    
    main_symptom = models.CharField(max_length=255,verbose_name='Main synptom',help_text="Patient's main symptom")
    admitted =models.IntegerField(verbose_name='Admitted', choices=ADMISSION_CHOICES, help_text="Patient's required admission?")

    class Meta:
        proxy:True
    
    """_constructor of the UrgencyPatient class initializes the vital sign fields inherited from the Patient class
        and adds the main_symptom and admitted fields specific to urgency patients_
    """
    def __init__(self,temperature,pulse,systolic_pressure,diastolic_pressure,main_symptom,admitted):
        super.__init__(temperature,pulse,systolic_pressure,diastolic_pressure) # Calls the constructor of the parent Patient class to initialize the inherited fields
        self.main_symptom = main_symptom
        self.admitted = admitted

    """_Registers the urgency patient with their vital signs, main symptoms, and admission status_.
       _Demonstrates the principle of inheritance and code reuse_
    """
    def register(self):
        # Registers the urgency patient with their vital signs, main symptom, and admission status
        vital_signs = self.get_vital_signs()
        admission_status = "Admitted" if self.admitted else "Not Admitted" # Determines the admission status based on the admitted field using a ternary operator
        return f"Urgency Patient - Main Symptom: {self.main_symptom}, Vital Signs: {vital_signs}, Admission Status: {admission_status}"
        

# Doctor Class (inherits from CustomUser)        
class Doctor(CustomUser):
    
    SPECIALTIES = (
        ('General Practice', 'General Practice'),
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Oncology', 'Oncology'),
        ('Pediatrics', 'Pediatrics'),
        ('Neurology', 'Neurology'),
        ('Orthopedics', 'Orthopedics'),
        ('Psychiatry', 'Psychiatry'),  
        # Add more specialties as needed
    )
    
    specialty = models.CharField(max_length=100,verbose_name='Specialty',help_text="Doctor's specialty", choices=SPECIALTIES)
    experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(50)],
        verbose_name="Experience",
        help_text="Doctor's Years of Experience",)
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} ({self.specialty})"
    
    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"