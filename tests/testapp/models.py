from django.db import models

from govtech_csg_xcg.modelpermissions.decorators import orm_default_permissions_check


@orm_default_permissions_check
class Person(models.Model):
    name = models.CharField(max_length=50)
