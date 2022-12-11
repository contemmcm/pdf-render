"""Module for handling aditional stamps to a document.
"""
import os
import json
import io

import PyPDF2

from pdf_render import settings


class Stamp:
    """Represents a stamp from resources directory.
    """

    def __init__(self, manifest_id):
        self._load_manifest(manifest_id)

    def get_id(self):
        """Returns the ID of a stamp
        """
        return self.manifest_id

    def get_manifest(self):
        """Returns a COPY of the manifest
        """
        return dict(self.manifest)

    def apply_stamp(self, pdf_bytes):
        """Applies the current stamp to a PDF document
        """
        # Download do arquivo PDF contendo o carimbo
        with open(self.manifest.get('attachment'), 'rb') as fin:
            carimbo_pdf = PyPDF2.PdfFileReader(io.BytesIO(fin.read()))

        input_pdf = PyPDF2.PdfFileReader(io.BytesIO(pdf_bytes))
        output_pdf = PyPDF2.PdfFileWriter()

        if self.manifest['pages'] == 'first_only':
            first_page = input_pdf.getPage(0)
            first_page.mergePage(carimbo_pdf.getPage(0))
            output_pdf.addPage(first_page)

            for i in range(1, input_pdf.getNumPages()):
                output_pdf.addPage(input_pdf.getPage(i))

        elif self.manifest['pages'] == 'all':
            watermark_page = carimbo_pdf.getPage(0)

            for i in range(input_pdf.getNumPages()):
                pdf_page = input_pdf.getPage(i)
                pdf_page.mergePage(watermark_page)
                output_pdf.addPage(pdf_page)

        in_memory = io.BytesIO()
        output_pdf.write(in_memory)

        in_memory.seek(0)
        return in_memory.read()

    def _load_manifest(self, manifest_id):
        self.manifest_root_path = os.path.join(
            settings.STAMP_RESOURCES_DIR, manifest_id
        )
        self.manifest_path = os.path.join(
            self.manifest_root_path, 'manifest.json'
        )
        self.manifest_id = manifest_id

        with open(self.manifest_path, 'r') as fin:
            self.manifest = json.loads(fin.read())
            self.manifest['attachment'] = os.path.join(
                self.manifest_root_path, 'stamp.pdf'
            )

    @staticmethod
    def get_all():
        """Lists all stamps loaded from the resources directory
        """
        stamps = {}

        for path, _, files in os.walk(settings.STAMP_RESOURCES_DIR):
            for name in files:
                if name != 'manifest.json':
                    continue

                stamp = Stamp(os.path.basename(path))
                stamps.update({
                    stamp.get_id(): stamp.get_manifest()
                })

        return stamps
