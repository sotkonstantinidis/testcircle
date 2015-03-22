import magic
import os
import sys
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import ugettext as _
from imagekit import ImageSpec
from imagekit.processors import ResizeToFill
from uuid import uuid4

from questionnaire.models import File


def handle_upload(file):
    """
    The main function to handle an uploaded file. Stores the file and
    creates a database entry for it. If the file is an image, thumbnails
    are created.

    The storage of the file is handled by :func:`store_file`.

    Args:
        ``file`` (django.core.files.uploadedfile.UploadedFile):
        An uploaded file.

    Returns:
        :mod:`questionnaire.models.File`.
    """
    file_uid = store_file(file)
    file_type = file.content_type.split('/')[0]
    thumbnails = {}
    if file_type == 'image':
        thumbnail_formats = settings.UPLOAD_IMAGE_THUMBNAIL_FORMATS
        for format_name, format_settings in thumbnail_formats.items():
            image_generator = Thumbnail(
                source=file,
                dimensions=(format_settings[0], format_settings[1]))
            result = image_generator.generate()
            thumbnails[format_name] = store_file(result.read())
    file_model = File.create_new(
        content_type=file.content_type, size=file.size, thumbnails=thumbnails,
        uuid=file_uid)
    return file_model


def store_file(file):
    """
    This function handles the actual storage of an uploaded file after
    checking it.

    Args:
        ``file`` (django.core.files.uploadedfile.UploadedFile or
        Buffer).

    Returns:
        ``str``. The uuid of stored file.
    """
    if isinstance(file, UploadedFile):
        content_type = file.content_type
        size = file.size
    else:
        content_type = magic.from_buffer(file, mime=True).decode('utf-8')
        size = sys.getsizeof(file)

    file_extension = get_file_extension_by_content_type(content_type)
    if file_extension is None:
        raise Exception(_('Unsupported file type'))

    if size > settings.UPLOAD_MAX_FILE_SIZE:
        raise Exception(_('File is too big'))

    upload_folder = settings.MEDIA_ROOT
    uid = str(uuid4())
    filename = '{}.{}'.format(uid, file_extension)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    upload_path = os.path.join(
        upload_folder, *get_upload_folder_structure(uid))
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    with open(os.path.join(upload_path, filename), 'wb+') as destination:
        if isinstance(file, UploadedFile):
            for chunk in file.chunks():
                destination.write(chunk)
        else:
            destination.write(file)
    return uid


def get_all_file_extensions():
    """
    Return all file extensions which are valid according to the
    setting ``UPLOAD_VALID_FILES``.

    .. seealso::
        Configuration of ``UPLOAD_VALID_FILES`` in
        :doc:`/configuration/settings`

    Returns:
        ``list``. A list of tuples with the content type and extension.
        Example::

          [
            ('image/jpeg', 'jpg'),
            ('application/pdf', 'pdf')
          ]

    Raises:
        ``Exception``. If setting ``UPLOAD_VALID_FILES`` is not set or
        not correctly formatted.
    """
    try:
        valid_files = settings.UPLOAD_VALID_FILES
        ret = []
        for content_type, extensions in valid_files.items():
            ret.extend(extensions)
        return ret
    except:
        raise Exception(
            'Setting "UPLOAD_VALID_FILES" is not set or not valid. Please '
            'consult the documentation.')


def get_file_extension_by_content_type(content_type):
    """
    Return the file extension for a given content_type. Based on the
    setting ``UPLOAD_VALID_FILES``.

    .. seealso::
        Configuration of ``UPLOAD_VALID_FILES`` in
        :doc:`/configuration/settings`

    Args:
        ``content_type`` (str): The content type to find the file
        extension for.

    Returns:
        ``str`` or ``None``. The file extension for the given content
        type. ``None`` if the content type was not found.
    """
    file_extension = [
        v[1] for v in get_all_file_extensions() if v[0] == content_type]
    if len(file_extension) != 1:
        return None
    return file_extension[0]


def get_url_by_filename(filename):
    """
    Return the relative URL of a file based on its filename. The URL
    basically indicates the location where the file was stored in the
    upload folder.

    .. important::
        It is not verified if the file at the given location actually
        exists.

    Args:
        ``filename`` (str): The full filename of the file.

    Returns:
        ``str``. The relative URL of the file.
    """
    folder_path = os.path.join(*get_upload_folder_structure(filename))
    return os.path.join(settings.MEDIA_URL, folder_path, filename)


def get_url_by_identifier(uuid, thumbnail=None):
    """
    Return the relative URL of a file based on its identifier. A query
    is made to find the file in the database table, then the file's
    method is used to get its url.

    .. seealso::
        :func:`questionnaire.models.File.get_url`

    Args:
        ``uuid`` (str): The identifier of the file.

    Kwargs:
        ``thumbnail`` (str): The name of the thumbnail for which the URL
        shall be returned.

    Returns:
        ``str`` or ``None``. The relative URL of the file or ``None`` if
        the file was not found.
    """
    try:
        file = File.objects.get(uuid=uuid)
    except File.DoesNotExist:
        return None
    return file.get_url(thumbnail=thumbnail)


def get_thumbnail_format_by_name(name):
    """
    Return a thumbnail format based on its name as specified in the
    setting ``UPLOAD_IMAGE_THUMBNAIL_FORMATS``. If the name was not
    found, dimensions (0, 0) are returned.

    Args:
        ``name`` (str): The name of the thumbnail format.

    Returns:
        ``tuple``. A tuple of two integers (width, height), representing
        the dimensions of the thumbnail.
    """
    return settings.UPLOAD_IMAGE_THUMBNAIL_FORMATS.get(name, (0, 0))


def get_upload_folder_structure(filename):
    """
    Return the structure in the upload folder used for storing and
    retrieving uploaded files.

    Two folder levels are created based on the filename (UUID). The
    first level consists of the first two characters, the second level
    consists of the third character of the uuid.

    Example: ``9cd7b281-2c70-42eb-86ec-e29fc755cc1e.jpg`` is stored to
    ``9c/d/9cd7b281-2c70-42eb-86ec-e29fc755cc1e.jpg``.

    Args:
        ``filename`` (str): The name of the file.

    Returns:
        ``tuple`` or ``None``. A tuple of the folders or none if there
        was a problem with the filename.
    """
    try:
        return filename[0:2], filename[2:3]
    except:
        return None


class Thumbnail(ImageSpec):
    """
    This is the class used for creating thumbnails of uploaded images.
    The dimensions of the thumbnails are passed as constructor
    arguments.

    .. important::
        The thumbnails are always stored as JPEG files with the
        extension ``.jpg``.
    """
    format = 'JPEG'
    options = {'quality': 60}

    def __init__(self, source=None, dimensions=(0, 0)):
        self.processors = [ResizeToFill(dimensions[0], dimensions[1])]
        super(Thumbnail, self).__init__(source)
