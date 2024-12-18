from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser,HOD,Faculty,Student,Course,Batch,Department


CustomUser = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password",
            "full_name",
            "phone",
            "dob",
            "gender",
            "role"        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class HODSerializer(BaseUserSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ["department"]

    def create(self, validated_data):
        department = validated_data.pop("department")
        user = super().create(validated_data)
        HOD.objects.create(user=user, department=department)
        return user



class FacultySerializer(BaseUserSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ["department"]

    def create(self, validated_data):
        department = validated_data.pop("department")
        user = super().create(validated_data)
        Faculty.objects.create(user=user, department=department)
        return user



class StudentSerializer(BaseUserSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ["department", "course"]

    def create(self, validated_data):
        department = validated_data.pop("department")
        course = validated_data.pop("course")
        user = super().create(validated_data)
        Student.objects.create(user=user, department=department, course=course)
        return user
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','role','is_active','date_joined']





    


