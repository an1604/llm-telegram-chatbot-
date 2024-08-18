import pywhatkit
from prompts.prompts import get_text_from_file
import os


class WhatsAppBot(object):
    @staticmethod
    def send_text_private_message(phone_number, message):
        pywhatkit.sendwhatmsg_instantly(phone_no=phone_number, message=message)

    @staticmethod
    def send_image_private_message(phone_number, image_path):
        pywhatkit.sendwhats_image(phone_number, image_path)

    @staticmethod
    def send_text_message_to_group(group_id, message):
        sendwhatmsg_to_group_instantly(group_id, message)

    @staticmethod
    def get_message_template(zoom_url, profile_name):
        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.dirname(current_directory) + "\prompts\whatsapp_invitation.txt"
        return get_text_from_file(parent_directory).format(zoom_url=zoom_url, name=profile_name, target='Hemi')
