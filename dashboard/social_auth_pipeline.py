from dashboard.models import Customer, Employee

import stripe
from tribarbDesktop.settings import STRIPE_API_KEY
stripe.api_key = STRIPE_API_KEY

def create_user_by_type(backend, user, request, response, *args, **kwargs):
    request = backend.strategy.request_data()

    if backend.name == 'facebook':
        avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']
        email = response['email']

    if request['user_type'] == "employee" and not Employee.objects.filter(user_id=user.id):
    	Employee.objects.create(user_id=user.id, avatar=avatar, email=email)

    elif not Customer.objects.filter(user_id=user.id):
        customer = stripe.Customer.create(email = email, name = response['name'])
        Customer.objects.create(user_id=user.id, avatar=avatar, email=email, stripe_id=customer['id'])