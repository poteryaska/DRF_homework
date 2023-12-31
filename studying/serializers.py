from datetime import date

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from payments.models import Payment
from payments.services import create_and_save_link_to_pay
from studying.models import Course, Lesson, Subscription
from studying.validators import VideoValidator
from users.serializers import UserSerializer


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [
            VideoValidator(field='video'),
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField(read_only=True)
    subscribed = serializers.SerializerMethodField(read_only=True)
    payment_link = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Course
        fields = "__all__"
        validators = [
            VideoValidator(field='description'),
        ]

    def get_payment_link(self, course):
        user = self.context['request'].user
        current_date = date.today()
        Payment.objects.create(
            user=user,
            date=current_date,
            amount=course.price,
            payment_method='Transfer',
            course_payment_id=course.pk,

        )
        return create_and_save_link_to_pay(course)
    def get_lessons_count(self, instance):
        return instance.lesson.count()

    def get_subscribed(self, instance):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=instance, subscribed=True).exists()
        return False