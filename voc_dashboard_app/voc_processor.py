#!/usr/bin/env python3
"""
VOC Dashboard Data Processor
월별 VOC 데이터 처리 및 AI 요약 생성
"""

import os
import io
import json
import hashlib
import pandas as pd
import msoffcrypto
from openai import OpenAI
import warnings
warnings.filterwarnings('ignore')

# 대분류별 고정 색상 매핑
# 대분류별 색상 매핑 (밝고 부드러운 파스텔톤)
CATEGORY_COLORS = {
    '아이템스토어': '#FF9B9B',      # 연한 코랄
    '구독': '#7EDCD2',              # 연한 민트
    '베리': '#7DD3E8',              # 연한 스카이블루
    '랭킹': '#FFB899',              # 연한 피치
    '이벤트': '#B8E8D8',            # 연한 민트그린
    '커뮤니티': '#FFE99A',          # 연한 옐로우
    '앱 설정': '#D4A9E8',           # 연한 라벤더
    '개인정보': '#A8D8F0',          # 연한 블루
    '기관/기타': '#FFCCA8',         # 연한 오렌지
    '모니터링': '#C8D0D4',          # 연한 그레이
    '라이브': '#FF9A8A',            # 연한 살몬
    'LIVE': '#FF9A8A',
    '계정 관리': '#8ED8A8',         # 연한 그린
    'Account': '#8ED8A8',
    '계정관리': '#8ED8A8',          # 띄어쓰기 없는 버전도 추가
    '이의 제기': '#FFD080',         # 연한 골드
    'Report': '#FFD080',
    '스푼 결제': '#C9A8E8',         # 연한 퍼플
    '스푼 환전': '#FF8A8A',         # 연한 레드
    '스푼 환불': '#FFB8E8',         # 연한 핑크
    '유저신고': '#D8A8FF',          # 연한 바이올렛
    '신고': '#D8A8FF',
    'CAST': '#8AC8FF',              # 연한 블루
    '캐스트': '#8AC8FF',
    '기타': '#D0D8DC',              # 연한 그레이
    '문의': '#B8A8FF',              # 연한 퍼플
    '버그': '#FFA8A8',              # 연한 레드
    '제안': '#FFE8A0',              # 연한 옐로우
    '칭찬': '#E8F0A0'               # 연한 라임
}

# 일본어 → 한국어 대분류 번역
CATEGORY_TRANSLATION_JP = {
    'アイテムストア': '아이템스토어',
    'サブスクライブ': '구독',
    'ベリー': '베리',
    'ランキング': '랭킹',
    'イベント': '이벤트',
    'コミュニティ': '커뮤니티',
    'アプリの設定': '앱 설정',
    '個人情報': '개인정보',
    '機関/その他': '기관/기타',
    'モニタリング': '모니터링',
    'LIVE': '라이브',
    'Account': '계정 관리',
    'Report': '이의 제기',
    'スプーン 決済': '스푼 결제',
    'スプーン Cashout': '스푼 환전',
    'CAST': '캐스트'
}

