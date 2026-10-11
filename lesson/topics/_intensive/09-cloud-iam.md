## Thiết kế cloud từ luồng dữ liệu và quyền

Trước khi chọn AWS/Azure/GCP service, vẽ request: Internet -> edge -> ứng dụng -> DB/queue/storage, cộng thêm đường quản trị và monitoring. Đánh dấu dữ liệu nào rời vùng riêng, danh tính nào gọi API nào và failure domain của từng dịch vụ. VM, container, App Service hoặc serverless đều có compute; managed DB chuyển một phần trách nhiệm patch/HA cho provider nhưng bạn vẫn sở hữu schema, quyền, backup policy và kiểm tra restore. “Managed” không có nghĩa không cần vận hành.

**Shared responsibility** thay đổi theo dịch vụ. Trên VM, bạn thường chịu OS hardening và patch; trên managed app platform, provider làm nhiều hơn ở host nhưng app code, dependency, identity và dữ liệu vẫn thuộc bạn. Cần đọc thỏa thuận cụ thể của provider/service, không dùng một bảng chung để kết luận mọi cấu hình an toàn. Ở hybrid, đường on-prem -> cloud có thêm VPN/ExpressRoute/Direct Connect, DNS, firewall, route và identity trust; lỗi ở bất kỳ lớp nào có thể giống lỗi ứng dụng.

## IAM: chủ thể, hành động, tài nguyên và điều kiện

Mỗi quyết định quyền có bốn phần: **ai** (human/service identity), **làm gì** (action), **trên tài nguyên nào**, **trong điều kiện nào**. Ví dụ CI chỉ cần đẩy image vào một registry repo, không cần quyền sửa VNet. App chỉ cần đọc một secret hoặc ghi một queue, không cần owner cả subscription/account. Quyền rộng làm giảm thời gian gỡ lỗi trước mắt nhưng mở rộng blast radius. Dùng managed/workload identity và token ngắn hạn khi nền tảng hỗ trợ; tránh cất access key lâu dài trong repo hoặc máy cá nhân.

RBAC cho phép có điều kiện không đồng nghĩa network đã mở; network mở không đồng nghĩa identity có quyền. Nếu Azure SQL trả lỗi, phân biệt DNS/private route/TCP/TLS/auth/database permission. Nếu cloud API trả `Forbidden`, xem principal thực của workload (khác principal bạn dùng ở portal), role scope, deny policy và thời gian propagation. Ghi lại identity qua log/audit, không đoán dựa vào tên Pod.

## Mạng riêng qua một kịch bản

Notes API chạy trong subnet ứng dụng; DB dùng private endpoint. App gọi hostname DB chuẩn. DNS phải trả IP private từ nơi app chạy; route và NSG/firewall phải cho app tới IP/cổng; DB auth phải chấp nhận identity; DB engine phải phục vụ query. Nếu bạn hardcode IP private vào app, thay endpoint có thể phá kết nối và TLS hostname validation. Nếu cùng hostname trả IP public trên laptop nhưng private trong VNet, đó có thể là split DNS dự kiến; dùng `nslookup`/resolver từ đúng runtime để xác minh.

Thiết kế CIDR không chồng lấp với on-prem và các VNet/VPC kết nối. Public subnet/private subnet là mô tả đường route và exposure, không phải nhãn bảo mật tự động. NAT Gateway giúp egress có kiểm soát nhưng không thay firewall/identity. Load balancer có health check nhưng health check `GET /` nông có thể đưa traffic tới app không ghi DB được. Cloud firewall rule và Kubernetes NetworkPolicy ở hai lớp khác nhau; khi điều tra phải biết packet đi qua lớp nào.

## Lab thiết kế không tốn tiền

**Đề bài:** vẽ một môi trường staging cho Notes API gồm edge HTTPS, 2 replica app, DB managed, object storage backup và telemetry. Giả định cần riêng tư dữ liệu, một zone có thể hỏng, ngân sách hạn chế. Tạo bảng cho từng thành phần: dịch vụ, vùng mạng, identity, inbound/outbound, secret, dữ liệu lưu, backup, điểm hỏng và ước lượng chi phí cần kiểm tra trong calculator chính thức. Không tạo cloud resource ở bài này.

**Bước 1:** vẽ hai luồng: request người dùng và đường backup/restore. **Bước 2:** tạo quyền tối thiểu: app đọc một secret, truy cập DB và ghi object backup chỉ nếu thật sự là app phụ trách; CI không được đọc dữ liệu DB. **Bước 3:** đặt failure domain: hai app replica trên hai zone có ích nếu DB/edge không cùng điểm hỏng, nhưng cũng làm tăng chi phí. **Bước 4:** lập kế hoạch kiểm chứng: DNS private từ app, HTTP smoke, DB restore sang môi trường cách ly, mất một zone, alert. **Bước 5:** ghi tradeoff: khi ngân sách chưa cho multi-zone DB, RTO/RPO nào chấp nhận và rủi ro nào còn lại.

**Lời giải định hướng:** đừng bắt đầu bằng “dùng AKS/EKS”. Nếu chỉ một API nhỏ, managed app platform + DB managed có thể giảm gánh vận hành. Nếu yêu cầu nhiều microservices, policy và đội có năng lực, K8s có thể hợp lý. Chọn sau khi định lượng tải, độ tin cậy, kỹ năng và chi phí. Tính cả log ingestion, network egress, storage snapshot và tài nguyên idle; chi phí cloud không chỉ là VM giờ chạy.

## Câu hỏi phỏng vấn có lời giải

**Private Endpoint đã tạo nhưng app vẫn tới public IP.** Kiểm tra private DNS zone/link/resolver trong runtime app và cache; endpoint object riêng chưa ép mọi DNS trả IP private. **App có role nhưng vẫn Forbidden.** Xác định principal thực, action/resource scope và deny/propagation; đừng thêm Owner ngay. **Hai VM ở hai zone nhưng DB một zone.** Ứng dụng chưa chịu được mất zone DB; xét DB HA, restore và dependency khác. **Lab xong không dọn.** Tài nguyên có thể tiếp tục tính phí; phải có tag, budget alert, IaC destroy plan và kiểm tra sau dọn.

Nguồn: [Azure Well-Architected identity](https://learn.microsoft.com/en-us/azure/well-architected/security/identity-access), [Azure mission-critical networking](https://learn.microsoft.com/en-us/azure/well-architected/mission-critical/mission-critical-networking-connectivity), [AWS IAM introduction](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html).
