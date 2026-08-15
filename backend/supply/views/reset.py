from django.core.management import call_command
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def reset(request):
    call_command("seed_demo")
    return Response({"success": True})
