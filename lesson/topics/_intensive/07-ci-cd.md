## Một pipeline tốt phải chứng minh điều gì?

Pipeline không chỉ là danh sách stage `build/test/deploy`. Hãy chọn một commit cụ thể rồi theo dấu: source và dependency nào tạo artifact; test nào đã chạy trên artifact ấy; ai có thể đổi pipeline; ai phê duyệt production; bản chạy hiện tại có đúng artifact được duyệt không. Nếu build lại image ở mỗi môi trường từ cùng tag, bạn có thể có byte khác nhau vì dependency/base image đổi. Build một lần, định danh bằng digest, promote cùng artifact qua staging và production là mô hình dễ truy vết hơn.

Một workflow tối thiểu có `lint/unit`, `integration`, `build`, `scan`, `publish`, `deploy-staging`, `smoke`, `approve-production`, `deploy-production`, `observe`. Không nhất thiết mọi dự án có đủ ngay; mỗi gate cần nói rõ nó giảm rủi ro nào. Unit test bắt logic nhỏ; integration test bắt tương tác DB; SAST tìm pattern mã nguy hiểm nhưng có false positive/negative; SCA báo dependency có CVE nhưng phải triage khả năng ảnh hưởng; DAST kiểm tra ứng dụng đang chạy trong phạm vi test. Không gate nào thay quan sát production.

### Artifact, cache và secret là ba thứ khác nhau

Artifact là kết quả cần giữ để dùng ở job sau hoặc audit, ví dụ test report, SBOM, image digest. Cache tăng tốc bước lặp và có thể bỏ/rebuild; không dùng cache làm bằng chứng phiên bản. Secret cấp quyền cho job, phải giới hạn theo branch/environment, thời gian sống và scope. “Masked” chỉ che một số cách hiển thị trong log; code độc hại chạy trong job vẫn có thể gửi secret ra ngoài. Review thay đổi pipeline như review code đặc quyền. GitLab tài liệu hiện hành mô tả protected variables và protected runners cho protected refs; [đọc chính sách chi tiết](https://docs.gitlab.com/ci/pipelines/) trước khi tin rằng PR từ người lạ không chạm secret.

## Lab thiết kế: hai commit chạy chồng nhau

**Bối cảnh:** commit A và B merge liên tiếp; pipeline A deploy staging chậm, pipeline B deploy staging nhanh hơn. Nếu A hoàn tất sau B, staging có thể quay về bản cũ dù UI pipeline B xanh. Vẽ timeline của hai pipeline và chỉ ra môi trường tại từng phút. **Giải pháp:** serialize deployment vào cùng môi trường bằng cơ chế của nền tảng, hoặc kiểm soát revision mới nhất/guard. Thêm kiểm tra sau deploy rằng digest thực đang chạy bằng digest của pipeline thắng. Không dựa vào thứ tự commit để suy ra thứ tự job hoàn tất.

**Bài tập 2:** production deploy B, smoke test xanh nhưng error rate tăng sau 10 phút. Tính năng mới tạo queue backlog. Quy trình cần thời gian quan sát, alert theo SLO và quyết định rollback/roll-forward. Nếu DB migration không tương thích A, rollback image đơn giản không an toàn. Ghi quyết định trước release: chỉ số nào kích hoạt dừng, ai được quyết định, lệnh kiểm tra nào, đường phục hồi nào đã tập. Đây là nội dung runbook của release, không thể để tới lúc incident mới nghĩ.

## Mapping công cụ qua cùng một khái niệm

GitLab CI dùng `.gitlab-ci.yml`, GitHub Actions dùng workflow YAML, Azure DevOps Pipelines dùng YAML và environments/approvals, Jenkins dùng Jenkinsfile/pipeline. Cú pháp khác nhưng luôn hỏi: trigger, runner/agent, job dependency, artifact handoff, environment, secret scope, approval, concurrency và log audit. Argo CD không build code; nó đồng bộ manifest Git với Kubernetes. Ansible cấu hình máy/ứng dụng theo playbook; Terraform quản lý hạ tầng và state. Kết hợp công cụ theo trách nhiệm thay vì cố bắt một tool làm mọi việc.

### Ca phỏng vấn có lời giải

**CI xanh nhưng production chạy image cũ.** So commit -> image digest publish -> config deploy revision -> sync operation -> image ID trên Pod. Nếu repo triển khai còn digest cũ, lỗi ở promotion. Nếu Git đã đổi nhưng Argo OutOfSync, lỗi ở sync/policy. Nếu Deployment khai báo digest mới nhưng Pod cũ chưa rollout, xem readiness/capacity/rollout status. Câu trả lời “restart Jenkins” không gắn với bằng chứng.

**Pipeline có quyền cluster-admin để deploy.** Giảm phạm vi: service identity theo môi trường, namespace/resource tối thiểu, token ngắn hạn/OIDC khi hỗ trợ, branch protection và audit. Nếu dùng GitOps, pipeline chỉ cần cập nhật repo deploy qua PR; Argo controller có quyền được giới hạn bằng Project và RBAC cluster. Không có mô hình nào tự động an toàn nếu người được merge manifest có quyền quá rộng.

Đạt bài khi bạn vẽ được chuỗi commit-digest-revision-Pod, chỉ ra một race giữa hai deploy, phân biệt artifact/cache/secret và giải thích hai phương án rollback có điều kiện. Nguồn: [GitLab CI pipeline](https://docs.gitlab.com/ci/pipelines/), [GitHub Actions](https://docs.github.com/en/actions), [Azure Pipelines YAML](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/), [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/).
