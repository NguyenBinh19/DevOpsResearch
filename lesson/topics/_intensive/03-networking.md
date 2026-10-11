## Theo dấu một request, không học giao thức rời nhau

Khi bạn gõ `https://notes.example.com/notes`, trình duyệt cần phân giải tên, chọn IP, mở TCP tới cổng 443, thương lượng TLS, gửi HTTP request; reverse proxy có thể tiếp tục gọi upstream và upstream gọi DB. Mỗi chặng có kiểu lỗi riêng. `NXDOMAIN` xảy ra trước TCP. TCP timeout khác TLS certificate mismatch. HTTP 502 nghĩa một HTTP proxy đã trả lời, thường vì không nói chuyện được với upstream hợp lệ; HTTP 500 thường do server xử lý request nhưng lỗi nội bộ. Mã 502/503/504 phụ thuộc proxy cụ thể, vì vậy hãy đọc log của lớp phát mã thay vì coi bảng mã là chẩn đoán cuối.

Một IP không đủ xác định dịch vụ: cần giao thức, cổng, tên host và đôi khi đường URL. Ở TLS, Server Name Indication giúp server chọn chứng chỉ; ở HTTP, `Host` hoặc `:authority` giúp proxy chọn virtual host. Gọi thẳng IP có thể cho kết quả khác domain, dù cùng server. Nếu DNS chuyển domain sang IP mới mà bạn vẫn thấy IP cũ, phải xét TTL/cache ở resolver/client/proxy, không chỉ kiểm tra bản ghi authoritative.

### Ví dụ bốn phép thử có ý nghĩa khác nhau

`nslookup notes.example.com` kiểm tra một góc của DNS nhưng không chứng minh cổng mở. `Test-NetConnection notes.example.com -Port 443` trên PowerShell hoặc `nc -vz host 443` trên Linux kiểm tra TCP connect, chưa chứng minh TLS/HTTP. `curl -vI https://notes.example.com/` cho thấy TLS và HTTP headers, nhưng `HEAD /` có thể không tương đương `POST /notes`. Request nghiệp vụ có ID và body cụ thể mới kiểm tra ứng dụng. Ghi kết quả **thực** ở mỗi lớp; đừng ghi “network OK” sau một ping, vì ICMP có thể bị chặn hoặc đi đường khác TCP 443.

## CIDR và route qua một phép tính

Mạng `10.20.4.0/24` có 256 địa chỉ trong IPv4; trong thiết kế truyền thống, .0 là network và .255 là broadcast, nhưng số địa chỉ dùng được trên cloud còn phụ thuộc provider. Một subnet `10.20.4.0/24` và subnet `10.20.5.0/24` không chồng lấp; `10.20.4.128/25` nằm trong `/24` đầu. Nếu VNet/VPC on-prem và cloud dùng dải chồng lấp, route qua VPN có thể mơ hồ dù firewall mở. Trước khi tạo hybrid VPN, lập bảng CIDR của từng site, route table, NAT, DNS và owner. Một packet đi từ app đến DB cần route đi **và** route về; chỉ thấy SYN đi không chứng minh đường hồi đáp.

Security Group/NSG/firewall là lớp lọc; route xác định đường đi. Mở port trong firewall không tạo route. Một Private Endpoint mang IP riêng không tự bảo đảm hostname app phân giải về IP riêng; DNS zone/link và resolver path là phần của thiết kế. Chẩn đoán theo thứ tự: phân giải domain ở **nơi app chạy**, xem IP, route, TCP, TLS, auth. Tránh thử từ laptop rồi suy ra Pod trong cluster cũng đi cùng đường.

## Lab local: quan sát DNS, TCP và HTTP

