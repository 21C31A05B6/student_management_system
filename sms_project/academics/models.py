from django.db import models


class Department(models.Model):
    """Module 4 - Department Management (e.g. CSE, ECE, MBA)."""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    head_of_department = models.ForeignKey(
        'teachers.Teacher', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='heads_department'
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    """Module 5 - Course/Class Management (e.g. CSE - Year 1 - Section A)."""
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=100)  # e.g. B.Tech CSE
    duration_years = models.PositiveSmallIntegerField(default=4)

    class Meta:
        ordering = ['department__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.department.code})"


class Section(models.Model):
    """A specific year+section within a course, e.g. Year 2 - Section A."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=10)  # A, B, C

    class Meta:
        ordering = ['course__name', 'year', 'name']
        unique_together = ('course', 'year', 'semester', 'name')

    def __str__(self):
        return f"{self.course.name} - Y{self.year} Sem{self.semester} - {self.name}"


class Subject(models.Model):
    """Module 4 - Subject Management."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    semester = models.PositiveSmallIntegerField()
    credits = models.PositiveSmallIntegerField(default=3)
    teachers = models.ManyToManyField(
        'teachers.Teacher', blank=True, related_name='subjects_taught'
    )
    sections = models.ManyToManyField(Section, blank=True, related_name='subjects')

    class Meta:
        ordering = ['semester', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"
