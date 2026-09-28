import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 여러 장르가 있는 경우 첫 번째 장르만 사용
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

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


df = load_data()


st.caption(f"분석 대상 영화: {len(df):,}편")


# ==================================================
# 그래프 1. 장르별 영화 편수
# ==================================================
st.header("📊 그래프 1. 장르별 영화 편수")

genre_count = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]


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

st.info(
    "이 그래프로 알 수 있는 것: "
    "1년간 10위권에 든 영화에서 어떤 장르가 많이 나타났는지와 "
    "각 장르의 비중을 알 수 있습니다."
)


# ==================================================
# 그래프 2. 장르별 영화 총 관객 트리맵
# ==================================================
st.header("📊 그래프 2. 장르별 영화 총 관객 트리맵")

treemap_data = df[
    ["genre", "movieNm", "total_audi"]
].copy()

treemap_data = treemap_data.dropna(
    subset=["genre", "movieNm", "total_audi"]
)

treemap_data = treemap_data[
    treemap_data["total_audi"] > 0
]


fig2 = px.treemap(
    treemap_data,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르 안에 영화가 들어 있는 총 관객 트리맵"
)

fig2.update_traces(
    hovertemplate=(
        "영화명: %{label}<br>"
        "총 관객: %{value:,}명"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: "
    "각 장르에 어떤 영화가 포함되어 있는지와 "
    "영화별 총 관객 규모를 한눈에 비교할 수 있습니다."
)


# ==================================================
# 그래프 3. 총 관객 수 분포
# ==================================================
st.header("📊 그래프 3. 영화별 총 관객 수 분포")

histogram_data = df[
    ["movieNm", "total_audi"]
].copy()

histogram_data = histogram_data.dropna(
    subset=["movieNm", "total_audi"]
)

histogram_data = histogram_data[
    histogram_data["total_audi"] > 0
]


fig3 = px.histogram(
    histogram_data,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 히스토그램",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# --------------------------------------------------
# 대부분의 영화가 몰려 있는 구간 계산
# --------------------------------------------------
bin_counts = pd.cut(
    histogram_data["total_audi"],
    bins=20
).value_counts().sort_index()

most_common_bin = bin_counts.idxmax()

range_start = int(most_common_bin.left)
range_end = int(most_common_bin.right)


# --------------------------------------------------
# 총 관객이 가장 많은 영화 찾기
# --------------------------------------------------
max_audience_row = histogram_data.loc[
    histogram_data["total_audi"].idxmax()
]

max_movie_name = max_audience_row["movieNm"]
max_audience = int(max_audience_row["total_audi"])


st.info(
    f"이 그래프로 알 수 있는 것: "
    f"대부분의 영화는 총 관객 약 {range_start:,}명~"
    f"{range_end:,}명 구간에 몰려 있습니다. "
    f"총 관객이 가장 많은 영화는 **{max_movie_name}**이며, "
    f"총 관객은 **{max_audience:,}명**입니다."
)
