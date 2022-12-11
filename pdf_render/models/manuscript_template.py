"""Module for handling manuscript templates.
"""
import os
import json

from pdf_render import settings


MANUSCRIPT_MANIFEST_FNAME = 'manuscript.json'
COMMON_FIELDS_FNAME = 'common-fields.json'


class ManuscriptTemplate:
    """Stores the manifest of a manuscript template.
    """

    def __init__(self, path):
        self._load_label(path)
        self._load_manuscript(path)
        self._load_common_fields(path)

    def _load_label(self, path):
        self.label = os.path.basename(path)

    def _load_manuscript(self, path):
        with open(os.path.join(path, MANUSCRIPT_MANIFEST_FNAME)) as fin:
            self.manuscript = json.loads(fin.read())

        self.manuscript['basePath'] = os.path.abspath(path)
        self.manuscript['rootPath'] = os.path.abspath(os.path.dirname(path))
        self.manuscript['baseLatex'] = os.path.join(path, 'base.tex')

    def _load_common_fields(self, path):
        common_fpath = os.path.join(
            os.path.dirname(path), COMMON_FIELDS_FNAME
        )

        if os.path.exists(common_fpath):
            with open(common_fpath) as fin:
                self.common_fields = json.loads(fin.read())

    def get_manifest(self):
        """Returns the template manifest as dict
        """
        manifest = dict(self.manuscript)

        if self.common_fields:
            manifest['commonFields'] = list(self.common_fields)

        return manifest

    def get_label(self):
        """Returns the label (ID) of the template
        """
        return self.label

    @staticmethod
    def get_all():
        """Lists all templates from resources directory.
        """
        templates = {}

        for path, _, files in os.walk(settings.MANUSCRIPT_RESOURCES_DIR):
            for name in files:
                if name != MANUSCRIPT_MANIFEST_FNAME:
                    continue

                manuscript = ManuscriptTemplate(path)

                templates.update({
                    manuscript.get_label(): manuscript.get_manifest()
                })

        return templates
