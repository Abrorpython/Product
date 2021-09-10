import sys
from PIL import Image
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile

from io import BytesIO

User = get_user_model()


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(self, *args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in kwargs:
                    return sorted(
                        products, key=lambda x: x.__class__.meta.model.startwith(with_respect_to), reverse=True
                    )
        return products


class LatestProducts:
    objects = LatestProductsManager()


# 1 Product
# 2 Category
# 3 CartProduct
# 4 Cart
# 5 Order
# ********************
# 6 Customer
# 7 Specification


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Category')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Categoriya', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Nomi')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Rasm')
    descriptions = models.TextField(verbose_name='Haqida', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Narxi')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # image = self.image
        # img = Image.open(image)
        # min_height, min_width = self.MIN_RESOLUTION
        # max_height, max_width = self.MAX_RESOLUTION
        # if img.height < min_height or img.width < min_width:
        #     raise MinResolutionErrorException('Kichkina xajmdegi suratlarga ruxsat berilgan')
        # if img.height < max_height or img.width < max_width:
        #     raise MaxResolutionErrorException('Katta xajmdegi suratlarga ruxsat berilgan')
        image = self.image
        img = Image.open(image)
        new_img = img.convert('RGB')
        resized_new_img = new_img.resize((200, 200), Image.ANTIALIAS)
        filestream = BytesIO()
        resized_new_img.save(filestream, 'JPEG', quality=90)
        filestream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
        )
        super().save(*args, **kwargs)


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display = models.CharField(max_length=255, verbose_name='Display turi')
    processor_freq = models.CharField(max_length=255, verbose_name='Protsessor chastottasi')
    ram = models.CharField(max_length=255, verbose_name='Operativ hotira')
    video = models.CharField(max_length=255, verbose_name='Video Karta')
    time_without_change = models.CharField(max_length=255, verbose_name='Batareya yetish vaqti')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)


class SmartPhone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Display turi')
    resultion = models.CharField(max_length=255, verbose_name='Ekran razmer')
    accum_volume = models.CharField(max_length=255, verbose_name='Batareya Hajmi')
    ram = models.CharField(max_length=255, verbose_name='Tezkor Xotira')
    sd = models.BooleanField(default=True)
    sd_volume_max = models.CharField(max_length=255, verbose_name='Maksimalniy sigim')
    main_cam_mp = models.CharField(max_length=255, verbose_name='Asosiy Kamer')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Frontalnaya Kamera')

    def __str__(self):
        return "{} : {} ".format(self.category.name, self.title)


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Xaridor', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Savatcha', on_delete=models.CASCADE, related_name='related_product')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Jami summa')

    def __str__(self):
        return "Mahsulot:{} (Savatcha uchun)".format(self.product.title)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Egasi', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Jami summa')

    def __str__(self):
        return str(self.id)


# cartproduct.related_products.all()


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Foydalanuvchi', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Telefon raqam')
    addres = models.CharField(max_length=255, verbose_name='Manzil')

    def __str__(self):
        return 'Xaridor: {} {}'.format(self.user.first_name, self.user.last_name)


class SomeModel(models.Model):
    image = models.ImageField()

    def __str__(self):
        return str(self.id)

# class Specifications(models.Model):
#     content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
#     objects_id = models.PositiveIntegerField()
#     name = models.CharField(max_length=255,verbose_name='Mahsulot haqida malumot')
#
#     def __str__(self):
#         return 'Mahuslot haqida malumot:{}'.format(self.name)
