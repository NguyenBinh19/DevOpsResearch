## Tách bốn câu hỏi: đúng dữ liệu, nhanh, sẵn sàng và khôi phục được

DB quan hệ giữ dữ liệu theo bảng, ràng buộc và transaction. **Đúng dữ liệu** cần khóa, isolation, constraint và logic app; **nhanh** cần query/index/capacity; **sẵn sàng** cần failover/replication; **khôi phục** cần backup và restore. Một replica khỏe không bảo đảm backup: thao tác `DELETE` nhầm có thể được nhân bản. Một backup tốt không bảo đảm HA: restore có thể mất hàng giờ. Một query nhanh ở staging nhỏ không bảo đảm nhanh ở production dữ liệu lớn. Đừng dùng từ “DB ổn” mà không nói tiêu chí nào.

### Query plan và index qua một ví dụ

`SELECT * FROM notes WHERE owner_id = ? ORDER BY created_at DESC LIMIT 20` trên bảng 10 triệu dòng có thể cần index phù hợp `(owner_id, created_at)` tùy engine, selectivity và cách sắp xếp. Index chỉ trên `created_at` có thể vẫn phải lọc nhiều owner; index nhiều cột thay đổi chi phí ghi/storage. Đọc `EXPLAIN`/actual execution stats theo engine để xem scan, rows, sort, join và latency; không thêm index chỉ vì cột xuất hiện trong WHERE. `SELECT *` lấy nhiều dữ liệu hơn cần; pagination offset lớn có thể đắt; connection pool quá lớn có thể làm DB quá tải dù CPU API thấp.

Transaction dài giữ lock và tăng contention. Khi API timeout, hỏi nó chờ connection pool, lock, disk I/O, network hay query CPU. MySQL/MariaDB/PostgreSQL có lệnh/metric khác; Oracle càng khác về kiến trúc/license/vận hành. Học mô hình chung trước, rồi đọc tài liệu đúng engine/version. Redis không thay DB quan hệ chỉ vì đọc nhanh; cache invalidation và consistency là bài toán riêng.

## Replication và failover cần chứng minh bằng timeline

Giả sử primary nhận một giao dịch lúc 10:00:00, client thấy success lúc 10:00:01, replica lag 5 giây; primary mất lúc 10:00:02. Nếu failover sang replica chưa nhận giao dịch, có thể mất dữ liệu dù API đã trả success, tùy chế độ replication/ack. RPO thực phải đo theo cơ chế và tải. Read replica có thể trả dữ liệu cũ; nếu client vừa ghi rồi đọc từ replica, trải nghiệm không nhất quán. Failover còn cần chọn leader, đổi connection/DNS, tránh split-brain và kiểm tra app reconnect. Không gọi “có replication” là “HA xong”.

MySQL point-in-time recovery thường cần full backup và binary log liên quan để replay tới thời điểm; chỉ giữ full backup hàng tuần khó đạt RPO phút. PostgreSQL dùng base backup và WAL archiving cho mục tiêu tương tự theo cấu hình. Lưu backup/log ở failure domain khác, mã hóa, quyền tối thiểu và retention phù hợp. Đọc [MySQL 8.4 backup/recovery](https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html) và [PITR](https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery.html) theo version thực.

## Lab restore có kiểm chứng trên dữ liệu giả

**Điều kiện:** database lab riêng hoặc SQLite app mẫu, không dùng DB production. Tạo bản ghi A lúc T1, tạo backup nhất quán, tạo bản ghi B lúc T2. Restore vào **instance/đường khác**; kiểm tra schema, row count, checksum hoặc truy vấn nghiệp vụ: A có, B không có nếu backup ở giữa. Ghi thời gian từ bắt đầu restore đến smoke test API đọc/ghi thành công. Nếu dùng MySQL/PostgreSQL lab, thử thêm log/WAL để phục hồi tới gần T2 và xác định RPO thực. Dọn bản restore sau khi đã ghi kết quả; không ghi đè source DB để “thử nhanh”.

**Lỗi có chủ đích:** app mới yêu cầu cột `priority`, migration chưa chạy. Pod Ready vì `/health` chỉ kiểm tra process; `POST /notes` trả 500. Bằng chứng: app log báo thiếu cột, schema version cũ, release diff. Giảm tác động: rollback app nếu schema vẫn tương thích, hoặc chạy migration đã review/roll-forward theo runbook. Sau đó thêm integration test chạy migration và smoke test ghi dữ liệu. Chỉ tăng DB CPU không chữa schema thiếu.

## Tuning theo giả thuyết

Đừng bắt đầu bằng “tăng max_connections”. Nếu pool app mở 500 connection tới DB có giới hạn bộ nhớ, tăng thêm có thể làm máy nghẹt hơn. Xem active/idle, queue wait, transaction duration, slow query, locks, buffer cache hit, disk latency và network. Một query chậm có thể do plan đổi khi dữ liệu tăng; có thể do storage shared bị backup job chiếm IOPS; có thể do lock từ migration. Thử một thay đổi có đo trước/sau. Khi thay index, tính write amplification và thời gian tạo index, nhất là bảng lớn.

**Câu hỏi:** replica có thay backup không? Không. **CPU DB thấp nhưng API timeout?** Chờ lock/I/O/network/pool vẫn có thể làm timeout. **RPO 0 với async replication?** Không bảo đảm trong lỗi primary nếu giao dịch chưa tới replica. **Backup thành công nghĩa restore được?** Chưa; cần restore drill và kiểm tra dữ liệu/app. Nguồn: [PostgreSQL backup/restore](https://www.postgresql.org/docs/current/backup.html), [MySQL replication](https://dev.mysql.com/doc/refman/8.4/en/replication.html).
