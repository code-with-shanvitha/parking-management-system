from django.contrib.auth import login
from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.db.models import Q
from django.db.models import Count
from django.contrib import auth
import heapq
# Create your views here.
from .models import *

def loginfrom(req):
    if req.method == "POST":
        username = req.POST.get('username')
        password = req.POST.get('password')
        user = authenticate(req,username=username,password=password)
        if user:
            login(req,user)
            return redirect('dashboard')
        else:
            messages.info(req,'username or password are incorrect')
    return  render(req,'loginpage.html')

# from django.contrib.auth import logout
# from django.http import HttpResponseRedirect
# from django.urls import reverse
@login_required
def logout_view(request):
    logout(request)
    # Redirect to a specific URL after logout
    return  render(request,'loginpage.html')



@login_required
def categorymodule(req):
    data = add_category.objects.all()
    page = Paginator(data, 3)
    page_list = req.GET.get('page')
    page = page.get_page(page_list)
    context = {
        'data': data,
        'page':page,
    }
    return render(req,'categorymodule.html',context)

@login_required
def dashboard(req):
    total_parked_vehicles = add_vehicle.objects.filter(status=True).count()
    total_deported_vehicles = add_vehicle.objects.filter(status=False).count()
    total_available_categories = add_category.objects.filter(status=True).count()
    total_earnings = add_vehicle.objects.filter(status=True).aggregate(Sum('parkingharge'))['parkingharge__sum']
    total_records = add_vehicle.objects.count()
    total_parking_slots = add_category.objects.aggregate(models.Sum('vehiclelimit'))['vehiclelimit__sum']

    context = {
        'total_parked_vehicles': total_parked_vehicles,
        'total_deported_vehicles': total_deported_vehicles,
        'total_available_categories': total_available_categories,
        'total_earnings': total_earnings,
        'total_records': total_records,
        'total_parking_slots': total_parking_slots,

    }
    return  render(req,'dashboard.html',context)

@login_required
def managevehicle(req):
    vehicle = add_vehicle.objects.all()
    paginator = Paginator(vehicle,3)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={
        'page_obj':page_obj,
        'vehicle':vehicle,
    }
    return  render(req,'managevehicles.html',context)

@login_required
def parkingstatus(req):
    data=add_vehicle.objects.all()
    context={
        'data':data,
    }
    return  render(req,'parkingstatus.html',context)
@login_required
def reset(req):
    return  render(req,'reset.html')

@login_required
def vehicleentry(req):
    dataa=add_category.objects.all()
    data2=add_vehicle.objects.all()
    
    vehicle_counts = add_vehicle.objects.values('vehicletype').annotate(vehicle_count=Count('id'))
    
    # Combine vehicle type, limit, and count data
    combined_data = {}
    for category in dataa:
        vehicle_type = category.vehicletype
        vehicle_limit = category.vehiclelimit
        status=category.status
        count = next((item['vehicle_count'] for item in vehicle_counts if item['vehicletype'] == vehicle_type), 0)
        vehicle_left = data2.filter(vehicletype=vehicle_type,status =False).count()
        counts = vehicle_limit-count +vehicle_left
        if  status == True and counts > 0:
            combined_data[vehicle_type] = {'vehiclelimit': vehicle_limit, 'counts': counts}

    paginator = Paginator(data2, 3)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if req.method == "POST":
        a = req.POST.get('vehicleno')
        b = req.POST.get('vehicletype')
        c = add_category.objects.get(pk=req.POST.get('parkingareano'))
        d = req.POST.get('parkingcharge')
        save=add_vehicle(vehicle_no=a,parkingareanumber=c,vehicletype=b,parkingharge=d)
        save.save()
        return redirect('vehicleentry')
    context={
        'dataa':dataa,
        'page_obj':page_obj,
        'data2':data2,
        'combined_data': combined_data,
    }
    return  render(req,'vehicleentry.html',context)

def parked_vehicle(req,id):
    Data =add_vehicle.objects.get(id=id)
    Data.status =False
    Data.save()
    return  redirect('vehicleentry')

def leaved_vehicle(req,id):
    Data = add_vehicle.objects.get(id=id)
    Data.status = True
    Data.save()
    return  redirect('vehicleentry')

@login_required
def add_category1(req):
    data=add_category.objects.all()

    page = Paginator(data, 3)
    page_list = req.GET.get('page')
    page = page.get_page(page_list)

    if req.method == "POST":
        a = req.POST.get("parkingareano")
        b = req.POST.get("vehicletype")
        c = req.POST.get("vehiclelimit")
        d = req.POST.get("parkingcharge")

        save = add_category(parkingareanumber=a,vehicletype=b,vehiclelimit=c,parkingharge=d)
        save.save()
        return redirect('categorymodule')
    context = {
            'data': data,
            'page':page,
        }
    return render(req, 'categorymodule.html', context)


def deletecategory(req, id):
    data = add_category.objects.get(id=id)
    context = {
        'data': data
    }
    return render(req, 'confirm_delete.html', context)

def confirmed_delete(req, id):
    data = add_category.objects.get(id=id)
    data.delete()
    return redirect('addcategory')

