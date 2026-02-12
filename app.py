import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="장기렌트 손익분석 시스템", layout="wide")

# 2. 엑셀 로직 기반 데이터 (수치.csv 내용 반영)
INSURANCE_DATA = {
    "만 26세 이상": {"1억": 850000, "2억": 870000, "3억": 900000},
    "만 21세 이상": {"1억": 1200000, "2억": 1250000, "3억": 1300000}
}

# 3. 화면 구성
st.title("📊 장기렌트 원가 및 손익분석 견적기")

with st.sidebar:
    st.header("차량 및 보험 설정")
    raw_price = st.number_input("차량 출고가 (VAT포함)", value=30000000)
    period = st.selectbox("이용기간", [24, 36, 48, 60], index=2)
    mileage = st.selectbox("약정거리 (연)", ["1만km", "2만km", "3만km"])
    age = st.radio("보험연령", ["만 26세 이상", "만 21세 이상"])
    liability = st.selectbox("대물한도", ["1억", "2억", "3억"])

# 4. 엑셀 '손익' 탭 원가 계산 로직
supply_price = raw_price / 1.1  # 면세가 
total_acq = supply_price + 250000 # 취득원가 (탁송료 포함)

# 잔가율 설정
rv_rate = 0.58 if period == 48 else 0.45
rv_amt = supply_price * rv_rate

# 금융 계산
st.subheader("💰 수수료 및 금융 설정")
agent_fee_p = st.slider("에이전트 수수료 (%)", 1, 6, 2)

# 월 렌트료 산출 (엑셀 수식 기반)
interest = (0.05 + (agent_fee_p / 100)) / 12
principal = total_acq - (rv_amt / (1 + interest)**period)
monthly_fund = (principal * interest * (1 + interest)**period) / ((1 + interest)**period - 1)
final_rent = int((monthly_fund + (INSURANCE_DATA[age][liability]/12) + 20000) * 1.1)

# 결과 출력
st.divider()
st.success(f"### 예상 월 납입액: {final_rent:,} 원")
st.info(f"만기 인수금(잔가): {int(rv_amt):,} 원")
