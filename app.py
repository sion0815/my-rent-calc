import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="장기렌트 정밀 손익분석", layout="wide")

# 2. 고정 데이터 (엑셀 수치 기반)
INSURANCE_DB = {
    "만 26세 이상": {"1억": 850000, "2억": 880000, "3억": 920000},
    "만 21세 이상": {"1억": 1250000, "2억": 1290000, "3억": 1350000}
}
MONTHLY_MGMT_FEE = 15000 # 관리비/인건비

# 3. 입력부 (사이드바)
with st.sidebar:
    st.header("1. 차량 정보")
    maker = st.selectbox("메이커", ["현대", "기아", "제네시스"])
    raw_price = st.number_input("차량 출고가 (VAT포함)", value=30000000, step=10000)
    dc_amt = st.number_input("차량 할인액 (-)", value=0)
    consignment = st.number_input("탁송료 (+)", value=250000)
    
    st.header("2. 계약 조건")
    period = st.selectbox("이용기간", [24, 36, 60], index=1)
    mileage = st.selectbox("약정거리", ["1만km", "1.5만km", "2만km", "2.5만km", "3만km", "4만km"])
    
    st.header("3. 보험/기타")
    age = st.radio("보험 연령", ["만 26세 이상", "만 21세 이상"])
    limit = st.selectbox("대물 한도", ["1억", "2억", "3억"])

# 4. 금융 조건 (메인)
st.title("📑 장기렌터카 정밀 견적 시스템")
c1, c2, c3 = st.columns(3)

with c1:
    pre_p = st.selectbox("선수금 (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
    pre_v = st.number_input("선수금 직접입력(원)", value=0) if pre_p == "직접입력" else 0
with c2:
    dep_p = st.selectbox("보증금 (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
    dep_v = st.number_input("보
