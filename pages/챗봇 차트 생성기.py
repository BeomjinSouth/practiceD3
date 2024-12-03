import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np
import os
import matplotlib.font_manager as fm

# 페이지 설정은 반드시 최상단에서 실행
st.set_page_config(
    page_title="데이터 차트 생성기",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 'openpyxl' 라이브러리 확인
try:
    import openpyxl
except ImportError:
    st.error("'openpyxl' 라이브러리가 설치되어 있지 않습니다. 터미널에서 'pip install openpyxl' 명령을 실행하여 설치해 주세요.")
    st.stop()

# 현재 파일의 위치를 기준으로 폰트 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
# 폰트 파일이 'pages' 폴더의 상위 디렉토리의 'fonts' 폴더에 있는 경우
font_path = os.path.join(current_dir, '..', 'fonts', 'Maplestory Bold.ttf')

# 디버깅을 위한 경로 출력
st.write(f"현재 작업 디렉토리: {os.getcwd()}")
st.write(f"현재 파일 경로: {current_dir}")
st.write(f"폰트 파일 경로: {font_path}")

if not os.path.exists(font_path):
    st.error(f"폰트 파일을 찾을 수 없습니다: {font_path}")
    st.stop()

# 폰트 등록
fm.fontManager.addfont(font_path)
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)

# Streamlit에 폰트 적용
st.markdown(
    f"""
    <style>
    @font-face {{
        font-family: 'Maplestory Bold';
        src: url('file://{font_path}') format('truetype');
    }}
    html, body, [class*="css"]  {{
        font-family: 'Maplestory Bold', sans-serif;
    }}
    </style>
    """,
    unsafe_allow_html=True
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
        # 파일 확장자에 따라 처리
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error("지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 업로드하세요.")
            data = None

        st.sidebar.success("데이터가 성공적으로 업로드되었습니다.")
    except UnicodeDecodeError:
        st.sidebar.error("파일 인코딩 문제로 읽을 수 없습니다. 파일의 인코딩 방식을 확인하세요.")
        data = None
    except Exception as e:
        st.sidebar.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        data = None
else:
    data = None

# 차트 선택
chart_options = ["줄기와 잎 그림", "히스토그램", "도수분포표", "도수분포다각형", "히스토그램+도수분포다각형"]
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
            if chart_type in ["히스토그램", "도수분포다각형", "히스토그램+도수분포다각형"]:
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
                line_color = st.sidebar.color_picker(
                    "도수분포다각형 색상 선택:",
                    value="#FF0000",
                    help="도수분포다각형의 색상을 선택합니다."
                )
                line_style = st.sidebar.selectbox(
                    "선 스타일 선택:",
                    ["-", "--", "-.", ":"],
                    help="차트의 선 스타일을 선택합니다."
                )
            if chart_type == "도수분포표":
                # 도수분포표 열 이름 설정
                class_interval_label = st.sidebar.text_input(
                    "계급 구간 열 이름:",
                    value="계급 구간",
                    help="계급 구간 열의 제목을 입력합니다."
                )
                frequency_label = st.sidebar.text_input(
                    "빈도수 열 이름:",
                    value="빈도수",
                    help="빈도수 열의 제목을 입력합니다."
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
                    stem_leaf = pd.DataFrame({'줄기': stems, '잎': leaves})
                    stem_leaf.sort_values(by=['줄기', '잎'], inplace=True)
                    grouped = stem_leaf.groupby('줄기')['잎'].apply(lambda x: ' '.join(x.astype(str))).reset_index()
                    st.write("**줄기와 잎 그림**")
                    st.table(grouped.style.hide_index())  # 인덱스 숨기기
                elif chart_type == "도수분포표":
                    # 도수분포표 생성
                    bins = np.arange(bin_start, data[column].max() + bin_width, bin_width)
                    labels = [f"{bins[i]} ~ {bins[i+1]}" for i in range(len(bins)-1)]
                    freq_series = pd.cut(data[column], bins=bins, labels=labels, right=False)
                    freq_table = freq_series.value_counts().sort_index().reset_index()
                    freq_table.columns = [class_interval_label, frequency_label]
                    st.write("**도수분포표**")
                    st.table(freq_table.style.hide_index())  # 인덱스 숨기기
                    # 도수분포표 다운로드 기능 추가
                    csv = freq_table.to_csv(index=False)
                    st.download_button(
                        label="도수분포표 다운로드 (CSV)",
                        data=csv,
                        file_name="frequency_table.csv",
                        mime="text/csv"
                    )
                else:
                    # 히스토그램, 도수분포다각형 또는 히스토그램+도수분포다각형 생성
                    bins = np.arange(bin_start, data[column].max() + bin_width, bin_width)
                    fig, ax = plt.subplots()
                    if chart_type == "히스토그램":
                        ax.hist(data[column], bins=bins, color=color, edgecolor='black')
                    elif chart_type == "도수분포다각형":
                        counts, bins = np.histogram(data[column], bins=bins)
                        bin_centers = 0.5 * (bins[:-1] + bins[1:])
                        ax.plot(bin_centers, counts, linestyle=line_style, color=line_color)
                    elif chart_type == "히스토그램+도수분포다각형":
                        ax.hist(data[column], bins=bins, color=color, edgecolor='black', alpha=0.5)
                        counts, bins = np.histogram(data[column], bins=bins)
                        bin_centers = 0.5 * (bins[:-1] + bins[1:])
                        ax.plot(bin_centers, counts, linestyle=line_style, color=line_color)
                    ax.set_xlabel(x_label)
                    ax.set_ylabel(y_label)
                    ax.set_title(chart_title)
                    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # y축을 정수로
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
                    plt.close(fig)
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
    with st.spinner("개선 사항을 생성 중입니다..."):
        st.markdown("### 💡 개선 사항 제안")
        st.write("데이터의 분포를 더 잘 이해하기 위해 다른 차트 유형을 시도해 보세요. 또는 데이터의 이상치를 확인하고 제거해 볼 수 있습니다.")

# 힌트 제공 버튼 기능
if hint_btn and data is not None and column is not None:
    with st.spinner("힌트를 생성 중입니다..."):
        st.markdown("### 📝 힌트")
        st.write(f"{chart_type}을 분석할 때 데이터의 중앙값이나 분산을 고려해 보세요.")

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
