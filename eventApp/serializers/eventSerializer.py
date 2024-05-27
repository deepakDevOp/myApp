from rest_framework import serializers
from eventApp.models import Event
from .validators import EventValidatorMixin
from eventApp.utils import upload_image_to_s3,delete_image_s3


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class GetEventSerializer(EventValidatorMixin, serializers.Serializer):
    eventid = serializers.CharField()


class CreateEventSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_name = serializers.CharField()

    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {'pic': {'write_only': True}}


class UpdateEventSerializer(EventValidatorMixin, serializers.ModelSerializer):
    eventid = serializers.CharField()
    pic = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=True
    )

    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {'pic': {'write_only': True}}

    def update(self, instance, validated_data):
        request = self.context.get('request')
        pictures = request.FILES.getlist("pic", None)
        updated_image_urls = instance.image_urls
        for image in pictures:
            eventid = validated_data.get("eventid")
            image_url, file_name = upload_image_to_s3(image_data=image, event_id=eventid)
            image_data = {"image_id": file_name,
                          "image_url": image_url}
            updated_image_urls.append(image_data)
        remove_ids = request.GET.get("remove_ids", None)
        if remove_ids:
            remove_ids = remove_ids.split(",")
            delete_image_s3(remove_ids=remove_ids, eventid=request.data.get("eventid"))
            for image_id in remove_ids:
                for img_obj_index in range(len(updated_image_urls)):
                    if image_id in updated_image_urls[img_obj_index].values():
                        del updated_image_urls[img_obj_index]
                        break
        # Update the remaining fields
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the instance
        instance.image_urls = updated_image_urls
        instance.save()
        return instance


class DeleteEventSerializer(EventValidatorMixin, serializers.Serializer):
    eventid = serializers.CharField()
