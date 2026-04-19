from django.core.management.base import BaseCommand, CommandError
from corp_manager.models import Corporation 
import dart_fss as dart
from django.conf import settings
#custom command
class Command(BaseCommand):
    help = "Loads corporation list from dart_fss api"

    def handle(self, *args, **kwargs):
        #get corporation list from DART FSS library
        DART_API_KEY = settings.DART_API_KEY

        if not DART_API_KEY:
            self.stderr.write(self.style.ERROR("MISSING API KEY"))
            return
        

        dart.set_api_key(DART_API_KEY)

        corp_list = dart.corp.get_corp_list()
        new_corp = []

        for corp in corp_list:
            if corp.stock_code: #상장사 
                new_corp.append(
                    Corporation(
                        corp_code = corp.corp_code,
                        corp_name = corp.corp_name,
                        stock_code = corp.stock_code,
                        modify_date = corp.modify_date
                    )
                )
        
        self.stdout.write(f"Parsing Complete, number of public corporation: {len(new_corp)}")

        Corporation.objects.bulk_create(new_corp, ignore_conflicts= True)
        