import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0002_order_name'),
        ('payment', '0002_payment_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to='order.order',
            ),
        ),
    ]
