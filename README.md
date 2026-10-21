# YouTube 댓글 워드클라우드

YouTube Data API v3 키와 영상 링크를 입력하면 영상 제목을 표시하고, 공개된 최상위 댓글에서 단어 빈도를 분석해 한글 워드클라우드를 만듭니다.

## 기능

- YouTube URL 또는 11자리 영상 ID 입력
- YouTube Data API v3로 제목과 공개 최상위 댓글 조회
- 한국어·영어 단어 빈도 워드클라우드
- 조회 댓글 수 선택 (100 / 300 / 500 / 1,000)
- PNG 다운로드
- Nanum Gothic 한글 글꼴 자동 설치 설정

## API 키 준비

1. Google Cloud Console에서 프로젝트를 선택하거나 새로 만듭니다.
2. YouTube Data API v3를 사용 설정합니다.
3. API 키를 발급하고 가능하면 YouTube Data API v3로 제한합니다.
4. 앱에서 키를 비밀번호 입력란에 붙여넣습니다.

API 키는 저장소에 올리지 않습니다. 이 앱은 키를 서버 메모리에서 사용해 Google API 요청을 보냅니다. Streamlit Community Cloud에 공개 배포하면 입력한 키가 배포된 앱의 서버를 통과하므로, 본인만 사용할 경우 앱 접근을 제한하고 키 사용량을 확인하세요.

## 댓글 API 참고

이 앱은 `commentThreads.list`로 공개 최상위 댓글을 가져옵니다. 댓글이 비활성화된 영상이나 공개 댓글이 없는 영상은 분석할 수 없으며, 대댓글은 현재 포함하지 않습니다. YouTube Data API 할당량을 사용합니다.

## 로컬 실행

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 배포

1. GitHub에 이 저장소를 올립니다.
2. Streamlit Community Cloud에서 GitHub로 로그인하고 **New app**을 선택합니다.
3. 저장소와 `main` 브랜치, 메인 파일 `app.py`를 지정합니다.
4. **Deploy**를 누릅니다.

`packages.txt`가 Nanum Gothic 시스템 글꼴을 설치해 한글 워드클라우드를 표시합니다.

