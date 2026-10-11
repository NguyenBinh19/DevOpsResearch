## Chuyên đề thực chiến: đọc log và tài nguyên theo thời gian

Một log line chỉ có ý nghĩa khi đặt trong timeline. Ví dụ 09:58 deploy bản B; 10:01 API 500 tăng; 10:02 systemd restart service ba lần; 10:03 disk `/var` còn 0 byte. Có thể B ghi log quá nhiều làm đầy `/var`, nhưng cũng có thể một job khác gây đầy trước rồi B chỉ là trùng thời điểm. Thu thập `journalctl` theo khoảng thời gian, `df -h`, `df -i`, kích thước thư mục log và thời điểm file tăng; so với mốc deploy. Đừng xóa log đang dùng trước khi ghi bằng chứng hoặc biết chính sách retention. Nếu filesystem báo read-only, xem `mount` và kernel log; `chmod` không chữa mount read-only.

### Tiến trình chạy nhưng không phục vụ

Giả sử `systemctl status notes-api` báo `active (running)` nhưng `curl localhost:8000` bị từ chối. Kiểm tra unit `ExecStart`, process PID, `ss -ltnp` cho cổng 8000; có thể process đang nghe 8001 do biến môi trường đổi, hoặc bind Unix socket. Nếu `ss` có listener 127.0.0.1:8000 và localhost gọi được nhưng proxy từ container khác không tới, bind address/network namespace là nghi vấn. Nếu `ss` có 0.0.0.0:8000 mà curl trả 500, chuyển sang app log/DB, không tiếp tục sửa firewall. Đây là một decision tree: mỗi phép thử loại bỏ một lớp.

### File descriptor và limit

Mỗi TCP socket/file mở chiếm file descriptor. Service có thể trả “too many open files” khi rò socket/log hoặc limit thấp. `ulimit -n` trong shell của bạn không nhất thiết là limit của service chạy qua systemd; xem unit/`/proc/<pid>/limits`. Đếm FD hiện tại của process trong lab và quan sát xu hướng, rồi tìm nguyên nhân rò trước khi tăng limit. Tăng limit có thể giúp tạm thời nhưng làm lỗi tăng chậm hơn và khó thấy. Một service với connection pool không đóng còn có thể làm DB cạn connection đồng thời.

## Bài tập so sánh bốn lỗi giống nhau ở trình duyệt

**A: DNS sai.** Trình duyệt báo không tìm thấy host. Xác nhận `nslookup` và resolver path; `systemctl restart notes-api` không liên quan. **B: process chết.** IP đúng, TCP bị từ chối ở cổng; đọc service status và journal. **C: app bind loopback.** Trên host curl localhost được, từ proxy ở host khác không được; đọc `ss` và network path. **D: DB file không ghi được.** HTTP tới app, app trả 500 khi POST; đọc exception, owner/mode và filesystem. Hãy viết một phép thử chứng minh và một phép thử bác bỏ cho mỗi giả thuyết. Nếu chỉ viết “check logs”, bài chưa đạt vì chưa nói log nào và kỳ vọng gì.

## Shell script vận hành an toàn

Một script tự động dọn log cần xác định thư mục, owner, điều kiện xóa, dry-run và báo kết quả. Đường dẫn rỗng hoặc biến sai có thể làm tác động rộng; quote biến, kiểm tra thư mục tồn tại/thuộc phạm vi cho phép, tránh wildcard không kiểm soát. Trong Bash, kiểm tra exit status của lệnh và dừng/ghi lỗi đúng chỗ; trong PowerShell dùng `-LiteralPath` khi đường dẫn có ký tự đặc biệt. Không đặt mật khẩu trong đối số command line vì có thể lộ qua process listing/log. Script backup phải xác nhận file output tồn tại, checksum hợp lệ và restore thử được; “exit 0” không tự chứng minh dữ liệu dùng được.

**Bài tập thiết kế:** viết pseudocode cho script kiểm tra `/var/lib/notes` còn trên 20% dung lượng trống trước deploy, ghi tình trạng, từ chối deploy khi dưới ngưỡng, không tự xóa dữ liệu. Sau deploy gọi health endpoint và rollback nếu fail theo runbook. Nêu rủi ro TOCTOU: dung lượng có thể đổi giữa kiểm tra và deploy, nên vẫn cần metric/alert và xử lý lỗi ghi. Đây là sự khác nhau giữa automation có kiểm chứng và chỉ nối vài lệnh với `&&`.

## Phỏng vấn sâu có đáp án

**Vì sao `free -h` cho “used” cao chưa đủ kết luận hết RAM?** Linux dùng RAM cho cache/buffer có thể thu hồi; xem available, swap/reclaim, PSI và tiến trình/cgroup. **Vì sao `df -h` còn chỗ mà app báo ENOSPC?** Có thể hết inode, quota, mount khác, hoặc filesystem riêng của container. **Vì sao root chạy được nhưng service user lỗi?** UID/GID, thư mục traverse, env, working directory và SELinux/AppArmor/policy có thể khác. **Vì sao restart chữa lỗi tạm thời nhưng không phải root cause?** Nó giải phóng state/connection/FD hoặc reset process, nhưng lỗi rò/giới hạn sẽ quay lại. Câu trả lời tốt nêu phép đo để kiểm tra mỗi khả năng.
