# Chuyên đề 12 - Edge, gateway và quan sát hệ thống

Các JD nêu Nginx, HAProxy, PHP-FPM, ingress, Kong, WSO2, Keycloak, Prometheus, Grafana, ECK/ELK, Loki, Zabbix, OpenTelemetry và Azure Monitor. Học các tên này theo **đường đi của một request**. Khi người dùng báo lỗi, bạn phải biết request dừng ở lớp nào, tín hiệu nào xác nhận và ai có thể sửa. Không nên cài đồng thời mọi stack chỉ để có ảnh dashboard.

```text
DNS -> TLS/LB -> proxy/ingress/gateway -> Service -> Pod -> DB
         |                |                 |       |
       logs             access log       metrics  trace spans
         +---------------- request/trace ID --------+
```

Để đọc sơ đồ, chọn một request cụ thể và lần theo mã định danh của nó. Metric cho phạm vi/tần suất, log cho sự kiện, trace cho thời gian qua từng hop.

## Bài 1. Từ trình duyệt đến tiến trình ứng dụng

Người dùng gõ tên miền. DNS trả địa chỉ; client tạo kết nối TCP; TLS xác thực máy chủ và mã hóa; HTTP request tới load balancer/reverse proxy; proxy định tuyến tới ứng dụng; ứng dụng gọi database/cache/queue rồi trả response. Với Kubernetes, đường đi có thể thêm cloud load balancer -> ingress controller/gateway -> Service -> Pod. Mỗi hop có log, timeout, giới hạn kết nối và health check khác nhau.

`502 Bad Gateway` thường cho thấy proxy không nhận được phản hồi hợp lệ từ upstream; `503` có thể do thiếu backend sẵn sàng; `504` là timeout ở một gateway. Đây là manh mối, không phải chẩn đoán cuối. Cần xem **proxy nào** trả mã, upstream status, request ID, thời gian, pod endpoints và log ứng dụng. Một request chậm 30 giây có thể bị timeout ở proxy dù ứng dụng vẫn xử lý xong và ghi database; retry từ client khi đó có nguy cơ tạo thao tác trùng.

### Bài tập đọc luồng lỗi

Notes API local trả `/health` bình thường nhưng người dùng qua tên miền nhận 502. Liệt kê kiểm tra từ ngoài vào: DNS trỏ đúng chưa; TLS handshake; proxy có route đúng path/host; upstream host/port; service process có lắng nghe; firewall; application log. Với mỗi bước viết lệnh hoặc tín hiệu định dùng và kết quả nào sẽ loại trừ giả thuyết. Không bắt đầu bằng restart mọi thành phần: restart có thể làm mất bằng chứng.

## Bài 2. Nginx, HAProxy, web server và PHP-FPM

Nginx có thể phục vụ file tĩnh, reverse proxy, TLS termination và load balancing. HAProxy mạnh ở proxy/load balancing tầng TCP/HTTP, health check và điều tiết traffic. Hai công cụ có vùng giao nhau; lựa chọn phụ thuộc lưu lượng, cách cấu hình, hệ sinh thái và yêu cầu vận hành. Với PHP stack, Nginx nhận HTTP rồi chuyển yêu cầu PHP qua FastCGI tới PHP-FPM; PHP-FPM quản lý worker thực thi PHP. Trả file tĩnh và chạy PHP là hai công việc khác.

Một cấu hình proxy cần các quyết định rõ: upstream nào, thuật toán phân phối, timeout connect/read/write, kích thước request, header `Host`/`X-Forwarded-*`, TLS certificate, health check, log format và giới hạn kết nối. Health check quá nông (`200` từ web server) có thể bỏ sót database chết; quá sâu lại có thể làm toàn backend bị loại khi một dependency tạm chậm. Header forwarded sai có thể khiến app tạo URL HTTP thay vì HTTPS hoặc ghi sai IP client. Chỉ tin forwarded headers từ proxy đáng tin; client có thể tự gửi header giả.

### Lab 1 - Reverse proxy cho Notes API

