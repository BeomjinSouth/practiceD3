import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

# Streamlit 앱 설정
st.set_page_config(
    page_title="데이터 차트 생성기",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 사용자 매뉴얼 섹션
with st.expander("📖 사용자 매뉴얼"):
    st.markdown("""
    ### 사용 방법
    1. **데이터 업로드**: 왼쪽 사이드바에서 CSV 또는 Excel 파일을 업로드하세요.
    2. **차트 설정**: 생성할 차트 유형과 관련 옵션을 선택하세요.
    3. **차트 생성**: '차트 생성' 버튼을 클릭하여 차트를 생성합니다.
    4. **결과 확인 및 저장**:
       - 생성된 차트를 확인하고 다운로드할 수 있습니다.
       - 도수분포표의 경우, 데이터를 CSV 파일로 다운로드할 수 있습니다.
    5. **개선 사항 및 힌트**:
       - **개선 사항 제안**: '개선 사항 제안' 버튼을 클릭하여 데이터나 차트의 개선 아이디어를 받아보세요.
       - **힌트 제공**: '힌트 제공' 버튼을 클릭하여 데이터 분석에 도움이 되는 간접적인 힌트를 받아보세요.
    """)

# 사이드바 설정
st.sidebar.header("🗂 데이터 및 설정")

# 데이터 파일 업로드
uploaded_file = st.sidebar.file_uploader(
    "CSV 또는 Excel 파일을 업로드하세요",
    type=["csv", "xlsx"],
    help="데이터 분석을 위한 CSV 또는 Excel 파일을 업로드합니다."
)

# 데이터 읽기 및 표시
if uploaded_file:
    try:
        # 파일 형식에 따라 데이터 읽기
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)
        
        st.sidebar.success("데이터가 성공적으로 업로드되었습니다.")
    except Exception as e:
        st.sidebar.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        data = None
else:
    data = None

# 차트 선택
chart_options = ["줄기와 잎 그림", "히스토그램", "도수분포표", "도수분포다각형"]
chart_type = st.sidebar.selectbox(
    "생성할 차트를 선택하세요:",
    chart_options,
    help="생성하고자 하는 차트의 유형을 선택합니다."
)

# 컬럼 선택 및 추가 설정
if data is not None:
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_columns:
        st.error("숫자형 데이터가 포함된 컬럼이 없습니다.")
        column = None
    else:
        # 공통 옵션
        column = st.sidebar.selectbox(
            "데이터 컬럼 선택:",
            numeric_columns,
            help="차트를 생성할 때 사용할 데이터 컬럼을 선택합니다."
        )
        
        # 차트별 옵션
        if chart_type == "줄기와 잎 그림":
            # 줄기와 잎 그림 옵션
            stem_unit = st.sidebar.number_input(
                "줄기의 자릿수 (예: 1, 10, 100):",
                value=1,
                min_value=1,
                help="줄기와 잎 그림에서 줄기의 자릿수를 설정합니다."
            )
        else:
            # 계급 간격 및 시작 값 설정
            bin_width = st.sidebar.number_input(
                "계급의 간격 (bin width):",
                value=5.0,
                min_value=0.1,
                help="히스토그램 등에서 계급의 간격을 설정합니다."
            )
            bin_start = st.sidebar.number_input(
                "계급의 시작 값:",
                value=float(data[column].min()),
                help="계급이 시작되는 값을 설정합니다."
            )
            # 히스토그램 및 도수분포다각형 추가 옵션
            if chart_type in ["히스토그램", "도수분포다각형"]:
                x_label = st.sidebar.text_input(
                    "X축 레이블:",
                    value=column,
                    help="X축의 레이블을 입력합니다."
                )
                y_label = st.sidebar.text_input(
                    "Y축 레이블:",
                    value="빈도수",
                    help="Y축의 레이블을 입력합니다."
                )
                chart_title = st.sidebar.text_input(
                    "차트 제목:",
                    value=chart_type,
                    help="차트의 제목을 입력합니다."
                )
                color = st.sidebar.color_picker(
                    "차트 색상 선택:",
                    value="#0000FF",
                    help="차트의 색상을 선택합니다."
                )
                line_style = st.sidebar.selectbox(
                    "선 스타일 선택:",
                    ["-", "--", "-.", ":"],
                    help="차트의 선 스타일을 선택합니다."
                )
else:
    column = None

# 메인 화면
st.header("📊 차트 생성 및 결과")

# 버튼들 정렬
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    generate_btn = st.button("차트 생성")
with col2:
    reset_btn = st.button("초기화")
with col3:
    suggest_btn = st.button("개선 사항 제안")
with col4:
    hint_btn = st.button("힌트 제공")

