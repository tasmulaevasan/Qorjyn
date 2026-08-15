from rest_framework import serializers

from businesses.models import Business, Location


class LocationSerializer(serializers.ModelSerializer):
    coordinates = serializers.ReadOnlyField()

    class Meta:
        model = Location
        fields = ["id", "business_id", "name", "address", "coordinates"]


class BusinessSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        fields = [
            "id", "name", "type", "district", "phone", "contact_name",
            "logo_emoji", "allow_surplus_sharing", "favorite_tools", "locations",
        ]
