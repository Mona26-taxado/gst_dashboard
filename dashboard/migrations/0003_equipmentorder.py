from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_equipment'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.equipment')),
            ],
            options={
                'verbose_name': 'Equipment Order',
                'verbose_name_plural': 'Equipment Orders',
            },
        ),
    ] 