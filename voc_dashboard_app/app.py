#!/usr/bin/env python3
"""
VOC Dashboard Streamlit App
월별 VOC 데이터 업로드 및 대시보드 시각화
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
from datetime import datetime
from voc_processor import (
    generate_monthly_data,
    save_monthly_data,
    load_all_monthly_data,
    CATEGORY_COLORS
)

# 페이지 설정
st.set_page_config(
    page_title="VOC Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 테마 CSS 정의
LIGHT_THEME_CSS = """
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">

<style>
    /* Material Symbols 폰트 적용 */
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded' !important;
        font-size: 24px !important;
        visibility: visible !important;
        display: inline-block !important;
    }
    
    /* 사이드바 접기 버튼 숨기기 (깨진 아이콘) */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Streamlit 상단 메뉴 & 푸터 숨기기 */
    #MainMenu,
    [data-testid="stToolbar"],
    footer,
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Pretendard 폰트 적용 */
    * {
        font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* 라이트 모드 배경 */
    .stApp {
        background: linear-gradient(180deg, #FFFFFF 0%, #F7F6F9 100%);
    }
    
    /* 상단 헤더 영역 */
    header[data-testid="stHeader"],
    [data-testid="stHeader"] {
        background: #FFFFFF !important;
    }
    
    /* 메인 컨텐츠 영역 */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main,
    .block-container {
        background: transparent !important;
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #EBEAEE 100%);
        border-right: 1px solid #EBEAEE;
    }
    
    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }
    
    /* 텍스트 색상 */
    .stMarkdown, .stText, p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }
    
    /* 제목 스타일 */
    h1, h2, h3 {
        font-weight: 700 !important;
    }
    
    /* 메트릭 카드 */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,102,0,0.05) 0%, rgba(255,87,216,0.05) 50%, rgba(191,0,255,0.05) 100%);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255,102,0,0.1);
    }
    
    [data-testid="stMetric"] * {
        color: #333333 !important;
    }
    
    /* 버튼 - Spoon Gradient */
    .stButton > button {
        background: linear-gradient(135deg, #FF6600 0%, #FF57D8 50%, #BF00FF 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255,102,0,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,102,0,0.4);
    }
    
    /* Secondary 버튼도 그라디언트 적용 */
    .stButton > button[kind="secondary"],
    button[kind="secondary"] {
        background: linear-gradient(135deg, #FF6600 0%, #FF57D8 50%, #BF00FF 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #FF7700 0%, #FF67E8 50%, #CF10FF 100%) !important;
        color: white !important;
    }
    
    /* 버튼 내부 텍스트도 흰색 볼드 */
    .stButton > button *,
    button[kind="secondary"] *,
    .stButton > button span,
    button[kind="secondary"] span {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input {
        background: #FFFFFF !important;
        color: #333333 !important;
        border: 2px solid #EBEAEE !important;
        border-radius: 12px !important;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FF6600 !important;
        box-shadow: 0 0 0 3px rgba(255,102,0,0.1) !important;
    }
    
    /* 셀렉트박스 */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border: 2px solid #EBEAEE !important;
        border-radius: 12px !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #FF6600 !important;
    }
    
    /* 파일 업로더 */
    [data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 2px dashed #FF6600;
        border-radius: 16px;
        padding: 20px;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
        padding: 8px 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 16px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: 15px;
        color: #333333 !important;
        background: rgba(255,102,0,0.08);
        border: 1px solid rgba(255,102,0,0.15);
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,102,0,0.15);
        transform: translateY(-1px);
    }
    
    .stTabs [aria-selected="true"],
    .stTabs [data-baseweb="tab"][aria-selected="true"],
    .stTabs [data-baseweb="tab"][aria-selected="true"] * {
        background: linear-gradient(135deg, #FF6600 0%, #FF57D8 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(255,102,0,0.3);
    }
    
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Expander 스타일 (사이드바) */
    [data-testid="stExpander"] {
        background: rgba(255,102,0,0.05);
        border-radius: 12px;
        border: 1px solid rgba(255,102,0,0.1);
        margin-top: 8px;
    }
    
    [data-testid="stExpander"] summary {
        padding: 12px 16px;
        font-weight: 500;
    }
    
    [data-testid="stExpander"] svg {
        color: #FF6600 !important;
    }
    
    /* 데이터프레임 */
    .stDataFrame,
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div,
    .stDataFrame iframe {
        background: #FFFFFF !important;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* 테이블 셀 */
    .stDataFrame table,
    .stDataFrame th,
    .stDataFrame td,
    [data-testid="stDataFrame"] table,
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] td {
        background: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* 테이블 헤더 */
    .stDataFrame thead th,
    [data-testid="stDataFrame"] thead th {
        background: linear-gradient(135deg, #FF6600, #FF57D8) !important;
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* 성공 메시지 */
    .stSuccess {
        background: rgba(255,102,0,0.1);
        border-left: 4px solid #FF6600;
        border-radius: 8px;
    }
    
    /* 경고 메시지 */
    .stWarning {
        background: rgba(255,87,216,0.1);
        border-left: 4px solid #FF57D8;
        border-radius: 8px;
    }
    
    /* Divider */
    hr {
        border-color: #EBEAEE !important;
    }
    
    /* 차트 컨테이너 */
    .js-plotly-plot,
    .plot-container,
    .svg-container,
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(255,102,0,0.08) !important;
    }
    
    /* Plotly 내부 배경 */
    .js-plotly-plot .plotly .main-svg,
    .js-plotly-plot .plotly .main-svg .bg {
        fill: #FFFFFF !important;
    }
    
    /* 드롭다운/셀렉트 박스 */
    [data-baseweb="select"] > div,
    [data-baseweb="popover"] {
        background: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* 모든 입력 필드 배경 */
    input, select, textarea {
        background: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* 텍스트 입력 필드 전체 컨테이너 */
    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] > div > div,
    [data-testid="stTextInput"] input,
    .stTextInput > div,
    .stTextInput > div > div {
        background: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* 셀렉트박스 전체 */
    [data-testid="stSelectbox"] > div,
    [data-testid="stSelectbox"] > div > div,
    .stSelectbox > div,
    .stSelectbox > div > div,
    [data-baseweb="select"],
    [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* 드롭다운 팝업 메뉴 - 강력하게 적용 */
    [data-baseweb="popover"],
    [data-baseweb="popover"] *,
    [data-baseweb="menu"],
    [data-baseweb="menu"] *,
    [data-baseweb="list"],
    [data-baseweb="list"] *,
    ul[role="listbox"],
    ul[role="listbox"] *,
    div[role="listbox"],
    div[role="listbox"] *,
    [data-baseweb="select"] ul,
    [data-baseweb="select"] li,
    .st-emotion-cache-1n76uvr,
    .st-emotion-cache-1n76uvr * {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* 드롭다운 옵션 호버 */
    ul[role="listbox"] li:hover,
    ul[role="listbox"] li:hover *,
    div[role="listbox"] div:hover,
    div[role="listbox"] div:hover *,
    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] li:hover *,
    [data-baseweb="list"] li:hover,
    [data-baseweb="list"] li:hover * {
        background: linear-gradient(135deg, #FF6600, #FF57D8) !important;
        background-color: transparent !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* 선택된 옵션 */
    li[aria-selected="true"],
    li[aria-selected="true"] *,
    div[aria-selected="true"],
    div[aria-selected="true"] * {
        background: linear-gradient(135deg, #FF6600, #FF57D8) !important;
        background-color: transparent !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* 드롭다운 화살표 아이콘 */
    [data-baseweb="select"] svg {
        fill: #333333 !important;
    }
    
    /* 파일 업로더 내부 */
    [data-testid="stFileUploader"] > div,
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] button {
        background: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* 비밀번호 입력 필드 */
    input[type="password"] {
        background: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* 모든 div 기본 배경 투명하게 */
    [data-testid="stVerticalBlock"] > div,
    [data-testid="column"] > div {
        background: transparent !important;
    }
</style>
"""

# 라이트 모드 CSS 적용
st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)

# 사이드바 - 설정
with st.sidebar:
    st.title("📊 VOC Dashboard")

    # 저장된 월 목록 표시
    all_data = load_all_monthly_data('data')
    months = list(all_data.get('months', {}).keys())

    if months:
        st.success(f"📅 저장된 월: {len(months)}개")
        st.markdown("**저장된 월 목록**")
        for month in sorted(months, reverse=True):
            st.caption(f"• {month}")
    else:
        st.info("📅 저장된 월이 없습니다")

# 메인 화면 - 탭 (대시보드 보기가 기본)
tab1, tab2 = st.tabs(["📊 대시보드 보기", "📤 파일 업로드"])

# 탭 2: 파일 업로드 (관리자 전용)
with tab2:
    st.header("📤 월별 VOC 데이터 업로드")
    
    # 관리자 접근 패스워드 (st.secrets 또는 환경변수에서 로드)
    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", os.environ.get("ADMIN_PASSWORD", ""))
    
    admin_password = st.text_input(
        "🔐 관리자 패스워드",
        type="password",
        help="파일 업로드 권한을 위한 패스워드를 입력하세요",
        key="admin_password"
    )
    
    if admin_password != ADMIN_PASSWORD:
        if admin_password:
            st.error("❌ 패스워드가 올바르지 않습니다.")
        else:
            st.info("🔒 파일 업로드는 관리자 전용입니다. 패스워드를 입력하세요.")
    else:
        st.success("✅ 관리자 인증 완료")
        
        # 업로드 성공 팝업 표시
        if st.session_state.get('upload_success', False):
            success_month = st.session_state.get('success_month', '')
            st.balloons()
            
            # 성공 다이얼로그
            @st.dialog("🎉 대시보드 생성 완료!")
            def show_success_dialog():
                st.markdown(f"### ✅ {success_month} 대시보드가 성공적으로 생성되었습니다!")
                st.info("💡 '대시보드 보기' 탭으로 이동하여 확인하세요.")
                if st.button("확인", type="primary", use_container_width=True):
                    st.session_state.upload_success = False
                    st.rerun()
            
            show_success_dialog()
        
        # 입력값 초기화
        if st.session_state.get('clear_inputs', False):
            # 초기화할 키 목록
            keys_to_clear = ['file_password_input', 'api_key_input', 'file_uploader']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.clear_inputs = False
        
        col1, col2 = st.columns(2)

        with col1:
            # 월 선택
            selected_month = st.text_input(
                "월 선택",
                value="",
                placeholder="YYYY-MM",
                help="YYYY-MM 형식으로 입력하세요 (예: 2025-11)",
                key="month_input"
            )

        with col2:
            # 국가 선택
            is_japan = st.selectbox(
                "국가 선택",
                options=["한국", "일본"],
                help="VOC 데이터 국가를 선택하세요",
                key="country_select"
            ) == "일본"

        # 파일 업로드
        uploaded_file = st.file_uploader(
            "Excel 파일 업로드",
            type=["xlsx", "xls"],
            help="암호화된 Excel 파일을 업로드하세요",
            key="file_uploader"
        )

        # 파일 비밀번호 입력
        file_password = st.text_input(
            "🔒 파일 비밀번호",
            type="password",
            help="업로드한 Excel 파일의 비밀번호를 입력하세요",
            key="file_password_input"
        )

        # OpenAI API Key 입력
        api_key = st.text_input(
            "🔑 OpenAI API Key",
            type="password",
            help="VOC 요약을 위해 OpenAI API 값을 입력해주세요.\n주의: API 비용 발생",
            key="api_key_input"
        )

        # 기존 데이터 확인
        existing_data = load_all_monthly_data('data')
        # 국가별 키 형식으로 확인
        if selected_month and selected_month.strip():
            country_suffix = "_JP" if is_japan else "_KR"
            month_key = f"{selected_month.strip()}{country_suffix}"
            month_exists = month_key in existing_data.get('months', {})

            if month_exists:
                st.warning(f"⚠️ {selected_month.strip()} 데이터가 이미 존재합니다. 생성하면 기존 데이터를 덮어씁니다!")

        # 처리 상태 관리
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'cancelled' not in st.session_state:
            st.session_state.cancelled = False

        # 생성/취소 버튼
        col_btn1, col_btn2 = st.columns([3, 1])
        
        with col_btn1:
            start_button = st.button("🚀 대시보드 생성", type="primary", use_container_width=True, disabled=st.session_state.processing)
        
        with col_btn2:
            if st.button("🛑 취소", type="secondary", use_container_width=True, disabled=not st.session_state.processing):
                st.session_state.cancelled = True
                st.session_state.processing = False
                st.warning("⚠️ 처리가 취소되었습니다.")
                st.rerun()

        st.divider()
        
        # 저장된 데이터 삭제 섹션
        st.subheader("🗑️ 저장된 데이터 삭제")
        
        saved_months = list(existing_data.get('months', {}).keys())
        if saved_months:
            # 표시용 월 이름 변환 함수
            def format_month_display(month_key):
                if month_key.endswith('_KR'):
                    return f"🇰🇷 {month_key[:-3]}"
                elif month_key.endswith('_JP'):
                    return f"🇯🇵 {month_key[:-3]}"
                return month_key
            
            delete_month = st.selectbox(
                "삭제할 월 선택",
                options=sorted(saved_months, reverse=True),
                format_func=format_month_display,
                key="delete_month_select"
            )
            
            col_del1, col_del2 = st.columns([3, 1])
            with col_del2:
                if st.button("🗑️ 삭제", type="secondary", use_container_width=True):
                    st.session_state.confirm_delete = delete_month
            
            # 삭제 확인 다이얼로그
            if st.session_state.get('confirm_delete'):
                @st.dialog("⚠️ 삭제 확인")
                def confirm_delete_dialog():
                    month_to_delete = st.session_state.confirm_delete
                    st.warning(f"**{format_month_display(month_to_delete)}** 데이터를 정말 삭제하시겠습니까?")
                    st.caption("이 작업은 되돌릴 수 없습니다.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("취소", use_container_width=True):
                            st.session_state.confirm_delete = None
                            st.rerun()
                    with col2:
                        if st.button("삭제", type="primary", use_container_width=True):
                            # 데이터 삭제
                            del existing_data['months'][month_to_delete]
                            with open('data/monthly_data.json', 'w', encoding='utf-8') as f:
                                import json
                                json.dump(existing_data, f, ensure_ascii=False, indent=2)
                            st.session_state.confirm_delete = None
                            st.session_state.delete_success = month_to_delete
                            st.rerun()
                
                confirm_delete_dialog()
            
            # 삭제 성공 메시지
            if st.session_state.get('delete_success'):
                st.success(f"✅ {format_month_display(st.session_state.delete_success)} 데이터가 삭제되었습니다.")
                st.session_state.delete_success = None
        else:
            st.info("📅 저장된 데이터가 없습니다.")

        if start_button:
            if not selected_month or selected_month.strip() == "":
                st.error("⚠️ 월을 입력하세요! (YYYY-MM 형식, 예: 2025-11)")
            elif not api_key:
                st.error("⚠️ OpenAI API Key를 입력하세요!")
            elif not uploaded_file:
                st.error("⚠️ Excel 파일을 업로드하세요!")
            elif not file_password:
                st.error("⚠️ 파일 비밀번호를 입력하세요!")
            else:
                # YYYY-MM 형식 검증
                import re
                if not re.match(r'^\d{4}-\d{2}$', selected_month.strip()):
                    st.error("⚠️ 월 형식이 올바르지 않습니다. YYYY-MM 형식으로 입력하세요 (예: 2025-11)")
                else:
                    st.session_state.processing = True
                    st.session_state.cancelled = False
                    
                    try:
                        # 임시 파일로 저장
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())

                        # 진행 상태 표시
                        progress_placeholder = st.empty()
                        progress_placeholder.info(f"🤖 {selected_month.strip()} 데이터 처리 중... (AI 요약 생성 중)\n\n💡 취소하려면 위의 '취소' 버튼을 누르거나 페이지를 새로고침하세요.")
                        
                        with st.spinner("처리 중..."):
                            # 월별 데이터 생성
                            monthly_data = generate_monthly_data(
                                temp_path,
                                selected_month.strip(),
                                api_key,
                                file_password,
                                is_japan
                            )

                            # 취소 확인
                            if st.session_state.cancelled:
                                raise Exception("사용자가 처리를 취소했습니다.")

                            # 데이터 저장
                            save_monthly_data(monthly_data, 'data')

                        # 임시 파일 삭제
                        os.remove(temp_path)
                        
                        st.session_state.processing = False
                        progress_placeholder.empty()

                        # 성공 상태 저장 및 입력값 초기화
                        st.session_state.upload_success = True
                        st.session_state.success_month = selected_month.strip()
                        
                        # 입력값 초기화를 위한 플래그
                        st.session_state.clear_inputs = True

                        # 페이지 리로드
                        st.rerun()

                    except Exception as e:
                        st.session_state.processing = False
                        st.error(f"❌ 오류 발생: {e}")
                        if 'temp_path' in locals() and os.path.exists(temp_path):
                            os.remove(temp_path)

# 탭 1: 대시보드 보기 (기본 탭)
with tab1:
    st.header("📊 VOC Dashboard")

    # 저장된 데이터 로드
    all_data = load_all_monthly_data('data')
    all_months_data = all_data.get('months', {})

    if not all_months_data:
        st.warning("⚠️ 저장된 월별 데이터가 없습니다. '파일 업로드' 탭에서 데이터를 먼저 업로드하세요.")
    else:
        # 국가 선택
        col_country, col_month = st.columns(2)
        
        with col_country:
            dashboard_country = st.selectbox(
                "🌏 국가 선택",
                options=["🇰🇷 한국", "🇯🇵 일본"],
                key="dashboard_country",
                help="확인할 국가를 선택하세요"
            )
        
        is_japan_filter = (dashboard_country == "🇯🇵 일본")
        country_suffix = "_JP" if is_japan_filter else "_KR"
        
        # 선택한 국가에 맞는 월 목록 필터링 (키 접미사 기반 + is_japan 필드 기반)
        filtered_months = []
        for month_key, data in all_months_data.items():
            # 새 형식: _KR 또는 _JP 접미사로 구분
            if month_key.endswith(country_suffix):
                filtered_months.append(month_key)
            # 기존 형식: is_japan 필드로 구분 (마이그레이션 호환)
            elif not month_key.endswith('_KR') and not month_key.endswith('_JP'):
                if data.get('is_japan', False) == is_japan_filter:
                    filtered_months.append(month_key)
        
        if not filtered_months:
            country_name = "일본" if is_japan_filter else "한국"
            st.warning(f"⚠️ {country_name} 데이터가 없습니다. '파일 업로드' 탭에서 데이터를 먼저 업로드하세요.")
        else:
            with col_month:
                # 월 키에서 표시용 월 추출 (2025-09_KR -> 2025-09)
                def get_display_month(month_key):
                    if month_key.endswith('_KR') or month_key.endswith('_JP'):
                        return month_key[:-3]
                    return month_key
                
                # 월 선택 (표시는 순수 월만, 값은 전체 키)
                selected_display_month = st.selectbox(
                    "📅 월 선택",
                    options=sorted(filtered_months, reverse=True),
                    format_func=get_display_month,
                    help="확인할 월을 선택하세요"
                )

            # 선택한 월 데이터
            month_data = all_data['months'][selected_display_month]

            # RFM 세그먼트 선택
            rfm_segments = list(month_data['rfm_segments'].keys())

            if not rfm_segments:
                st.warning(f"⚠️ {selected_display_month}의 RFM 세그먼트 데이터가 없습니다.")
            else:
                selected_rfm = st.selectbox(
                    "RFM 세그먼트 선택",
                    options=rfm_segments,
                    help="확인할 RFM 세그먼트를 선택하세요"
                )

                segment_data = month_data['rfm_segments'][selected_rfm]

                # 통계 정보
                display_month = get_display_month(selected_display_month)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📅 선택 월", display_month)
                with col2:
                    st.metric("🎧 DJ 건수", f"{segment_data['dj_count']:,}")
                with col3:
                    st.metric("🎵 Listener 건수", f"{segment_data['listener_count']:,}")

                st.divider()

                # 차트 생성
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=('DJ', 'Listener'),
                    specs=[[{'type': 'pie'}, {'type': 'pie'}]],
                    horizontal_spacing=0.1
                )

                # DJ 파이 차트
                if segment_data['dj_categories']:
                    dj_categories = list(segment_data['dj_categories'].keys())
                    dj_values = [segment_data['dj_categories'][cat]['count'] for cat in dj_categories]
                    dj_colors = [CATEGORY_COLORS.get(cat, '#CCCCCC') for cat in dj_categories]

                    fig.add_trace(go.Pie(
                        labels=dj_categories,
                        values=dj_values,
                        marker=dict(colors=dj_colors, line=dict(color='white', width=2)),
                        textinfo='label+percent',
                        textposition='auto',
                        hovertemplate='<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>',
                        hole=0.3
                    ), row=1, col=1)

                # Listener 파이 차트
                if segment_data['listener_categories']:
                    listener_categories = list(segment_data['listener_categories'].keys())
                    listener_values = [segment_data['listener_categories'][cat]['count'] for cat in listener_categories]
                    listener_colors = [CATEGORY_COLORS.get(cat, '#CCCCCC') for cat in listener_categories]

                    fig.add_trace(go.Pie(
                        labels=listener_categories,
                        values=listener_values,
                        marker=dict(colors=listener_colors, line=dict(color='white', width=2)),
                        textinfo='label+percent',
                        textposition='auto',
                        hovertemplate='<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>',
                        hole=0.3
                    ), row=1, col=2)

                # 레이아웃 설정 (라이트 모드)
                fig.update_layout(
                    height=600,
                    showlegend=False,
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FFFFFF',
                    font=dict(color='#333333')
                )

                st.plotly_chart(fig, use_container_width=True)

                st.divider()

                # AI 요약 섹션
                st.subheader("🤖 AI 요약")

                # 테이블 스타일 (라이트 모드)
                table_bg = "#FFFFFF"
                table_text = "#333333"
                header_bg = "linear-gradient(135deg, #FF6600, #FF57D8)"
                row_alt_bg = "rgba(255,102,0,0.03)"
                border_color = "rgba(255,102,0,0.1)"

                # DJ 요약
                if segment_data['dj_categories']:
                    st.markdown(f"### 🎧 DJ ({segment_data['dj_count']:,}건)")

                    dj_html = f"""
                    <table style='width: 100%; border-collapse: separate; border-spacing: 0;
                        margin: 10px 0 0 0; border-radius: 12px; overflow: hidden;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08); background: {table_bg};'>
                        <thead>
                            <tr style='background: {header_bg}; color: white;'>
                                <th style='padding: 16px; text-align: left; width: 15%; font-weight: 700;'>대분류</th>
                                <th style='padding: 16px; text-align: center; width: 10%; font-weight: 700;'>건수</th>
                                <th style='padding: 16px; text-align: left; font-weight: 700;'>주요 이슈 요약</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    for idx, (category, data) in enumerate(segment_data['dj_categories'].items()):
                        bg = row_alt_bg if idx % 2 == 0 else table_bg
                        dj_html += f"""
                            <tr style='background: {bg};'>
                                <td style='padding: 14px 16px; border-bottom: 1px solid {border_color}; color: {table_text}; font-weight: 500;'>{category}</td>
                                <td style='padding: 14px 16px; text-align: center; border-bottom: 1px solid {border_color}; color: {table_text};'>{data['count']}</td>
                                <td style='padding: 14px 16px; border-bottom: 1px solid {border_color}; color: {table_text}; line-height: 1.6;'>{data['summary']}</td>
                            </tr>
                        """
                    dj_html += "</tbody></table>"
                    # 요약 텍스트 길이에 따라 동적 높이 계산
                    dj_total_height = 60  # 헤더 높이
                    for cat, dat in segment_data['dj_categories'].items():
                        text_len = len(dat['summary'])
                        # 약 70자당 1줄 (화면 폭 고려)
                        lines = max(1, (text_len // 70) + 1)
                        dj_total_height += 30 + (lines * 28)  # 패딩 + 줄 높이
                    components.html(dj_html, height=dj_total_height, scrolling=False)

                # Listener 요약
                if segment_data['listener_categories']:
                    st.markdown(f"<h3 style='margin-top: 10px;'>🎵 Listener ({segment_data['listener_count']:,}건)</h3>", unsafe_allow_html=True)

                    listener_html = f"""
                    <table style='width: 100%; border-collapse: separate; border-spacing: 0;
                        margin: 10px 0 0 0; border-radius: 12px; overflow: hidden;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08); background: {table_bg};'>
                        <thead>
                            <tr style='background: {header_bg}; color: white;'>
                                <th style='padding: 16px; text-align: left; width: 15%; font-weight: 700;'>대분류</th>
                                <th style='padding: 16px; text-align: center; width: 10%; font-weight: 700;'>건수</th>
                                <th style='padding: 16px; text-align: left; font-weight: 700;'>주요 이슈 요약</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    for idx, (category, data) in enumerate(segment_data['listener_categories'].items()):
                        bg = row_alt_bg if idx % 2 == 0 else table_bg
                        listener_html += f"""
                            <tr style='background: {bg};'>
                                <td style='padding: 14px 16px; border-bottom: 1px solid {border_color}; color: {table_text}; font-weight: 500;'>{category}</td>
                                <td style='padding: 14px 16px; text-align: center; border-bottom: 1px solid {border_color}; color: {table_text};'>{data['count']}</td>
                                <td style='padding: 14px 16px; border-bottom: 1px solid {border_color}; color: {table_text}; line-height: 1.6;'>{data['summary']}</td>
                            </tr>
                        """
                    listener_html += "</tbody></table>"
                    # 요약 텍스트 길이에 따라 동적 높이 계산
                    listener_total_height = 60  # 헤더 높이
                    for cat, dat in segment_data['listener_categories'].items():
                        text_len = len(dat['summary'])
                        # 약 70자당 1줄 (화면 폭 고려)
                        lines = max(1, (text_len // 70) + 1)
                        listener_total_height += 30 + (lines * 28)  # 패딩 + 줄 높이
                    components.html(listener_html, height=listener_total_height, scrolling=False)

# Footer
st.divider()
st.caption("✨ Thanks to Claude Code, Cursor, and OpenAI GPT-4o-mini")