# 템플릿 텍스트 (한국) - 제거할 안내 문구들
TEMPLATE_TEXTS_KR = [
    "스푸너님의 문의에 빠르게 답변해 드릴 수 있도록 아래 정보를 입력해주세요.\n※ 비회원의 경우 일부 답변이 제한될 수 있으니, 로그인 후 문의하시는 것을 권장합니다.\n※ 이벤트 혹은 랭킹명을 포함하여 내용을 작성해주세요.",
    "본인 확인이 필요한 문의입니다.\n답변을 위해 로그인 후 문의해 주시거나, 아래 정보를 정확히 입력해 주세요.\n※ 아래 정보가 확인되지 않으면 문의 처리가 불가합니다.",
    "본인 확인이 필요한 문의입니다.\n답변을 위해 로그인 후 문의해 주시거나, 아래 정보를 정확히 입력해 주세요.\n※ 아래 정보가 확인되지 않으면 문의 처리가 불가합니다.\n\n휴대폰 본인인증 초기화 또는 변경을 원하실 경우, 아래 서류와 링크를 확인해 주세요.\nhttps://buly.kr/FWTcvhY\n[제출 서류]\n- 개인정보 삭제 요구서: 아래 첨부된 보라색 버튼을 눌러 작성해 주세요.\n- 대리인 신청 시: 본인과의 관계를 증명할 수 있는 가족관계증명서 또는 등본",
    "스푸너님의 문의에 빠르게 답변해 드릴 수 있도록 아래 정보를 입력해주세요.\n* 비회원의 경우 일부 답변이 제한될 수 있으니, 로그인 후 문의하시는 것을 권장합니다.",
    "스푸너님의 문의에 빠르게 답변해 드릴 수 있도록 아래 정보를 입력해주세요.\n구독 결제 관련 문의는 아래 정보가 없으면 문의 처리가 불가합니다.",
    "본인 확인이 필요한 문의입니다.\n답변을 위해 로그인 후 문의해 주시거나, 아래 정보를 정확히 입력해 주세요.\n※ 아래 정보가 확인되지 않으면 문의 처리가 불가합니다.",
    "본인 확인이 필요한 문의입니다.\n답변을 위해 로그인 후 아래 정보를 정확히 입력해 주세요.\n비회원으로 접수된 문의는 답변이 제한될 수 있는 점 양해 부탁드립니다.\n※ 아래 정보가 확인되지 않으면 문의 처리가 불가합니다.",
    "환전 관련 문의는 반드시 로그인 후 접수해 주셔야 확인 및 답변이 가능합니다.\n비회원으로 접수된 문의는 답변이 제한될 수 있는 점 양해 부탁드립니다.",
    "신고하실 내용을 입력해 주세요.\n보다 정확한 처리를 위해 로그인 후 문의 접수를 권장드립니다.\n또한 신고 사실 확인이 어려운 경우 처리가 제한될 수 있으니, 반드시 캡처 이미지 또는 녹화본을 함께 첨부해 주세요.",
    "스푸너님의 문의에 빠르게 답변해 드릴 수 있도록 아래 정보를 입력해주세요.\n※ 비회원의 경우 일부 답변이 제한될 수 있으니, 로그인 후 문의하시는 것을 권장합니다.",
    "본인 확인이 필요한 문의입니다. 아래 정보를 정확히 입력해 주세요.\n※ 아래 정보가 확인되지 않으면 문의 처리가 불가합니다.",
    # 추가된 템플릿들
    "*문의답변은 문의시 입력하신 이메일을 통해 확인하실 수 있습니다.\n\n*비회원 문의 시 일부 문의는 답변이 어렵습니다. 정확한 답변을 위해 로그인 후 문의해 주세요.\n*빠른 처리를 위해 아래 항목을 반드시 입력해 주세요.",
    "*문의답변은 문의시 입력하신 이메일을 통해 확인하실 수 있습니다.\n*비회원 문의 시 일부 문의는 답변이 어렵습니다. 정확한 답변을 위해 로그인 후 문의해 주세요.\n*빠른 처리를 위해 아래 항목을 반드시 입력해 주세요.",
    "*문의답변은 문의시 입력하신 이메일을 통해 확인하실 수 있습니다.\n*빠른 처리를 위해 아래 항목을 반드시 입력해 주세요.",
    "[휴대폰 본인인증 초기화/변경을 위한 제출 자료] \n● 개인정보 삭제 요구서 - 본문 하단의 보라색 \"개인정보 삭제 요구서\" 선택 \n● 요구서 작성자가 대리인인 경우\n본인인증 명의자와의 관계 확인을 위한 가족관계증명서 혹은 등본\n [유의 사항] \n① 명의자를 사칭하는 경우 관련 법령에 의하여 처벌받을 수 있습니다. \n② 요구서 내 주체자는 '계정의 현재(변경 전) 휴대폰 본인 인증 정보'로 작성되어야 합니다. \n③ 요구서 접수 후 라이브 인증 초기화 상태로 복구되며, 라이브 방송 진행 및 환전 서비스 이용을 위해 DJ 본인 명의의 휴대폰으로 다시 인증 절차를 진행해야 하는 점 양해 부탁드립니다.",
    "*문의내용의 답변은 문의시 기재하신 이메일 주소에서 확인 가능합니다.\n*비회원 문의는 답변이 어렵습니다.  정확한 확인을 위해 로그인 후 문의 부탁드립니다.\n*빠른 처리를 위해 아래 상세 내역을 꼭 기재하셔서 문의 부탁드립니다.\n● 구매 상세 내역을 확인 할 수 있는 영수증 첨부 여부 (거래 내역 : 구매 일시, 상품명, 금액 확인 필요)\n : 예 / 아니오\n● 구매 후 사용 내역이 없는 마이월렛 캡쳐 이미지 : 예 / 아니오\n● 구매 후 사용 내역이 없는 스푼 아이템 보유  : 예 / 아니오\n● 문의 내용 : \n-구매일로부터 7일 이내 '구매 취소' 의사 전달되어야 환불 가능합니다.",
    "*문의내용의 답변은 문의시 기재하신 이메일 주소에서 확인 가능합니다.\n*비회원 문의시 일부 문의는 답변이 어렵습니다.  정확한 확인을 위해 로그인 후 문의 부탁드립니다.\n*빠른 처리를 위해 아래 상세 내역을 꼭 기재하셔서 문의 부탁드립니다.",
    "*문의답변은 문의시 입력하신 이메일을 통해 확인하실 수 있습니다.\n*비회원 문의 시 일부 문의는 답변이 어렵습니다. 정확한 답변을 위해 로그인 후 문의해 주세요."
]

