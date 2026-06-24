import streamlit as st

STRINGS = {
    "en": {
        # Page meta
        "page_title": "Story Viewer — Anonymous & Free",
        "lang_toggle": "🇻🇳 Tiếng Việt",

        # Sidebar
        "sidebar_login": "### 🔑 VIP Login",

        # Hero
        "hero_title": "# 🕵️ Anonymous Story Viewer",
        "hero_subtitle": "**View Instagram & TikTok stories anonymously — no login, no trace.**",
        "hero_info": "Choose a platform below, enter a public username, and view stories instantly.",

        # Platform tabs
        "tab_instagram": "Instagram",
        "tab_tiktok": "TikTok",

        # TikTok search form
        "tt_input_label": "TikTok Username",
        "tt_input_placeholder": "e.g. _jessica.anh_",
        "tt_search_button": "View TikTok Stories Now",
        "tt_empty_input": "Please enter a TikTok username.",
        "tt_no_stories": "This TikTok user has no active stories (stories expire every 24 h).",

        # Quota
        "vip_access": "⭐ VIP access — unlimited searches, logged in as",
        "quota_remaining": "⭐ Free searches remaining today:",
        "quota_of": "/ 5",

        # Search form
        "input_label": "Instagram Username",
        "input_placeholder": "e.g. cristiano_ronaldo",
        "search_button": "View Stories Now",

        # Errors & states
        "empty_input": "Please enter an Instagram username.",
        "rate_limit_error": (
            "🚫 Daily Limit Reached! You have exhausted your 5 free daily anonymous "
            "views. Please return tomorrow or sign in as a VIP user."
        ),
        "spinner_fetch": "Fetching secure media stream...",
        "spinner_buffer": "Buffering…",
        "no_stories": "This user currently has no stories published in the last 24 hours.",
        "capacity_error": (
            "⚠️ Server Capacity Peak Reached. Our team is adjusting throughput, "
            "please try again shortly."
        ),
        "found_stories_one": "Found **1** story for",
        "found_stories_many": "Found **{n}** stories for",
        "video_unavailable": "Video unavailable.",
        "image_unavailable": "Image unavailable.",
        "download_unavailable": "Download unavailable.",

        # Download buttons
        "dl_image": "📥 Download Image",
        "dl_video": "📥 Download Video",

        # Footer
        "footer": (
            "This application is an independent public media proxy tool. "
            "Please read our [Terms of Service](2_Terms) and [Privacy Policy](3_Privacy)."
        ),

        # Terms page
        "terms_title": "# 📜 Terms of Service",
        "terms_updated": "Last updated: June 2026",
        "terms_body": """
## 1. Nature of the Service
**Anonymous Story Viewer** is an independent educational utility acting as a transparent
proxy for publicly accessible Instagram and TikTok story media. The Service does **not**
store, reproduce, redistribute, or monetise any third-party copyrighted content.

## 2. No Affiliation
This tool is entirely unaffiliated with Meta Platforms, Inc., Instagram, ByteDance, TikTok,
or any of their subsidiaries. All trademarks belong to their respective owners.

## 3. Acceptable Use
You agree to use the Service solely to view **public** Instagram and TikTok accounts.
You must **not**:
- Attempt to access private, restricted, or minors' accounts.
- Use the Service for commercial surveillance, stalking, or harassment.
- Circumvent the rate-limiting system using bots or scrapers.
- Violate any applicable local, national, or international laws.

## 4. Limitation of Liability
The Service is provided **"as is"** without warranties of any kind.
""",

        # Privacy page
        "privacy_title": "# 🔒 Privacy Policy",
        "privacy_updated": "Last updated: June 2026",
        "privacy_body": """
## 1. Data Minimisation
We collect only the minimum data necessary to operate the Service safely.

## 2. What We Collect
| Data | Purpose | Retention |
|---|---|---|
| Hashed IP address | Rate-limit enforcement | 24 hours |
| Daily query count | 5-query free-tier quota | 24 hours |

We do **not** collect names, email addresses, raw IP addresses, or any personally
identifiable information.

## 3. Third-Party Platforms
Story media is fetched in real time from Instagram and TikTok public CDNs.
We act only as a pass-through proxy — no media is stored on our servers.

## 4. No Mandatory Registration
No account is required. Users are identified only by a hashed IP address used
solely for rate-limit enforcement. The hash cannot be reversed to an IP address.

## 5. Cookies
This Service does not set any tracking or advertising cookies.
""",
    },

    "vi": {
        # Page meta
        "page_title": "Xem Story Ẩn Danh & Miễn Phí",
        "lang_toggle": "🇬🇧 English",

        # Sidebar
        "sidebar_login": "### 🔑 Đăng nhập VIP",

        # Hero
        "hero_title": "# 🕵️ Xem Story Ẩn Danh",
        "hero_subtitle": "**Xem story Instagram & TikTok ẩn danh — không cần đăng nhập, không để lại dấu vết.**",
        "hero_info": "Chọn nền tảng bên dưới, nhập tên người dùng công khai và xem story ngay.",

        # Platform tabs
        "tab_instagram": "Instagram",
        "tab_tiktok": "TikTok",

        # TikTok search form
        "tt_input_label": "Tên người dùng TikTok",
        "tt_input_placeholder": "ví dụ: _jessica.anh_",
        "tt_search_button": "Xem Story TikTok Ngay",
        "tt_empty_input": "Vui lòng nhập tên người dùng TikTok.",
        "tt_no_stories": "Người dùng TikTok này chưa đăng story (story hết hạn sau 24 giờ).",

        # Quota
        "vip_access": "⭐ Truy cập VIP — không giới hạn, đăng nhập với tên",
        "quota_remaining": "⭐ Lượt xem miễn phí còn lại hôm nay:",
        "quota_of": "/ 5",

        # Search form
        "input_label": "Tên người dùng Instagram",
        "input_placeholder": "ví dụ: cristiano_ronaldo",
        "search_button": "Xem Story Ngay",

        # Errors & states
        "empty_input": "Vui lòng nhập tên người dùng Instagram.",
        "rate_limit_error": (
            "🚫 Đã đạt giới hạn ngày! Bạn đã dùng hết 5 lượt xem ẩn danh miễn phí. "
            "Vui lòng quay lại vào ngày mai hoặc đăng nhập tài khoản VIP."
        ),
        "spinner_fetch": "Đang tải dữ liệu story...",
        "spinner_buffer": "Đang xử lý...",
        "no_stories": "Người dùng này hiện không có story nào trong 24 giờ qua.",
        "capacity_error": (
            "⚠️ Máy chủ đang quá tải. Đội ngũ chúng tôi đang xử lý, "
            "vui lòng thử lại sau ít phút."
        ),
        "found_stories_one": "Tìm thấy **1** story của",
        "found_stories_many": "Tìm thấy **{n}** story của",
        "video_unavailable": "Video không khả dụng.",
        "image_unavailable": "Ảnh không khả dụng.",
        "download_unavailable": "Không thể tải xuống.",

        # Download buttons
        "dl_image": "📥 Tải ảnh",
        "dl_video": "📥 Tải video",

        # Footer
        "footer": (
            "Ứng dụng này là công cụ proxy media độc lập. "
            "Vui lòng đọc [Điều khoản sử dụng](2_Terms) và [Chính sách bảo mật](3_Privacy)."
        ),

        # Terms page
        "terms_title": "# 📜 Điều Khoản Sử Dụng",
        "terms_updated": "Cập nhật lần cuối: Tháng 6 năm 2026",
        "terms_body": """
## 1. Bản chất của dịch vụ
**Xem Story Ẩn Danh** là công cụ giáo dục độc lập, hoạt động như một proxy minh bạch cho
nội dung story Instagram và TikTok công khai. Dịch vụ **không** lưu trữ, sao chép,
phân phối lại hoặc kiếm tiền từ bất kỳ nội dung có bản quyền nào.

## 2. Không liên kết với các nền tảng
Công cụ này hoàn toàn không có liên kết với Meta Platforms, Inc., Instagram, ByteDance,
TikTok hoặc bất kỳ công ty con nào của họ. Mọi nhãn hiệu thuộc về chủ sở hữu tương ứng.

## 3. Sử dụng hợp lệ
Bạn đồng ý chỉ sử dụng dịch vụ để xem các tài khoản Instagram và TikTok **công khai**.
Bạn **không** được:
- Cố gắng truy cập tài khoản riêng tư, bị hạn chế hoặc tài khoản trẻ vị thành niên.
- Sử dụng dịch vụ cho mục đích giám sát thương mại, theo dõi hoặc quấy rối.
- Vượt qua hệ thống giới hạn tốc độ bằng bot hoặc công cụ tự động.
- Vi phạm bất kỳ luật pháp nào hiện hành.

## 4. Giới hạn trách nhiệm
Dịch vụ được cung cấp **"nguyên trạng"** không có bảo đảm dưới bất kỳ hình thức nào.
""",

        # Privacy page
        "privacy_title": "# 🔒 Chính Sách Bảo Mật",
        "privacy_updated": "Cập nhật lần cuối: Tháng 6 năm 2026",
        "privacy_body": """
## 1. Tối thiểu hoá dữ liệu
Chúng tôi chỉ thu thập dữ liệu tối thiểu cần thiết để vận hành dịch vụ an toàn.

## 2. Dữ liệu chúng tôi thu thập
| Dữ liệu | Mục đích | Thời gian lưu |
|---|---|---|
| Địa chỉ IP đã mã hoá | Giới hạn tốc độ | 24 giờ |
| Số lượt truy vấn mỗi ngày | Hạn mức 5 lượt miễn phí | 24 giờ |

Chúng tôi **không** thu thập tên, địa chỉ email, địa chỉ IP gốc hoặc bất kỳ thông tin
nhận dạng cá nhân nào.

## 3. Nền tảng bên thứ ba
Nội dung story được tải trực tiếp từ CDN công khai của Instagram và TikTok.
Chúng tôi chỉ hoạt động như một proxy trung gian — không lưu trữ bất kỳ media nào.

## 4. Không bắt buộc đăng ký
Không cần tài khoản. Người dùng được nhận dạng bằng địa chỉ IP đã mã hoá SHA-256,
chỉ dùng để giới hạn tốc độ. Mã hash không thể giải mã ngược thành IP gốc.

## 5. Cookie
Dịch vụ này không sử dụng cookie theo dõi hay quảng cáo.
""",
    },
}


def t(key: str, **kwargs) -> str:
    """Return translated string for current language."""
    lang = st.session_state.get("lang", "en")
    text = STRINGS.get(lang, STRINGS["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text
