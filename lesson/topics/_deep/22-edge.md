## Đọc một lỗi 502/503/504 theo lớp

Người dùng gửi HTTPS tới LB/reverse proxy; proxy chọn upstream qua DNS hoặc service discovery; upstream có thể là Nginx/PHP-FPM hoặc Kubernetes Service/Pod. `502` là phản hồi không hợp lệ từ upstream trong nhiều proxy; `503` thường do backend không sẵn sàng hoặc từ chối; `504` gợi ý timeout. Nhưng sản phẩm/config có thể khác nhau: phải xác định **thành phần nào tạo status**, xem access/error log và upstream status/time. Một request được proxy trả 504 vẫn có thể tiếp tục chạy ở app; client retry có thể tạo giao dịch trùng.

### Lab Nginx cho Notes API

Tại `lesson/labs/edge-local/`, chạy `docker compose up --build -d`. Nginx lắng nghe cổng 8080, `proxy_pass http://notes-api:8000`, chuyển `Host` và request ID. Gọi `GET /health` qua 8080 và trực tiếp 8000; ghi status/latency. Đổi upstream trong `nginx.conf` thành `notes-api:9999`, tái tạo Nginx container, gọi lại và đọc error log để xác nhận `connect() failed` hoặc lỗi tương ứng. Sửa về 8000; kiểm tra phục hồi. Dọn bằng `docker compose down` và chỉ thêm `-v` nếu chắc chắn không cần dữ liệu lab. Nếu chưa cài Docker, đọc config và giải thích vì sao hostname service được phân giải trong network Compose, còn `localhost` trong Nginx container không trỏ về Notes API.

## Load balancing và health check

Round robin, least connections hoặc weight giải vấn đề phân phối khác nhau; một backend chậm có thể giữ nhiều kết nối. Health check phải đủ phát hiện backend không phục vụ request quan trọng nhưng không phụ thuộc quá sâu khiến mọi backend bị loại khi một dependency chung lỗi. Cần timeout, retry, circuit breaking và connection limits có chủ đích. Nếu ba backend cùng gọi một DB đang chết, chuyển traffic qua lại không khắc phục DB. Khi thiết kế HA, xét LB cũng cần HA và DNS/route trỏ đúng khi một LB mất.

## Ingress, gateway, PHP-FPM và identity

Ingress controller áp route HTTP trong Kubernetes; API gateway có thể thêm auth, quota, transform, chính sách API; Keycloak cung cấp identity/token; PHP-FPM chạy code PHP phía sau web server. Chúng có thể cùng có mặt nhưng trách nhiệm khác nhau. Nếu auth chỉ ở gateway, kiểm tra service không bị truy cập bypass và token đúng issuer/audience/expiry. Nếu Nginx nói chuyện với PHP-FPM, kiểm tra pool worker, queue và memory khi tải cao; tăng worker bừa có thể làm DB quá tải. Luôn giữ request ID qua các hop để nối log.

### Tình huống phỏng vấn

Pod Ready, Service endpoints có, ingress trả 503 cho một path. Kiểm tra rule host/path, ingress controller event/log, service port/targetPort, NetworkPolicy và app route. Nếu chỉ một path lỗi, có thể rule rewrite hoặc app route thay đổi; không cần kết luận cluster hỏng. Trả lời theo bằng chứng: kết quả `curl` trực tiếp Service/Pod so với qua ingress, rồi diff cấu hình release gần nhất.
