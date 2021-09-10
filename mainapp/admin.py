from django.contrib import admin
from django.forms import ModelChoiceField,ModelForm,ValidationError
from django.utils.safestring import mark_safe
from .models import *


class NotebookAdminForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['image'].help_text = mark_safe("<span style = 'color:red; font-size:14px;'>Fotosuratni eng yuqori razmeri {}x{}</span>".format(
                *Product.MIN_RESOLUTION
            )
        )

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_height, min_width = Product.MIN_RESOLUTION
        max_height, max_width = Product.MAX_RESOLUTION
        if image.size > Product.MAX_IMAGE_SIZE:
            raise ValidationError('3 Mb dan kam bolmagan fotosurat yuklashingiz mumkin')
        if img.height < min_height or img.width < min_width:
            raise ValidationError('Kichkina xajmdegi suratlarga ruxsat berilgan')
        if img.height > max_height or img.width > max_width:
            raise ValidationError('Katta xajmdegi suratlarga ruxsat berilgan')
        return image


class NotebookAdmin(admin.ModelAdmin):

    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug = 'notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartPhoneAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug = 'smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Notebook,NotebookAdmin)
admin.site.register(SmartPhone,SmartPhoneAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(SomeModel)