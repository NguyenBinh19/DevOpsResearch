## Reflog và cứu thay đổi trong lab

Trong repo lab, tạo hai commit A/B, sau đó thử `git reset --hard HEAD~1` **chỉ sau khi xác nhận không còn thay đổi chưa commit cần giữ**. Commit B không còn trên branch, nhưng `git reflog` thường lưu tham chiếu HEAD gần đây để bạn tìm hash và tạo branch cứu B trước khi garbage collection. Mục tiêu bài này là hiểu thao tác dời branch tip và cách phòng mất dữ liệu, không khuyến khích reset lịch sử chia sẻ. Ghi hash trước/sau và vẽ branch pointer. Nếu bạn chưa chắc lệnh nào phá dữ liệu, dừng ở `git status`/`git log` và tạo bản sao lab trước.

**Revert merge** phức tạp hơn revert commit thường vì phải chọn mainline parent; đừng chạy mù trên production. Một hotfix release nên được xem xét cả code và config deploy: revert source commit không tự đổi image đang chạy nếu pipeline không build/promote lại. Với GitOps, revert manifest commit thường tạo desired state cũ; Argo đồng bộ lại nhưng DB/schema có thể không đảo. Vì vậy Git history là bản đồ quyết định, không phải nút thời gian quay lùi mọi hệ thống.

## Review một pull request như người vận hành

PR đổi image tag trong manifest và thêm env `FEATURE_X=true`. Hãy hỏi: image digest đã build/test chưa, tag có bất biến không, env ảnh hưởng DB/traffic ra sao, rollback có tương thích dữ liệu không, `resources`/probe có đổi không, secret nào được tham chiếu, staging có chạy cùng artifact không. Nếu PR cũng sửa pipeline, xem quyền runner/secret và trigger. Một diff 2 dòng có thể có blast radius lớn hơn 500 dòng tài liệu.

**Bài tập:** tạo PR giả trên giấy với thay đổi `replicas: 2 -> 4` và `maxConnections: 100 -> 400`. App tăng Pod nhưng DB max connections có thể không đủ, hoặc connection storm làm DB nghẹt. Viết review comment hỏi capacity DB, HPA, load test và kế hoạch quan sát. Đây là “Git governance” nối với kiến trúc chứ không chỉ check style.

## Git tags, branching và hotfix

Trunk-based development giữ branch sống ngắn, tích hợp thường xuyên; release branch dài hơn có thể cần khi hỗ trợ nhiều version nhưng tăng công việc backport. Không có một chiến lược thắng mọi đội; chọn theo nhịp phát hành, quy mô, quy định và khả năng test. Một hotfix production cần commit trên đúng base, test, review khẩn cấp, build artifact, promote, rồi merge/backport lại các nhánh khác để lỗi không quay lại. Nếu sửa trực tiếp nhánh production mà quên main, lần release sau có thể mất hotfix.

**Câu hỏi có lời giải:** `git pull` báo conflict, dùng `git push --force` được không? Force push không giải conflict và có thể ghi đè lịch sử người khác. Đọc branch/remote, fetch, giải quyết merge/rebase trong nhánh của bạn và chỉ force-with-lease khi chính sách cho phép trên branch cá nhân đã rebase. **Secret commit nhầm rồi xóa ở commit sau có đủ không?** Không; token vẫn trong lịch sử/caches, phải revoke/rotate, hạn chế access và xử lý lịch sử theo quy trình.
