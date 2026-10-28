# YouTube 댓글 워드클라우드

본인 YouTube Data API v3 키를 비공개 설정에 등록하고 영상 링크를 입력하면, 영상 제목과 공개 최상위 댓글을 가져와 한글 워드클라우드를 만듭니다.

## 기능

- YouTube URL 또는 11자리 영상 ID 입력
- 본인 소유 API 키를 비공개 설정에서 사용 (방문자가 키를 입력하지 않음)
- YouTube Data API v3로 제목과 공개 최상위 댓글 조회
- 한국어·영어 단어 빈도 워드클라우드
- 조회 댓글 수 선택 (100 / 300 / 500 / 1,000)
- PNG 다운로드
- Nanum Gothic 한글 글꼴 자동 설치 설정

## 본인 API 키 설정

1. Google Cloud Console에서 프로젝트를 선택하거나 새로 만듭니다.
2. YouTube Data API v3를 사용 설정합니다.
3. API 키를 발급하고 가능하면 YouTube Data API v3로 제한합니다.
4. 로컬에서는 프로젝트의 `.streamlit/secrets.toml` 파일을 만들고 아래처럼 저장합니다.

```toml
YOUTUBE_API_KEY = "여기에_본인_API_키"
```

Streamlit Community Cloud에서는 앱의 **Settings → Secrets**에 같은 설정을 추가합니다. `.streamlit/secrets.toml`은 `.gitignore`에 포함되어 있어 GitHub에 올라가지 않습니다. 코드와 GitHub 저장소에 실제 API 키를 붙여넣지 마세요.

이 앱은 설정된 키로 서버에서 YouTube API를 호출합니다. Streamlit 앱을 공개하면 방문자가 본인 API 할당량을 사용할 수 있으므로, 본인만 사용할 경우 앱 공유 설정을 비공개로 제한하세요.

## 댓글 API 참고

이 앱은 `commentThreads.list`로 공개 최상위 댓글을 가져옵니다. 댓글이 비활성화된 영상이나 공개 댓글이 없는 영상은 분석할 수 없으며, 대댓글은 현재 포함하지 않습니다. YouTube Data API 할당량은 앱 소유자의 키에서 사용됩니다.

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

