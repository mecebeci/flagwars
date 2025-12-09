from django.core.management.base import BaseCommand
from apis.models import Country

class Command(BaseCommand):
    help = 'Load country data into database'

    def handle(self, *args, **options):
        # Step 1: Clear existing countries (optional - good for testing)
        self.stdout.write('Clearing existing countries...')
        Country.objects.all().delete()
        
        # Step 2: Define country data (10 countries for testing)
        countries_data = [
            {
                'name': 'United States of America',
                'code': 'USA',
                'flag_emoji': '🇺🇸',
                'aliases': ['United States', 'USA', 'US', 'America', 'United States of America']
            },
            {
                'name': 'United Kingdom',
                'code': 'GBR',
                'flag_emoji': '🇬🇧',
                'aliases': ['UK', 'Great Britain', 'Britain', 'England', 'United Kingdom']
            },
            {
                'name': 'Germany',
                'code': 'DEU',
                'flag_emoji': '🇩🇪',
                'aliases': ['Germany', 'Deutschland', 'DE']
            },
            {
                'name': 'France',
                'code': 'FRA',
                'flag_emoji': '🇫🇷',
                'aliases': ['France', 'FR']
            },
            {
                'name': 'Japan',
                'code': 'JPN',
                'flag_emoji': '🇯🇵',
                'aliases': ['Japan', 'Nippon', 'JP']
            },
            {
                'name': 'Turkey',
                'code': 'TUR',
                'flag_emoji': '🇹🇷',
                'aliases': ['Turkey', 'Türkiye', 'TR']
            },
            {
                'name': 'Canada',
                'code': 'CAN',
                'flag_emoji': '🇨🇦',
                'aliases': ['Canada', 'CA']
            },
            {
                'name': 'Brazil',
                'code': 'BRA',
                'flag_emoji': '🇧🇷',
                'aliases': ['Brazil', 'Brasil', 'BR']
            },
            {
                'name': 'Australia',
                'code': 'AUS',
                'flag_emoji': '🇦🇺',
                'aliases': ['Australia', 'AU']
            },
            {
                'name': 'Italy',
                'code': 'ITA',
                'flag_emoji': '🇮🇹',
                'aliases': ['Italy', 'Italia', 'IT']
            },
        ]
        
        # Step 3: Create countries in the database
        self.stdout.write('Loading countries...')
        for data in countries_data:
            Country.objects.create(**data)
            self.stdout.write(f'  ✓ Created {data["name"]}')
        
        # Step 4: Success message
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully loaded {len(countries_data)} countries!'))