# 템플릿 텍스트 (일본) - 제거할 안내 문구들
TEMPLATE_TEXTS_JP = [
    "・迅速なご案内のため、ログイン状態でお問い合わせください\n・ご案内はご入力いただいたメールアドレスにお送りいたします\n・情報が不足している場合、サポートできる範囲が限られてしまうため詳細のご記載にご協力くださいませ",
    "・ご案内はご入力いただいたメールアドレスにお送りいたします\n・ログイン情報の確認につきましては、以下の情報が登録情報と一致しない場合、ご案内いたしかねます",
    "・未ログインでのお問い合わせにはご案内できかねます\n・ご案内はご入力いただいたメールアドレスにお送りいたします\n・情報が不足している場合、サポートできる範囲が限られてしまうため詳細のご記載にご協力くださいませ",
    "・ご案内はご入力いただいたメールアドレスにお送りいたします\n・アカウント情報の確認につきましては、以下の情報が登録情報と一致しない場合、ご案内いたしかねます",
    # 추가된 템플릿들 (빈 줄 포함 버전)
    "・迅速なご案内のため、ログイン状態でお問い合わせください\n\n・ご案内はご入力いただいたメールアドレスにお送りいたします\n・情報が不足している場合、サポートできる範囲が限られてしまうため詳細のご記載にご協力くださいませ",
    "・・迅速なご案内のため、ログイン状態でお問い合わせください\n\n・ご案内はご入力いただいたメールアドレスにお送りいたします\n・情報が不足している場合、サポートできる範囲が限られてしまうため詳細のご記載にご協力くださいませ",
]


def load_excel_file(file_path, password="!drw951130"):
    """암호화된 Excel 파일 로드"""
    try:
        with open(file_path, 'rb') as f:
            file = msoffcrypto.OfficeFile(f)
            file.load_key(password=password)
            decrypted = io.BytesIO()
            file.decrypt(decrypted)
            decrypted.seek(0)
            df = pd.read_excel(decrypted, engine='openpyxl')
        return df
    except Exception as e:
        raise Exception(f"파일 읽기 실패: {e}")


def classify_r_score(score):
    """R 점수 분류: 4~5=H, 2~3=M, 0~1=L"""
    if pd.isna(score):
        return 'L'
    if 4 <= score <= 5:
        return 'H'
    elif 2 <= score <= 3:
        return 'M'
    else:
        return 'L'


def classify_fm_score(score):
    """F/M 점수 분류: 8~10=H, 4~7=M, 0~3=L"""
    if pd.isna(score):
        return 'L'
    if 8 <= score <= 10:
        return 'H'
    elif 4 <= score <= 7:
        return 'M'
    else:
        return 'L'


def remove_template_text(text, is_japan=False):
    """템플릿 텍스트 제거"""
    if pd.isna(text):
        return ""
    text = str(text).replace('\r\n', '\n')

    templates = TEMPLATE_TEXTS_JP if is_japan else TEMPLATE_TEXTS_KR
    for template in templates:
        template_normalized = template.replace('\r\n', '\n')
        text = text.replace(template_normalized, "")

    return text.strip()


