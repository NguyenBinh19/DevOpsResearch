## Một transaction lỗi có thể không làm CPU cao

API gọi `UPDATE notes SET ... WHERE id=?` rồi treo. DB CPU chỉ 20%, nhưng một transaction khác giữ lock trên row/table lâu; request chờ lock, pool app đầy, proxy trả 504. Bằng chứng cần: active sessions, wait event/lock graph, transaction age, query đang chạy và request trace. Nếu chỉ tăng CPU/RAM, lock không biến mất. Cần xác định transaction giữ lock và vì sao: migration, batch job, code quên commit, isolation level hoặc thiếu index khiến lock phạm vi rộng hơn. Giảm tác động có thể hủy một query/transaction theo runbook sau khi xét rollback dữ liệu, rồi sửa app/migration.

## Backup/restore theo mốc thời gian

Full backup lúc 00:00, binary log/WAL lưu liên tục, lỗi xóa bảng lúc 14:35. Muốn phục hồi trước 14:35, restore full vào instance cách ly, replay log đến thời điểm/position phù hợp, kiểm tra dữ liệu và tính nhất quán, sau đó quyết định chuyển traffic hoặc trích dữ liệu cần phục hồi. Đừng replay tới sau lệnh DELETE rồi ngạc nhiên dữ liệu vẫn mất. Đồng hồ/timezone và log retention cần rõ. Với MySQL/PostgreSQL, công cụ/cú pháp khác nhau; bài này dạy quy trình và câu hỏi kiểm chứng, không thay runbook version cụ thể.

### Lag replication và đọc sau ghi

App ghi primary rồi đọc replica ngay; nếu replica lag 3 giây, request đọc có thể không thấy note mới. Một lựa chọn là đọc primary cho giao dịch vừa ghi, hoặc chờ token/position đồng bộ theo cơ chế engine, hoặc chấp nhận eventual consistency và thông báo UX. Không giải bằng `sleep(1)` cố định. Alert replication lag phải đo theo giây/byte và ảnh hưởng nghiệp vụ; lag 10 giây có thể chấp nhận báo cáo nhưng không chấp nhận xác nhận giao dịch tài chính.

## Tự kiểm tra phỏng vấn

**Vì sao unique constraint tốt hơn check trùng ở app?** Hai request đồng thời có thể cùng thấy chưa tồn tại; constraint ở DB quyết định cuối cùng trong transaction. **Vì sao backup file DB bằng `cp` khi server đang ghi nguy hiểm?** Có thể copy các trang ở thời điểm khác nhau; dùng backup API/snapshot nhất quán theo engine. **Index nhiều có luôn tốt?** Không; mỗi ghi phải cập nhật index, tăng storage và có thể thay query plan. **Failover có thể gây split-brain?** Nếu hai node cùng nhận write sau partition mà không có cơ chế leader/fencing phù hợp, dữ liệu phân kỳ.

Bạn đạt phần này khi phân biệt được latency do CPU, I/O, lock, connection pool và replication, đồng thời mô tả được một restore có mốc thời gian và phép kiểm ứng dụng. Nguồn: [PostgreSQL monitoring](https://www.postgresql.org/docs/current/monitoring.html), [MySQL backup/recovery](https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html).

**Bài tập giải thích WAL/binlog:** một full backup lúc 00:00 cho bạn một điểm bắt đầu, còn log thay đổi cho phép tiến gần thời điểm cần khôi phục nếu log được giữ và tương thích. Nếu log 10:00–11:00 bị mất, bạn không thể giả định replay liên tục qua khoảng ấy. Viết lịch backup/log retention khớp RPO, đặt bản sao ở failure domain khác và diễn tập restore tới mốc ngẫu nhiên. Đây là cách biến “có backup” thành khả năng phục hồi đo được.
