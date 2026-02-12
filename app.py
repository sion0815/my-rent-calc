import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="장기렌트 정밀 손익분석", layout="wide")

# 2. 고정 수치 설정 (엑셀 '수치' 및 '손익' 탭 참조)
INSURANCE_DB = {
    "만 26세 이상": {"1억": 850000, "2억": 880000, "3억": 920000},
    "만 21세 이상": {"1억": 1250000, "2억": 1290000, "3억": 1350000}
}
TAX_FREE_DISCOUNT = 1.1  # 면세가 산출 나누기 값
MONTHLY_MGMT_FEE = 15000  # 차량관리비/인건비 등

# 3. 입력 화면 (사이드바)
with st.sidebar:
    st.header("1. 차량 상세 설정")
    maker = st.selectbox("메이커", ["현대", "기아", "제네시스"])
    raw_price = st.number_input("차량 출고가 (VAT포함)", value=30000000, step=10000)
    dc_rate = st.number_input("차량 할인액 (-)", value=0)
    consignment = st.number_input("탁송료 (+)", value=250000)
    
    st.header("2. 계약 조건")
    period = st.selectbox("이용기간", [24, 36, 60], index=1)
    mileage = st.selectbox("약정거리", ["1만km", "1.5만km", "2만km", "2.5만km", "3만km", "4만km"])
    
    st.header("3. 보험 및 기타")
    age = st.radio("보험 연령", ["만 26세 이상", "만 21세 이상"])
    limit = st.selectbox("대물 한도", ["1억", "2억", "3억"])
    st.caption("자손: 1억 / 면책금: 30만원 고정")

# 4. 금융 조건 (메인 화면 상단)
st.title("📑 장기렌터카 정밀 견적 시스템")
col_fin1, col_fin2, col_fin3 = st.columns(3)

with col_fin1:
    prepay_sel = st.selectbox("선수금 (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
    prepay_val = st.number_input("선수금 직접입력(원)", value=0) if prepay_sel == "직접입력" else 0
with col_fin2:
    deposit_sel = st.selectbox("보증금 (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
    deposit_val = st.number_input("보증금 직접입력(원)", value=0) if deposit_sel == "직접입력" else 0
with col_fin3:
    agent_fee = st.select_slider("에이전트 수수료 (%)", options=[1, 2, 3, 4, 5, 6], value=2)

# 5. 정밀 계산 로직 (엑셀 수식 이식)
# 면세가 및 취득원가
net_price = (raw_price - dc_rate) / TAX_FREE_DISCOUNT
acq_cost = net_price + consignment

# 선수금/보증금 실제 금액 계산
final_prepay = prepay_val if prepay_sel == "직접입력" else acq_cost * (int(prepay_sel.replace('%',''))/100)
final_deposit = deposit_val if deposit_sel == "직접입력" else acq_cost * (int(deposit_sel.replace('%',''))/100)

# 잔존가치 자동 산출 (기간/거리별 차등)
rv_base = {24: 0.65, 36: 0.60, 60: 0.45}
mile_idx = ["1만km", "1.5만km", "2만km", "2.5만km", "3만km", "4만km"].index(mileage)
rv_rate = rv_base[period] - (mile_idx * 0.02)
rv_amt = net_price * rv_rate

# 금융 이자 및 원리금 (수수료 포함)
interest_rate = (0.05 + (agent_fee / 100)) / 12
principal = acq_cost - final_prepay - (rv_amt / (1 + interest_rate)**period)
monthly_fund = (principal * interest_rate * (1 + interest_rate)**period) / ((1 + interest_rate)**period - 1)

# 보험/세금/관리비 합산
monthly_ins = INSURANCE_DB[age][limit] / 12
monthly_tax = (raw_price * 0.005) / 12  # 간이 자동차세 로직
final_rent = int((monthly_fund + monthly_ins + monthly_tax + MONTHLY_MGMT_FEE) * 1.1)

# 6. 결과 출력
st.divider()
res_1, res_2 = st.columns([1.5, 1])

with res_1:
    st.subheader("📋 견적 상세 내역")
    out_data = {
        "항목": ["면세가 적용 금액", "최종 취득원가", "선수금액", "보증금액", "잔존가치(인수금)"],
        "금액": [f"{int(net_price):,} 원", f"{int(acq_cost):,} 원", f"{int(final_prepay):,} 원", f"{int(final_deposit):,} 원",
