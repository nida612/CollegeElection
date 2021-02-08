import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'election.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
import django
from college_election.models import *
import names
django.setup()


# write script
def populate(n):
    for i in range(1, n + 1):
        user = Account()
        user.user_id = 'MS1835-'+str(i)
        user.set_password("password")
        user.name = names.get_full_name(gender='female')
        user.is_student = True
        user.save()
        stud = Student()
        stud.user = user
        stud.save()
    user = Account()
    user.user_id = 'don'
    user.set_password("don")
    user.name = 'Nida'
    user.is_student = False
    user.is_staff = True
    user.save()
    staff = Staff()
    staff.user = user
    staff.save()


# end script
if __name__ == '__main__':
    populate(11)
