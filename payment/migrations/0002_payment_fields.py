from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount',
            field=models.BigIntegerField(),
        ),
        migrations.AddField(
            model_name='payment',
            name='paymentID',
            field=models.CharField(db_index=True, max_length=600),
        ),
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(
                choices=[('SUCCESS', 'Success'), ('PENDING', 'Pending'), ('FAILED', 'Failed')],
                default='PENDING',
                max_length=7,
            ),
        ),
    ]