Trên máy lab có Docker, chạy Notes API từ `lesson/labs/notes-api/compose.yaml` rồi thêm một Nginx container cùng network. Cấu hình một `server` lắng nghe cổng lab và `proxy_pass` tới tên service/port Notes API; giữ `Host`, gửi request ID nếu cần. Gọi `GET /health` qua proxy, so response trực tiếp qua app. Sau đó cố ý đổi upstream port sai; quan sát HTTP status và error log của Nginx. Sửa lại và xác nhận phục hồi. **Kết quả mong đợi:** đường trực tiếp còn sống khi proxy lỗi, chứng minh phạm vi sự cố ở edge. **Dọn dẹp:** dừng stack và xóa container lab; giữ database volume nếu còn dùng ở module khác.

### Tình huống tải cao

Proxy nhận 10.000 kết nối nhưng PHP-FPM chỉ có ít worker, database query chậm. Tăng `max_children` bừa có thể tăng memory và làm DB quá tải. Hãy lấy queue length, worker busy, request latency, DB connection/slow query và memory trước. Nếu nhiều request đang chờ cùng một dependency, tăng worker chỉ chuyển hàng đợi xuống DB. Đây là ví dụ cần quan sát toàn đường đi.

## Bài 3. Ingress controller, API gateway và identity provider

Ingress là tài nguyên mô tả quy tắc HTTP routing trong Kubernetes; cần ingress controller chạy để áp dụng. Nginx ingress controller là một cách thực hiện. Kubernetes Gateway API là mô hình resource khác với vai trò tách người quản trị hạ tầng và route ứng dụng. API gateway như Kong hoặc WSO2 có thể thêm auth, rate limit, transformation, developer portal hoặc quản trị API. Đừng thêm gateway khi chỉ cần route đơn giản: mỗi lớp thêm độ phức tạp, latency và điểm lỗi.

Keycloak là identity and access management: xác thực người dùng, cấp token theo giao thức như OAuth 2.0/OpenID Connect và quản lý realm/client/role. API gateway có thể kiểm tra token trước khi chuyển request, nhưng ứng dụng vẫn phải kiểm tra quyền phù hợp nghiệp vụ. TLS bảo vệ đường truyền; token chứng minh danh tính/ủy quyền theo điều kiện; chúng không thay thế nhau. Một token có chữ ký hợp lệ nhưng sai audience hoặc hết hạn vẫn phải bị từ chối. Cần phân biệt lỗi 401 (chưa xác thực) với 403 (đã xác thực nhưng thiếu quyền) trong chính sách của app/gateway.

### Bài tập thiết kế gateway

Ba microservice `/users`, `/orders`, `/admin`. Dịch vụ admin chỉ cho một nhóm nội bộ. Vẽ nơi kết thúc TLS, nơi kiểm tra token, nơi áp rate limit, đường log và request ID. Nếu gateway hỏng, có bypass trực tiếp tới service không? Nếu có, chính sách auth ở gateway có thể bị vượt qua; hãy nói cách giới hạn network và/hoặc kiểm tra token ở service. Với Keycloak, mô tả quy trình rotation key/cert và cách dịch vụ lấy JWKS khi mạng gặp lỗi.

## Bài 4. Metric, log, trace: ba góc nhìn khác nhau

Metric là số liệu tổng hợp theo thời gian: request rate, error rate, latency percentile, CPU, queue depth. Log là bản ghi sự kiện có ngữ cảnh: request ID, phiên bản, lỗi cụ thể. Trace liên kết các span của cùng một request qua nhiều dịch vụ. Metric cho biết **có vấn đề**; trace gợi ý **đoạn nào chậm**; log giải thích **sự kiện cụ thể**. Không có một loại tín hiệu nào thay hoàn toàn hai loại kia.