# 초기화 버튼 기능
if reset_btn:
    st.experimental_rerun()

# 차트 생성
if generate_btn and data is not None and column is not None:
    # 입력 값 검증
    if chart_type != "줄기와 잎 그림" and bin_width <= 0:
        st.error("계급 간격은 0보다 커야 합니다.")
    else:
        with st.spinner("차트를 생성 중입니다..."):
            try:
                if chart_type == "줄기와 잎 그림":
                    # 줄기와 잎 그림 생성
                    df = data[column].dropna()
                    stems = (df // stem_unit).astype(int)
                    leaves = (df % stem_unit).astype(int)
                    stem_leaf = pd.DataFrame({'Stem': stems, 'Leaf': leaves})
                    stem_leaf.sort_values(by=['Stem', 'Leaf'], inplace=True)
                    grouped = stem_leaf.groupby('Stem')['Leaf'].apply(lambda x: ' '.join(x.astype(str))).reset_index()
                    st.write("**줄기와 잎 그림**")
                    st.table(grouped)
                elif chart_type == "도수분포표":
                    # 도수분포표 생성
                    bins = np.arange(bin_start, data[column].max() + bin_width, bin_width)
                    freq_table = pd.cut(data[column], bins=bins, right=False).value_counts().sort_index().reset_index()
                    freq_table.columns = ['계급 구간', '빈도수']
                    st.write("**도수분포표**")
                    st.table(freq_table)
                    # 도수분포표 다운로드 기능 추가
                    csv = freq_table.to_csv(index=False)
                    st.download_button(
                        label="도수분포표 다운로드 (CSV)",
                        data=csv,
                        file_name="frequency_table.csv",
                        mime="text/csv"
                    )
                else:
                    # 히스토그램 또는 도수분포다각형 생성
                    bins = np.arange(bin_start, data[column].max() + bin_width, bin_width)
                    fig, ax = plt.subplots()
                    counts, bins, patches = ax.hist(data[column], bins=bins, color=color, edgecolor='black')
                    if chart_type == "도수분포다각형":
                        bin_centers = 0.5 * (bins[:-1] + bins[1:])
                        ax.plot(bin_centers, counts, linestyle=line_style, color=color)
                    ax.set_xlabel(x_label)
                    ax.set_ylabel(y_label)
                    ax.set_title(chart_title)
                    st.pyplot(fig)
                    # 차트 다운로드
                    buf = BytesIO()
                    fig.savefig(buf, format="png")
                    buf.seek(0)
                    st.download_button(
                        label="차트 다운로드",
                        data=buf,
                        file_name="chart.png",
                        mime="image/png"
                    )
                    buf.close()
            except Exception as e:
                st.error(f"차트를 생성하는 데 오류가 발생했습니다: {e}")
else:
    if data is None:
        st.info("CSV 또는 Excel 파일을 업로드하세요.")
    elif column is None:
        st.info("적절한 데이터 컬럼을 선택하세요.")
    else:
        st.info("필요한 옵션을 선택하고 '차트 생성'을 클릭하세요.")

# 개선 사항 제안 버튼 기능
if suggest_btn and data is not None and column is not None:
    with st.spinner("GPT-4o를 사용해 개선 사항을 생성 중입니다..."):
        prompt = f"""
        현재 생성된 {chart_type}에 대한 개선 사항을 제안해 주세요. 데이터 분석 및 시각화 측면에서 유용한 아이디어를 제공합니다.
        데이터: {data[column].dropna().tolist()}
        차트 설정: 계급 간격={bin_width if 'bin_width' in locals() else 'N/A'}, 시작 값={bin_start if 'bin_start' in locals() else 'N/A'}, 색상={color if 'color' in locals() else 'N/A'}, 선 스타일={line_style if 'line_style' in locals() else 'N/A'}
        """
        response = client.completions.create(
            engine="gpt-4o",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        suggestions = response["choices"][0]["text"]
        st.markdown("### 💡 개선 사항 제안")
        st.write(suggestions)

# 힌트 제공 버튼 기능
if hint_btn and data is not None and column is not None:
    with st.spinner("GPT-4o를 사용해 힌트를 생성 중입니다..."):
        prompt = f"""
        학생들이 {chart_type}을(를) 분석할 때 도움이 되는 간접적인 힌트를 발문의 형태로 제공해 주세요.
        데이터: {data[column].dropna().tolist()}
        """
        response = client.completions.create(
            engine="gpt-4o",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        hints = response["choices"][0]["text"]
        st.markdown("### 📝 힌트")
        st.write(hints)

# CSS 스타일 적용
st.markdown(
    """
    <style>
    .stButton>button {
        height: 3em;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)
