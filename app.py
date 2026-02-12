import streamlit as st
import pandas as pd
import numpy as np

# 1. 웹 페이지 기본 설정
st.set_page_config(page_title="전문가용 장기렌트 정밀견적", layout="wide")

# --- [내부 데이터 설정: 엑셀 로직 기반] ---
# 1. 보험료 테이블 (21세/26세, 대물한도별 월 비용)
INS_TABLE = {
    "만 26세 이상": {"1억": 45000, "2억": 47000, "3억": 50000},
    "만 21세 이상": {"1억": 58000, "2억": 61000, "3억": 65000}
}
# 2. 잔존가치(RV) 테이블 (기간 및 주행거리별) - 엑셀 DATA 탭 참조 기반
RV_MAP = {
    24: {"1만km": 68, "1.5만km": 66, "2만km": 64, "2.5만km": 62, "3만km": 60, "4만km": 55},
    36: {"1만km": 62, "1.5만km": 60, "2만km": 58, "2.5만km": 56, "3만km": 54, "4만km": 49},
    60: {"1만km": 50, "1.5만km": 48, "2만km": 46, "2.5만km": 44, "3만km": 42, "4만km": 37}
}

# --- [UI: 사이드바 - 차량 및 옵션 선택] ---
with st.sidebar:
    st.header("🚗 1. 차량 상세 정보")
    maker = st.selectbox("메이커 선택", ["현대", "기아", "제네시스", "수입차"])
    raw_price = st.number_input("차량 출고가 (VAT 포함)", value=35000000, step=100000)
    option_price = st.number_input("추가 옵션가 (VAT 포함)", value=0, step=100000)
    dc_rate = st.number_input("차량 할인액 (원)", value=0, step=10000)
    
    st.header("🗓️ 2. 계약 조건")
    period = st.selectbox("이용 기간 (개월)", [24, 36, 60], index=1)
    mileage = st.selectbox("연간 약정거리", ["1만km", "1.5만km", "2만km", "2.5만km", "3만km", "4만km"], index=2)
    
    st.header("⚙️ 3. 차량 속성")
    cc = st.number_input("배기량 (cc)", value=2000, step=100)
    fuel_type = st.radio("연료 선택", ["가솔린", "디젤", "하이브리드", "전기"], horizontal=True)

# --- [메인 화면: 금융 및 보험 조건] ---
st.title("📑 전문가용 장기렌트 정밀 손익분석 견적")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("💰 금융 조건")
    pre_choice = st.selectbox("선수금 (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
    pre_val = st.number_input("선수금 금액(원)", value=0) if pre_choice == "직접입력" else 0
    
    dep_choice = st.selectbox("보증금 (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
    dep_val = st.number_input("보증금 금액(원)", value=0) if dep_choice == "직접입력" else 0

with col2:
    st.subheader("🛡️ 보험 및 서비스")
    ins_age = st.radio("보험 연령", ["만 26세 이상", "만 21세 이상"])
    ins_limit = st.selectbox("대물보험 한도", ["1억", "2억", "3억"])
    st.write("✅ 자손: 1억/1.5천")
    st.write("✅ 면책금: 30만원")

with col3:
    st.subheader("📈 마진 및 기타")
    agent_fee_p = st.select_slider("에이전트 수수료 (%)", options=[1, 2, 3, 4, 5, 6], value=2)
    consignment = st.number_input("탁송료 (VAT 제외)", value=250000)
    mgmt_fee = st.number_input("월 관리비/인건비 (원)", value=29000)

# --- [정밀 연산 로직: 엑셀 수식 기반] ---
# 1. 면세가 및 취득원가 산출
total_raw = raw_price + option_price - dc_rate
tax_free_price = total_raw / 1.1 # 엑셀 면세율 1.1 적용
acq_tax = tax_free_price * 0.04 # 취득세+등록세(4%)
acq_cost = tax_free_price + acq_tax + consignment + 32300 # 32,300은 인지대/번호판대

# 2. 선수금/보증금 계산
prepay_amt = pre_val if pre_choice == "직접입력" else acq_cost * (int(pre_choice.replace("%",""))/100)
deposit_amt = dep_val if dep_choice == "직접입력" else acq_cost * (int(dep_choice.replace("%",""))/100)

# 3. 잔존가치(RV) 자동 적용
rv_rate = RV_MAP[period][mileage] / 100
rv_amt = tax_free_price * rv_rate

# 4. 월 원가 산출 (이자/보험/세금)
base_rate = 0.055 # 기본 조달 금리 5.5% 가정
total_rate = (base_rate + (agent_fee_p / 100)) / 12 # 에이전트 마진 가산
# 원리금 산출 공식 (금융원가)
principal_to_pay = acq_cost - prepay_amt - (rv_amt / (1 + total_rate)**period)
monthly_fund = (principal_to_pay * total_rate * (1 + total_rate)**period) / ((1 + total_rate)**period - 1)

# 보험료 및 자동차세
monthly_ins = INS_TABLE[ins_age][ins_limit]
car_tax_factor = 24 if cc > 2500 else 19
monthly_car_tax = (cc * car_tax_factor) / 12

# 5. 최종 월 렌트료 (VAT 포함)
final_rent = int((monthly_fund + monthly_ins + monthly_car_tax + mgmt_fee) * 1.1)

# --- [결과 출력 섹션] ---
st.divider()
res_col1, res_col2 = st.columns([1.5, 1])

with res_col1:
    st.subheader("📋 견적서 요약")
    summary_df = pd.DataFrame({
        "구분": ["공급가액(면세)", "취득원가 합계", "선수금액", "보증금액", "잔존가치(인수금)"],
        "금액": [f"{int(tax_free_price):,}원", f"{int(acq_cost):,}원", 
                f"{int(prepay_amt):,}원", f"{int(deposit_amt):,}원", f"{int(rv_amt):,}원 ({int(rv_rate*100)}%)"]
    })
    st.table(summary_df)

with res_col2:
    st.metric(label="월 납입액 (VAT 포함)", value=f"{final_rent:,} 원")
    st.info(f"선택 사양: {maker} / {period}개월 / {mileage}\n보험: {ins_age} (대물 {ins_limit})")
    
    if st.button("📤 카카오톡 전송용 텍스트 복사"):
        copy_text = f"[{maker} 장기렌트 견적]\n- 월 대여료: {final_rent:,}원\n- 기간: {period}개월\n- 약정거리: {mileage}\n- 보증금/선납금: {dep_choice}/{pre_choice}\n- 만기인수가: {int(rv_amt):,}원"
        st.code(copy_text)
