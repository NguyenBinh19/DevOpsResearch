## Phân biệt lỗi bằng thời điểm request dừng

Một client báo “không vào được web” là triệu chứng quá rộng. Dùng timeline: **phân giải tên** (DNS trả gì), **mở kết nối** (SYN/SYN-ACK hoặc timeout), **bắt tay TLS** (chứng chỉ/SNI), **HTTP** (status/headers), **proxy upstream** (log và thời gian), **app/DB**. Ghi timestamp và điểm đo của từng phép thử. Nếu `curl` từ laptop thành công nhưng Pod lỗi, phép thử chỉ nói đường laptop tốt; phải chạy từ đúng Pod/node/subnet và đúng DNS resolver. Nếu lỗi chỉ từ một khu vực, xem CDN/LB/DNS/route theo khu vực trước khi restart API toàn cầu.

### Đọc timeout đúng lớp

DNS timeout: resolver không trả lời kịp, có thể do network tới DNS hoặc overload. TCP connect timeout: không hoàn tất handshake tới IP:port; có thể route, firewall, server không nhận/packet drop. TLS handshake timeout: TCP đã kết nối, nhưng handshake không hoàn tất; có thể proxy/CPU/certificate negotiation/network. HTTP read timeout: request có thể đã tới server, server chậm hoặc response bị kẹt; retry POST có thể tạo side effect lặp. Bốn timeout này cần metric/log khác nhau. Nếu thư viện chỉ báo “timeout” chung, cấu hình/log instrumentation để thấy phase.

## Ví dụ tính tải kết nối

Một API nhận 500 request/giây; mỗi request giữ connection DB trung bình 200 ms. Theo phép tính xấp xỉ của Little's Law, trung bình khoảng 100 request đồng thời ở đoạn DB (`500 x 0,2`). Nếu pool DB chỉ 50, request phải chờ dù CPU app còn rảnh; nếu latency DB tăng lên 1 giây, nhu cầu đồng thời xấp xỉ 500. Đây là ví dụ lý tưởng hóa; traffic burst, keepalive, queue và timeout làm thực tế khác. Nó giải thích vì sao một lỗi DB chậm có thể làm pool cạn rồi kéo theo HTTP 504 ở proxy. Tăng pool lên 500 có thể đẩy overload sang DB; cần tối ưu query, backpressure và timeout budget.

### Timeout budget end-to-end

Giả sử client timeout 3 giây, edge proxy timeout 5 giây, app gọi DB timeout 10 giây và retry hai lần. Client đã bỏ đi trước khi app dừng; app vẫn dùng tài nguyên, làm tải tăng. Thiết kế deadline lan truyền: tổng thời gian các bước + retry/backoff phải nằm trong ngân sách request, có chút dự phòng. Retry chỉ khi lỗi có khả năng tạm thời và operation idempotent hoặc có idempotency key. Nếu tất cả tầng đều retry 3 lần, một request có thể nhân tải rất lớn vào dependency đang lỗi.

## Bài phỏng vấn có lời giải

**DNS trả đúng IP, ping được, vì sao HTTPS vẫn lỗi?** Ping ICMP không chứng minh TCP 443/TLS/HTTP; kiểm tra connect, SNI/cert, Host header và proxy. **Có HTTP 404, network đã tốt hoàn toàn chưa?** Đã có đường tới một HTTP server, nhưng có thể là sai virtual host/route/upstream; cần xác định server nào trả 404. **Có 502 từ Nginx, app có thấy request?** Có thể không; đọc access/error log Nginx và app log cùng request ID. **Private Endpoint DNS đúng nhưng TCP timeout?** Xem route, NSG/firewall và chiều hồi đáp; identity chưa được kiểm tra vì chưa tới bước auth.

Bạn đạt bài khi một đồng nghiệp đưa một triệu chứng mơ hồ, bạn đặt được năm câu hỏi phân lớp và chọn phép thử chỉ tác động read-only. Tham chiếu [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110) và [TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446) khi cần cơ chế chính xác.
