## PHP-FPM và reverse proxy: request chạy ở đâu?

Với PHP stack, Nginx nhận HTTP/TLS, phục vụ static hoặc chuyển PHP request tới PHP-FPM qua FastCGI socket/TCP; PHP code chạy trong worker PHP-FPM và gọi DB. Nếu Nginx trả 502, có thể socket PHP-FPM không tồn tại, sai quyền socket, pool worker hết/timeout hoặc PHP-FPM chết. Nếu Nginx phục vụ CSS được nhưng `/index.php` lỗi, DNS/TLS/edge tới Nginx đã đi qua; tập trung FastCGI/PHP-FPM. Nếu PHP-FPM log báo `max_children reached`, tăng worker có thể giúp nhưng phải tính RAM mỗi worker và DB connections; tăng mù có thể làm máy/DB quá tải.

### Health check và draining khi release

Một LB bỏ backend sau một lần health check fail có thể tạo dao động nếu endpoint chập chờn; cần threshold/interval và hiểu thời gian phát hiện. Khi rolling deploy, backend cũ cần ngừng nhận request mới, hoàn tất request đang chạy trong grace period, rồi thoát. Nếu proxy còn giữ keepalive tới Pod sắp chết, người dùng có thể thấy 502 rải rác. Đo số request lỗi theo backend/revision và mốc shutdown; chỉnh readiness, preStop/grace period hoặc LB draining theo implementation. Không tăng timeout vô hạn để giấu ứng dụng không shutdown đúng.

## Rate limiting, auth và client IP

Rate limit ở edge bảo vệ downstream nhưng có thể chặn người dùng chung NAT nếu key chỉ là IP; nếu key là user ID, cần xác thực trước và chống spoofing. Header `X-Forwarded-For` có thể chứa dữ liệu do client tự gửi nếu proxy không chuẩn hóa; chỉ tin danh sách proxy đã định. API gateway có thể validate token, nhưng app vẫn cần kiểm tra quyền đối tượng (user A không đọc dữ liệu user B). Keycloak/OIDC cung cấp identity/token; token cần kiểm tra issuer, audience, thời hạn và signature theo library/chính sách phù hợp, không chỉ decode base64.

## Case có lời giải: chỉ 504 ở endpoint export

`GET /export` mất 90 giây; proxy timeout 60 giây, app vẫn xử lý và tạo file. Tăng proxy timeout lên 120 giây có thể chữa triệu chứng ngắn hạn nhưng giữ connection/resource rất lâu. Thiết kế tốt hơn có thể là job bất đồng bộ: POST tạo export job với idempotency, trả job ID; worker tạo file, người dùng poll/download khi xong; alert backlog/age. Nếu buộc đồng bộ, đo tải, giới hạn concurrency, deadline và cancellation. Mã 504 từ proxy không tự nói app có hoàn tất hay chưa, nên retry có thể tạo job trùng.

**Câu hỏi:** Ingress YAML có host/path đúng nhưng không có traffic, vì sao? Kiểm tra ingress controller/IngressClass, LB address/DNS, Service backend/EndpointSlice, TLS, firewall. **502 chỉ từ một backend?** Gắn log/metric theo upstream, kiểm tra instance đó khác config/version/node. Nguồn: [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/), [NGINX admin guide](https://docs.nginx.com/nginx/admin-guide/).

**Bài tập thứ tự kiểm tra:** người dùng báo 503 từ domain public. Bắt đầu bằng request `curl -v` kèm Host/domain thật để biết IP, TLS và response headers. Nếu LB trả 503 trước ingress, xem LB target health; nếu ingress controller trả 503, xem Ingress route, Service và EndpointSlice; nếu app trả 503, xem log/DB/dependency. Ghi một dấu hiệu giúp phân biệt nguồn phát mã ở từng nhánh. Chỉ sau khi có nguồn phát mã mới quyết định sửa LB, ingress hoặc app. Một port-forward vào Pod thành công không chứng minh domain public được route đúng.
