from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_field):
        # Creates and saves a new user
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email)  , **extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password):
        # create and saves a new super user
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    # Custom user model that suppors using email instead of username
    email = models.EmailField(max_length=255,unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class Tag(models.Model):
    # tag to be used for a recipe
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    # Ingredient to be used in a recipe
    name = models.CharField(max_length = 255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE
    )
    # 這裡 on_delete 的 models.CASCADE 的意思 
    # 例如： 一個攤販會賣各式各樣的食物，當它今天收店了，你就也再也吃不到它賣的每一樣食物了 
    # 這些連帶的資料也會一併刪除

    def __str__(self):
        return self.name

class Recipe(models.Model):
    # Recipe object
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    link = models.CharField(max_length=255,blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags= models.ManyToManyField('Tag')

    def __str__(self):
        return self.title
