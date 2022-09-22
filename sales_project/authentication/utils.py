import re
import random
import requests
import string
import json
import base64, uuid, six
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from datetime import datetime
from decouple import config


class CustomPagination(PageNumberPagination):
    page_size_query_params = 'limit'
    page_query_params = 'offset'

def validate_phone(value):
    pattern = re.compile(r'^\+?1?\d{9,15}$')
    if not bool(pattern.match(value)):
        raise ValidationError(
            _("Invalid! Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."),
            params={'value': value},)


def get_random_string(length):
    # choose from all letter and digits
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters)
 for i in range(length))
    return result_str


def custom_normalize_email(email):
    return email.strip().lower()


# This class returns the string needed to generate the key
class generateKey:
    @staticmethod
    def returnValue(phone):
        return f'{phone}{datetime.date(datetime.now())}{settings.SECRET_KEY}'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')
            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except:
            # except TypeError:
                self.fail('invalid_image')
            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)
    def get_file_extension(self, file_name, decoded_file):
        import imghdr
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension