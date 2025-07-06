from django.shortcuts import render, redirect
from profiles.models import *
from django.core.exceptions import ObjectDoesNotExist       
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
from django.contrib import messages
import folium
from folium import plugins
from folium.plugins import MeasureControl, LocateControl
from bleak import BleakScanner
from math import radians, cos, sin, asin, sqrt
from django.utils.timezone import now
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime, time
from django.utils.timezone import now, is_naive, make_aware
from decimal import Decimal




# Create your views here.
def menu(request):
    if request.user.first_name == 'lecturer': 
        lecturer_profile = None
        location_class = None

        num_students_attending = int(RegisteredClass.objects.filter(lecturer=request.user).count())
        students_attending = RegisteredClass.objects.filter(lecturer=request.user)
        students8 = StudentProfile.objects.all()
        my_students = MyClasses.objects.filter(lecturer=request.user.username)

        try:
            lecturer_profile = LecturerProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            lecturer_profile = None
        except Exception as e:
            lecturer_profile = None

        try:
            location_class = LocationClass.objects.get(lecturer=request.user)
        except ObjectDoesNotExist:
            location_class = None
        except Exception as e:
            location_class = None

        data = [[obj.latitude, obj.longitude, obj.lecturer] for obj in LocationClass.objects.filter(lecturer=request.user)]
        maps = {}
        for obj in LocationClass.objects.all():
            map1 = folium.Map(location=[obj.latitude, obj.longitude], tiles='OpenStreetMap', zoom_start=12, min_zoom=2, max_zoom=18)
            plugins.Fullscreen(position='topright').add_to(map1)
            LocateControl().add_to(map1)
            for dt in data:
                folium.Marker([dt[0], dt[1]]).add_to(map1)
                map_html = map1._repr_html_()
                maps[obj.lecturer] = map_html

        context = {
            'lecturer_profile': lecturer_profile,
            'location_class': location_class,
            'maps': maps,
            'selected_class': request.user,
            'students_attending': students_attending,
            'num_students_attending': num_students_attending,
            'students8': students8,
            'my_students': my_students,
        }
        return render(request, 'dashboard/menu.html', context)
    else:
        classes = LocationClass.objects.all()
        my_classes = MyClasses.objects.filter(student=request.user.username)
        try:
            student_profile = StudentProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            student_profile = None
        except Exception as e:
            student_profile = None
        
        context = {
            'student_profile': student_profile,
            'classes': classes,
            'my_classes': my_classes,
        }
        return render(request, 'dashboard/menu.html', context)
    

