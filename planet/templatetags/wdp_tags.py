from django import template 

register = template.Library()
'''Used to register custom template filters into.'''

@register.filter(name='star_rating') 
def star_rating(rating: int) -> str:
    '''A custom template filter used to render a value 0-5 to a star rating string.'''
    if rating == 0:
        return 'No rating'
    elif rating > 5:
        return 'Invalid rating'
    else:
        return f'{"🟊" * rating}{"☆" * (5 - rating)}'