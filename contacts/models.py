from django.db import models

# Create your models here.
class ContactType(models.Model):
    ContactTitle = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ContactTitle


class Group(models.Model):
    GroupKey = models.CharField(max_length=100, unique=True)
    GroupDescription = models.TextField(blank=True)

    def __str__(self):
        return self.GroupKey


class Department(models.Model):
    DepartmentTitle = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.DepartmentTitle


class GovernamentOffice(models.Model):
    OfficeAddress = models.TextField(blank=True)
    Department = models.ForeignKey(Department, on_delete=models.CASCADE)
    Addressline1 = models.CharField(max_length=255)
    Addressline2 = models.CharField(max_length=255, blank=True)
    Addressline3 = models.CharField(max_length=255, blank=True)
    Pincode = models.CharField(max_length=20)
    City = models.CharField(max_length=100)
    State = models.CharField(max_length=100)

    def __str__(self):
        return (self.Addressline1 + ' - ' + self.Pincode)


class PrimaryDesignation(models.Model):
    PrimaryDesignation = models.CharField(max_length=100)
    Group = models.ForeignKey(Group, on_delete=models.CASCADE)
    Department = models.ForeignKey(Department, on_delete=models.CASCADE)
    ShortForm = models.CharField(max_length=50, blank=True)
    Alias = models.CharField(max_length=100, blank=True)
    DutiesandResponsibilities = models.TextField(blank=True)

    class Meta:
        unique_together = ('Department', 'PrimaryDesignation')

    def __str__(self):
        return self.PrimaryDesignation


class Position(models.Model):
    Position = models.CharField(max_length=100, unique=True)
    PrimaryDesignation = models.ForeignKey(PrimaryDesignation, on_delete=models.CASCADE)
    SupervisorPosition = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    Office = models.ForeignKey(GovernamentOffice, on_delete=models.CASCADE)
    DutiesandResponsibilities = models.TextField(blank=True)

    def __str__(self):
        return self.Position


class PositionContact(models.Model):
    Position = models.ForeignKey(Position, on_delete=models.CASCADE)
    ContactType = models.ForeignKey(ContactType, on_delete=models.CASCADE)
    ContactValue = models.CharField(max_length=255)

    class Meta:
        unique_together = ('Position', 'ContactType', 'ContactValue')

    def __str__(self):
        return f"{self.Position} - {self.ContactType}: {self.ContactValue}"