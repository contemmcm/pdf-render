"""Module with common parsing functions to handle user form inputs
"""
import latex
import pypandoc


def parse_request(request, template):
    """
    Convert the document params from HTTP request into a sanitized dictionary
    """
    params = {}

    fields = [
        field for row in template['formRows'] for field in row.get('fields')
    ]
    fields += [
        field for field in template.get('commonFields')
    ]

    for field in fields:
        if field['fieldType'].endswith('list'):
            params[field['fieldName']] = request.form.getlist(
                field['fieldName']+'[]'
            )
        else:
            params[field['fieldName']] = request.form.get(
                field['fieldName']
            )
        _parser_field(params, field)

    return params


def _parser_field(params, field):

    if params[field['fieldName']] is None:
        params[field['fieldName']] = ''

    if not params[field['fieldName']]:
        return

    if field['fieldType'] in ('text', 'text_autocomplete'):
        if isinstance(params[field['fieldName']], list):
            for _, obj in enumerate(params[field['fieldName']]):
                obj = latex.escape(obj)
        else:
            params[field['fieldName']] = latex.escape(
                params[field['fieldName']]
            )

    if field['fieldType'] == 'textarea':
        params[field['fieldName']] = params[field['fieldName']].replace(
            '\r\n', '\n'
        ).replace(
            '\n', '\\\\'
        )

    if field['fieldType'] in ('signatario', 'signatario_list'):
        params[field['fieldName']] = _parse_signatarios(params, field)

    if field['fieldType'] == 'markdown':
        params[field['fieldName']] = pypandoc.convert_text(
            params[field['fieldName']], format='md', to='latex'
        )

    if field['fieldName'] in ('documentoReferencias', 'documentoAnexos'):
        params[field['fieldName']] = [
            latex.escape(text) for text in params[field['fieldName']]
        ]

    if field['fieldName'] == 'documentoDestinatarios':
        params[field['fieldName']] = _beautify_destinatarios(
            params[field['fieldName']]
        )


def _parse_signatarios(params, field):
    """
    Cria uma linha extra e protege o campo de comandos LaTeX
    """
    field_name = field['fieldName']

    if isinstance(params[field_name], list):
        output = []
        for param in params[field_name]:
            param_clean = param.replace('\r\n', '\n')
            output.append('\\\\'.join([
                latex.escape(line)
                for line in param_clean.splitlines()
            ]))

        return output

    param_clean = params[field_name].replace('\r\n', '\n')
    return '\\\\'.join(
        [
            latex.escape(line)
            for line in param_clean.splitlines()
        ]
    )


def _beautify_destinatarios(destinatarios):
    """
    Transforma
    de:   ['Chefe', 'Diretor', 'Comandante']
    para: ['Chefe;', 'Diretor; e', 'Comandante.']
    """
    n_destinatarios = len(destinatarios)

    if n_destinatarios <= 1:
        return destinatarios

    suffix = [';'] * n_destinatarios

    if n_destinatarios >= 1:
        suffix[-1] = '.'

    if n_destinatarios >= 2:
        suffix[-2] = '; e'

    return [
        w[0] + w[1] for w in tuple(zip(destinatarios, suffix))
    ]
