## Thiết kế từ câu hỏi vận hành, không từ dashboard đẹp

Hỏi trước: khi người dùng báo “tạo note chậm”, bạn cần biết request nào, từ lúc nào, bao nhiêu người bị ảnh hưởng và nó chậm ở API, DB hay mạng? **Metric** trả lời xu hướng/tỷ lệ trên nhiều request; **log** giữ sự kiện chi tiết; **trace** nối một request qua nhiều bước. Không loại nào thay được loại còn lại. CPU thấp không chứng minh app nhanh; log đầy đủ nhưng thiếu request ID vẫn khó ghép chuỗi; trace mẫu có thể không bắt đúng request lỗi nếu sampling thấp.

Định nghĩa một SLI cụ thể cho `POST /notes`: tỷ lệ request hợp lệ trả 2xx/3xx trong dưới 500 ms tại edge, trong cửa sổ 30 ngày. Phải quyết định request 4xx do client có đưa vào mẫu số không, timeout đo ở đâu, maintenance có loại trừ không. SLO 99,9% trên 1.000.000 request đủ điều kiện cho tối đa khoảng 1.000 request “không tốt” theo định nghĩa này. Nếu 500 request hỏng trong một giờ, bạn đã tiêu nửa error budget tháng dù availability tính theo phút có thể kể khác. Một con số không có định nghĩa là khó dùng để quyết định release.

### Cardinality là chi phí và rủi ro

Metric `http_requests_total{route="/notes",status="500"}` có số tổ hợp label vừa phải. Nếu thêm `user_id` hoặc raw URL chứa ID, số series có thể tăng theo số người dùng/request, gây tốn bộ nhớ/chi phí và query chậm. Dùng route template (`/notes/{id}`), không dùng path thực làm label. Log có thể chứa ID chi tiết với chính sách bảo vệ dữ liệu và retention phù hợp; trace ID là cầu nối từ metric spike sang một request mẫu. Thiết kế telemetry cùng code/pipeline, không đợi sự cố mới thêm.

## Lab phân tích một sự cố giả định bằng ba tín hiệu

**Dữ kiện:** trước release, 10.000 req/5 phút, 20 lỗi 5xx, p95 180 ms. Sau release, 10.000 req/5 phút, 600 lỗi 5xx, p95 1,8 s, CPU API 35%, DB connection pool gần đầy. Tỷ lệ lỗi tăng từ 0,2% lên 6%. Nếu SLO là 99,9% request tốt, cửa sổ 5 phút này tiêu 600 lỗi trên 10.000 request; cần xem định nghĩa lỗi thực của SLI. Bạn không thể nói “CPU thấp nên không sao”.

**Bước 1:** dashboard metric xác định bắt đầu tăng từ revision nào và route nào. **Bước 2:** lọc log theo route, status và request ID; tìm lỗi `connection acquisition timeout` nếu có, không tự bịa log khi chưa quan sát. **Bước 3:** trace một request chậm; nếu phần lớn thời gian chờ lấy DB connection, giả thuyết mạnh là pool/leak/query chậm. **Bước 4:** đọc DB pool active/idle, DB connection count, slow query và thay đổi release. **Bước 5:** giảm tác động theo runbook, sau đó xác nhận error rate/p95 phục hồi. Viết rõ bằng chứng nào bác bỏ giả thuyết pool.

## Prometheus, Grafana, logs và OpenTelemetry đặt ở đâu?

Prometheus scrape metric từ target hoặc exporter; Grafana truy vấn/hiển thị và có thể hỗ trợ alert tùy cấu hình. Alertmanager nhận alert từ Prometheus, gom nhóm, route, silence/inhibit theo chính sách. Loki/ELK/ECK lưu/truy vấn log theo mô hình khác; OpenTelemetry chuẩn hóa thu thập traces/metrics/logs qua SDK/Collector và backend. Không coi “đã cài Prometheus/Grafana” là có observability: cần metric ứng dụng, ownership, retention, dashboard đúng câu hỏi và alert có người xử lý.

Khi triển khai ECK trên Kubernetes, Elasticsearch cần storage bền, capacity RAM/disk, chính sách index/retention, backup snapshot và kiểm soát quyền. Log pipeline có thể mất dữ liệu khi buffer đầy hoặc network đứt; phải biết yêu cầu mất mát chấp nhận được và alert cho chính pipeline. Một cluster logging production là workload stateful riêng, không phải vài YAML có thể thêm vào cuối lab K8s.

## Alert đáng đánh thức người trực ca

Một page nên gắn với triệu chứng người dùng hoặc rủi ro sắp gây ảnh hưởng, có ngưỡng, cửa sổ, severity, owner và hành động đầu tiên. “CPU > 80% trong 1 phút” thường không nói người dùng có đau không và có thể gây alert fatigue. Error rate/latency và burn rate theo SLO cho quyết định rõ hơn, cộng thêm capacity alert trước khi hết disk. Prometheus khuyến nghị ít alert, ưu tiên triệu chứng và có dashboard/runbook hữu ích; [xem alerting practices](https://prometheus.io/docs/practices/alerting/). Cần metamonitoring: nếu hệ thống giám sát chết, ai phát hiện?

**Bài tập:** viết một alert cho `POST /notes` lỗi cao trong 10 phút. Ghi numerator/denominator, số request tối thiểu để tránh nhiễu khi traffic thấp, link dashboard, runbook, owner và điều kiện tắt page sau khi phục hồi. Đọc thử với tình huống chỉ có 2 request và 1 lỗi: tỷ lệ 50% không nhất thiết đáng gọi người dậy. Đọc [Prometheus alerting overview](https://prometheus.io/docs/alerting/latest/overview/) và [OpenTelemetry docs](https://opentelemetry.io/docs/).
