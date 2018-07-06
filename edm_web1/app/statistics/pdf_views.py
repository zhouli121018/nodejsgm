# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import Http404
from wkhtmltopdf.views import PDFTemplateResponse
from app.statistics.utils import caches as statistics_caches
# http://www.cnblogs.com/colder/p/5819197.html

@login_required
def track_task_pdf(request):
    try:
        template='track/track_task_pdf.html'
        context = statistics_caches.track_task_pdf_context(request)
        return PDFTemplateResponse(
            request=request,
            template=template,
            filename=context["filename"],
            context=context,
            show_content_in_browser=False,
            cmd_options={
                'encoding': 'utf8',
                # 'margin-top': 10,
                "zoom":0.7,
                "viewport-size" :"1366 x 800",
                'javascript-delay': 1000,
                'footer-center' :'[page]/[topage]',
                "no-stop-slow-scripts":True,
                'debug-javascript': True,
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'margin-right': '20mm',
                'margin-top': '20mm',
                # 'page-width': '880',
            },
        )
    except BaseException as e:
        raise Http404

@login_required
def mail_statistics_report_pdf(request, task_id):
    context = statistics_caches.mail_statistics_report_pdf_context(request, task_id)
    template='statistics/mail_statistics_report_pdf.html',
    # return render(request, template, context=context)
    return PDFTemplateResponse(
        request=request,
        template=template,
        filename=context["filename"],
        context=context,
        show_content_in_browser=False,
        cmd_options={
            'encoding': 'utf8',
            # 'margin-top': 10,
            "zoom":0.7,
            "viewport-size" :"1366 x 800",
            'javascript-delay':1000,
            'footer-center' :'[page]/[topage]',
            "no-stop-slow-scripts":True,
            'debug-javascript': True,
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'margin-right': '20mm',
            'margin-top': '20mm',
            'page-width': '880',
        },
    )