@csrf_exempt
def save_class_location(request):
    RegisteredClass.objects.filter(lecturer=request.user.username).delete()
    if request.method == 'POST':
        print("Request received")
        try:
            data = json.loads(request.body)
            class_name = data.get('class_name')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            venue = data.get('venue')

            print("Data received:", class_name, latitude, longitude)

            if LecturerProfile.objects.filter(user=request.user).exists():
                lecturer_profile = LecturerProfile.objects.get(user=request.user)
                # Save to the database
                if LocationClass.objects.filter(lecturer=request.user, status='ON').exists():
                    messages.error(request, 'You already have a class in progress. Please end it before starting a new one.')
                    return JsonResponse({'success': False, 'message': 'You already have a class in progress. Please end it before starting a new one.'})
                elif LocationClass.objects.filter(lecturer=request.user, status='OFF').exists():
                    location_class = LocationClass.objects.get(lecturer=request.user)
                    location_class.name = class_name
                    location_class.latitude = latitude
                    location_class.longitude = longitude
                    location_class.created_at = timezone.now()  # Update with current time
                    location_class.status = 'ON'  # Set status to ON
                    location_class.venue = venue
                    location_class.save()
                    return JsonResponse({'success': True, 'message': 'Class venue updated successfully!'})
                else:
                    LocationClass.objects.create(
                        lecturer=request.user,
                        full_name=lecturer_profile.full_name,
                        name=class_name,
                        latitude=latitude,
                        status='ON',  # Set status to ON
                        venue=venue,
                        longitude=longitude
                    )
                    return JsonResponse({'success': True, 'message': 'Class venue saved successfully!'})
            else:
                return JsonResponse({'error': False, 'message': 'Complete your profile first.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Class Location failed to be saved: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from datetime import datetime, timedelta
import io
from django.utils import timezone

def delete_class(request, pk):
    # Get current datetime
    current_datetime = timezone.now()
    
    # Get the class information
    try:
        location_class = LocationClass.objects.get(lecturer=pk)
        location_class.status = 'OFF'  # Set status to OFF
        location_class.save()
    except LocationClass.DoesNotExist:
        messages.error(request, 'Class not found!')
        return redirect('some_redirect_view')
    
    # Use the full datetime directly (no need to combine)
    class_start_datetime = location_class.created_at
    
    # Calculate total class duration in minutes (rounded)
    class_duration = round((current_datetime - class_start_datetime).total_seconds() / 60, 1)
    
    # Ensure class duration isn't negative (in case of timezone issues)
    class_duration = max(0, class_duration)
    
    # Get all students who attended this class
    students_attended = RegisteredClass.objects.filter(lecturer=request.user.username)
    
    # Prepare data for PDF
    data = []
    for student_record in students_attended:
        # Get student profile
        try:
            student = StudentProfile.objects.get(username=student_record.student)
        except StudentProfile.DoesNotExist:
            continue
            
        # Use the full datetime directly for registration time
        registered_datetime = student_record.registered_at
        
        # Calculate student's attendance duration in minutes (rounded)
        attendance_duration = round((current_datetime - registered_datetime).total_seconds() / 60, 1)
        
        # Ensure duration is within bounds (0 <= duration <= class_duration)
        attendance_duration = max(0, min(attendance_duration, class_duration))

        if MyClasses.objects.filter(student=student.username, class_name=location_class.name).exists():
            my_class = MyClasses.objects.get(student=student.username, class_name=location_class.name)
            my_class.class_minutes = my_class.class_minutes + Decimal(str(attendance_duration))
            my_class.status = "Yes" if attendance_duration > 5  else "No"
            my_class.save()
        else:
            my_class = MyClasses(
                lecturer=location_class.lecturer,
                student=student.username,
                class_name=location_class.name,
                class_minutes=Decimal(str(attendance_duration)),
                status="Yes" if attendance_duration > 5 else "No"
            )
            my_class.save()

        # Calculate percentage of class attended
        attendance_percentage = 0
        if class_duration > 0:
            attendance_percentage = round((attendance_duration / class_duration) * 100, 1)
        
        # Prepare row data
        row = {
            'student_name': student.full_name,
            'student_id': student.student_id,
            'program': student.program,
            'class_started_at': class_start_datetime.strftime("%H:%M:%S"),
            'student_joined_at': registered_datetime.strftime("%H:%M:%S"),
            'duration_minutes': attendance_duration,
            'attendance_percentage': attendance_percentage,
            'current_time': current_datetime.strftime("%H:%M:%S"),
            'class_name': location_class.name,
            'lecturer_name': location_class.full_name,
            'venue': location_class.venue,
            'class_duration': class_duration
        }
        data.append(row)
    
    # Generate PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set up PDF title and headers with better vertical spacing
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1*inch, height-1*inch, f"Class Attendance Report: {location_class.name}")
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, height-1.5*inch, f"Lecturer: {location_class.full_name}")  # More space below title
    p.drawString(1*inch, height-2*inch, f"Total Class Duration: {class_duration} minutes")  # Better vertical spacing

    # Draw table headers with optimized spacing
    p.setFont("Helvetica-Bold", 10)
    y = height - 2.5*inch  # Start table higher up with more space from header

    # Adjusted column positions for better fit
    col_positions = {
        'name': 1*inch,        # Student Name
        'id': 2.5*inch,        # Student ID
        'program': 3.75*inch,  # Program
        'duration': 5.25*inch, # Duration
        'percentage': 6.25*inch # Attendance %
    }

    # Draw headers with new spacing
    p.drawString(col_positions['name'], y, "Student Name")
    p.drawString(col_positions['id'], y, "Student ID")
    p.drawString(col_positions['program'], y, "Program")
    p.drawString(col_positions['duration'], y, "Duration")
    p.drawString(col_positions['percentage'], y, "Attendance %")

    # Table rows with consistent spacing
    p.setFont("Helvetica", 10)
    y -= 0.35*inch  # More space between header and first row
    row_height = 0.3*inch  # Slightly taller rows

    for row in data:
        if y < 1.5*inch:  # More bottom margin before new page
            p.showPage()
            y = height - 1.5*inch
            # Redraw headers
            p.setFont("Helvetica-Bold", 10)
            p.drawString(col_positions['name'], y, "Student Name")
            p.drawString(col_positions['id'], y, "Student ID")
            p.drawString(col_positions['program'], y, "Program")
            p.drawString(col_positions['duration'], y, "Duration")
            p.drawString(col_positions['percentage'], y, "Attendance %")
            y -= 0.35*inch
            p.setFont("Helvetica", 10)
        
        # Draw row data with new spacing
        p.drawString(col_positions['name'], y, row['student_name'][:20])
        p.drawString(col_positions['id'], y, row['student_id'])
        p.drawString(col_positions['program'], y, row['program'][:15])
        p.drawString(col_positions['duration'], y, f"{row['duration_minutes']}m")
        p.drawString(col_positions['percentage'], y, f"{row['attendance_percentage']}%")
        y -= row_height

    # Summary page with better spacing
    p.showPage()
    p.setFont("Helvetica-Bold", 16)  # Larger title
    p.drawCentredString(width/2, height-1.5*inch, "Attendance Summary")
    p.setFont("Helvetica", 12)

    y = height - 2.5*inch  # More space below title
    p.drawString(1.5*inch, y, f"Total Students: {len(data)}")
    y -= 0.4*inch  # More space between summary items
    if data:
        avg_duration = sum(row['duration_minutes'] for row in data) / len(data)
        p.drawString(1.5*inch, y, f"Average Attendance Duration: {round(avg_duration, 1)} minutes")
        y -= 0.4*inch
        avg_percentage = sum(row['attendance_percentage'] for row in data) / len(data)
        p.drawString(1.5*inch, y, f"Average Attendance Percentage: {round(avg_percentage, 1)}%")

    p.save()
    # Prepare PDF response
    buffer.seek(0)
    filename = f"class_attendance_{location_class.name}_{current_datetime.strftime('%Y%m%d_%H%M%S')}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    LocationClass.objects.get(lecturer=pk).delete()
    
    messages.success(request, 'Class ended successfully and attendance report generated!')
    # Consider whether you want to delete the class records here
    # LocationClass.objects.filter(lecturer=pk).delete()
    # RegisteredClass.objects.filter(lecturer=request.user.username).delete()
    return redirect(request.META.get('HTTP_REFERER'))

