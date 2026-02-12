import streamlit as st
import pandas as pd

# --- [설정 단계] 실제 렌트사 운영 데이터 (이 부분을 나중에 엑셀 등으로 연동 가능) ---
VEHICLE_DATA = {
    "현대": {
        "아반떼": {
            "하이브리드": {
                "스마트": {"price": 24730000, "options": {"네비게이션": 1500000, "선루프": 500000}},
                "인스퍼레이션": {"price": 28220000, "options": {"선루프": 500000, "빌트인캠": 700000}}
            }
        },
        "그랜저": {
            "가솔린 2.5": {
                "프리미엄": {"price": 37680000, "options": {"HUD": 1000000}},
            }
        }
    }
}

# 기간 및 거리별 잔존가치 테이블 (예시: 48개월/2만km 일 때 60%)
RV_TABLE = {
    48: {"1만km": 62, "2만km": 60, "3만km": 55},
    60: {"1만km": 55, "2만km": 53, "3만km": 48}
}

# --- [메인 로직] ---
st.set_page_config(page_title="레드캡렌터카 견적시스템", layout="wide")
st.title(" 레드캡렌터카 상세 견적서")

# 사이드바: 차량 선택 섹션
with st.sidebar:
    st.header("1. 차량 정보 선택")
    maker = st.selectbox("메이커", list(VEHICLE_DATA.keys()))
    model = st.selectbox("차종", list(VEHICLE_DATA[maker].keys()))
    fuel = st.selectbox("연료", list(VEHICLE_DATA[maker][model].keys()))
    trim = st.selectbox("트림", list(VEHICLE_DATA[maker][model][fuel].keys()))
    
    selected_v = VEHICLE_DATA[maker][model][fuel][trim]
    base_price = selected_v["price"]
    
    # 옵션 다중 선택
    options = st.multiselect("추가 옵션", list(selected_v["options"].keys()))
    option_price = sum([selected_v["options"][opt] for opt in options])
    
    total_car_price = base_price + option_price

# 메인 화면: 계약 및 금융 조건
col1, col2 = st.columns(2)

with col1:
    st.subheader("🗓 계약 조건")
    period = st.radio("이용기간", [24, 36, 48, 60], index=2, horizontal=True)
    mileage = st.selectbox("약정거리", ["1만km", "1.5만km", "2만km", "2.5만km", "3만km", "4만km"])
    
    st.subheader("🛡 보험 및 서비스")
    age = st.radio("보험 연령", ["만 26세 이상", "만 21세 이상"], horizontal=True)
    liability = st.select_slider("대물보험 한도", options=["1억", "2억", "3억"])
    deductible = st.text_input("면책금", value="30만원", disabled=True)

with col2:
    st.subheader("💰 금융 조건")
    prepay_p = st.selectbox("선수금 (%)", [0, 10, 20, 30, 40, "직접입력"])
    if prepay_p == "직접입력":
        prepay_amt = st.number_input("선수금 금액(원)", value=0)
    else:
        prepay_amt = total_car_price * (prepay_p / 100)
        
    deposit_p = st.selectbox("보증금 (%)", [0, 10, 20, 30, 40, "직접입력"])
    if deposit_p == "직접입력":
        deposit_amt = st.number_input("보증금 금액(원)", value=0)
    else:
        deposit_amt = total_car_price * (deposit_p / 100)

    fee_rate = st.select_slider("에이전트 수수료 (%)", options=[1, 2, 3, 4, 5, 6], value=2)

# --- 정교한 계산 엔진 (수식 반영) ---
# 1. 잔가 자동 적용
rv_rate = RV_TABLE.get(period, {}).get(mileage, 45) / 100
rv_amt = total_car_price * rv_rate

# 2. 세금 및 비용 (면세가, 특소세 등 간이 반영)
tax_benefit = total_car_price * 0.05 # 하이브리드/전기차 감면액 예시
final_calc_price = total_car_price - tax_benefit

# 3. 월 렌트료 산출 (이자율 + 보험료 + 자동차세 + 관리비 포함)
# 실제 렌트료는 (취득원가 - 잔가)에 대한 원금상환액 + 이자 + 보험료로 구성됩니다.
interest_rate = 0.07 + (fee_rate / 100) # 기본이율 7% + 수수료 가산
monthly_interest = interest_rate / 12

# (단순화된 렌트료 공식)
principal = final_calc_price - prepay_amt - (rv_amt / (1 + monthly_interest)**period)
monthly_rent = (principal * monthly_interest * (1 + monthly_interest)**period) / ((1 + monthly_interest)**period - 1)

# --- 견적서 출력 (첨부 이미지 스타일) ---
st.divider()
st.header(f"{maker} {model} {fuel} 견적서")
st.write(f"날짜: 2026-02-12")

res_col1, res_col2 = st.columns([2, 1])

with res_col1:
    st.table(pd.DataFrame({
        "항목": ["출고가(계산서가)", "합계 금액", "보증금", "선수금", "약정거리", "잔존가치"],
        "내용": [f"{total_car_price:,} 원", f"{final_calc_price:,} 원", 
                f"{deposit_amt:,} 원 ({deposit_p}%)", f"{prepay_amt:,} 원 ({prepay_p}%)",
                f"{mileage}/연", f"{rv_rate*100}% / {int(rv_amt):,} 원"]
    }))

with res_col2:
    st.metric(label="월 납입액 (VAT 포함)", value=f"{int(monthly_rent):,} 원")
    st.info(f"인수 총 비용: {int(monthly_rent * period + rv_amt + prepay_amt):,} 원")

st.button("PDF로 저장하기 (준비중)")

