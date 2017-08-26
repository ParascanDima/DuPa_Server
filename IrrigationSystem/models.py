from django.db import models

class MeasureTime(models.Model):
	date = models.DateTimeField('date') 

class Wind(models.Model):
    speed = models.IntegerField(default=0, db_column="Speed", null=False)
    date = models.ForeignKey(MeasureTime, on_delete=models.CASCADE, null=True)

    def __str__(self):
    	return '%s' % self.speed


class GroundHumidity(models.Model):
    sensor = models.IntegerField(db_column="sensor", null=False)
    averange = models.IntegerField(db_column="Average", null=False)
    date = models.ForeignKey(MeasureTime, on_delete=models.CASCADE, null=True)


class Custom_User(models.Model):
    userName = models.CharField(db_column="UserName", null=False, max_length=100)
    password = models.CharField(db_column="Password", null=False, max_length=255)
    role = models.CharField(db_column="Role", null=False, max_length=50)
