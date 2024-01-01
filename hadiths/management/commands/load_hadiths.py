from csv import DictReader
from django.core.management import BaseCommand

# Import the model
from hadiths.models import Hadith, HadithSource

class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from hadiths.csv"

    def handle(self, *args, **options):
        for row in DictReader(open('hadiths2.csv', encoding='utf-8')):
            source_name = row['source']
            source, _ = HadithSource.objects.get_or_create(name=source_name)
            
            hadith_no=row['hadith_no']
            if not hadith_no:
                last_hadith = Hadith.objects.last()
                hadith_id = last_hadith.hadith_no + 1 if last_hadith else 1

            hadith = Hadith(
                source=source,
                chapter_no=row['chapter_no'],
                hadith_no=row['hadith_no'],
                chapter=row['chapter'],
                chain_indx=row['chain_indx'],
                text_ar=row['text_ar'],
                text_en=row['text_en']
            )
            hadith.save()
