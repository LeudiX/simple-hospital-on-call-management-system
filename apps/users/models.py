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
    Create and save a user with the given email and password.
    """
    def create_user(self, email, password,**extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    """
    Create and save a SuperUser with the given email and password ensuring
    access to Django admin interface
    """

    def create_superuser(self, email, password,**extra_fields):
        
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')
        
        return self.create_user(email, password, **extra_fields)
    
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
     
    SEX_FEMALE = 'Female'
    SEX_MALE = 'Male'
    SEX_UNSURE = 'Unsure'
     
    GENDER_CHOICES=(
        (SEX_MALE,'Male'),
        (SEX_FEMALE,'Female'),
        (SEX_UNSURE,'Unsure')
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
    
    birthdate = models.DateField(verbose_name='birthdate',help_text='Select your birth date',null=True,blank=True)
    gender = models.CharField(verbose_name='gender',max_length=20, choices=GENDER_CHOICES, help_text='Select your gender')
     
    """_Role based authorization purposes_
    """
    def is_patient(self):
        return self.user_type =='patient'
    
    def is_doctor(self):
        return self.user_type == 'doctor'
    
    def __str__(self):
        return f"Name: {self.first_name} {self.last_name} ({self.user_type})"
    
    """Calculate the age of the user in years."""
    def get_age(self):
        age=datetime.date.today()-self.birthdate 
        return int((age).days/365.25)
    
    """Check if the user's age is within human standards (18-120 years)."""
    def is_age_valid(self):
        age = self.get_age()
        return 0<= age <=120
    
    objects=CustomUserManager()

"""_Using Multi-table Inheritance and Proxy Models for handle the complex User Data Model and enhance future mantainment and scalability_"""

# Patient Class
class Patient(models.Model):
        
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=125,help_text='Your address info')
    medical_history = models.TextField()
    
    # Used by Django Admin when registered the Patient model
    # Used by Django forms when accessing objets of this type
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    """
    # Checking patient's profile completitud
    def is_profile_complete(self):
        return bool(self.temperature and self.pulse and self.systolic_pressure and self.diastolic_pressure)  
    """
    
    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        
    def save(self, *args, **kwargs):
        print(f"Saving Patient: {self.user.first_name}")
        super(Patient, self).save(*args, **kwargs)
        
# Doctor Class        
class Doctor(models.Model):
    
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
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    specialty = models.CharField(max_length=100,verbose_name='Specialty',help_text="Doctor's specialty", choices=SPECIALTIES)
    experience = models.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(50)],
        verbose_name="Experience",
        help_text="Doctor's Years of Experience",
        null=True,
        blank=True)
    
    # Used by Django Admin when registered this model
    # Used by Django forms when accessing objects of this type
    def __str__(self):
        return f"Dr.{self.user.first_name} {self.user.last_name} "
    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
    
    # Checking doctor's profile completitud
    def is_profile_complete(self):
        return bool(self.specialty and self.experience)   
    
    def save(self, *args, **kwargs):
        print(f"Saving Doctor: {self.user.first_name}, Specialty:{self.specialty},  Experience: {self.experience}")
        super(Doctor, self).save(*args, **kwargs)
      
