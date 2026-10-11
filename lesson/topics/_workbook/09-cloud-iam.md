## Quyền tối thiểu qua ma trận thao tác

Đừng viết “app cần quyền Storage” chung chung. Lập ma trận: `notes-api` cần đọc secret `db-password` và ghi blob vào bucket `notes-attachments`, không cần xóa bucket hay đọc secret của service khác; `ci-staging` cần push image vào repo staging và cập nhật manifest staging, không cần quyền production; người trực ca cần xem log/metric và một quyền break-glass có audit. Từ ma trận này tạo role/policy theo tài nguyên/scope, rồi kiểm tra bằng một thao tác được phép và một thao tác bị từ chối. Nếu chỉ kiểm tra đường happy path, một quyền quá rộng sẽ không bị phát hiện.

Identity có thể là user, service principal, managed/workload identity; credential có thể là password/key/token/chứng thực tạm. Secret manager bảo vệ nơi lưu và cấp phát, nhưng app vẫn có thể lộ secret qua log, exception hoặc quyền debug/exec. Lập kế hoạch rotate: secret cũ/mới cùng tồn tại trong một khoảng nếu cần, cập nhật consumer, xác nhận kết nối mới, thu hồi cũ, kiểm tra audit. Một rotation không có danh sách consumer có thể gây outage.

## Bài toán hybrid CIDR có lời giải

On-prem dùng `10.10.0.0/16`; VNet cloud A đề xuất `10.10.20.0/24`. Dải cloud nằm trong on-prem, route qua VPN không thể phân biệt đích bằng prefix đơn giản; cần chọn CIDR không chồng lấp hoặc thiết kế NAT/renumber với tradeoff rõ. Nếu cloud B dùng `10.20.0.0/16`, không chồng lấp on-prem trong ví dụ; vẫn phải kiểm tra mọi site khác, peering/transit và route. Đừng chỉ “mở NSG 1433” rồi kỳ vọng DB nối được: DNS private, route đi/về, firewall và auth là các điều kiện độc lập.

## Chi phí và an toàn lab

Một tài nguyên luôn chạy 24/7 trong tháng khoảng 730 giờ, nhưng hóa đơn còn storage, network egress, logging, snapshot và license. Trước khi tạo lab cloud, ghi region/SKU, số giờ dự kiến, tài nguyên phụ sẽ tự tạo và cách xóa. Đặt budget alert nhưng hiểu alert không tự ngắt tài nguyên trừ khi có automation riêng. Dùng IaC để tạo/dọn trong subscription/project lab riêng, tag mọi resource, kiểm tra sau destroy vì object ngoài state/manual có thể còn. Nếu muốn học Private Endpoint mà chưa có ngân sách, bài thiết kế DNS/route trên giấy có giá trị hơn tạo một cluster đắt rồi không hiểu chi phí.

### Case phỏng vấn

Một app mới được cấp Owner subscription để “fix Forbidden”; sau đó gọi DB vẫn timeout. Vì sao? Owner là quyền control plane rộng, còn timeout xảy ra trước auth DB và có thể do DNS/route/firewall. Trả quyền về tối thiểu, điều tra từ runtime theo lớp. Một role rộng không giúp TCP tới nơi và tạo rủi ro lớn hơn. Nguồn: [Azure RBAC overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview), [AWS IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html).