def editcategory(req,id):
    data = add_category.objects.get(id=id)
    context={
        'dataa':data,
    }
    return render(req,'editcategory.html',context)

def updatecategory(req,id):
    dataa=add_category.objects.all()

    if req.method == 'POST':
        a = req.POST.get('editvehicleno')
        b = req.POST.get("editvehicletype")
        c = req.POST.get('editvehicleno')
        d = req.POST.get('editvehiclecharge')

        save = add_category(id=id,parkingareanumber=a,vehicletype=b,vehiclelimit=c,parkingharge=d)
        save.save()
        return  redirect('addcategory')
    return render(req,'categorymodule.html')

def active_category(req,id):
    data=add_category.objects.get(id=id)
    data.status=False
    data.save()
    return redirect('addcategory')

def deactive_category(req,id):
    data= add_category.objects.get(id=id)
    data.status=True
    data.save()
    return  redirect('addcategory')


def status_manage_vehicle(request, id):
    vehicle = add_vehicle.objects.get(id=id)
    if vehicle.status:
        vehicle.status = False
    else:
        vehicle.status = True
    vehicle.save()
    return redirect('managevehicle')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def resetpassword(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentpassword')
        new_password = request.POST.get('newpassword')
        reentered_password = request.POST.get('reenterpassword')

        # Validate the form data as needed

        if new_password != reentered_password:
            messages.error(request, "New password and re-entered password do not match.")
            return redirect('reset')  # Assuming 'reset' is the name of your reset password page

        # You may want to validate the current password as well

        # Change the password only if the form is valid
        request.user.set_password(new_password)
        request.user.save()

        messages.success(request, "Password changed successfully.")
        return redirect('reset')  # Redirect to a success page or the reset password page

    return render(request, 'reset.html')  # Assuming 'reset.html' is the template for resetting the password

def categorysearch(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            data = add_category.objects.filter(
                Q(parkingareanumber__icontains=query) |
                Q(vehicletype__icontains=query) |
                Q(vehiclelimit__icontains=query) |
                Q(parkingharge__icontains=query)
            )
            return  render(request,'categorymodule.html',{'data':data})
        else:
            print('no vehicles is heree    ')
            return render(request,'categorymodule.html',)

def vehiclesearch(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            page_obj = add_vehicle.objects.filter(
                Q(parkingareanumber__parkingareanumber__icontains=query) |
                Q(vehicletype__icontains=query) |
                Q(parkingharge__icontains=query)|
                Q(vehicle_no__icontains=query)|
                Q(arrival_time__icontains=query)
            )
            return  render(request,'vehicleentry.html',{'page_obj':page_obj})
        else:
            print('no vehicles is heree ')
            return render(request,'vehicleentry.html',)

def managevehicesearch(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            page_obj = add_vehicle.objects.filter(
                Q(parkingareanumber__parkingareanumber__icontains=query) |
                Q(vehicletype__icontains=query) |
                Q(parkingharge__icontains=query)|
                Q(vehicle_no__icontains=query)|
                Q(arrival_time__icontains=query)
            )
            return  render(request,'managevehicles.html',{'page_obj':page_obj})
        else:
            print('no vehicles is heree ')
            return render(request,'managevehicles.html',)

def parkingsearch(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            data = add_vehicle.objects.filter(
                Q(parkingareanumber__parkingareanumber__icontains=query) |
                Q(vehicletype__icontains=query) |
                Q(parkingharge__icontains=query)|
                Q(vehicle_no__icontains=query)|
                Q(arrival_time__icontains=query)
            )
            return  render(request,'parkingstatus.html',{'data':data})
        else:
            print('no vehicles is heree ')
            return render(request,'parkingstatus.html')

def vehicle_reciept(req,id):
    data=add_vehicle.objects.get(id=id)
    return render(req,'reciept.html',{'data':data})


from django.shortcuts import render
from .models import add_category
import heapq

# Dijkstra's algorithm for shortest path calculation
def dijkstra(graph, start, end):
    heap = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    while heap:
        current_distance, current_node = heapq.heappop(heap)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(heap, (distance, neighbor))
    return distances[end]

# Parking graph (this could be dynamic or fetched from your DB in the future)
def parking_graph():
    categories = add_category.objects.all()
    graph = {}
    for category in categories:
        # Example, dynamically create connections between parking slots
        graph[category.parkingareanumber] = []
        # Example to add some dummy connections with weight (you can adjust this as needed)
        # Assuming you have some way to calculate the weight (distance) between parking areas
        for other_category in categories:
            if category != other_category:
                # Add a connection (for simplicity, we assume all connections have weight 1)
                graph[category.parkingareanumber].append((other_category.parkingareanumber, 1))
    return graph

# New view to calculate the shortest path
def shortest_path_view(request):
    if request.method == 'POST':
        start = request.POST.get('start_slot')
        end = request.POST.get('end_slot')
        graph = parking_graph()
        shortest_distance = dijkstra(graph, start, end)
        return render(request, 'shortest_path_result.html', {'start': start, 'end': end, 'distance': shortest_distance})
    
    # Get all categories for selection in the template
    categories = add_category.objects.all()
    return render(request, 'shortest_path.html', {'categories': categories})