def start_class(request):
    if request.method == 'POST':
        selected_class = request.POST.get('class')
        print(selected_class)
        classes = LocationClass.objects.all()

        try:
            location_class = LocationClass.objects.get(lecturer=selected_class)
        except ObjectDoesNotExist:
            location_class = None
        except Exception as e:
            location_class = None

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            student_profile = None
        except Exception as e:
            student_profile = None

        data = [[obj.latitude, obj.longitude, obj.lecturer] for obj in LocationClass.objects.filter(lecturer=selected_class)]
        maps = {}
        for obj in LocationClass.objects.all():
            map1 = folium.Map(location=[obj.latitude, obj.longitude], tiles='OpenStreetMap', zoom_start=12, min_zoom=2, max_zoom=18)
            plugins.Fullscreen(position='topright').add_to(map1)
            LocateControl().add_to(map1)
            for dt in data:
                folium.Marker([dt[0], dt[1]]).add_to(map1)
                map_html = map1._repr_html_()
                maps[obj.lecturer] = map_html

        if RegisteredClass.objects.filter(lecturer=selected_class, class_name=location_class.name, student=request.user).exists():
            pass
        else:
            if StudentProfile.objects.filter(user=request.user).exists():
                student_profile2 = StudentProfile.objects.get(user=request.user)
                student_profile2.registered = 'False'
                student_profile2.save()
        context = {
            'location_class': location_class,
            'student_profile': student_profile,
            'classes': classes,
            'maps': maps,
            'selected_class': selected_class,
        }
        return render(request, 'dashboard/menu.html', context)


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees).
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000  # Radius of Earth in meters
    return c * r

@csrf_exempt
def register_class(request):
    if request.method == 'POST':
        print("Request received")
        try:
            data = json.loads(request.body)
            class_name = data.get('class_name')
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))

            print("Data received:", class_name, latitude, longitude)

            if StudentProfile.objects.filter(user=request.user).exists():

                if LocationClass.objects.filter(name=class_name).exists():
                    my_class = LocationClass.objects.get(name=class_name)
                    distance = haversine(latitude, longitude, my_class.latitude, my_class.longitude)
                    print(f"Distance to class: {distance:.2f} meters")

                    if distance <= 30:

                        my_profile = StudentProfile.objects.get(user=request.user)
                        my_profile.registered = 'True'
                        my_profile.save()

                        if RegisteredClass.objects.filter(student=request.user).exists():
                            registered_class = RegisteredClass.objects.get(student=request.user)
                            registered_class.lecturer = my_class.lecturer
                            registered_class.class_name = class_name
                            registered_class.lecturer_name = my_class.full_name
                            registered_class.save()
                        else:
                            register_class = RegisteredClass(
                                lecturer=my_class.lecturer,
                                student=request.user,
                                class_name=class_name,
                                lecturer_name=my_class.full_name,
                                student_name=my_profile.full_name
                            )
                            register_class.save()
                        return JsonResponse({'success': True, 'message': 'Class registered successfully.'})
                    else:
                        return JsonResponse({'success': False, 'message': 'You are not within the class location range.'})
                else:
                    return JsonResponse({'success': False, 'message': 'You cannot register. Seems you did not attend the class.'})
            else:
                return JsonResponse({'success': False, 'message': 'Complete your profile first.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Class Location failed to be saved: {str(e)}'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    


def add_student(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Students.objects.filter(student=email).exists():
            messages.error(request, 'Student already exists.')  # Redirect to the menu or appropriate page
        else:
            student = Students(student=email)
            student.save()
            messages.success(request, 'Student added successfully.')
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.error(request, 'Student email cannot be empty.')
    return redirect(request.META.get("HTTP_REFERER"))

def register_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Username already exists.')
            return redirect(request.META.get('HTTP_REFERER'))

        user = User.objects.create_user(username=email, email=email, password=password, first_name='lecturer')
        user.save()
        messages.success(request, 'Registration successful!.')
        return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'home/index.html')