"""Main routes of PDF Render app
"""
import urllib.request
import ssl

import prometheus_client
import latex

from flask import Flask, request, render_template, make_response, Response
from flask_cors import cross_origin

from pdf_render import settings
from pdf_render.models import ManuscriptTemplate
from pdf_render.models import Stamp
from pdf_render.services import parser
from pdf_render.services import render


def create_app():
    """Overrides the default app in order to create singleton data.
    """
    flask_app = Flask(__name__)

    flask_app.config['DOC_TEMPLATES'] = ManuscriptTemplate.get_all()

    return flask_app


app = create_app()


@app.route("/", methods=['GET'])
def index():
    """
    Index page
    """
    return render_template(
        "index.html",
        doc_templates=app.config['DOC_TEMPLATES']
    )


@app.route("/form/<label>", methods=['GET', 'POST'])
def template_form(label):
    """
    Sample form for generating the pdf based on templates.
    """
    return render_template(
        "form.html",
        label=label,
        doc_template=app.config['DOC_TEMPLATES'][label]
    )


@app.route("/render/<label>", methods=['GET', 'POST'])
@cross_origin()
def render_pdf(label):
    """
    End point for pdf rendering.
    """
    template = app.config['DOC_TEMPLATES'][label]

    params = parser.parse_request(request, template)

    try:
        pdf_bytes = render.compile_document(template, params)

        response = make_response(pdf_bytes)
        response.headers[
            'Content-Type'
        ] = 'application/pdf'
        response.headers[
            'Content-Disposition'
        ] = 'inline; filename=%s.pdf' % 'documento'

        return response

    except latex.LatexBuildError as errexp:
        return str(errexp).replace('\n', '<BR>'), 500


@app.route("/stamp/", methods=['GET', 'POST'])
@cross_origin()
def stamp_pdf():
    """
    Adiciona um carimbo em um pdf
    """
    if request.method == 'GET':
        pdf_url = request.args.get('pdf')
        carimbos = request.args.getlist('carimbo')
    else:
        pdf_url = request.form.get('pdf')
        carimbos = request.form.getlist('carimbo')

    ctx = ssl.create_default_context()

    if settings.IGNORE_SSL_ERRORS:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(pdf_url, context=ctx) as url:
        pdf_bytes = url.read()

    for carimbo in carimbos:
        if not carimbo.strip():
            continue
        pdf_bytes = Stamp(carimbo).apply_stamp(pdf_bytes)

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'documento'

    return response


@app.route('/metrics/')
def metrics():
    """
    Endpoint for prometheus monitoring
    """
    return Response(
        prometheus_client.generate_latest(),
        mimetype='text/plain; version=0.0.4; charset=utf-8'
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=settings.DEBUG)