Prometheus thường scrape endpoint metrics và lưu time series với labels. Grafana truy vấn và hiển thị, nhưng dashboard không tự tạo metric. Label có cardinality quá cao, ví dụ gắn user ID hoặc request ID vào mỗi time series, làm tăng số series và chi phí. Dùng request ID trong log/trace; dùng route template như `/notes/{id}` làm metric label thay vì path chứa mọi ID. Alert nên gắn với triệu chứng người dùng, như tỷ lệ lỗi và độ trễ so với SLO, rồi thêm alert hạ tầng có hành động rõ. Alert cho mọi CPU spike dễ gây nhiễu.

ELK/ECK/EFK gom log: shipper/collector gửi, Elasticsearch lưu và index, Kibana truy vấn; ECK là operator quản lý Elastic trên Kubernetes. Loki chọn mô hình log khác: labels cho stream và nội dung log được tìm kiếm theo cách phù hợp; vẫn phải hạn chế cardinality của labels. Zabbix thường mạnh cho giám sát hạ tầng truyền thống, item/trigger/host. Không nên nói "có Prometheus thì không cần Zabbix" nếu còn network device/VM và team đã vận hành Zabbix tốt. Chọn theo câu hỏi cần trả lời, chi phí lưu giữ, quyền truy cập log và khả năng vận hành.

OpenTelemetry cung cấp API/SDK và collector cho telemetry, giúp thu thập/biến đổi/xuất metric, log, trace tới backend. OTel không phải dashboard hay hệ lưu trữ cuối cùng. Cần quyết định sampling cho trace, correlation giữa request ID/trace ID, retention và loại bỏ dữ liệu cá nhân hoặc secret khỏi telemetry.

### Lab 2 - Điều tra một request lỗi bằng ba loại tín hiệu

Giả sử dashboard cho thấy p95 latency tăng từ 200 ms lên 2 s sau release. Trace của request chậm có span DB 1.7 s; log ghi query timeout và version `v2`; metric DB cho thấy connection pool chạm trần. Viết giả thuyết, bằng chứng hỗ trợ và kiểm tra tiếp. Có thể lỗi do query mới, connection leak hoặc DB chậm; trace và metric chưa đủ để chọn một. Đề xuất mitigations như rollback v2 hoặc giới hạn traffic, rồi cách xác nhận p95/error rate hồi phục. Đừng chỉ nhìn CPU pod.

## Bài 5. Azure Monitor, App Insights và KQL

Trong nhánh Azure, Application Insights quan sát ứng dụng qua request/dependency/exception; Log Analytics Workspace lưu log có thể truy vấn bằng Kusto Query Language (KQL); Azure Monitor Alerts chạy rule trên metric hoặc query. Quan hệ giữa resource, workspace và bảng log tùy cấu hình, nên khi điều tra cần xác nhận app đang gửi telemetry vào workspace nào và có sampling/retention ra sao. Một biểu đồ trống có thể do không thu thập, sai workspace, sai time range, quyền truy cập hoặc query sai; đừng kết luận "không có lỗi".

Ví dụ KQL mang tính minh họa, cần đối chiếu tên bảng/schema của workspace đang dùng:

```kusto
AppRequests
| where TimeGenerated > ago(1h)
| summarize total=count(), failed=countif(Success == false) by bin(TimeGenerated, 5m)
| extend error_rate = todouble(failed) / total
```

Để điều tra một sự cố, lọc time range, service/version, operation/trace ID, rồi xem dependency và exception liên quan. KQL là công cụ đặt câu hỏi; chọn sai mẫu dữ liệu hoặc không tính sampling sẽ làm tỷ lệ sai. Với alert, ghi rõ ngưỡng, thời gian đánh giá, người nhận, runbook và cách kiểm tra alert đã hoạt động.

## Bài 6. Incident: từ phát hiện đến học lại

Một quy trình sự cố ngắn: xác nhận tác động người dùng; phân vai người điều phối và người điều tra; đặt mốc thời gian; giảm tác động (rollback, chuyển traffic, bật capacity dự phòng); thu bằng chứng; xác nhận phục hồi; viết postmortem không đổ lỗi. Không chờ hiểu toàn bộ root cause mới giảm tác động nếu có cách khôi phục an toàn. Nhưng cũng không "rollback mọi thứ" khi sự cố do cert hết hạn hay database đầy.

