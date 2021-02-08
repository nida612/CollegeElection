# Create your models here.
from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class MyAccountManager(BaseUserManager):
    def create_user(self, user_id, is_student=True, is_staff=False, password=None):
        if not user_id:
            raise ValueError('Users must have a userID')

        user = self.model(
            user_id=user_id,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, is_student=False, is_staff=False,password=None):
        user = self.create_user(
            user_id=user_id,
            password=password,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    user_id = models.CharField(verbose_name="user_id", unique=True, primary_key=True, max_length=10)
    name = models.CharField(max_length=30)
    image_url = models.CharField(blank=True, null=True, max_length=1000)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['is_student', 'is_staff']

    objects = MyAccountManager()

    def __str__(self):
        return str(self.user_id)

    # For checking permissions. to keep it simple all staff have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_staff

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True


class Student(models.Model):
    user = models.OneToOneField(Account,primary_key=True,on_delete=models.CASCADE)

    class Meta:
        db_table = 'student'


class Staff(models.Model):
    user = models.OneToOneField(Account, primary_key=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'staff'


class Election(models.Model):
    election_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    voting_start = models.DateField()
    voting_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def status(cls):
        IST = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz=IST)
        voting_start = datetime.combine(cls.voting_start, datetime.min.time()).astimezone(IST) + timedelta(
            hours=-5, minutes=-30)
        voting_end = datetime.combine(cls.voting_end, datetime.min.time()).astimezone(IST) + timedelta(hours=-5,
                                                                                                            minutes=-30)

        if now >= cls.created_at and now < voting_start:
            return 'Registration Open'
        elif now >= voting_start and now < voting_end:
            return 'Voting Live'
        else:
            return 'Archived'
    class Meta:
        db_table = 'election'


class Position(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    class Meta:
        db_table = 'position'
        unique_together = (('election', 'title'),)


class Candidate(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status_choices = [
        ('Waiting', 'Waiting'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Waiting')

    class Meta:
        db_table = 'candidate'
        unique_together = (('position', 'student'),)


class Vote(models.Model):
    voter = models.ForeignKey(Student, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    class Meta:
        db_table = 'vote'
        unique_together = (('voter', 'candidate'),)
