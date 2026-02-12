import streamlit as st

# --- [초기 설정] 엑셀 '수치' 탭의 주요 상수 ---
TAX_RATE = 0.07  # 취득세율
INSURANCE_DATA = {
    "만 26세 이상": {"1억": 850000, "2억": 870000, "3억": 900000},
    "만 21세 이상": {"1억": 1200000, "2억": 1250000, "3억": 1300000}
}
MAINTENANCE_FEE = 15000  # 월 관리비(인건비 등)

st.set_page_config(page_title="장기렌트 손익분석 시스템", layout="wide")

# 사이드바: 엑셀의 'DATA' 탭 역할 (입력부)
with st.sidebar:
    st.header("🛒 차량 및 옵션 선택")
    maker = st.selectbox("메이커", ["현대", "기아", "제네시스", "수입차"])
    raw_price = st.number_input("차량 출고가 (VAT포함)", value=30000000, step=10000)
    discount = st.number_input("차량 할인액 (-)", value=0)
    consignment = st.number_input("탁송료 (+)", value=250000)

    st.header("⚙️ 계약 및 보험")
    period = st.selectbox("이용기간", [24, 36, 48, 60], index=2)
    mileage = st.selectbox("약정거리 (연)", ["1만", "2만", "3만", "4만"])
    age = st.radio("보험연령", ["만 26세 이상", "만 21세 이상"])
    liability = st.selectbox("대물한도", ["1억", "2억", "3억"])

# 메인 화면: 계산 로직
st.title("📊 장기렌트 원가 및 손익 분석 견적")

# 1. 면세가 및 취득원가 계산 (엑셀 로직 반영)
supply_price = (raw_price - discount) / 1.1 # 면세가 추정
total_acquisition = supply_price + consignment # 취득원가

# 2. 잔존가치 자동 설정 (기간/거리별)
rv_rates = {48: {"1만": 0.60, "2만": 0.58, "3만": 0.55}, 60: {"1만": 0.55, "2만": 0.50, "3만": 0.45}}
rv_rate = rv_rates.get(period, {}).get(mileage, 0.40)
rv_amount = supply_price * rv_rate

# 3. 금융 조건 (에이전트 수수료 포함)
st.subheader("💰 금융 및 수수료 설정")
col1, col2, col3 = st.columns(3)
with col1:
    prepay_p = st.selectbox("선수금 (%)", [0, 10, 20, 30, 40], index=0)
with col2:
    deposit_p = st.selectbox("보증금 (%)", [0, 10, 20, 30, 40], index=0)
with col3:
    agent_fee_p = st.slider("에이전트 수수료 (%)", 1, 6, 2)

# 선수금 및 보증금 계산
prepay_amt = total_acquisition * (prepay_p / 100)
deposit_amt = total_acquisition * (deposit_p / 100)

# 4. 월 렌트료 산출 (원가 + 보험 + 세금 + 마진)
annual_interest = 0.05 + (agent_fee_p / 100) # 기본금리 + 수수료
monthly_ins = INSURANCE_DATA[age][liability] / 12
monthly_tax = (total_acquisition * 0.005) # 간이 자동차세 로직

# 원리금 균등 상환 방식 적용
principal = total_acquisition - prepay_amt - (rv_amount / (1 + (annual_interest/12))**period)
monthly_fund = (principal * (annual_interest/12)) / (1 - (1 + (annual_interest/12))**-period)
final_monthly_rent = int((monthly_fund + monthly_ins + monthly_tax + MAINTENANCE_FEE) * 1.1)

# --- 결과 출력 ---
st.divider()
c_res1, c_res2 = st.columns([1, 1])

with c_res1:
    st.info("### 최종 월 납입액 (VAT포함)")
    st.write(f"## {final_monthly_rent:,} 원")

with c_res2:
    st.warning("### 만기 인수금 (잔존가치)")
    st.write(f"## {int(rv_amount)::,} 원")

st.table({
    "구분": ["공급가액(면세)", "취득원가", "선수금액", "보증금액", "보험조건", "에이전트 수수료"],
    "상세 내용": [f"{int(supply_price):,}원", f"{int(total_acquisition):,}원", f"{int(prepay_amt):,}원", 
              f"{int(deposit_amt):,}원", f"{age} / 대물 {liability}", f"{agent_fee_p}% 포함"]
})
