## Mô hình ba vùng bằng một thay đổi thật

Git theo dõi snapshot nội dung qua commit. **Working tree** là file bạn đang sửa; **index/staging area** là snapshot dự kiến đưa vào commit; **HEAD** là commit hiện tại của branch. Giả sử bạn sửa `app.py`, sau đó `git add app.py`, rồi sửa thêm một dòng nữa. Commit kế tiếp chỉ chứa phiên bản đã stage, không tự lấy dòng sửa sau. `git diff` cho phần chưa stage; `git diff --staged` cho phần sẽ vào commit. Nếu không nắm mô hình này, rất dễ đưa nhầm secret hoặc quên file quan trọng.

Commit nên trả lời một ý định: “thêm readiness endpoint cho Notes API” thay vì “fix stuff”. Review pull request so thay đổi với base branch; người review cần thấy code, test, migration, cấu hình và rủi ro rollback. Một commit có hash là ID nội dung/lịch sử, nhưng đừng nhầm hash commit với image digest: build có thể không tái lập nếu dependency không khóa hoặc pipeline thay đổi. Ghi mối liên hệ commit -> build -> digest -> deploy revision.

### Khi nào dùng merge, rebase, revert?

Merge giữ lịch sử hai nhánh và tạo merge commit khi cần; rebase phát lại commit của nhánh bạn lên base mới, làm đổi hash các commit được phát lại. Rebase nhánh cá nhân chưa chia sẻ thường dễ review; rebase lại lịch sử đã được người khác dùng có thể gây rối. Revert tạo commit mới đảo tác động của một commit trước, phù hợp lịch sử đã chia sẻ và release production. Reset di chuyển branch tip và có thể đổi index/working tree tùy chế độ; dùng thận trọng, đặc biệt `--hard` làm mất thay đổi chưa lưu. Khi chưa chắc, xem `git status`, `git log --oneline --graph`, tạo branch bảo toàn trước và chọn thao tác không mất dữ liệu.

## Lab conflict có chủ đích trên repo mới

**Điều kiện:** Git đã cài; làm trong thư mục lab trống do bạn tạo. Không dùng repository dự án thật. Tạo `mkdir git-lab`, `cd git-lab`, `git init`, cấu hình tên/email cục bộ nếu Git yêu cầu. Tạo `config.txt` với một dòng `PORT=8000`, stage và commit. Tạo branch `feature-a`, đổi thành `PORT=8080`, commit. Quay về nhánh ban đầu (xem tên bằng `git branch --show-current`), tạo `feature-b`, đổi cùng dòng thành `PORT=9000`, commit. Merge `feature-a` vào nhánh gốc, sau đó merge `feature-b`.

**Kết quả dự kiến:** merge thứ hai có conflict vì cùng dòng có hai giá trị. Mở file, đọc marker `<<<<<<<`, `=======`, `>>>>>>>`. Không xóa marker rồi chọn bừa; hỏi cổng nào là quyết định sản phẩm, cấu hình có nên là biến môi trường thay vì giá trị cứng? Chọn giá trị có lý do, lưu file, `git add config.txt`, hoàn tất merge. `git status` phải sạch sau commit. Nếu merge đang dở và bạn muốn quay lại trạng thái trước merge trong repo lab, `git merge --abort` là đường phục hồi phù hợp khi còn có thể; đừng chạy trên repository chứa công việc chưa hiểu.

Thực hiện tiếp `git log --oneline --graph --all` để nhìn hai nhánh và merge commit. Ghi lại: conflict phát hiện ở **file/dòng**, không tự động chứng minh thay đổi nào đúng về nghiệp vụ. CI có thể giúp test kết quả merge, nhưng người review vẫn phải quyết định ý nghĩa. Dọn bằng cách xóa đúng thư mục lab sau khi bạn đã lưu ghi chú, không dùng lệnh reset trên dự án thật.

## Branch và release governance

Với pipeline production, bảo vệ nhánh cấu hình deploy và nhánh mã nguồn. Quy định PR review, CI bắt buộc, người được merge, người được bypass, quy trình emergency và log audit. Nếu pipeline dùng secret với quyền ghi cloud, một PR thay script pipeline có thể đánh cắp secret hoặc thay hạ tầng. Chạy workflow không tin cậy với quyền hạn tối thiểu; tránh cấp token production cho job chạy code của nhánh chưa review. Signed commit/tag và provenance có thể tăng truy vết nhưng không thay review và chính sách quyền.

Tag `v1.2.3` là tên tham chiếu tới commit, không bảo đảm artifact đã được build từ commit ấy hay tag không bị di chuyển nếu policy lỏng. Release record nên gồm commit, digest, SBOM/scan hoặc bằng chứng phù hợp, deploy config revision và môi trường. Khi rollback, xác định bạn quay lại **code**, **image** hay **manifest**; DB migration có thể vẫn ở schema mới.

## Ca điều tra có lời giải: hotfix không xuất hiện ở production

Developer sửa `app.py`, chạy test local, tạo commit và nói “đã push”. Production vẫn lỗi. Kiểm tra: commit có thật trên remote branch nào? PR đã merge chưa? Pipeline build commit nào? Image digest được đẩy lên registry chưa? Repo triển khai tham chiếu digest nào? Argo/CI/CD đã sync revision nào? Pod hiện chạy image nào? Mỗi câu hỏi có lệnh/UI tương ứng. Nếu developer chỉ push branch nhưng chưa merge, lỗi ở governance/delivery, không ở Kubernetes. Nếu deploy repo đã đổi nhưng Pod vẫn image cũ, xem sync/rollout. Nếu Pod đã image mới nhưng lỗi còn, hotfix chưa giải đúng nguyên nhân hoặc request đi tới bản cũ ở nơi khác.

**Câu hỏi có lời giải:** `git revert` và `git reset --hard` khác gì? Revert thêm commit đảo thay đổi và giữ lịch sử chia sẻ; reset `--hard` dời HEAD, index và working tree, có thể mất sửa đổi local. `git restore` dùng để khôi phục file ở working tree/index mà không dời branch tip. Đọc [tài liệu Git chính thức](https://git-scm.com/docs/git) trước khi dùng lệnh phá hủy lịch sử.
