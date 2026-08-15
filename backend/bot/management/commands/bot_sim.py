from django.core.management.base import BaseCommand

from bot.services.dialog import handle_message

DEFAULT_CHAT = "77011234567@c.us"


class Command(BaseCommand):
    help = "Прогоняет реплику через диалог бота без поднятия ngrok."

    def add_arguments(self, parser):
        parser.add_argument("text", type=str)
        parser.add_argument("--chat", type=str, default=DEFAULT_CHAT)
        parser.add_argument(
            "--type", type=str, default="text",
            choices=["text", "image", "audio"],
        )

    def handle(self, *args, **options):
        reply = handle_message(options["chat"], options["type"], options["text"])
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(reply))
        self.stdout.write("")
