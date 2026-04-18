from django.db import models
#datanbase interaction with ORM Django
# Create your models here.

#기업정보
class Corporation(models.Model):
    corp_code = models.CharField(primary_key = True, max_length = 8) #법인고유번호
    corp_name = models.CharField(max_length = 100) #종목명(법인명)
    stock_code = models.CharField(max_length = 6, null= True, blank = True, unique= True) #종목코드 != 법인고유번호 
    modify_date = models.CharField(max_length = 8) #YYYYMMDD

    def __str__(self):
        return f"{self.corp_name}: {self.corp_code}" 
    
#공시
class Filings(models.Model):
    class corp_cls_choices(models.TextChoices): #법인구분 : Y(유가), K(코스닥), N(코넥스), E(기타)
        Y = "Y", "유가"
        K = "K", "코스닥"
        N = "N", "코넥스"
        E = "E", "기타"

    corp_cls= models.CharField(
        max_length = 1,
        choices = corp_cls_choices
        )
    rcept_no = models.CharField(primary_key= True, max_length= 14) #공시 접수번호
    corp_code = models.ForeignKey(Corporation, on_delete = models.CASCADE) #법인고유번호
    report_nm = models.TextField() #보고서명: 공시구분 + 보고서명 + 기타정보 
    rcept_dt = models.CharField(max_length = 8) #공시접수일자 (YYYYMMDD)
    rm = models.TextField(null = True, blank = True) #비고 

#재무제표 
class FinancialStatemnent(models.Model):
    class reprt_code_choices(models.IntegerChoices): #보고서 코드
        Q1 = "11013", "1분기보고서"
        Q2 = "11012", "반기보고서"
        Q3 = "11014", "3분기보고서"
        Q4 = "11011", "사업보고서"
    
    class sj_div_choices(models.TextChoices): #재무제표 구분
        BS = "BS", "재무상태표"
        IS = "IS", "손익계산서"
        CIS = "CIS", "포괄손익계산서"
        CF = "CF", "현금흐름표"
        SCE = "SCE", "자본변동표"

    rcept_no = models.ForeignKey(Filings, on_delete = models.CASCADE) #공시 접수번호
    corp_code = models.ForeignKey(Corporation, on_delete = models.CASCADE) #고유번호

    reprt_code = models.CharField( #보고서 코드 
        max_length = 5,
        choices = reprt_code_choices
    )

    bsns_year = models.CharField(max_length = 4) #사업연도

    sj_div = models.CharField(
        max_length = 3,
        choices = sj_div_choices
        )
    sj_nm = models.TextField() # 재무제표명 ex) 재무상태표

    #계정 
    account_id = models.CharField(max_length = 100, default = "-표준계정코드 미사용-") #XBRL 표준계정코드
    account_nm = models.CharField(max_length = 100) # 계정명칭 ex) 자본총계
    account_detail = models.TextField(default = "-") #계정상세; 자본변동표에만 출력
    
    #당기, current period
    thstrm_nm = models.CharField(max_length = 100, null = True, blank = True) #당기명
    thstrm_amount = models.BigIntegerField(null = True, blank = True) #당기금액; #분/반기 보고서 & (포괄) 손익계산서일시 [3개월] 금액
    thstrm_add_amount = models.BigIntegerField(null = True, blank = True) #당기누적금액

    #전기, previous period
    frmtrm_nm = models.CharField(max_length = 100, null = True, blank = True) #전기명
    frmtrm_amount = models.BigIntegerField(null = True, blank = True) #전기금액
    frmtrm_q_nm = models.CharField(max_length = 100, null = True, blank = True) #전기명 (분/반기)
    frmtrm_q_amount = models.BigIntegerField(null = True, blank = True) #전기금액 (분/반기); 분/반기 보고서이면서 (포괄)손익계산서 일 경우 [3개월] 금액
    frmtrm_add_amount = models.BigIntegerField(null = True, blank = True) #전기누적금액
    
    #전전기, two periods ago; 사업보고서의 경우에만 출력
    bfefrmtrm_nm = models.CharField(max_length = 100, null = True, blank = True) #전전기명
    bfefrmtrm_amount = models.BigIntegerField(null = True, blank = True) #전전기금액

    ord = models.IntegerField(null = True, blank = True)
    currency = models.CharField(max_length = 3, null = True, blank = True)
    
    class Meta:
        unique_together = ('rcept_no', 'sj_div', 'account_id', 'account_nm')
