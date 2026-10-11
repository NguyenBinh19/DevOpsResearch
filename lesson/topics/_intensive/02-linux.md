## Mô hình sâu: một request trên Linux đi qua những gì?

Một máy Linux không phải tập hợp lệnh để học thuộc. Khi client gọi HTTP tới Notes API, kernel nhận gói mạng, tìm socket đang lắng nghe, đánh thức tiến trình, tiến trình đọc cấu hình và file/DB, rồi ghi response. Nếu service không chạy, điều tra tiến trình và unit. Nếu process chạy nhưng không nghe cổng, xem bind address và socket. Nếu nghe cổng nhưng chỉ từ localhost, xem firewall/network. Nếu response 500, xem log ứng dụng và dependency. Sơ đồ này giúp bạn không dùng `chmod 777` hoặc restart máy mỗi khi gặp lỗi.

Tiến trình có PID, UID/GID, working directory, biến môi trường, file descriptor và giới hạn tài nguyên. `ps`, `/proc/<pid>`, `ss`, `lsof`, `journalctl` quan sát những mặt khác nhau của cùng tiến trình. Một process có thể vẫn `active` trong systemd nhưng không trả request đúng; systemd chỉ biết trạng thái tiến trình và điều kiện unit, không biết nghiệp vụ. Ngược lại, nếu service khởi động rồi thoát với exit code 1, trước tiên đọc `systemctl status` và journal theo thời điểm, sau đó mới thử chạy tay với cùng user/env để tái hiện.

### Quyền file qua một ví dụ

Giả sử API chạy dưới user `notes`, cần đọc `/etc/notes/config.env` và ghi `/var/lib/notes/notes.db`. Đường tới file phải cho user đó quyền traverse (`x`) trên từng thư mục; file config cần quyền đọc; thư mục dữ liệu cần quyền ghi để tạo/đổi file và đôi khi file journal của SQLite. Quyền `644` trên DB nhưng thư mục không cho traverse vẫn lỗi. Root chạy được không chứng minh service user chạy được. Dùng `namei -l /var/lib/notes/notes.db`, `stat`, `id notes` và `sudo -u notes ...` trên VM lab để xác định lớp quyền. Tránh `chmod -R 777`: nó xóa ranh giới bảo vệ mà không tìm nguyên nhân.

### Bộ nhớ, CPU và đĩa cần đọc đúng

CPU cao có thể là ứng dụng xử lý, vòng lặp lỗi, nén log hoặc DB query. CPU thấp mà latency cao gợi I/O wait, khóa DB, chờ mạng hoặc queue. `free -h` hiển thị cache/buffer; không coi mọi memory “used” là hết RAM. Disk có hai giới hạn khác nhau: byte (`df -h`) và inode (`df -i`). Một triệu file log nhỏ có thể hết inode dù còn GB trống. Khi DB không ghi được, kiểm tra filesystem mount read-only, dung lượng, inode và quyền trước khi kết luận SQL sai. `du` đo thư mục ở userland; file đã xóa nhưng process còn mở có thể vẫn chiếm chỗ đến khi file descriptor đóng.

## Lab VM/WSL riêng: biến triệu chứng thành bằng chứng

**Điều kiện:** dùng Linux VM hoặc WSL riêng, không dùng máy production; có Python 3 và quyền đọc log của chính bạn. Không cần root cho phần đầu. Mở hai terminal. Ở terminal A tạo một thư mục tạm và chạy web server chỉ trên loopback:

```text
mkdir -p ~/devops-linux-lab
cd ~/devops-linux-lab
python3 -m http.server 8765 --bind 127.0.0.1
```

Ở terminal B chạy `curl -i http://127.0.0.1:8765/`, `ss -ltnp` và `ps -ef | grep http.server`. **Kết quả dự kiến:** HTTP 200; socket `127.0.0.1:8765` LISTEN; process Python hiện trong danh sách. Không ghi PID cố định vào bài vì PID thay đổi. Hỏi: máy khác có gọi được cổng này không? Bind `127.0.0.1` chỉ nhận từ loopback của chính môi trường mạng đó; WSL có thêm lớp ánh xạ nên thử nghiệm từ Windows có thể khác Linux VM thuần.

