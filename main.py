import streamlit as st
import pandas as pd
import plotly.express as px


# =======================================
# 기본 설정
# =======================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
)


# =======================================
# 데이터 불러오기
# =======================================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일을 실제 날짜 형식으로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 여러 장르가 "|"로 연결되어 있다면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("알 수 없음")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "movieCd",
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()


# =======================================
# 데이터 확인
# =======================================
st.caption(
    f"분석 대상 영화 수: {len(df):,}편"
)


# =======================================
# 그래프 1
# =======================================
st.header("🍩 그래프 1. 장르별 영화 편수")

# 장르별 영화 편수 계산
genre_count = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]


# 도넛 그래프
fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.5,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    legend_title="장르"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# 그래프로 알 수 있는 것
st.info(
    "이 그래프로 알 수 있는 것: 1년간 10위권에 든 영화가 어떤 장르로 구성되어 있는지와 각 장르의 비중을 확인할 수 있습니다."
)


# =======================================
# 그래프 2
# =======================================
st.header("📊 그래프 2. 추가 예정")

st.write(
    "다음 그래프에서는 영화의 여러 수치 사이의 관계를 분석할 수 있습니다."
)

st.info(
    "이 그래프로 알 수 있는 것: "
)


# =======================================
# 그래프 3
# =======================================
st.header("📊 그래프 3. 추가 예정")

st.write(
    "다음 그래프를 이곳에 추가할 수 있습니다."
)

st.info(
    "이 그래프로 알 수 있는 것: "
)
