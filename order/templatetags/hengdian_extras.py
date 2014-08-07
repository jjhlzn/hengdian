from django import template
from django.core.paginator import Paginator


register = template.Library()

def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
    page = context['page']
    page_no = page.number
    pages = page.paginator.num_pages
    page_numbers = [n for n in \
                    range(page_no - adjacent_pages, page_no + adjacent_pages + 1) \
                    if n > 0 and n <= pages]
    #print "page_numbers: "+str(page_numbers) + "!!!!!!!!!!!!!"
    return {
        #'hits': context['hits'],
        #'results_per_page': context['results_per_page'],
        'page': page_no,
        'pages': pages,
        'total_records': page.paginator.count,
        'page_numbers': page_numbers,
        'next':page_no + 1,
        'previous': page_no - 1,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'show_first': 1 not in page_numbers,
        'show_last': pages not in page_numbers,
        'search_params': context['search_params'],
    }

register.inclusion_tag('order/paginator.html', takes_context=True)(paginator)
