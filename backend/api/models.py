from django.db import models


class Cafe(models.Model):
    name = models.CharField(max_length=100,unique=True)        # must be unique
    latitude = models.FloatField(null=True,blank=True)                   # empty allowed
    longitude = models.FloatField(null=True,blank=True)                  # empty allowed

    def __str__(self):
        return self.name


class Visit(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name="visits")
    date = models.DateField()

    def __str__(self):
        return f"{self.date} - {self.cafe.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cafe", "date"], name="unique_cafe_per_day"),
        ]