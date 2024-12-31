from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser,HOD,Faculty,Student,Course,Batch,Department


CustomUser = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email","password","role","full_name","phone","dob","gender",]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class HODSerializer(BaseUserSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    courses = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), many=True, required=False)
    batches = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all(), many=True, required=False)
    # faculty = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.all())

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['department', 'courses', 'batches', 'photo']

    def create(self, validated_data):
        # First, handle the CustomUser part (email, password, role, etc.)
        password = validated_data.pop('password')
        # photo = validated_data.pop('photo', None) 

        # Create CustomUser instance
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)

        # Handle photo (if provided)
        # if photo:
        #     user.photo = photo

        # Save the user instance
        user.save()

        # Now handle the HOD-specific fields (department, courses, batches, faculty)
        # Create the HOD instance
        hod = HOD.objects.create(
            user=user,
            department=validated_data['department'],
            # faculty=validated_data['faculty']
        )

        # If courses or batches are provided, add them to the HOD instance
        if 'courses' in validated_data:
            hod.courses.set(validated_data['courses'])
        if 'batches' in validated_data:
            hod.batches.set(validated_data['batches'])

        # Save the HOD instance
        hod.save()

        return user




class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'user', 'name', 'address', 'department', 'courses', 'batches', 'photo']

    def create(self, validated_data):
        department = validated_data.pop('department')  
        user = validated_data.pop('user') 
        user_instance = CustomUser.objects.create(**user)
        user_instance.set_password(user['password'])
        user_instance.save()
        faculty = Faculty.objects.create(user=user_instance, department=department, **validated_data)
        return faculty 
    

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'name', 'department', 'course', 'batch', 'photo', 'address']

    def create(self, validated_data):
        # Extract the department and user field separately
        department = validated_data.pop('department')
        user = validated_data.pop('user')

        # Create the user instance (assumes `create_user` exists for custom user)
        user_instance = CustomUser.objects.create_user(**user)  # Replace with `create_user` if available
        user_instance.set_password(user['password'])
        user_instance.save()

        # Create the student instance and associate it with the created user and department
        student = Student.objects.create(user=user_instance, department=department, **validated_data)
        return student
            




    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','role','is_active','date_joined']





    


