from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .fill_database import *
from .forms import *


def start_page(request):
    #fill_database_van_character()
    #fill_database_train()
    #fill_database_van()
    return render(request, 'start_page.html')

def login_page(request):
    return HttpResponse('Логин')

def register_page(request):
    return HttpResponse('Регистрация')

class RegisterUserView(CreateView):
    model = User
    template_name = 'register_page.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('create_user')
    success_msg = "Пользователь успешно создан"

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)  # Авторизация пользователя
        return response

class LoginUserView(LoginView):
    template_name = "login_page.html"
    form_class = AuthUserForm
    success_url = reverse_lazy('main_page')
    def get_success_url(self):
        return self.success_url

def create_user(request):
    error = ''
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            created_user = form.save(commit=False)
            created_user.django_user = get_object_or_404(User, id=request.user.id)
            created_user.save()
            return redirect('main_page')
        else:
            error = 'Форма была неверной'
    form = PassengerForm()
    data = {
        'form': form,
        'error': error
    }
    return render(request, 'create_user.html', data)

def main_page(request):
    check_fill_seats()
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    trains = Train.objects.all()
    error = ''
    if request.method == 'POST':
        form = ChildrenAnimalsForm(request.POST)
        if form.is_valid():
            user_obj.trip_with_animals = form.cleaned_data.get('trip_with_animals')
            user_obj.trip_with_child = form.cleaned_data.get('trip_with_child')
            user_obj.save()
            return redirect('main_page')
        else:
            HttpResponse('Где-то накосячили..')
    else:
        form = ChildrenAnimalsForm(instance=user_obj)

    data = {
        "user": user_obj,
        "train": trains,
        "form": form
    }
    return render(request, 'main_page.html', context=data)

def check_fill_seats():
    vans = list(obj for obj in Van.objects.values_list('id', 'train', 'character'))
    seats = list(obj for obj in Seat.objects.values_list('id'))
    if seats == []:
        for j in vans:
            if j[2] == 1:
                for i in range(0,54):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=2800, seat_number=i + 1)
                    seat.save()
            elif j[2] == 2:
                for i in range(0, 54):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=3000, seat_number=i+1)
                    seat.save()
            elif j[2] == 3:
                for i in range(0, 36):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=4000, seat_number=i + 1)
                    seat.save()
            elif j[2] == 4:
                for i in range(0, 36):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=4500, seat_number=i + 1)
                    seat.save()
            elif j[2] == 5:
                for i in range(0, 18):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=5000, seat_number=i + 1)
                    seat.save()
            elif j[2] == 6:
                for i in range(0, 18):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=4800, seat_number=i + 1)
                    seat.save()
            elif j[2] == 7:
                for i in range(0, 12):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=14000, seat_number=i + 1)
                    seat.save()

def route_page(request, pk=''):
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    train = Train.objects.get(id=pk)
    vans = Van.objects.filter(train=train)

    plac = vans.filter(character__in=[1, 2])
    coupe = vans.filter(character__in=[3, 4])
    sv = vans.filter(character__in=[5, 6])
    lux = vans.filter(character=7)
    if list(plac.values_list('id')) == []:
        plac = None
    if list(coupe.values_list('id')) == []:
        coupe = None
    if list(sv.values_list('id')) == []:
        sv = None
    if list(lux.values_list('id')) == []:
        lux = None
    return render(request, 'route_page.html', context={
        'plac': plac,
        'coupe': coupe,
        'sv': sv,
        'lux': lux,
        'train': train,
        'user': user_obj
    })

