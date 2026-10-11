## Thiết kế HA theo failure domain

VMware vSphere quản lý VM trên host, network ảo và datastore. Một cụm có hai host nhưng cùng một switch và một datastore vẫn có điểm lỗi chung. Trước khi nói "HA", lập bảng cho từng thành phần: host mất thì ai khởi động VM, storage mất thì dữ liệu ở đâu, network mất thì client đổi đường thế nào, site mất thì ai quyết định DR. vSphere HA có thể restart VM trên host còn lại, nhưng ứng dụng vẫn mất thời gian khởi động và kiểm tra dữ liệu. Live migration phục vụ bảo trì theo điều kiện hạ tầng; nó không thay backup.

### Bài tập capacity N-1

Host A và B mỗi host có 64 GiB RAM; VM trên mỗi host hiện dùng 45 GiB thực. Nếu một host mất, host còn lại không chứa được tổng 90 GiB mà không giảm tải hoặc đổi placement. Dù dashboard bình thường còn 19 GiB mỗi host, cluster không đạt mục tiêu chịu mất một host ở tải hiện tại. Tính lại với RAM overhead và VM quan trọng trước; cân nhắc thêm host, giảm overcommit/tải hoặc ưu tiên workload. Làm phép tính tương tự cho storage IOPS và network bandwidth; không chỉ CPU.

## Hybrid path và quyền sở hữu

API cloud gọi database on-prem qua private link/VPN. Đường đi phụ thuộc DNS, route, firewall, certificate, identity và DB grants. Chia owner: đội cloud quản lý VNet/route một phía, đội network quản lý tunnel/firewall, đội DB quản lý listener/user, đội app quản lý timeout/retry. Khi lỗi, một bản đồ owner tiết kiệm thời gian hơn câu "mạng có vấn đề". Kiểm tra từ đúng runtime cloud, không chỉ từ laptop trong văn phòng. Một `ping` thành công chưa chứng minh TLS/DB auth.

### Case: mất link 10 phút

Nếu API ghi đồng bộ vào DB on-prem, request sẽ timeout; retry không giới hạn có thể làm link/DB quá tải khi hồi phục. Chọn chính sách rõ: trả lỗi sớm và cho người dùng thử lại, đưa yêu cầu vào queue durable, hoặc chỉ cho đọc dữ liệu cache có nhãn stale. Mỗi chính sách cần nêu tính nhất quán, trải nghiệm và cách đối soát sau khi link trở lại. Đặt timeout ở app/ngateway hợp lý, circuit breaker theo nhu cầu, metric số request lỗi và backlog. Trong phỏng vấn, không hứa "hybrid luôn sẵn sàng" nếu chưa có đường mạng và data replication dự phòng được kiểm chứng.

## Thay đổi host an toàn

Trước maintenance: inventory VM, dependency, placement, backup, capacity host còn lại và khả năng rollback. Trong maintenance: di chuyển theo batch, health check ứng dụng, theo dõi storage latency và network. Sau maintenance: xác nhận workload về trạng thái mong muốn, lỗi/độ trễ và backup job. Ghi lại VM nào có thể di chuyển, VM nào cần downtime và điều kiện dừng. Mô phỏng trên giấy hoặc lab VM cá nhân chỉ chứng minh quy trình tư duy; vận hành vSphere production cần môi trường được giao quyền.