**Điều kiện:** PowerShell hoặc Linux terminal, Python 3 và curl; dùng máy cá nhân. Ở terminal A chạy `python -m http.server 8765 --bind 127.0.0.1` (Linux có thể dùng `python3`). Ở terminal B thử `curl -v http://127.0.0.1:8765/`. **Dự kiến:** TCP connect rồi HTTP response 200 nếu server chạy và thư mục cho đọc. Tiếp tục gọi `/khong-co-file` để nhận HTTP 404: TCP vẫn thành công, lỗi nằm ở tài nguyên HTTP. Dừng server rồi gọi lại: kết nối thường bị từ chối. Ghi rõ ba dấu hiệu khác nhau trong output.

Tạo một file `hello.txt` trong thư mục lab và thử `curl -v http://localhost:8765/hello.txt`. `localhost` có thể phân giải IPv4/IPv6; nếu client thử `::1` trước nhưng server chỉ bind IPv4, curl có thể thử tiếp `127.0.0.1`. Đọc từng dòng connect thay vì kết luận từ một địa chỉ đầu tiên. Trên Windows, `curl` có thể là alias ở PowerShell cũ; dùng `curl.exe` nếu cần để xem output curl thực. Không mở server ra `0.0.0.0` trên mạng công cộng cho bài này.

**Bài tập lỗi proxy giả định:** proxy nghe 443, upstream cấu hình `127.0.0.1:8766` nhưng app nghe 8765. Client có thể hoàn tất DNS/TCP/TLS tới proxy rồi nhận 502. Sửa upstream port và kiểm chứng bằng request qua proxy; đổi DNS không chữa upstream sai. Nếu proxy chạy trong container, `127.0.0.1` là loopback của **container proxy**, không phải host/app container; cần tên service/mạng đúng.

## TLS và HTTP cho người vận hành

TLS cung cấp xác thực server qua certificate chain và mã hóa trên đoạn kết nối. Kiểm tra tên domain trong SAN, thời hạn, issuer/trust chain và thời gian hệ thống. Certificate hợp lệ trên client của bạn có thể không hợp lệ trong container thiếu CA phù hợp. TLS termination ở load balancer khiến đoạn LB->upstream là một kết nối khác; cần quyết định có mã hóa tiếp hay không, header `X-Forwarded-Proto`/client IP có được tin cậy từ proxy đúng không. Không tắt verify TLS trong script production để “cho chạy”.

HTTP là giao thức request/response: method, path, headers, body, status. GET nên không thay state theo kỳ vọng phổ biến; POST có thể tạo tài nguyên và cần chiến lược retry/idempotency. Timeout ở client có thể xảy ra sau khi server đã ghi DB nhưng trước khi response tới client. Nếu client retry POST không có idempotency key, dữ liệu có thể bị tạo đôi; đây là vấn đề ứng dụng và mạng cùng tham gia. WebSocket bắt đầu bằng handshake HTTP rồi nâng cấp thành kết nối lâu dài; proxy timeout/upgrade headers ảnh hưởng khác request ngắn.

## Ca điều tra có lời giải: API chỉ lỗi từ Kubernetes

Laptop gọi DB cloud được, Pod gọi báo timeout. Bước đầu không phải tăng timeout. Trong Pod, xác định hostname phân giải ra IP nào; so với laptop. Nếu Pod dùng Private Endpoint IP, kiểm tra route/NSG/network policy từ subnet node/Pod và firewall DB, rồi kiểm tra đường về. Nếu laptop dùng public IP, hai phép thử không tương đương. Nếu TCP kết nối được nhưng auth lỗi, chuyển sang identity/credential/TLS. Nếu chỉ một node lỗi, so route/CNI/DNS cache của node đó. Câu trả lời tốt nói rõ bằng chứng nào sẽ bác bỏ từng giả thuyết.

Bạn đạt bài khi vẽ request theo các lớp DNS -> route/TCP -> TLS -> HTTP -> upstream -> DB và chọn được phép thử cho từng lớp. Tài liệu chuẩn: [RFC 9110 HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110), [RFC 8446 TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446).
