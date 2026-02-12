import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="장기렌트 실시간 견적기", layout="wide")

# 2. 데이터 베이스 (엑셀 '수치' 및 '손익' 탭 반영)
INS_DB = {
    "만 26세 이상": {"1억": 45000, "2억": 48000, "3억": 50000},
    "만 21세 이상": {"1억": 58000, "2억": 62000, "3억": 65000}
}
RV_DB = {
    24: {"1만km": 0.65, "2만km": 0.63, "3만km": 0.60},
    36: {"1만km": 0.60, "2만km": 0.58, "3만km": 0.55},
    60: {"1만km": 0.48, "2만km": 0.45, "3만km": 0.40}
}

# 3. 사이드바 - 차량 선택 (모딜 스타일 단계별 선택)
with st.sidebar:
    st.header("🚘 차량 선택")
    brand = st.selectbox("브랜드", ["현대", "기아", "제네시스", "테슬라"])
    car_name = st.text_input("모델명 입력 (예: 그랜저, GV80)", "그랜저")
    raw_price = st.number_input("차량 총 가격 (VAT포함)", value=40000000, step=100000)
    dc_amt = st.number_input("할인 금액 (-)", value=0)
    
    st.header("🗓️ 계약 조건")
    period = st.selectbox("이용기간", [24, 36, 60], index=1)
    mileage = st.selectbox("약정거리", ["1만km", "2만km", "3만km"])

# 4. 메인 화면 - 상세 설정
st.title("📑 실시간 장기렌트 정밀 견적 시스템")

col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 금융 설정")
    # 선수금 설정
    pre_p = st.selectbox("선수금 (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
    pre_v = st.number_input("선수금 직접입력(원)", value=0) if pre_p == "직접입력" else 0
    # 보증금 설정
    dep_p = st.selectbox("보증금 (%)", ["0%", "10%", "20%", "30%", "40%", "직접입력"])
    dep_v = st.number_input("보증금 직접입력(원)", value=0) if dep_p == "직접입력" else 0

with col2:
    st.subheader("🛡️ 보험 및 수수료")
    age = st.radio("보험 연령", ["만 26세 이상", "만 21세 이상"], horizontal=True)
    limit = st.selectbox("대물 한도", ["1억", "2억", "3억"])
    fee = st.select_slider("에이전트 수수료 (%)", options=[1, 2, 3, 4, 5, 6], value=2)

# 5. 핵심 연산 로직 (엑셀 원가 산식)
# 면세가 및 취득원가 계산
net_price = (raw_price - dc_amt) / 1.1
acq_cost = net_price + 250000 + 32300 # 탁송료 + 부대비용

# 선수금/보증금 실제 금액
pre_amt = pre_v if pre_p == "직접입력" else acq_cost * (int(pre_p.replace('%','')) / 100)
dep_amt = dep_v if dep_p == "직접입력" else acq_cost * (int(dep_p.replace('%','')) / 100)

# 잔가 및 렌트료 산출
rv_rate = RV_DB[period][mileage]
rv_amt = net_price * rv_rate

# 원리금 계산 (이자율 반영)
int_rate = (0.05 + (fee / 100)) / 12
principal = acq_cost - pre_amt - (rv_amt / (1 + int_rate)**period)
monthly_fund = (principal * int_rate * (1 + int_rate)**period) / ((1 + int_rate)**period - 1)

# 보험료 및 세금, 관리비 합산
m_ins = INS_DB[age][limit]
m_tax = (raw_price * 0.005) / 12
m_mgmt = 25000 # 인건비 및 관리비
final_rent = int((monthly_fund + m_ins + m_tax + m_mgmt) * 1.1)

# 6. 결과 레이아웃
st.divider()
res1, res2 = st.columns([1.5, 1])

with res1:
    st.subheader("📝 상세 견적 내역")
    res_table = {
        "항목": ["차량 가격(VAT포함)", "취득원가(면세가 기준)", "선수금액", "보증금액", "잔존가치(인수금)"],
        "금액": [f"{int(raw_price):,}원", f"{int(acq_cost):,}원", f"{int(pre_amt):,}원", f"{int(dep_amt):,}원", f"{int(rv_amt):,}원 ({int(rv_rate*100)}%)"]
    }
    st.table(pd.DataFrame(res_table))

with res2:
    st.markdown(f"### 🗓️ {period}개월 / {mileage}")
    st.metric(label="예상 월 납입액", value=f"{final_rent:,} 원")
    st.caption("보험료, 자동차세, 부가세 포함")
    
    if st.button("📋 견적 텍스트 복사"):
        msg = f"[{brand} {car_name} 견적]\n월 대여료: {final_rent:,}원\n기간: {period}개월\n보증/선납: {dep_p}/{pre_p}\n만기인수가: {int(rv_amt):,}원"
        st.code(msg)
