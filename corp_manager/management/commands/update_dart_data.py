from django.core.management.base import BaseCommand
from corp_manager.models import Filings, Corporation
import dart_fss as dart
from datetime import datetime
from django.conf import settings
from services import fs_extract_parse

class Command(BaseCommand):
    
    help = "get filing for companies"
    def handle(self, *args, **kwargs):
        DART_API_KEY = settings.DART_API_KEY
        today = datetime.today()
        formatted_date = today.strftime("%Y%m&d") #YYYYMMDD

        if not DART_API_KEY:
            self.stderr.write(self.style.ERROR("MISSING API KEY"))
            return
        try:
            search_results = dart.filings.search(
                bgn_de= formatted_date, 
                pblntf_detail_ty=['a001,a002,a003,i002'] #a분기,반기,사업보고서 i는 공정공시 (잠정)실적
                )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"API call error:{e}"))

        if not search_results:
            self.stderr.write(self.style.ERROR("There is no new public filing available"))
            return

        for report in search_results:
            try:
                corp_obj = Corporation.objects.get(corp_code =report.corp_code)
            except Corporation.DoesNotExist:
                continue #skip => corp update must be done before this command
            
            is_preliminary_rpt= False
            if '실적' in report.report_nm:
                is_preliminary_rpt = True
            
            filing_object, created = Filings.objects.get_or_create(
                rcept_no= report.rcept_no,
                defaults={
                    "corp_cls": report.cls,
                    "corp_code": corp_obj,
                    "rcept_dt": report.rcept_dt,
                    "report_nm": report.report_nm,
                    "rm": getattr(report, 'rm', ''),
                    "is_preliminary": is_preliminary_rpt
                }
            )

            if created:
                self.stdout.write(f"new filing saved [{corp_obj.corp_name}] {filing_object.report_nm}")
                
                if filing_object.is_preliminary:
                    self.stdout.write(self.style.WARNING("start preliminary earning parsing "))
                    #rcept_no로 viewer띄우는걸로 
               
                else: #사업보고서 (분/반기)
                    self.stdout.write(self.style.WARNING("start ordinary report parsing; extracting financial statements"))
                    extraction_result = fs_extract_parse(filing_object)

                    if not extraction_result:
                        self.stderr.write(self.style.ERROR("ordinary report extraction gone wrong"))
                        return

