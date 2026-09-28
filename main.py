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


# 가장 많이 몰려 있는 구간 계산
bin_counts = pd.cut(
    histogram_data["total_audi"],
    bins=20
).value_counts().sort_index()

most_common_bin = bin_counts.idxmax()

range_start = int(most_common_bin.left)
range_end = int(most_common_bin.right)


# 총 관객이 가장 많은 영화 찾기
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


# ==================================================
# 그래프 4. 개봉일 스크린 수와 총 관객의 관계
# ==================================================
st.header("📊 그래프 4. 개봉일 스크린 수와 총 관객의 관계")

scatter_data = df[
    ["movieNm", "genre", "first_scrn", "total_audi"]
].copy()

scatter_data = scatter_data.dropna(
    subset=["movieNm", "genre", "first_scrn", "total_audi"]
)

scatter_data = scatter_data[
    (scatter_data["first_scrn"] > 0)
    & (scatter_data["total_audi"] > 0)
]


fig4 = px.scatter(
    scatter_data,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린 수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre": "장르"
    }
)

fig4.update_traces(
    hovertemplate=(
        "영화명: %{hovertext}<br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    legend_title="장르"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: "
    "영화의 개봉일 스크린 수와 총 관객 수가 어떤 관계를 보이는지, "
    "그리고 장르별 영화들이 어느 위치에 분포하는지 살펴볼 수 있습니다."
)


# ==================================================
# 그래프 5. 장르별 총 관객 수 박스플롯
# ==================================================
st.header("📊 그래프 5. 장르별 총 관객 수 분포")

# 영화가 10편 이상인 장르 찾기
genre_counts = (
    df["genre"]
    .value_counts()
)

selected_genres = genre_counts[
    genre_counts >= 10
].index


boxplot_data = df[
    df["genre"].isin(selected_genres)
][
    ["genre", "movieNm", "total_audi"]
].copy()

boxplot_data = boxplot_data.dropna(
    subset=["genre", "movieNm", "total_audi"]
)

boxplot_data = boxplot_data[
    boxplot_data["total_audi"] > 0
]


fig5 = px.box(
    boxplot_data,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    title="영화가 10편 이상인 장르의 총 관객 수 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객 수"
    }
)

fig5.update_traces(
    hovertemplate=(
        "영화명: %{hovertext}<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: "
    "영화가 10편 이상인 장르에서 총 관객 수가 어떻게 분포하는지와 "
    "일반적인 범위에서 크게 벗어난 영화가 무엇인지 살펴볼 수 있습니다."
)


# ==================================================
# 그래프 6. 개봉일 스크린 수와 총 관객의 버블 그래프
# ==================================================
st.header("📊 그래프 6. 개봉일 스크린 수와 총 관객의 관계 - 버블 그래프")

bubble_data = df[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
].copy()

# 필요한 데이터가 없는 행 제거
bubble_data = bubble_data.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
)

# 0 이하의 값 제거
bubble_data = bubble_data[
    (bubble_data["first_scrn"] > 0)
    & (bubble_data["total_audi"] > 0)
    & (bubble_data["first_week_audi"] > 0)
]


fig6 = px.scatter(
    bubble_data,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=45,
    title="개봉일 스크린 수와 총 관객의 관계 - 첫 주 관객을 크기로 표현",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "first_week_audi": "첫 주 관객",
        "genre": "장르"
    }
)

fig6.update_traces(
    hovertemplate=(
        "영화명: %{hovertext}<br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{marker.size:,}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    legend_title="장르"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: "
    "개봉일 스크린 수와 총 관객 수의 관계를 살펴보면서, "
    "첫 주 관객이 많은 영화가 어떤 위치에 분포하는지도 함께 확인할 수 있습니다."
)


# ==================================================
# 그래프 7. 제작 국가 → 장르 선버스트
# ==================================================
st.header("📊 그래프 7. 제작 국가와 장르의 관계")

sunburst_data = df[
    ["nation", "genre"]
].copy()

# 제작 국가와 장르가 없는 데이터 제거
sunburst_data = sunburst_data.dropna(
    subset=["nation", "genre"]
)

# 문자열로 변환하고 앞뒤 공백 제거
sunburst_data["nation"] = (
    sunburst_data["nation"]
    .astype(str)
    .str.strip()
)

sunburst_data["genre"] = (
    sunburst_data["genre"]
    .astype(str)
    .str.strip()
)

# 빈 값 제거
sunburst_data = sunburst_data[
    (sunburst_data["nation"] != "")
    & (sunburst_data["genre"] != "")
]


# 국가 × 장르별 영화 편수 계산
sunburst_count = (
    sunburst_data
    .groupby(["nation", "genre"])
    .size()
    .reset_index(name="영화 편수")
)


fig7 = px.sunburst(
    sunburst_count,
    path=["nation", "genre"],
    values="영화 편수",
    title="제작 국가 → 장르별 영화 편수"
)

fig7.update_traces(
    hovertemplate=(
        "%{label}<br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    margin=dict(
        t=60,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: "
    "제작 국가별로 어떤 장르의 영화가 많이 만들어졌는지와 "
    "각 국가와 장르가 전체 영화에서 차지하는 비중을 살펴볼 수 있습니다."
)


# ==================================================
# 그래프 8. 10위권에 어떤 나라의 영화가 많이 포함되었을까?
# ==================================================
st.header("📊 그래프 8. 10위권에 어떤 나라의 영화가 많이 포함되었을까?")

nation_count_data = df[
    ["movieNm", "nation"]
].copy()

# 제작 국가가 없는 데이터 제거
nation_count_data = nation_count_data.dropna(
    subset=["movieNm", "nation"]
)

# 국가 이름 정리
nation_count_data["nation"] = (
    nation_count_data["nation"]
    .astype(str)
    .str.strip()
)

nation_count_data = nation_count_data[
    nation_count_data["nation"] != ""
]

# 국가별 영화 편수 계산
nation_count = (
    nation_count_data["nation"]
    .value_counts()
    .reset_index()
)

nation_count.columns = [
    "제작 국가",
    "영화 편수"
]

# 영화 편수가 많은 국가부터 표시
nation_count = nation_count.sort_values(
    "영화 편수",
    ascending=False
)

fig8 = px.bar(
    nation_count,
    x="제작 국가",
    y="영화 편수",
    title="10위권에 어떤 나라의 영화가 많이 포함되었을까?",
    labels={
        "제작 국가": "영화 제작 국가",
        "영화 편수": "영화 편수"
    },
    text="영화 편수"
)

fig8.update_traces(
    hovertemplate=(
        "제작 국가: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig8.update_layout(
    xaxis_title="영화 제작 국가",
    yaxis_title="영화 편수"
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: "
    "10위권에 포함된 영화의 제작 국가별 편수를 비교하여 "
    "어느 나라의 영화가 많이 포함되었는지 살펴볼 수 있습니다."
)
