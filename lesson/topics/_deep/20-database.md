## Theo dõi một câu query từ API xuống đĩa

Request tới API lấy connection từ pool, gửi SQL, database parse/plan, đọc index hoặc scan bảng, có thể đợi lock/I/O, rồi trả rows. Vì vậy độ trễ DB có thể do query plan, thiếu index, lock, số connection, đĩa hoặc mạng. Chỉ xem CPU DB không đủ. `EXPLAIN` giúp thấy hướng thực thi; metric query latency và slow query log cho biết tần suất/tác động. Thêm index có thể giúp đọc nhưng làm ghi nặng và tốn dung lượng; phải đo trước-sau.

### Lab SQL có đối chứng

Với Notes API lab, tạo 100-1000 ghi chú thử trong DB riêng. Chạy `SELECT COUNT(*)`, truy vấn `WHERE id=?`, xem schema và index. Tạo một query tìm theo body, đo thời gian lặp lại ở dữ liệu nhỏ và lớn; đừng kết luận hiệu năng production từ SQLite lab, mục tiêu là học cách đo và nêu giả thuyết. Khi chuyển MySQL/PostgreSQL, dùng `EXPLAIN` theo phiên bản, xem rows ước lượng/thực tế, index được chọn và lock/connection. Ghi một thay đổi duy nhất rồi đo lại. Tránh tạo index tùy tiện trên database dùng chung.

## Replication, HA và backup là ba cơ chế khác nhau

Replica nhận thay đổi từ primary/source, có thể trễ. HA cần phát hiện lỗi, chọn leader, ngăn split-brain, chuyển client và xác nhận. Backup giữ điểm phục hồi; nó có thể bảo vệ trước thao tác xóa nhầm mà replica đã nhân bản. RPO là lượng dữ liệu tối đa chấp nhận mất; RTO là thời gian tối đa khôi phục. Nếu replica chậm 30 giây và RPO bằng 0, promote ngay có thể vi phạm cam kết. Nếu backup hàng ngày, RPO không thể 15 phút trừ khi có log/continuous backup và quy trình khôi phục tương ứng.

### Diễn tập restore

Tạo dữ liệu A -> backup -> tạo dữ liệu B -> restore vào instance/file khác -> kiểm tra A có, B không. Đo thời gian từ lúc tuyên bố sự cố tới API có thể đọc/ghi trên DB khôi phục; đó mới gần với RTO, không chỉ thời gian chạy lệnh restore. Ghi quyền, credential, DNS/connection string và schema version. Nếu app mới không tương thích schema trong backup, phải có kế hoạch tương thích. Không restore đè dữ liệu đang hoạt động để thử nghiệm.

## Case: DB CPU thấp, API timeout

API timeout 5 giây; DB CPU 20%; connection pool exhausted. Có thể app giữ connection quá lâu do transaction dài, query chờ lock hoặc pool size nhỏ so với concurrency. Thu số active/idle/waiting connections, transaction tuổi cao, lock wait, query latency và thay đổi gần nhất. Nếu chỉ tăng pool từ 20 lên 200, database có thể nhận thêm tải và chậm hơn. Giảm tác động có thể rollback query mới, giới hạn traffic hoặc sửa transaction; xác nhận bằng error rate và wait time. Đây là ví dụ phỏng vấn cần đi từ triệu chứng đến bằng chứng, không từ một metric tới kết luận.
