from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# პროდუქტის კლასი
class Product(models.Model):
    category = models.CharField(max_length=100, verbose_name="კატეგორია", default="")
    title = models.CharField(max_length=200, verbose_name="დასახელება")
    image = models.ImageField(upload_to='products/', verbose_name="ნივთის სურათი")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ფასი")
    release_date = models.DateField(verbose_name="გამოშვების თარიღი")
    brand = models.CharField(max_length=100, verbose_name="ბრენდი")
    stock = models.PositiveIntegerField(verbose_name="საწყობში დარჩენილი რაოდენობა")
    description = models.TextField(verbose_name="დეტალური ინფორმაცია")

    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        # მოგვაქვს ამ კონკრეტული პროდუქტის ყველა შეფასება
        reviews = self.reviews.all()
        if reviews:
            avg = sum([review.rating for review in reviews]) / len(reviews)
            return round(avg, 1) 
        return 0

# შეფასების კლასი
class Review(models.Model):
    # ვაკავშირებთ კონკრეტულ პროდუქტთან
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    # ვაკავშირებთ ავტორიზებულ ვებ-იუზერთან
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="შემფასებელი")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="რეიტინგი")

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"