### Diễn tập tổng hợp

Sau một release, 30% request qua ingress trả 503, direct pod health vẫn 200. Hãy kiểm tra endpoints, readiness, selector, policy, upstream error, chỉ số theo pod và phiên bản. Nếu chỉ pod mới lỗi, tách traffic/rollback deployment; nếu mọi pod cùng lỗi, xem dependency chung. Sau khi khôi phục, viết timeline gồm phát hiện, giả thuyết, bằng chứng loại trừ, hành động, thời điểm metric trở lại bình thường và thay đổi để lần sau phát hiện nhanh hơn.

## Case study có lời giải: p95 tăng nhưng CPU bình thường

**Bối cảnh:** p95 latency tăng từ 180 ms lên 1,8 s, CPU pod 35%, error rate chưa tăng. Đừng loại trừ sự cố vì CPU thấp. Xem latency theo route, theo version và theo upstream; trace cho thấy 1,5 s chờ SQL; DB metric báo connection pool đang chờ. Từ đây cần phân biệt query chậm, số connection bị giữ quá lâu hoặc pool quá nhỏ so với tải. Xem slow query/lock, active vs idle connection, tốc độ request và thay đổi gần thời điểm tăng. Nếu có query mới, rollback hoặc tối ưu query có thể giảm tác động nhanh; chỉ tăng pool có thể làm DB quá tải.

**Alert tốt hơn:** nếu SLO latency bị đốt nhanh trong một khoảng xác định và đủ traffic, báo người vận hành cùng link dashboard, query/trace mẫu và runbook. Đừng alert mỗi lần một request đơn lẻ chậm; cũng đừng chờ đến 5xx vì trải nghiệm đã xấu trước đó. Sau khôi phục, so p95, throughput, pool wait và phản hồi người dùng với baseline.

## Cổng hoàn thành và câu hỏi phỏng vấn

1. Vẽ đường request từ DNS/TLS qua proxy/ingress đến app và database; chỉ ra log/metric ở mỗi hop.
2. Tự tạo lỗi upstream sai port trong lab và xác định bằng status + log, không chỉ đoán theo mã 502.
3. Phân biệt ingress, API gateway, identity provider, reverse proxy và load balancer bằng trách nhiệm cụ thể.
4. Với một request chậm, dùng metric, trace và log để đề xuất phép kiểm tra kế tiếp; giải thích cardinality và sampling.
5. Viết một alert có hành động, runbook ngắn và bằng chứng sau khôi phục.

Các stack Enterprise như ECK, WSO2 và HAProxy cluster cần tài nguyên/hệ thật để tích lũy kinh nghiệm sâu. Bài thiết kế và lab nhỏ giúp hiểu cơ chế; hãy trình bày trung thực mức thực hành khi phỏng vấn.

## Tài liệu chính thức

- Nginx admin guide: https://docs.nginx.com/nginx/admin-guide/
- HAProxy documentation: https://www.haproxy.org/documentation/
- PHP-FPM: https://www.php.net/manual/en/install.fpm.php
- Kubernetes ingress: https://kubernetes.io/docs/concepts/services-networking/ingress/
- Kong Gateway docs: https://developer.konghq.com/gateway/
- Keycloak docs: https://www.keycloak.org/documentation
- Prometheus concepts: https://prometheus.io/docs/concepts/data_model/
- Grafana docs: https://grafana.com/docs/grafana/latest/
- Elastic Cloud on Kubernetes: https://www.elastic.co/guide/en/cloud-on-k8s/current/index.html
- Loki docs: https://grafana.com/docs/loki/latest/
- Zabbix docs: https://www.zabbix.com/documentation/current/en/manual
- OpenTelemetry docs: https://opentelemetry.io/docs/
- Azure Monitor logs/KQL: https://learn.microsoft.com/azure/azure-monitor/logs/log-query-overview