def summarize_voc_with_ai(df_segment, category, role, api_key, is_japan=False):
    """OpenAI API로 대분류별 VOC 요약"""
    try:
        if not api_key:
            return "⚠️ OPENAI_API_KEY가 필요합니다."

        client = OpenAI(api_key=api_key)

        voc_samples = df_segment[df_segment['대분류'] == category].head(20)
        if len(voc_samples) == 0:
            return "데이터 없음"

        voc_texts = []
        for idx, row in voc_samples.iterrows():
            title = str(row.get('문의 제목', ''))
            content = str(row.get('문의 내용', ''))
            content_cleaned = remove_template_text(content, is_japan)
            if content_cleaned:
                voc_texts.append(f"- {title}: {content_cleaned[:100]}")

        voc_text = "\n".join(voc_texts)

        if is_japan:
            prompt = f"""다음은 일본 사용자의 '{category}' 대분류 문의 내용입니다.
이 일본어 VOC 내용을 분석하여 한국어로 핵심 이슈를 1~2문장으로 요약하세요.

요구사항:
- 일본어 내용을 읽고 한국어로 요약
- 1~2문장으로만 작성
- 문장의 끝을 '~되고 있음', '~발생하고 있음', '~이어지고 있음' 스타일로 마무리
- '~에 대한 문의', '문의가 많음', '주로', '많음' 등 관찰자 표현 금지
- 번호, 하이픈, 불릿포인트 금지
- 감정·부사·추측 제거, 사실만 요약
- 원문에 없는 해석 추가 금지

일본어 VOC 내용:
{voc_text}

[좋은 예시]
환전이 인증 실패로 자주 중단되고, 진행 상황을 확인하기 어려운 구조로 인해 처리 지연이 반복되고 있음.

[나쁜 예시]
1. 환전 지연
- 환전 관련 문의 많음
환전에 대한 문의가 주로 발생함
"""
        else:
            prompt = f"""다음은 '{category}' 대분류의 고객 문의 내용입니다.
대시보드 요약용으로 핵심 이슈를 1~2문장으로 작성하세요.

요구사항:
- 1~2문장으로만 작성
- 문장의 끝을 '~되고 있음', '~발생하고 있음', '~이어지고 있음' 스타일로 마무리
- '~에 대한 문의', '문의가 많음', '주로', '많음' 등 관찰자 표현 금지
- 번호, 하이픈, 불릿포인트 금지
- 감정·부사·추측 제거, 사실만 요약
- 원문에 없는 해석 추가 금지

{voc_text}

[좋은 예시 스타일]
환전이 인증 실패로 자주 중단되고, 진행 상황을 확인하기 어려운 구조로 인해 처리 지연이 반복되고 있음.

[나쁜 예시]
1. 환전 지연
- 환전 관련 문의 많음
환전에 대한 문의가 주로 발생함
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"요약 실패: {str(e)}"


def process_voc_data(df, is_japan=False):
    """VOC 데이터 처리 및 RFM 분류"""
    # RFM 분류
    df['DJ_R'] = df['djScoreR'].apply(classify_r_score)
    df['DJ_F'] = df['djScoreF'].apply(classify_fm_score)
    df['DJ_M'] = df['djScoreM2'].apply(classify_fm_score)
    df['DJ_RFM'] = df['DJ_R'] + df['DJ_F'] + df['DJ_M']

    df['Listener_R'] = df['listenerScoreR'].apply(classify_r_score)
    df['Listener_F'] = df['listenerScoreF'].apply(classify_fm_score)
    df['Listener_M'] = df['listenerScoreM2'].apply(classify_fm_score)
    df['Listener_RFM'] = df['Listener_R'] + df['Listener_F'] + df['Listener_M']

    # 대분류 처리
    df['대분류'] = df['대분류'].str.strip()

    if is_japan:
        df['대분류'] = df['대분류'].map(CATEGORY_TRANSLATION_JP).fillna(df['대분류'])
        exclude_categories = ['警告', 'ブラインド', '違反未該当', 'アカウント停止']
    else:
        exclude_categories = ['경고', '반려', '블라인드', '로그인 정지']

    df_filtered = df[~df['대분류'].isin(exclude_categories)]

    return df_filtered


def generate_monthly_data(file_path, month, api_key, password="!drw951130", is_japan=False):
    """월별 VOC 데이터 생성 (AI 요약 포함)"""
    print(f"📂 {month} 데이터 처리 중...")

    # 파일 로드
    df = load_excel_file(file_path, password)
    print(f"✅ 파일 로드 완료: {len(df):,}건")

    # 데이터 처리
    df_filtered = process_voc_data(df, is_japan)
    print(f"🔍 필터링 완료: {len(df_filtered):,}건")

    # RFM 세그먼트
    important_rfm = [
        'HHH',
        'HHM', 'HHL', 'HMH', 'HLH', 'MHH', 'LHH',
        'HMM', 'HML', 'HLL', 'MHM', 'MHL', 'LHM', 'LHL'
    ]

    # 월별 데이터 구조
    monthly_data = {
        'month': month,
        'is_japan': is_japan,
        'total_count': len(df_filtered),
        'rfm_segments': {}
    }

    print(f"🤖 AI 요약 생성 중...")

    # 각 RFM 세그먼트별 데이터 생성
    for rfm in important_rfm:
        dj_data = df_filtered[df_filtered['DJ_RFM'] == rfm]
        listener_data = df_filtered[df_filtered['Listener_RFM'] == rfm]

        dj_count = len(dj_data)
        listener_count = len(listener_data)

        if dj_count > 0 or listener_count > 0:
            segment_data = {
                'dj_count': dj_count,
                'listener_count': listener_count,
                'dj_categories': {},
                'listener_categories': {}
            }

            # DJ 카테고리별 데이터 및 AI 요약
            if dj_count > 0:
                top_categories = dj_data['대분류'].value_counts().head(5)
                for category, count in top_categories.items():
                    print(f"  - {rfm} DJ {category} 요약 중...")
                    summary = summarize_voc_with_ai(dj_data, category, 'DJ', api_key, is_japan)
                    segment_data['dj_categories'][category] = {
                        'count': int(count),
                        'summary': summary
                    }

            # Listener 카테고리별 데이터 및 AI 요약
            if listener_count > 0:
                top_categories = listener_data['대분류'].value_counts().head(5)
                for category, count in top_categories.items():
                    print(f"  - {rfm} Listener {category} 요약 중...")
                    summary = summarize_voc_with_ai(listener_data, category, 'Listener', api_key, is_japan)
                    segment_data['listener_categories'][category] = {
                        'count': int(count),
                        'summary': summary
                    }

            monthly_data['rfm_segments'][rfm] = segment_data

    print(f"✅ {month} 데이터 생성 완료!")
    return monthly_data


def save_monthly_data(monthly_data, data_dir='data'):
    """월별 데이터를 JSON 파일로 저장 (국가별로 구분)"""
    os.makedirs(data_dir, exist_ok=True)

    # 기존 데이터 로드
    json_path = os.path.join(data_dir, 'monthly_data.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = {'months': {}}

    # 새 월 데이터 추가 (국가별로 키 구분: YYYY-MM_KR 또는 YYYY-MM_JP)
    month = monthly_data['month']
    is_japan = monthly_data.get('is_japan', False)
    country_suffix = '_JP' if is_japan else '_KR'
    month_key = f"{month}{country_suffix}"
    
    # 기존 형식(접미사 없음)의 데이터가 있으면 삭제 (마이그레이션)
    if month in all_data['months']:
        old_data = all_data['months'][month]
        # 같은 국가의 데이터면 삭제
        if old_data.get('is_japan', False) == is_japan:
            del all_data['months'][month]
            print(f"🔄 기존 형식 데이터 마이그레이션: {month} → {month_key}")
    
    all_data['months'][month_key] = monthly_data

    # 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"💾 데이터 저장 완료: {json_path} ({month_key})")
    return json_path


def load_all_monthly_data(data_dir='data'):
    """저장된 모든 월별 데이터 로드"""
    json_path = os.path.join(data_dir, 'monthly_data.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'months': {}}
