from django.db import models


class UserEmail(models.Model):
    username = models.CharField(max_length=256, default='')
    email = models.EmailField(blank=True, default='')
    occurrence = models.IntegerField(default=0)

    class Meta:
        unique_together = ('username', 'email')
