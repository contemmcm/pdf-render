\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{apostila}[2021/02/12 Template Apostila]

\LoadClass{article}
\RequirePackage{fabdoc}

\newcommand*{\header}{
(Fl \thepage /\zpageref{LastPage} da Apostila - \fromorganizationunitacronym, de \setsepchar{ }\readlist\mydate{\docdate}\mydate[1] \expandafter\MakeUppercase\expandafter {\substring{\mydate[3]}{1}{3}} \mydate[5])
}

\lhead{\header}

\newenvironment{apostila}
{
\thispagestyle{empty}


% Timbre 5
\timbreCinco


% Cabeçalho
\vspace{20pt}
\centralizado{\textbf{A P O S T I L A}}


% Corpo do texto
\textoIndentado

}
{

\assinaturaComData

}
