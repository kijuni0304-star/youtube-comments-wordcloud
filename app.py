import html
import io
import re
from collections import Counter
from pathlib import Path

import requests
import streamlit as st
from wordcloud import WordCloud

st.set_page_config(
    page_title="YouTube 댓글 워드클라우드",
    page_icon="☁️",
    layout="wide",
)

st.title("☁️ YouTube 댓글 워드클라우드")
st.write("YouTube Data API 키와 영상 링크를 입력하면 영상의 댓글을 모아 워드클라우드로 보여줍니다.")
st.info(
    "입력한 API 키는 영상 정보와 공개 댓글을 조회하기 위해 Google YouTube Data API로 전달됩니다. "
    "앱이나 GitHub 저장소에 키를 저장하지 않습니다."
)

API_BASE = "https://www.googleapis.com/youtube/v3"
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")

STOPWORDS = {
    "그리고", "그러나", "그래서", "그런데", "하지만", "때문", "정말", "조금",
    "이렇게", "저렇게", "그렇게", "여기", "저기", "이거", "저거", "그거",
    "합니다", "습니다", "입니다", "있는", "있어요", "없어요", "같아요",
    "하는", "하게", "해서", "하면", "되고", "되는", "보다", "에서", "에게",
    "으로", "까지", "부터", "대한", "통해", "수는", "것은", "거는", "저는",
    "제가", "여러분", "여러분들", "오늘", "이번", "그냥", "이제", "정도",
    "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "ㅠ", "ㅋ", "ㅎ", "yeah", "okay", "like", "just",
    "really", "thing", "things", "know", "this", "that", "with", "from",
}


def extract_video_id(value: str) -> str | None:
    """Accept a YouTube URL or a bare 11-character video ID."""
    value = value.strip()
    if VIDEO_ID_PATTERN.fullmatch(value):
        return value

    match = re.search(
        r"(?:youtube\.com/(?:watch\?(?:[^#]*&)?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})",
        value,
        flags=re.IGNORECASE,
    )
    return match.group(1) if match else None


def youtube_get(resource: str, params: dict, api_key: str) -> dict:
    response = requests.get(
        f"{API_BASE}/{resource}",
        params={**params, "key": api_key},
        timeout=20,
    )
    if response.status_code != 200:
        try:
            reason = response.json().get("error", {}).get("errors", [{}])[0].get("reason", "")
        except (ValueError, IndexError, AttributeError):
            reason = ""
        if reason == "commentsDisabled":
            raise ValueError("이 영상은 댓글이 사용 중지되어 있습니다.")
        if reason == "quotaExceeded":
            raise ValueError("YouTube API 일일 할당량을 초과했습니다. 나중에 다시 시도해 주세요.")
        if reason in {"keyInvalid", "invalid", "forbidden"}:
            raise ValueError("API 키를 확인해 주세요. YouTube Data API v3 사용 설정과 키 제한도 확인해야 합니다.")
        raise ValueError(f"YouTube API 요청에 실패했습니다. (HTTP {response.status_code})")
    return response.json()


def get_video_title(video_id: str, api_key: str) -> str:
    data = youtube_get("videos", {"part": "snippet", "id": video_id}, api_key)
    items = data.get("items", [])
    if not items:
        raise ValueError("영상을 찾을 수 없습니다. 링크가 맞는지 확인해 주세요.")
    return items[0]["snippet"]["title"]


def fetch_comments(video_id: str, api_key: str, limit: int) -> list[str]:
    comments: list[str] = []
    page_token = None

    while len(comments) < limit:
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(100, limit - len(comments)),
            "textFormat": "plainText",
        }
        if page_token:
            params["pageToken"] = page_token

        data = youtube_get("commentThreads", params, api_key)
        for item in data.get("items", []):
            comment = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {}).get("textDisplay", "")
            if comment:
                comments.append(html.unescape(comment))
                if len(comments) >= limit:
                    break

        page_token = data.get("nextPageToken")
        if not page_token or not data.get("items"):
            break
    return comments


def tokenize(comments: list[str]) -> Counter[str]:
    """Count Korean and English words while removing common filler words."""
    words = re.findall(r"[가-힣]{2,}|[A-Za-z][A-Za-z'-]{2,}", " ".join(comments).lower())
    return Counter(word for word in words if word not in STOPWORDS)


with st.form("wordcloud_form"):
    api_key = st.text_input(
        "YouTube Data API v3 키",
        type="password",
        help="Google Cloud Console에서 YouTube Data API v3를 사용 설정한 뒤 발급한 키를 입력하세요.",
    )
    video_url = st.text_input(
        "YouTube 영상 링크",
        placeholder="https://www.youtube.com/watch?v=xxxxxxxxxxx",
    )
    comment_limit = st.selectbox("가져올 최상위 댓글 수", [100, 300, 500, 1000], index=1)
    submitted = st.form_submit_button("댓글 워드클라우드 만들기", type="primary")

if submitted:
    video_id = extract_video_id(video_url)
    if not api_key.strip():
        st.error("YouTube Data API v3 키를 입력해 주세요.")
    elif not video_id:
        st.error("유효한 YouTube 영상 링크 또는 11자리 영상 ID를 입력해 주세요.")
    else:
        try:
            with st.spinner("영상 정보와 댓글을 가져오는 중입니다..."):
                title = get_video_title(video_id, api_key.strip())
                comments = fetch_comments(video_id, api_key.strip(), comment_limit)

            if not comments:
                st.warning("가져올 수 있는 공개 댓글이 없습니다.")
            else:
                frequencies = tokenize(comments)
                st.subheader(title)
                st.caption(f"영상 ID: {video_id} · 가져온 최상위 댓글: {len(comments):,}개")
                if not frequencies:
                    st.warning("워드클라우드로 만들 단어를 찾지 못했습니다.")
                else:
                    font_candidates = [
                        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
                    ]
                    font_path = next((path for path in font_candidates if Path(path).exists()), None)
                    if font_path is None:
                        st.error("한글 폰트를 찾지 못했습니다. 배포 환경에 fonts-nanum 패키지가 설치되어 있는지 확인해 주세요.")
                    else:
                        cloud = WordCloud(
                            width=1400,
                            height=800,
                            background_color="white",
                            font_path=font_path,
                            colormap="viridis",
                            collocations=False,
                            max_words=150,
                        ).generate_from_frequencies(frequencies)
                        st.image(cloud.to_array(), use_container_width=True)
                        image_buffer = io.BytesIO()
                        cloud.to_image().save(image_buffer, format="PNG")
                        st.download_button(
                            "워드클라우드 PNG 다운로드",
                            data=image_buffer.getvalue(),
                            file_name="youtube_comments_wordcloud.png",
                            mime="image/png",
                        )
                        st.caption(f"분석 단어 {sum(frequencies.values()):,}개 · 고유 단어 {len(frequencies):,}개")
        except requests.RequestException:
            st.error("YouTube API에 연결하지 못했습니다. 네트워크 상태를 확인해 주세요.")
        except ValueError as error:
            st.error(str(error))

st.markdown("---")
st.caption("현재 버전은 공개 최상위 댓글을 분석합니다. 대댓글은 포함하지 않으며, 댓글이 꺼진 영상은 분석할 수 없습니다.")


