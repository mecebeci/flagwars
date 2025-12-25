import os
import pycountry
from django.core.management.base import BaseCommand
from django.core.files import File
from apis.models import Country


class Command(BaseCommand):
    help = 'Populate Country model with flag images from initial_data/flags/'

    EXCLUDED_COUNTRIES = [
        'IL', 'CY', 'AX', 'AS', 'AI', 'AQ', 'AW', 'BM', 'BQ', 'BV', 'IO', 'KY', 'CX', 
        'CC', 'CK', 'CW', 'FK', 'FO', 'GF', 'PF', 'TF', 'GI', 'GP', 'GU', 'GG', 'HK',
        'IM', 'JE', 'MO', 'MQ', 'YT', 'MS', 'NC', 'NU', 'NF', 'MP', 'PN', 'RE', 'BL', 
        'SH', 'MF', 'PM', 'SX', 'GS', 'SJ', 'TK', 'TC', 'UM', 'VG', 'VI', 'WF', 'EH'
    ]

    def handle(self, *args, **options):
        flags_dir = '/app/initial_data/flags'
        
        # Verify directory exists
        if not os.path.exists(flags_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {flags_dir}'))
            return
        
        # Get all .svg files
        flag_files = [f for f in os.listdir(flags_dir) if f.endswith('.svg')]
        
        if not flag_files:
            self.stdout.write(self.style.ERROR(f'No .svg files found in {flags_dir}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(flag_files)} flag files'))
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for filename in flag_files:
            # Extract ISO code from filename (e.g., 'tr.svg' -> 'TR')
            iso_code = filename.replace('.svg', '').upper()
            if iso_code in self.EXCLUDED_COUNTRIES:
                self.stdout.write(
                    self.style.WARNING(f'⏭️  Skipped (excluded): {iso_code}')
                )
                skipped_count += 1
                continue

            # Get country info from pycountry
            try:
                country_info = pycountry.countries.get(alpha_2=iso_code)
                country_name = country_info.name
            except (AttributeError, LookupError):
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Skipping {filename}: Unknown ISO code {iso_code}')
                )
                skipped_count += 1
                continue
            
            # Full path to the flag file
            file_path = os.path.join(flags_dir, filename)
            
            # Create or update Country
            country, created = Country.objects.get_or_create(
                code=iso_code,
                defaults={'name': country_name}
            )
            
            # Upload flag image to MinIO
            with open(file_path, 'rb') as flag_file:
                country.flag_image.save(
                    f'{iso_code.lower()}.svg',
                    File(flag_file),
                    save=True
                )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created: {country_name} ({iso_code})')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'🔄 Updated: {country_name} ({iso_code})')
                )
                updated_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS(f'✅ Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'🔄 Updated: {updated_count}'))
        self.stdout.write(self.style.WARNING(f'⚠️  Skipped: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('='*50))