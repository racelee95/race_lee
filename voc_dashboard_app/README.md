# VOC Dashboard App

월별 VOC 데이터 업로드 및 대시보드 시각화 Streamlit 앱

## 주요 기능

- 📤 **파일 업로드**: 암호화된 Excel 파일 업로드
- 🤖 **AI 요약**: OpenAI GPT-4o-mini로 자동 요약 생성
- 📊 **대시보드**: 월별/RFM별 인터랙티브 차트
- 💾 **데이터 저장**: JSON 파일로 월별 데이터 보관
- 🔑 **개인 API 키**: 각 사용자가 자신의 OpenAI API 키 사용

## 설치 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

## 사용 방법

### 1. API 키 설정
- 사이드바에서 OpenAI API Key 입력
- 파일 비밀번호 입력 (기본값: !drw951130)

### 2. 파일 업로드
- "파일 업로드" 탭 선택
- 월 선택 (YYYY-MM 형식)
- 국가 선택 (한국 또는 일본)
- Excel 파일 업로드
- "대시보드 생성" 버튼 클릭

### 3. 대시보드 보기
- "대시보드 보기" 탭 선택
- 월 선택
- RFM 세그먼트 선택
- 차트 및 AI 요약 확인

## 파일 구조

```
voc_dashboard_app/
├── app.py              # Streamlit 앱 메인
├── voc_processor.py    # VOC 데이터 처리 로직
├── requirements.txt    # 의존성 목록
├── README.md          # 문서
└── data/              # 월별 데이터 저장
    └── monthly_data.json
```

## 배포 (Streamlit Cloud)

1. GitHub 저장소에 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. "New app" 클릭
4. 저장소 선택 및 배포

## 기술 스택

- **Frontend**: Streamlit
- **시각화**: Plotly
- **AI**: OpenAI GPT-4o-mini
- **데이터**: Pandas, JSON
