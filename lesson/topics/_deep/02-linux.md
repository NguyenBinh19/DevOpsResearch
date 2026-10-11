## Đọc một máy Linux theo lớp

Khi ứng dụng lỗi, bắt đầu từ dấu hiệu: người dùng không kết nối, kết nối được nhưng 5xx, hay request chậm. Kiểm tra process/service đang chạy (`ps`, `systemctl status` trên hệ dùng systemd), cổng lắng nghe (`ss -ltnp`), disk (`df -h`, `df -i`), memory (`free -h`), CPU/load (`uptime`, `top`) và log (`journalctl -u <service>`). Mỗi lệnh trả lời một câu hỏi khác. `df -h` còn dung lượng nhưng `df -i` hết inode vẫn có thể không tạo file mới. `systemctl active` chỉ cho biết service manager, không chứng minh API nghiệp vụ tốt.

Quyền file gồm owner, group và permission; process chạy dưới một user cụ thể. Nếu Notes API chạy user 10001 nhưng `/data` chỉ root được ghi, GET health có thể thành công còn POST ghi DB thất bại. Hỏi "process là user nào?", "đường ghi là gì?", "mount read-only không?" trước khi `chmod 777`. Quyền rộng có thể che lỗi cấu hình và tạo rủi ro dữ liệu. Với production, thay đổi owner/permission cần hiểu service khác có dùng cùng thư mục không.

## Lab: ba lỗi ứng dụng cùng một triệu chứng

Chạy Notes API local trên máy lab. Trường hợp A: port 8000 đã có process khác; app không bind được. Dùng `ss -ltnp` hoặc công cụ OS tương đương để tìm process, không giết bừa nếu không phải lab. Trường hợp B: cấu hình `NOTES_DB` trỏ tới đường không writable; quan sát GET health và POST note, log Python. Trường hợp C: filesystem lab gần đầy (mô phỏng trong volume riêng, không làm đầy ổ hệ thống); quan sát lỗi ghi và inode/capacity. Với mỗi trường hợp ghi giả thuyết, bằng chứng, sửa và phép xác nhận. Sau lab trả lại port, đường DB và dung lượng như ban đầu.

## Bash/PowerShell và tự động hóa an toàn

Một script vận hành cần nhận input rõ, kiểm tra lỗi, ghi log có ngữ cảnh và có thể chạy lại. Với Bash, phân biệt exit code của command và output của command; một lệnh thành công không đồng nghĩa cả chuỗi thao tác thành công nếu script nuốt lỗi. Tránh đặt secret trực tiếp trong command line vì có thể xuất hiện trong history/process list. Với PowerShell, đọc cmdlet `-WhatIf` khi hỗ trợ, kiểm tra `$ErrorActionPreference`/exception và dùng đường dẫn tuyệt đối cho thao tác file nhạy cảm. Chỉ chạy trên danh sách host/tài nguyên đã xác định.

Ví dụ script backup Notes API: kiểm tra file nguồn tồn tại, tạo tên backup chứa timestamp, copy tới thư mục lab, tính hash, restore thử vào file **khác**, rồi đọc dữ liệu. Nếu chỉ copy và in "success" nhưng không restore, chưa chứng minh khả năng phục hồi. Khi viết automation, luôn hỏi điều gì xảy ra nếu chạy lần hai, giữa chừng chết hoặc đầu vào thiếu.
