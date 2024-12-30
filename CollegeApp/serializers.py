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
            "role",
            "full_name",
            "phone",
            "dob",
            "gender",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        # Handle password
        password = validated_data.pop("password")
        
        # Handle photo (optional)
        # photo = validated_data.pop("photo", None)

        # Create user
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        
        # Set photo if provided
        # if photo:
        #     user.photo = photo
        
        # Save the user
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




class FacultySerializer(BaseUserSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ["department"]

    def create(self, validated_data):
        user = super().create(validated_data)  # Create the CustomUser
        # No need to pop() department, it's now a ForeignKey on CustomUser
        Faculty.objects.create(user=user, department=validated_data['department'])
        return user


class StudentSerializer(BaseUserSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all())

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ["department", "course", "batch"]

    def create(self, validated_data):
        user = super().create(validated_data)  # Create the CustomUser
        # No need to pop() department, course, and batch, they are ForeignKeys on CustomUser
        Student.objects.create(user=user, department=validated_data['department'], course=validated_data['course'], batch=validated_data['batch'])
        return user

    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','role','is_active','date_joined']





    


