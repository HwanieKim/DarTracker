import requests
from django.conf import settings
import io
import dart_fss
import re
from corp_manager.models import FinancialStatement

def extract_fs(filing_obj):
    """
    사업보고서 (매출,영업이익) 추출
    args: corp_code (회사 고유번호)
    
    returns:
    
    """
    bsns_year, reprt_code = _get_bsns_year_reprt_code(filing_obj.report_nm)

    if not bsns_year or not reprt_code:
        print(f"error parsing business year/report code.\n check for filing: {filing_obj.rcept_no}") 

    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"

    params = {
        "crtfc_key": settings.DART_API_KEY,
        "corp_code": filing_obj.corp_code,
        "bsns_year": bsns_year,
        "reprt_code": reprt_code,
        "fs_div": "CFS" #연결재무제표
    }
    try:
        respone = requests.get(url=url, params=params, timeout= 10)


        if respone.get("status") != "000":
            print(f"error retrieving financial report from filing: {filing_obj.rcept_no}.\n retrying with OFS")
            params["fs_div"] = "OFS"
            respone = requests.get(url=url, params=params)
            
            if respone.get("status") != "000":
                print(f"error retrieving financial report from filing: {filing_obj.rcept_no}.")
                return False
    except requests.exceptions.RequestException as e:
        print(f"{e}")
        return False
    
    new_list = []

    for item in respone["list"]:
        record = FinancialStatement(
            rcept_no = filing_obj,
            corp_code = filing_obj.corp_code,
            reprt_code = reprt_code,
            bsns_year = bsns_year,
            sj_div = item.get('sj_div'),
            sj_nm = item.get('sj_nm'),
            account_id = item.get('account_id'),
            account_nm= item.get('account_nm'),
            account_detail = item.get('account_detail'),
            thstrm_nm = item.get('thstrm_nm'),
            thstrm_amount = item.get('thstrm_amount'),
            frmtrm_nm= item.get('frmtrm_nm'),
            frmtrm_amount= item.get('frmtrm_amount'),
            bfefrmtrm_nm = item.get('bfefrmtrm_nm'),
            bfefrmtrm_amount = item.get('bfefrmtrm_amount'),
            ord = item.get('ord'),
            currency = item.get('currency')
        )

        new_list.append(record)

    if new_list :
        FinancialStatement.objects.bulk_create(new_list, ignore_conflicts= True)
        print(f"{filing_obj.corp.code.corp_name}의 공시({filing_obj.rcept_no}) DB저장")
        return True
    
    return False

    

def _get_bsns_year_reprt_code(report_nm):


    match = re.search(r'\(\d{4}\.)\d{2}\)', report_nm)

    if not match :
        return None, None
    
    bsns_year = match.group(1) 
    month = match.group(2)
    reprt_code = ""
    #bsns year parsing from report nm
    if "사업" in report_nm :
        reprt_code = "11011"
    elif "반기" in report_nm:
        reprt_code = "11012" 
    elif "분기" in report_nm: #분기 구분
        if  month == "03": reprt_code= "11013"
        elif month == "09": reprt_code ="11014"

    return bsns_year, reprt_code


