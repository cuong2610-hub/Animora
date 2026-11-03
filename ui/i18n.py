TEXT = {
    "Home": "Trang chủ", "Library": "Thư viện", "Editor": "Trình chỉnh sửa", "Settings": "Cài đặt",
    "Animation desktop": "Hoạt ảnh trên desktop", "Animation Library": "Thư viện hoạt ảnh", "Import Animation": "Nhập hoạt ảnh",
    "Import Sprite Sheet": "Nhập sprite sheet", "Search animations…": "Tìm hoạt ảnh…", "Import an animation to preview": "Nhập hoạt ảnh để xem trước",
    "Play": "Phát", "Pause": "Tạm dừng", "Resume": "Tiếp tục", "Stop": "Dừng", "Add to Desktop": "Thêm lên Desktop",
    "Welcome to Animora": "Chào mừng đến với Animora", "Manage and display your animated companions on the desktop.": "Quản lý và hiển thị hoạt ảnh trên desktop.",
    "Playback": "Phát lại", "Loop animation": "Lặp hoạt ảnh", "Frame rate": "Tốc độ khung hình", "Add an image animation as a layer to edit": "Thêm hoạt ảnh dạng ảnh làm lớp để chỉnh sửa",
    "Add selected animation as layer": "Thêm hoạt ảnh đã chọn làm lớp", "Remove selected layer": "Xóa lớp đã chọn", "Effects": "Hiệu ứng",
    "% opacity": "% độ mờ", "° rotation": "° xoay", "Export GIF": "Xuất GIF", "Settings": "Cài đặt",
    "Keep animation windows above other windows": "Giữ cửa sổ hoạt ảnh luôn nổi", "Desktop windows": "Cửa sổ Desktop",
    "Click through desktop animations": "Cho phép bấm xuyên qua hoạt ảnh", "Interaction": "Tương tác", "Plugins": "Plugin",
    "Plugins are local Python code and run with Animora's permissions.": "Plugin là mã Python chạy với quyền của Animora.",
    "Load Plugin…": "Tải plugin…", "Unload Selected": "Gỡ mục đã chọn", "Run Selected Action": "Chạy tác vụ đã chọn",
    "Sort by": "Sắp xếp", "Name": "Tên", "Recently opened": "Mở gần đây", "Type": "Loại", "Theme": "Giao diện",
    "System": "Theo hệ thống", "Light": "Sáng", "Dark": "Tối", "Language": "Ngôn ngữ", "English": "English", "Tiếng Việt": "Tiếng Việt",
    "Recent animations": "Hoạt ảnh gần đây", "Show Main Window": "Mở cửa sổ chính", "Hide Main Window": "Ẩn cửa sổ chính", "Hide Animations": "Ẩn hoạt ảnh", "Show Animations": "Hiện hoạt ảnh", "Pause All": "Tạm dừng tất cả", "Resume All": "Tiếp tục tất cả", "Click-through animations": "Bấm xuyên hoạt ảnh", "Exit": "Thoát", "Close animation": "Đóng hoạt ảnh",
    "Rename": "Đổi tên", "Remove from Library": "Xóa khỏi thư viện", "File not found": "Không tìm thấy tệp", "Unsupported or damaged animation": "Hoạt ảnh không hỗ trợ hoặc bị hỏng",
    "This file format is not supported. Use GIF, APNG, PNG, WebP, or a Qt-supported video.": "Định dạng tệp này không được hỗ trợ. Hãy dùng GIF, APNG, PNG, WebP hoặc video Qt hỗ trợ.",
    "The animation file could not be found. It may have been moved or deleted.": "Không tìm thấy tệp hoạt ảnh. Tệp có thể đã bị di chuyển hoặc xóa.",
    "Animora could not read this animation. The file may be damaged or its video codec may be unavailable.": "Animora không thể đọc hoạt ảnh này. Tệp có thể bị hỏng hoặc thiếu codec video.",
    "Sort by": "Sắp xếp theo", "Columns": "Số cột", "Rows": "Số hàng", "Sprite sheet layout": "Bố cục sprite sheet",
    "Load Python plugin": "Tải plugin Python", "Run plugin code?": "Chạy mã plugin?",
    "This Python plugin can access files and run code with the same permissions as Animora. Load it only if you trust its source.": "Plugin Python này có thể truy cập tệp và chạy mã với quyền của Animora. Chỉ tải nếu bạn tin nguồn cung cấp.",
    "Plugin load failed": "Không thể tải plugin", "Plugin action failed": "Tác vụ plugin thất bại", "Unable to load animation": "Không thể tải hoạt ảnh",
    "Video layer": "Lớp video", "Video preview is supported; video layers are not supported by the frame-based editor yet.": "Có thể xem trước video; trình chỉnh sửa theo khung hình hiện chưa hỗ trợ lớp video.",
    "Unable to add layer": "Không thể thêm lớp", "Nothing to export": "Không có nội dung để xuất", "Add at least one visible image layer first.": "Hãy thêm ít nhất một lớp ảnh đang hiển thị.",
    "Export animation": "Xuất hoạt ảnh", "Export failed": "Xuất thất bại", "Load Plugin…": "Tải plugin…",
}


def translate(value, language):
    return TEXT.get(value, value) if language == "vi" else value
