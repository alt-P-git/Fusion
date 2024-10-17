from rest_framework import serializers
from applications.complaint_system.models import StudentComplain
from applications.globals.models import User

class StudentComplainSerializers(serializers.ModelSerializer):

    class Meta:
        model=StudentComplain
        fields=('__all__')


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('__all__')
        