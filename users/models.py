from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.conf import settings

class Profile(models.Model): 
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='default.jpg', upload_to='profile_pics')
	bio = models.CharField(max_length=255, blank=True)
	friends = models.ManyToManyField("Profile", blank=True)

	def __str__(self):
		return f'self.user.username Profile'

	def save(self, *args, **kwargs):
		super(Profile, self).save(*args, **kwargs)

		img = Image.open(self.image.path)
		if img.height > 500 or img.width > 500:
			output_size = (500,500)
			img.thumbnail(output_size)
			img.save(self.image.path)

class FriendRequest(models.Model):
	to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='to_user', on_delete=models.CASCADE)
	from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='from_user', on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "From {}, to {}".format(self.from_user.username, self.to_user.username)
