"""Functions for converting form inputs into a pretty pdf file.
"""
import os
import re
import ssl
import urllib.request
import tempfile

import latex

from pdf_render.models import Stamp
from pdf_render import settings


def compile_document(template, params):
    """
    Applies parameters to the template and generate a PDF file
    """

    # Applies the template and generate LaTeX source
    with open(template['baseLatex']) as fin:
        latex_source = render_latex(
            params, tex_base=fin.read()
        )

    # Compile the LaTeX source with PDFLatex
    pdf_bytes = render_pdf(
        latex_source, template
    )

    # Apply additional stamps to the generated PDF
    if 'carimbo' in params:
        for carimbo in params['carimbo']:
            if not carimbo.strip():
                continue
            pdf_bytes = Stamp(carimbo).apply_stamp(pdf_bytes)

    return pdf_bytes


def render_pdf(tex_content, template):
    """
    Assembles the source latex, apply the parameters using jinja2,
    download all images and generates the PDF using pdflatex.
    """
    base_path = template.get('basePath')
    root_path = template.get('rootPath')

    tempdir = tempfile.mkdtemp()

    tex_content = download_document_images(tex_content, tempdir)

    return latex.build_pdf(
        tex_content, texinputs=[base_path, root_path, tempdir]
    ).data


def render_latex(params, tex_base):
    """
    Preenche as variáveis no template LaTeX
    """
    tex_content = settings.LATEX_JINJA_ENV.from_string(tex_base).render(params)

    # Hack: corrigindo numeração dos parágrafos depois das listas
    tex_content = tex_content.replace(
        '\\end{enumerate}', '\\end{enumerate}\r\n\r\n \\everypar{\\p}'
    )
    tex_content = tex_content.replace(
        '\\end{itemize}', '\\end{itemize}\r\n\r\n \\everypar{\\p}'
    )

    return tex_content


def download_document_images(tex_content, tempdir):
    """
    Faz o download das imagens e retorna o diretório onde foram baixadas,
    bem como o 'tex_content' alterado (sem URLs nas referencias a imagens)
    """
    regex = r'\\includegraphics(\[.+\])?\{(https?:\/\/[-a-zA-Z0-9@:%._\+~#=\/]{1,256})\}+'

    if settings.IGNORE_SSL_ERRORS:
        # pylint: disable=protected-access
        ssl._create_default_https_context = ssl._create_unverified_context

    for match in re.finditer(regex, tex_content):
        img_url = match.group(2)
        fname = img_url.split('/')[-1]

        urllib.request.urlretrieve(img_url, os.path.join(tempdir, fname))

        tex_content = tex_content.replace(
            str(match.group()),
            str(match.group()).replace(img_url, fname)
        )

    return tex_content
