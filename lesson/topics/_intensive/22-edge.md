## Edge là nơi nhiều lớp cùng có thể trả lỗi

Một request từ Internet có thể đi qua DNS, CDN/WAF, external LB, Nginx/HAProxy, Kubernetes ingress controller, Service, Pod, PHP-FPM/app và DB. Khi thấy 502, 503 hoặc 504, trước tiên xác định **lớp nào phát mã** từ response headers và log tương ứng. 502 thường gợi proxy nhận response upstream không hợp lệ hoặc không kết nối được; 503 có thể là không có backend/overload/maintenance; 504 là timeout ở một proxy. Ý nghĩa chi tiết phụ thuộc sản phẩm/config. Một request có thể nhận 502 từ Nginx dù app hoàn toàn không nhận request; sửa app code khi chưa kiểm tra upstream sẽ mất thời gian.

Reverse proxy nhận request rồi gửi tới upstream. Load balancer chọn một trong nhiều backend theo thuật toán/health; web server có thể phục vụ static và proxy dynamic; PHP-FPM thực thi PHP qua FastCGI, không phải HTTP server công khai theo cách Nginx là. API gateway có thêm auth, rate limit, routing/transform/policy; identity provider như Keycloak phát hành/quản lý danh tính/tokens theo giao thức, không thay app authorization từng object. Kong/WSO2 có tập tính năng riêng và overhead vận hành; chọn sau khi rõ nhu cầu, không thêm gateway chỉ vì có trong JD.

## Port, Host, path và TLS qua ví dụ

Client gọi `https://api.example.com/v1/notes`. TLS có thể kết thúc ở LB; Nginx nhận HTTP với Host `api.example.com`, match `/v1/`, proxy tới app `notes:8000`. Nếu Nginx gửi nguyên `/v1/notes` nhưng app chỉ có route `/notes`, app trả 404; nếu Nginx strip prefix đúng, request thành công. Dấu `/` ở `proxy_pass` và rule rewrite có thể thay path theo cú pháp sản phẩm; không suy đoán, đọc config render và thử request cụ thể. Nếu proxy gửi sai `Host` hoặc `X-Forwarded-Proto`, app có thể tạo redirect sai vòng lặp hoặc link HTTP trong trang HTTPS. Chỉ tin forwarded headers từ proxy đáng tin cậy để tránh spoofing.

TLS ở edge bảo vệ đoạn client->edge; đoạn edge->upstream có thể dùng HTTP hoặc TLS khác. Với môi trường yêu cầu mã hóa end-to-end, xác định chứng chỉ/CA ở từng đoạn, SNI, hostname validation và rotation. Chứng chỉ hết hạn có thể làm client fail trước khi request tới app. Dùng `curl -v`/công cụ certificate để xem thời hạn/chain; không dùng `-k` làm cách chữa production vì bỏ kiểm tra identity server.

## Lab Nginx local từ cấu hình có sẵn

**Điều kiện:** Docker/Compose trên máy lab, file `lesson/labs/edge-local/compose.yaml` và `nginx.conf` đã có. Đọc trước để vẽ đường `client -> Nginx -> upstream`; ghi host port, Nginx listen port, upstream service/port, health path. Chạy Compose theo tài liệu dự án trong đúng thư mục, kiểm tra `docker compose ps`, gọi `curl -i` tới host port và đọc access/error logs. **Kết quả dự kiến:** request qua proxy tới app theo config; tên container và port phải lấy từ file thực, không dùng output giả định.

Gây lỗi trong **bản sao lab**: đổi upstream port sang port không có listener rồi reload/recreate Nginx; request có thể trả 502/504 tùy điều kiện. Đọc error log để thấy `connect() failed` hay timeout, thử gọi upstream trực tiếp từ mạng Compose, sửa port và xác nhận request phục hồi. Lỗi thứ hai: đổi path route sai để nhận 404 từ proxy/app; phân biệt bằng access log của app có request hay không. Dọn đúng Compose project và volume lab, không chạy `docker system prune` trên máy dùng chung.

## Ingress trên Kubernetes và Gateway API

Ingress resource mô tả host/path -> Service, nhưng phải có ingress controller triển khai; chỉ `kubectl apply` Ingress không tạo một proxy hoạt động. Kiểm tra IngressClass, controller pods, events, LB address, Service backend và EndpointSlice. Kubernetes docs hiện nói Ingress API đã frozen và khuyến nghị Gateway API cho khả năng mới; Ingress vẫn ổn định và được dùng rộng, không có nghĩa phải migrate ngay. Gateway API tách các vai trò/route theo tài nguyên và implementation cụ thể; đọc khả năng controller đang dùng. Nguồn: [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) và [Gateway API](https://kubernetes.io/docs/concepts/services-networking/gateway/).

## Health check và thuật toán không thay capacity

LB health check chỉ tốt bằng endpoint kiểm tra. Nếu chỉ kiểm tra TCP connect, app có thể accept socket nhưng trả 500 mọi request. Nếu health check gọi DB quá nặng và DB chập chờn, toàn bộ backend có thể bị loại cùng lúc. Thiết kế endpoint rẻ, có ý nghĩa “có thể nhận request” và đo qua luồng người dùng riêng. Round robin chia đều số request nhưng request dài/ngắn khác nhau; least connections hoặc weight có thể hữu ích tùy workload/implementation. Không chọn thuật toán trước khi đo bottleneck và capacity downstream.

**Ca có lời giải:** sau deploy, Nginx 502 cho mọi request; Pod app Ready. Đọc upstream trong config và log Nginx, kiểm tra DNS tên service từ proxy, Service selector/EndpointSlice, port/targetPort và process bind. Pod Ready không chứng minh proxy đang gọi đúng port. Nếu một số request lỗi, xem backend cụ thể, keepalive/timeout, canary revision và app logs theo request ID. **Câu hỏi:** Keycloak đã xác thực user A, API có cho đọc note của user B không? Không tự động; app phải kiểm tra authorization theo object/tenant.

Nguồn: [NGINX reverse proxy/load balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/), [HAProxy documentation](https://www.haproxy.org/documentation/), [Keycloak docs](https://www.keycloak.org/docs/).
