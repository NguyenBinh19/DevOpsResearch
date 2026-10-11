## Histogram và p95 phải đọc có ngữ cảnh

Nếu 95% request dưới 200 ms và 5% request mất 10 giây, trung bình có thể trông vừa phải nhưng p95/p99 cho thấy đuôi chậm. Ngược lại, p95 của một route có 10 request trong 5 phút rất nhiễu. Khi xem latency, tách route/method/status và traffic volume, tránh label user ID. Histogram bucket phải đủ độ phân giải quanh SLO threshold; bucket 0,1s và 10s không giúp đánh giá mục tiêu 500 ms chính xác. Nếu hệ thống dùng trace sampling, 1 trace chậm không đại diện thống kê toàn bộ; dùng metric để định lượng, trace để giải thích một mẫu.

## Mẫu runbook alert

Alert `NotesApiHighErrorRate` nổ khi SLI 5xx/eligible requests vượt ngưỡng trong cửa sổ đủ dài và lưu lượng tối thiểu. Runbook mở dashboard theo route/revision, kiểm tra synthetic request, so deploy gần nhất, log request ID, DB/queue health, rồi chọn giảm tác động. Annotation chứa owner, link dashboard và cách silence hợp lệ khi bảo trì. Sau incident, xem alert có nổ sớm quá/muộn quá, có page trùng nhau không, và người trực ca có hành động rõ không. Một alert chỉ nói “CPU 80%” thường thiếu hành động.

**Câu hỏi:** log đầy đủ có thay metric không? Không; tổng hợp log khi incident có thể chậm/tốn và thiếu dữ liệu nếu pipeline lỗi. **Metric xanh có chứng minh người dùng ở ngoài vào được?** Không nếu chỉ scrape nội bộ; thêm blackbox/synthetic từ đường người dùng. Nguồn: [Prometheus alerting practices](https://prometheus.io/docs/practices/alerting/).
