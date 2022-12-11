""" Main configuration script for pdf_renderer.
"""

import os
import jinja2

DEBUG = os.getenv('PDF_RENDER_DEBUG', '1') == '1'
EXTERNAL_URL = os.getenv('PDF_RENDER_EXTERNAL_URL', 'http://localhost:5000')
IGNORE_SSL_ERRORS = os.getenv('PDF_RENDER_IGNORE_SSL_ERRORS', '0') == '1'

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

ROOT_RESOURCES = os.getenv('PDF_RENDER_ROOT_RESOURCES', 'resources')

MANUSCRIPT_RESOURCES_DIR = os.path.join(ROOT_RESOURCES, 'manuscript_templates')
STAMP_RESOURCES_DIR = os.path.join(ROOT_RESOURCES, 'stamps')

LATEX_JINJA_ENV = jinja2.Environment(
    block_start_string=r'\BLOCK{',
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.BaseLoader
)

LATEX_JINJA_ENV.globals.update(zip=zip)