**Lỗi 1 – cổng bận:** trong terminal C thử chạy server thứ hai cùng địa chỉ/cổng. Dự kiến lỗi bind “address already in use”. Đọc `ss` để biết ai sở hữu cổng; không kill một PID chỉ vì số cổng trùng trên máy dùng chung. Trong lab, Ctrl+C terminal A rồi chạy lại C. Giải thích: chỉ một listener phù hợp có thể bind tuple địa chỉ/cổng theo điều kiện thông thường.

**Lỗi 2 – process dừng:** Ctrl+C server, gọi lại curl. Dự kiến kết nối bị từ chối nhanh nếu không có listener; timeout sẽ gợi đường mạng/firewall hoặc packet bị bỏ. Phân biệt lỗi TCP này với HTTP 404: 404 nghĩa là đã tới một HTTP server nhưng tài nguyên không có.

**Lỗi 3 – quyền đọc:** tạo file `secret.txt` trong thư mục lab, đặt quyền `600`, rồi thử đọc bằng một user lab khác nếu có VM phù hợp. Nếu không có user thứ hai, chỉ đọc `stat` và dự đoán; đừng thay quyền hệ thống. Giải thích owner/group/other, quyền `x` trên thư mục, và vì sao chạy service bằng root để tránh lỗi là giải pháp kém.

**Dọn:** Ctrl+C tiến trình thử nghiệm; xóa đúng thư mục `~/devops-linux-lab` sau khi xác nhận nó là thư mục bạn vừa tạo. Không dùng wildcard xóa bên ngoài lab.

## Systemd: đọc unit như hợp đồng khởi động

Một unit service thường chứa `ExecStart`, `User`, `WorkingDirectory`, `Environment` hoặc `EnvironmentFile`, `Restart`, dependencies và phần install. Nếu chạy tay tốt nhưng systemd lỗi, so **cùng binary**, **cùng working directory**, **cùng user**, **cùng env**, quyền file và thời điểm dependency. `After=network.target` chỉ định thứ tự; nó không luôn chứng minh network/DB đã sẵn sàng. `Restart=always` có thể tạo vòng lặp restart che lỗi cấu hình; xem restart count và log lần chạy trước.

Trên VM lab có systemd, đọc một service hệ thống vô hại bằng `systemctl cat <ten-service>` và `systemctl show <ten-service> -p User -p ExecStart -p Restart`. Không chỉnh unit hệ thống trong bài học. Tự phác một unit cho Notes API rồi trả lời: nếu file env thiếu thì log nào sẽ xuất hiện, service có quyền đọc DB không, và khi API trả 500 nhưng process sống thì systemd có phát hiện không?

## Checklist điều tra có lời giải

**Triệu chứng: HTTP timeout.** Xem DNS/IP, TCP connect, listener `ss`, firewall, process; timeout chưa đủ để kết luận app lỗi. **Triệu chứng: Connection refused.** Trên IP đó không có listener phù hợp hoặc kết nối bị từ chối; kiểm tra bind address/cổng. **Triệu chứng: HTTP 500.** TCP/HTTP đã tới server; xem app log, dependency, quyền và tài nguyên. **Triệu chứng: process OOMKilled.** Xem kernel/cgroup signal, memory usage/limit và thay đổi tải; restart chỉ phục hồi tạm thời. **Triệu chứng: No space left on device.** Kiểm tra byte, inode, mount và file descriptor; không xóa log chưa rõ chủ sở hữu.

Bạn đạt bài này khi tự chỉ ra bằng chứng cho process, socket, quyền và filesystem; giải thích được vì sao cùng lệnh chạy tay và chạy qua service có thể khác nhau. Tài liệu gốc: [systemd service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html), [Linux proc filesystem](https://www.kernel.org/doc/html/latest/filesystems/proc.html).
