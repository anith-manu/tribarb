from dashboard.models import Customer, Employee

def create_user_by_type(backend, user, request, response, *args, **kwargs):
    request = backend.strategy.request_data()
    if backend.name == 'facebook':
        avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']

    if request['user_type'] == "employee" and not Employee.objects.filter(user_id=user.id):
    	Employee.objects.create(user_id=user.id, avatar=avatar)

    elif not Customer.objects.filter(user_id=user.id):
    	Customer.objects.create(user_id=user.id, avatar=avatar)
