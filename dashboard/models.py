from django.db import models

class Students(models.Model):
    student = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.student

class LocationClass(models.Model):
    lecturer = models.CharField(max_length=200, null=True)
    full_name = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=100)  # Class name or identifier
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # Latitude with high precision
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # Longitude with high precision
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Timestamp for when the record was created
    venue = models.CharField(max_length=200, null=True)  # Venue for the class
    registered = models.IntegerField(default=0)  # Number of students registered for the class
    status = models.CharField(max_length=100, default='OFF')  # Class status (e.g., "In Progress", "Completed")

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class RegisteredClass(models.Model):
    lecturer = models.CharField(max_length=200, null=True)
    student = models.CharField(max_length=200, null=True)
    lecturer_name = models.CharField(max_length=200, null=True)
    student_name = models.CharField(max_length=200, null=True)
    class_name = models.CharField(max_length=100)  # Class name or identifier
    registered_at = models.DateTimeField(auto_now_add=True, null=True)  # Timestamp for when the record was created

    def __str__(self):
        return f"{self.name}"
    
class MyClasses(models.Model):
    lecturer = models.CharField(max_length=200, null=True)
    student = models.CharField(max_length=200, null=True)
    class_name = models.CharField(max_length=100)  # Class name or identifier
    class_minutes = models.DecimalField(max_digits=5, decimal_places=1)  # Class duration in minutes
    status = models.CharField(max_length=100, default='No')  # Class status (e.g., "In Progress", "Completed")

    def __str__(self):
        return f"{self.class_name} ({self.lecturer} - {self.student})"