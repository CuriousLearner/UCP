from rest_framework import serializers
from .models import User, GENDER_CHOICES, USER_TYPE, Address
from django.contrib.auth.models import Group
from UCP.settings import UNIVERSITY_DOMAIN


class GroupSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('name', 'id')

    def validate(self, value):
        return value


class AddSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ('id', 'line1', 'line2', 'city', 'state', 'zipcode')
        readonlyfields = ('id',)

    def create(self, validated_data):

        ud = Address(**validated_data)
        ud.save()
        return ud


class UserSerializer(serializers.ModelSerializer):
    address = AddSerializer(many=False)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',
                  'age', 'gender', 'address', 'phone',
                  'is_staff', 'is_active', 'groups', 'password')
        depth = 1
        readonlyfields = ('id', 'groups')
        write_only_fields = ('password',)

    def create(self, validated_data):

        address_data = validated_data.pop("address")
        ud = User(**validated_data)
        add = Address(**address_data)
        add.save()
        ud.address = add
        ud.set_password(validated_data["password"])
        email = validated_data.pop("email")
        domain = email.split('@')[-1]
        if domain != UNIVERSITY_DOMAIN:
            ud.is_active = False
        else:
            ud.is_active = True
        ud.add_to_group('STUDENT')
        ud.save()
        return ud

class OwnerSerializer(serializers.ModelSerializer):

    address = AddSerializer(many=False)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',
                   'age', 'address', 'groups')
        depth = 1
        readonlyfields = ('id', 'groups')
        write_only_fields = ('password',)


    def create(self, validated_data):
        address_data = validated_data.pop('address')
        ud = User(**validated_data)
        ud.is_active = True
        add = Address(**address_data)
        add.save()
        ud.address = add
        ud.save()
        ud.add_to_group('OWNER')
        ud.save()
        return ud

