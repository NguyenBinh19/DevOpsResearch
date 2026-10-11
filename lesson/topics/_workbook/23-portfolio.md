## Rubric tự chấm trước khi đưa dự án vào CV

Chấm mỗi năng lực theo 0–3: **0** chưa làm; **1** đọc và giải thích được; **2** lab chạy có bằng chứng, gây/sửa một lỗi; **3** thiết kế tradeoff, automation, metric/rollback và có người khác review hoặc dùng được. Không tự cho điểm 3 vì xem tutorial. Đối với Linux, ví dụ điểm 2 là tự chẩn đoán process/socket/quyền/đĩa trên VM lab; điểm 3 đòi runbook/automation có kiểm chứng và đánh giá giới hạn. Với Kubernetes, điểm 2 gồm Deployment/Service/probe/EndpointSlice/rollout và một failure injection; điểm 3 gồm topology/capacity, security, observability và release plan. Điểm 3 lab vẫn chưa bằng nhiều năm on-call production; ghi rõ bối cảnh.

### Checklist trình bày một case 5 phút

1. Bài toán và ràng buộc: số dịch vụ, traffic, RTO/RPO, ngân sách lab. 2. Kiến trúc và vì sao chọn công cụ, kể cả phương án đơn giản hơn. 3. Một thay đổi bạn đã làm, commit/digest và gate. 4. Một sự cố bạn tự tạo hoặc gặp thật: triệu chứng, giả thuyết, bằng chứng, sửa và xác nhận. 5. Điều chưa làm và kế hoạch nếu chuyển production. Tập kể bằng sơ đồ một trang; người phỏng vấn có thể đào bất kỳ mũi tên nào, nên chỉ đưa thứ bạn giải thích được.

**Bài tập:** viết hai dòng CV. Dòng yếu: “Experienced Kubernetes, Jenkins, Terraform, ELK, Azure.” Dòng mạnh phải có hành động/đầu ra/bằng chứng đúng sự thật, ví dụ “Xây pipeline cho Notes API: test + build image digest + triển khai staging bằng Argo CD; mô phỏng lỗi readiness và ghi runbook xác nhận phục hồi.” Không bịa số uptime hay tiết kiệm chi phí. Nếu chưa làm thực tế, dùng từ “dự án lab” rõ ràng. Nguồn: [DORA capabilities](https://dora.dev/capabilities/).
