import streamlit as st
import pandas as pd

# 페이지 설정 (에이전트 모바일 사용 고려)
st.set_page_config(page_title="렌트매니저 Pro", layout="centered")

def calculate_quote(car_price, period, deposit_rate, prepayment_rate, rv_rate, commission_rate):
    # 1. 초기 비용 계산
    acquisition_tax = int(car_price * 0.07) # 취득세 7% 고정
    total_car_price = car_price + acquisition_tax
    
    deposit_amt = int(car_price * (deposit_rate / 100))
    prepayment_amt = int(car_price * (prepayment_rate / 100))
    rv_amt = int(car_price * (rv_rate / 100))
    
    # 2. 대여료 산출 로직 (간이 공식: 할부 금융 방식 원리금 계산 적용)
    # 실제 렌트사는 리스료 산정 알고리즘이 복잡하므로 에이전트용 마진율(commission_rate)을 가산함
    annual_interest = 0.06 + (commission_rate / 100) # 기본 6% + 에이전트 마진
    monthly_interest = annual_interest / 12
    
    # 할부 원금 = (차량가 + 취득세) - 선납금 - (잔가 / (1+이자)^기간)
    # 실제로는 잔가에 대한 이자도 포함되므로 아래와 같이 단순화
    principal = total_car_price - prepayment_amt - (rv_amt / (1 + monthly_interest)**period)
    
    if monthly_interest > 0:
        monthly_fee = (principal * monthly_interest * (1 + monthly_interest)**period) / ((1 + monthly_interest)**period - 1)
    else:
        monthly_fee = principal / period
        
    return {
        "monthly_fee": int(monthly_fee),
        "deposit": deposit_amt,
        "prepayment": prepayment_amt,
        "rv": rv_amt,
        "tax": acquisition_tax
    }

# --- UI 레이아웃 ---
st.title("🚗 장기렌트 견적 매니저 Pro")
st.caption("에이전트 배포용 프로토타입 v1.0")

with st.container():
    st.subheader("1. 차량 기본 정보")
    car_price = st.number_input("차량가 (VAT 포함, 원)", value=35000000, step=100000)
    
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("계약 기간", [24, 36, 48, 60], index=2)
    with col2:
        rv_rate = st.slider("잔존가치 (%)", 30, 55, 45)

st.divider()

with st.container():
    st.subheader("2. 금융 조건 설정")
    c1, c2 = st.columns(2)
    with c1:
        deposit_rate = st.slider("보증금 (%)", 0, 50, 0, step=10)
    with c2:
        prepayment_rate = st.slider("선납금 (%)", 0, 50, 0, step=10)
    
    # 에이전트 전용 마진 설정 (접이식 메뉴로 숨김)
    with st.expander("🛠 에이전트 전용 설정 (마진)"):
        comm_rate = st.slider("추가 마진 이율 (%)", 0.0, 5.0, 1.5)

# --- 결과 출력 ---
res = calculate_quote(car_price, period, deposit_rate, prepayment_rate, rv_rate, comm_rate)

st.success(f"### 예상 월 대여료: {res['monthly_fee']:,} 원")

# 상세 견적 테이블
df_res = pd.DataFrame({
    "항목": ["차량가", "취득세(7%)", "보증금", "선납금", "만기인수가(잔가)"],
    "금액": [f"{car_price:,}원", f"{res['tax']:,}원", f"{res['deposit']:,}원", f"{res['prepayment']:,}원", f"{res['rv']:,}원"]
})
st.table(df_res)

if st.button("견적 결과 복사하기"):
    summary = f"[장기렌트 견적]\n차량가: {car_price:,}원\n기간: {period}개월\n보증/선납: {deposit_rate}/{prepayment_rate}%\n월 대여료: {res['monthly_fee']:,}원"
    st.write("아래 내용을 복사하여 고객에게 전달하세요:")
    st.code(summary)