def van_page(request, pk=''):
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)
    trips = Trip.objects.filter(finished=False)


    van = Van.objects.get(id=pk)
    seat_quantity = van.character.seat_quantity
    seat_list = [0] * seat_quantity
    trip_list = [None] * seat_quantity
    neighbours = [None] * seat_quantity
    seat_numbers = [i + 1 for i in range(0, seat_quantity)]
    ticket_purchased = False

    for s in trips:
        if s.seats.van == van:
            if s.passenger == user_obj:
                ticket_purchased = True
            seat_list[s.seats.seat_number-1] = 1
            neighbours[s.seats.seat_number-1] = s.passenger
            trip_list[s.seats.seat_number-1] = s

    print(neighbours)

    if van.character.class_van <= 2:
        print(seat_numbers)
        seat_top = []
        seat_top_took = []
        seat_bottom = []
        seat_bottom_took = []
        seat_side = []
        seat_side_took = []
        for i in seat_numbers:
            if i % 2 == 0 and i <= 36:
                seat_top.append(i)
                seat_top_took.append(seat_list[i-1])
            elif i % 2 != 0 and i <= 36:
                seat_bottom.append(i)
                seat_bottom_took.append(seat_list[i-1])
            else:
                seat_side.append(i)
                seat_side_took.append(seat_list[i-1])
        print(seat_top_took)
        print(seat_bottom_took)
        print(seat_side_took)
        data = {
            'seat_numbers': zip(seat_numbers, neighbours, trip_list),
            'seat_top': zip(seat_top, seat_top_took),
            'seat_bottom': zip(seat_bottom, seat_bottom_took),
            'seat_side': zip(seat_side[::-1], seat_side_took[::-1]),
            'van': van,
            'van_ch': van.character,
            'price': Seat.objects.filter(van=van)[0].price,
            'user': user_obj,
            'phone_view': ticket_purchased

        }

    elif van.character.class_van <= 4:
        seat_top = []
        seat_top_took = []
        seat_bottom = []
        seat_bottom_took =[]
        for i in seat_numbers:
            if i % 2 == 0:
                seat_top.append(i)
                seat_top_took.append(seat_list[i - 1])
            elif i % 2 != 0:
                seat_bottom.append(i)
                seat_bottom_took.append(seat_list[i - 1])

        data = {
            'seat_numbers': zip(seat_numbers, neighbours, trip_list),
            'seat_top': zip(seat_top, seat_top_took),
            'seat_bottom': zip(seat_bottom, seat_bottom_took),
            'van': van,
            'van_ch': van.character,
            'price': Seat.objects.filter(van=van)[0].price,
            'user': user_obj,
            'phone_view': ticket_purchased
        }
    elif van.character.class_van <= 6:
        data = {
            'seat_numbers': zip(seat_numbers, neighbours, trip_list),
            'seat_bottom': zip(seat_numbers, seat_list),
            'van': van,
            'van_ch': van.character,
            'price': Seat.objects.filter(van=van)[0].price,
            'user': user_obj,
            'phone_view': ticket_purchased
        }
    elif van.character.class_van == 7:
        seat_top = []
        seat_top_took = []
        seat_bottom = []
        seat_bottom_took = []
        for i in seat_numbers:
            if i % 2 == 0:
                seat_top.append(i)
                seat_top_took.append(seat_list[i - 1])
            elif i % 2 != 0:
                seat_bottom.append(i)
                seat_bottom_took.append(seat_list[i - 1])

        data = {
            'seat_numbers': zip(seat_numbers, neighbours, trip_list),
            'seat_top': zip(seat_top, seat_top_took),
            'seat_bottom': zip(seat_bottom, seat_bottom_took),
            'van': van,
            'van_ch': van.character,
            'price': Seat.objects.filter(van=van)[0].price,
            'user': user_obj,
            'phone_view': ticket_purchased
        }


    return render(request, 'van_page.html', context=data)

def buy_ticket(request, tr='', vn='', st=''):
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    van = Van.objects.get(train=tr, id=vn)
    seats = Seat.objects.get(van=van, seat_number=st)
    trip = Trip.objects.create(passenger=user_obj, seats=seats, finished=False, with_children=user_obj.trip_with_child,
                               with_animals=user_obj.trip_with_animals)
    user_obj.trip_with_child = 0
    user_obj.trip_with_animals = False
    user_obj.save()

    trip.save()

    return redirect('van_page', pk=vn)

def reject_ticket(request, tr='', vn='', st='', id=''):
    if id != '':
        Trip.objects.get(id=id).delete()
        return redirect('my_trips')
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    van = Van.objects.get(train=tr, id=vn)
    seats = Seat.objects.get(van=van, seat_number=st)

    Trip.objects.filter(passenger=user_obj, seats=seats, finished=False).delete()
    return redirect('van_page', pk=vn)



def my_trips(request):
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    active_trips = Trip.objects.filter(passenger=user_obj, finished=False)
    finished_trips = Trip.objects.filter(passenger=user_obj, finished=True)
    if list(finished_trips.values_list('id')) == []:
        finished_trips = None
    if list(active_trips.values_list('id')) == []:
        active_trips = None
    data = {
        'active': active_trips,
        'finished': finished_trips
    }
    return render(request, 'my_trips.html', context=data)
