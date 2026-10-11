## Portfolio phải chứng minh quyết định và vận hành

Một ảnh “Argo CD xanh” không chứng minh bạn hiểu DevOps. Dự án mạnh cho người phỏng vấn thấy: yêu cầu, kiến trúc, vì sao chọn công cụ, source và IaC, đường build/release, kiểm thử, telemetry, bảo mật, lỗi bạn đã gây có kiểm soát, cách bạn tìm và sửa, giới hạn còn lại. Nếu không có cloud budget, local kind/VM vẫn có giá trị khi bạn nói rõ điều gì chưa mô phỏng được: multi-zone HA, managed IAM, storage enterprise, traffic thật và on-call production. Đừng viết “kinh nghiệm production 3 năm” từ một lab.

Chọn một sản phẩm nhỏ xuyên suốt, ví dụ Notes API. Version 1 chạy trên Linux VM với systemd/Nginx/SQLite để học process, cổng và DB. Version 2 đóng Docker và Compose, thêm test/pipeline. Version 3 triển khai Kubernetes/Helm/Argo, metrics/logs, secret, backup/restore. Version 4 là thiết kế hybrid hoặc Azure theo JD, có IaC và cost/DR plan. Mỗi version giải một vấn đề mới; không thêm công cụ chỉ để tăng danh sách CV. Mục tiêu là kể được một câu chuyện kỹ thuật nối các lớp.

## Hồ sơ bằng chứng cho một dự án

Repository nên có README chạy local, sơ đồ luồng request và delivery, cấu trúc thư mục rõ, script/lab dùng được, pipeline config, IaC/manifest, runbook, bảng test/smoke và phần cleanup. Tạo `docs/decisions/` cho ADR ngắn: bối cảnh, lựa chọn, tradeoff, điều kiện xem lại. Ví dụ “chọn SQLite cho lab một instance vì đơn giản; khi scale API nhiều replica chuyển sang DB server managed/on-prem có backup/replication”; đây là đánh giá trưởng thành hơn khoe “đã cài MySQL”.

Evidence report nên ghi ngày, phiên bản tool, commit/digest, lệnh đã chạy, **kết quả thực đã quan sát**, lỗi gặp, cách sửa và điều gì chưa thử. Khi chụp output, xóa token, IP nội bộ nhạy cảm và dữ liệu cá nhân. Nếu không đủ tài nguyên chạy Ceph/ECK, hãy viết mô hình, bài toán capacity, rủi ro và kế hoạch test thực ở môi trường doanh nghiệp; không khẳng định đã vận hành chúng.

## Bài tập mock interview theo JD

**Câu 1: “Pipeline xanh nhưng sau release tỷ lệ 5xx tăng, bạn làm gì?”** Trả lời theo thứ tự: xác định tác động/đặt incident, mốc release/digest, metric theo route, log/trace request lỗi, diff config, Pod/Service/DB, quyết định giảm tác động và rollback có điều kiện, xác nhận phục hồi, postmortem. Không liệt kê 20 lệnh thiếu giả thuyết.

**Câu 2: “Ba VM K8s ở VMware, mỗi VM khác host, đủ HA chưa?”** Hỏi tiếp về rack/power/datastore/network/LB/DB, capacity N-1, etcd/control plane, storage, RTO/RPO và thử failover. Nếu chưa có thông tin, nêu giả định và giới hạn, không trả lời “đủ” chỉ vì ba host.

**Câu 3: “Bạn biết Terraform đến mức nào?”** Đưa một plan có thay đổi tạo/thay/xóa, giải thích state/backend/lock, drift, review, permission, destroy/restore và một ví dụ bạn tự làm. Nếu mới lab local, nói rõ và mô tả cách bạn sẽ áp dụng trên cloud dưới review. Trung thực về độ sâu giúp người phỏng vấn đặt câu hỏi đúng.

## Kế hoạch ôn phỏng vấn có bằng chứng

Lập ma trận JD: mỗi dòng là một trách nhiệm, ví dụ “triển khai GitLab CI”, “xử lý MySQL replication lag”, “tối ưu Nginx 502”, “Azure Private Endpoint”. Cột tiếp theo: khái niệm giải thích được, lab đã làm, lỗi đã xử lý, bằng chứng URL/file, giới hạn. Điền “chưa làm” thay vì dấu tick mơ hồ. Ưu tiên khoảng trống xuất hiện ở nhiều JD: Linux, networking, Git, Docker, CI/CD, IaC, K8s, observability, security, database. Công cụ chuyên biệt như WSO2/Oracle/Ceph có thể học theo vai trò mục tiêu sau nền tảng.

Mỗi tuần chọn một năng lực, thực hiện ba vòng: **giải thích** (viết sơ đồ 1 trang), **làm** (lab có bằng chứng), **phá và sửa** (failure injection có kiểm soát). Sau đó nhờ một người hoặc tự đóng vai interviewer hỏi “vì sao?” ba lần. Nếu câu trả lời cuối chỉ là “vì tutorial bảo vậy”, quay lại mô hình. Lặp lại lab sau một tuần mà không nhìn tài liệu để kiểm tra bạn còn nhớ cách suy luận, không chỉ nhớ lệnh.

## Mẫu câu trả lời trung thực và sắc nét

“Trong dự án lab của tôi, tôi triển khai Notes API trên kind bằng Helm và Argo CD. Tôi cố tình sửa sai Service selector; Pod vẫn Ready nhưng EndpointSlice không có backend, nên request qua Service lỗi. Tôi so labels/selector, khôi phục manifest trong Git, sync lại và xác nhận HTTP 200. Điều tôi chưa thử là cluster nhiều zone và ingress/LB production; nếu áp dụng thật, tôi sẽ thêm topology, SLO, capacity và rollback plan.” Câu trả lời có **bối cảnh, hành động, bằng chứng, kết quả và giới hạn**; tốt hơn một danh sách tên công cụ.

**Câu hỏi có lời giải:** chứng chỉ có thay portfolio không? Không; chứng chỉ chứng minh một loại kiến thức ở thời điểm thi, portfolio chứng minh cách làm và suy luận; cả hai không tự thay kinh nghiệm vận hành thật. **Một dự án gồm 15 tool có mạnh hơn ba dự án nhỏ?** Chỉ khi các tool có lý do, tích hợp đúng và có bằng chứng; độ rộng không bù lỗi nền tảng. Nguồn đọc thêm: [DORA capabilities](https://dora.dev/capabilities/) và [Google SRE Workbook](https://sre.google/workbook/).
