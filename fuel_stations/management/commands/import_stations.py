import csv
from django.core.management.base import BaseCommand
from fuel_stations.models import FuelStation

class Command(BaseCommand):
    help = 'Import fuel stations from CSV'

    def handle(self, *args, **options):
        # 👇 Fixed path format
        csv_path = r"C:\Users\Ali Haidar\Downloads\fuel-prices-for-be-assessment.csv"
        
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                FuelStation.objects.create(
                    truckstop_id=row['OPIS Truckstop ID'],
                    name=row['Truckstop Name'],
                    address=row['Address'],
                    city=row['City'],
                    state=row['State'],
                    price=float(row['Retail Price'])
                )
        self.stdout.write(self.style.SUCCESS('✅ Data imported successfully!'))