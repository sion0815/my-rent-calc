import streamlit as st
import pandas as pd

# --- [초기 설정] 엑셀 '수치' 탭 기반 데이터 ---
# 보험료 및 세금 (엑셀의 수치.csv 기반)
INSURANCE_DB = {
    "만 26세 이상": {"1억": 850000, "2억": 875000, "3억": 900000},
    "만 21세 이상": {"1억": 1250000, "2억": 1280000, "3억": 1320000}
}
MONTHLY_MANAGEMENT_FEE = 15000 # 차량관리비 및 인건비

# 차량 데이터 샘플 (실제 데이터에 맞춰 확장 가능)
VEHICLE_DB = {
    "현대": {
        "아반떼": {
            "하이브리드": {
                "스마트": 24730000,
                "인스퍼레이션": 28220000
            },
            "가솔린 1.6": {
                "스마트": 19970000
            }
        }
    },
    "기아": {
        "K5": {
            "가솔린 2.0": {"프레스티지": 28550000}
        }
    }
}

# --- UI 레이아웃 ---
st.set_page_config(page_title="장기렌트 손익분석 시스템", layout="wide")
st.title("📑 전문가용 장기렌트 정밀 견적 시스템")

# 1. 차종 세부 선택 (사이드바)
with st.sidebar:
    st.header("1. 차량 세부 선택")
    maker = st.selectbox("메이커", list(VEHICLE_DB.keys()))
    model = st.selectbox("차종", list(VEHICLE_DB[maker].keys()))
    fuel = st.selectbox("연료", list(VEHICLE_DB[maker][model].keys()))
    trim = st.selectbox("트림", list(VEHICLE_DB[maker][model][fuel].keys()))
    
    base_price = VEHICLE_DB[maker][model][fuel][trim]
    st.write(f"기본가: {base_price:,}원")
    
    options_total = st.number_input("추가 옵션 총액(원)", value=0, step=10000)
    discount_amt = st.number_input("차량 할인율/할인액(원)", value=0)
    total_raw_price = base_price + options_total - discount_amt

# 2. 계약 및 보험 조건
col1, col2 = st.columns(2)
with col1:
    st.subheader("🗓 계약 조건")
    period = st.selectbox("이용기간", [24, 36, 48, 60], index=2)
    mileage = st.selectbox("약정거리", ["1만km", "1.5만km", "2만km", "2.5만km", "3만km", "4만km"])
    
    # 잔가율 자동 적용 (예시 테이블)
    rv_map = {24: 0.65, 36: 0.60, 48: 0.55, 60: 0.45}
    rv_rate = rv_map[period] - (["1만km", "1.5만km", "2만km", "2.5만km", "3만km", "4만km"].index(mileage) * 0.02)
    
    st.subheader("🛡 보험 설정")
    ins_age = st.radio("보험 연령", ["만 26세 이상", "만 21세 이상"], horizontal=True)
    ins_limit = st.selectbox("대물보험 한도", ["1억", "2억", "3억"])
    st.caption("자손: 1억/1천5백, 면책금: 30만원 고정")

with col2:
    st.subheader("💰 금융 조건")
    def get_amt(label):
        choice = st.selectbox(f"{label} (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
        if choice == "직접입력":
            return st.number_input(f"{label} 직접입력(원)", value=0)
        return total_raw_price * (int(choice.replace('%','')) / 100)

    prepay_amt = get_amt("선수금")
    deposit_amt = get_amt("보증금")
    agent_fee = st.select_slider("에이전트 수수료 (%)", options=[1, 2, 3, 4, 5, 6], value=2)

# --- 3. 원가 및 렌트료 연산 (엑셀 손익 탭 로직) ---
# 면세가/특소세 산출
tax_free_price = total_raw_price / 1.1 
consignment_fee = 250000 # 탁송료 예시
acquisition_cost = tax_free_price + consignment_fee # 취득원가

# 월 보험료 및 세금
monthly_ins = INSURANCE_DB[ins_age][ins_limit] / 12
monthly_car_tax = (total_raw_price * 0.005) / 12 # 자동차세 간이계산

# 금리 산출 (원가이율 + 에이전트 마진)
final_interest = (0.06 + (agent_fee / 100)) / 12
rv_value = tax_free_price * rv_rate

# 원리금 산출
principal = acquisition_cost - prepay_amt - (rv_value / (1 + final_interest)**period)
monthly_fund = (principal * final_interest * (1 + final_interest)**period) / ((1 + final_interest)**period - 1)

# 최종 렌트료 (VAT 포함)
final_rent = int((monthly_fund + monthly_ins + monthly_car_tax + MONTHLY_MANAGEMENT_FEE) * 1.1)

# --- 결과 출력 (이미지 스타일) ---
st.divider()
res_col1, res_col2 = st.columns([1.5, 1])

with res_col1:
    st.subheader(f"📊 {model} {fuel} 상세 견적")
    data = {
        "항목": ["출고가(합계)", "취득원가(면세+탁송)", "보증금액", "선수금액", "잔존가치(인수금)"],
        "금액": [f"{int(total_raw_price):,}원", f"{int(acquisition_cost):,}원", 
                f"{int(deposit_amt):,}원", f"{int(prepay_amt):,}원", f"{int(rv_value):,}원 ({int(rv_rate*100)}%)"]
