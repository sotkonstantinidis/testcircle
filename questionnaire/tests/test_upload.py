from django.test.utils import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, Mock

from qcat.tests import TestCase
from questionnaire.models import File
from questionnaire.upload import (
    get_all_file_extensions,
    get_file_extension_by_content_type,
    get_thumbnail_format_by_name,
    get_upload_folder_structure,
    get_url_by_filename,
    get_url_by_identifier,
    handle_upload,
    store_file,
)
from questionnaire.tests.test_models import get_valid_file
from questionnaire.tests.test_views import valid_file

TEST_UPLOAD_IMAGE_THUMBNAIL_FORMATS = {
    'header_1': (900, 300),
    'header_2': (200, 100),
}

TEST_UPLOAD_VALID_FILES = {
    'image': (
        ('image/jpeg', 'jpg'),
        ('image/png', 'png'),
    ),
    'document': (
        ('application/pdf', 'pdf'),
    )
}


class HandleUploadTest(TestCase):

    @patch('questionnaire.upload.store_file')
    def test_calls_store_file(self, mock_store_file):
        mock_store_file.return_value = 'foo'
        file = SimpleUploadedFile('img.jpg', open(valid_file, 'rb').read())
        file.content_type = 'text/plain'
        handle_upload(file)
        mock_store_file.assert_called_once_with(file)

    @override_settings(
        UPLOAD_IMAGE_THUMBNAIL_FORMATS=TEST_UPLOAD_IMAGE_THUMBNAIL_FORMATS)
    @patch('questionnaire.upload.store_file')
    def test_calls_store_file_image(self, mock_store_file):
        mock_store_file.return_value = 'foo'
        file = SimpleUploadedFile('img.jpg', open(valid_file, 'rb').read())
        file.content_type = 'image/jpeg'
        handle_upload(file)
        mock_store_file.assert_called_count(3)

    @override_settings(UPLOAD_VALID_FILES=TEST_UPLOAD_VALID_FILES)
    def test_returns_file_model(self):
        file = SimpleUploadedFile('img.png', open(valid_file, 'rb').read())
        file.content_type = 'image/png'
        ret = handle_upload(file)
        self.assertIsInstance(ret, File)


class StoreFileTest(TestCase):

    @patch('questionnaire.upload.magic.from_buffer')
    def test_uses_magic_to_determine_content_type(self, mock_magic):
        file = Mock()
        with self.assertRaises(Exception):
            store_file(file)
        mock_magic.assert_called_once_with(file, mime=True)

    @override_settings(UPLOAD_VALID_FILES=TEST_UPLOAD_VALID_FILES)
    @patch('questionnaire.upload.get_file_extension_by_content_type')
    def test_calls_get_file_extension_by_content_type(self, mock_func):
        file = SimpleUploadedFile('img.png', open(valid_file, 'rb').read())
        file.content_type = 'image/png'
        store_file(file)
        mock_func.assert_called_once_with('image/png')

    @override_settings(UPLOAD_VALID_FILES=TEST_UPLOAD_VALID_FILES)
    def test_raises_exception_if_invalid_file_extension(self):
        file = SimpleUploadedFile('img.png', open(valid_file, 'rb').read())
        file.content_type = 'foo'
        with self.assertRaises(Exception):
            store_file(file)

    @override_settings(UPLOAD_MAX_FILE_SIZE=1)
    @patch('questionnaire.upload.get_file_extension_by_content_type')
    @patch('questionnaire.upload.sys.getsizeof')
    @patch('questionnaire.upload.magic.from_buffer')
    def test_raises_exception_if_file_too_big(
            self, mock_from_buffer, mock_get_size_of, mock_get_file_extension):
        mock_from_buffer.return_value = b''
        mock_get_size_of.return_value = 2
        mock_get_file_extension.return_value = 'some/filetype'
        file = Mock()
        with self.assertRaises(Exception):
            store_file(file)

    def test_returns_str(self):
        file = SimpleUploadedFile('img.png', open(valid_file, 'rb').read())
        file.content_type = 'image/png'
        ret = store_file(file)
        self.assertIsInstance(ret, str)


@override_settings(UPLOAD_VALID_FILES=TEST_UPLOAD_VALID_FILES)
class GetAllFileExtensionsTest(TestCase):

    def test_returns_list(self):
        ext = get_all_file_extensions()
        self.assertIsInstance(ext, list)
        self.assertEqual(len(ext), 3)
        self.assertIn(('image/jpeg', 'jpg'), ext)
        self.assertIn(('image/png', 'png'), ext)
        self.assertIn(('application/pdf', 'pdf'), ext)

    @override_settings(UPLOAD_VALID_FILES=None)
    def test_handles_no_files(self):
        with self.assertRaises(Exception):
            get_all_file_extensions()


@override_settings(UPLOAD_VALID_FILES=TEST_UPLOAD_VALID_FILES)
class GetFileExtensionByContentTypeTest(TestCase):

    def test_returns_file_extension(self):
        ext = get_file_extension_by_content_type('image/png')
        self.assertEqual(ext, 'png')

    def test_returns_None_if_unknown_content_type(self):
        ext = get_file_extension_by_content_type('foo')
        self.assertIsNone(ext)


class GetUrlByFilenameTest(TestCase):

    @patch('questionnaire.upload.get_upload_folder_structure')
    def test_calls_get_upload_folder_structure(self, func):
        func.return_value = 'foo'
        get_url_by_filename('foo.jpg')
        func.assert_called_once_with('foo.jpg')

    @override_settings(MEDIA_URL='/media/')
    @patch('questionnaire.upload.get_upload_folder_structure')
    def test_returns_url(self, mock_get_upload_folder_structure):
        mock_get_upload_folder_structure.return_value = 'a', 'b'
        url = get_url_by_filename('foo.jpg')
        self.assertEqual(url, '/media/a/b/foo.jpg')


class GetUrlByIdentifierTest(TestCase):

    @patch.object(File, 'get_url')
    def test_calls_file_get_url(self, mock_get_url):
        file = get_valid_file()
        get_url_by_identifier(file.uuid, thumbnail='foo')
        mock_get_url.assert_called_once_with(thumbnail='foo')

    def test_returns_none_if_file_not_found(self):
        self.assertIsNone(get_url_by_identifier('foo'))


@override_settings(
    UPLOAD_IMAGE_THUMBNAIL_FORMATS=TEST_UPLOAD_IMAGE_THUMBNAIL_FORMATS)
class GetThumbnailFormatByName(TestCase):

    def test_returns_format(self):
        format = get_thumbnail_format_by_name('header_1')
        self.assertEqual(format, (900, 300))

    def test_returns_zero_if_not_found(self):
        format = get_thumbnail_format_by_name('foo')
        self.assertEqual(format, (0, 0))


class GetUploadFolderStructureTest(TestCase):

    def test_returns_folders(self):
        folders = get_upload_folder_structure('filename')
        self.assertEqual(folders, ('fi', 'l'))

    def test_returns_None_if_exception(self):
        self.assertIsNone(get_upload_folder_structure(None))
