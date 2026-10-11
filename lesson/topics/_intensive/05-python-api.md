## Đọc API như một hệ thống vận hành, không chỉ là mã Python

Một request `POST /notes` đi qua TCP/HTTP, router, validation, logic nghiệp vụ, truy vấn DB, commit transaction rồi trả response. Ở mỗi bước có dạng lỗi khác nhau: request sai trả 4xx, code exception thường 5xx, DB bận có thể timeout, response mất sau commit tạo tình huống client không biết việc ghi đã thành công. Người DevOps cần đọc code đủ để biết endpoint health kiểm tra gì, log có request ID không, DB file nằm đâu, biến môi trường nào bắt buộc và migration chạy lúc nào. Không cần viết toàn bộ ứng dụng như backend engineer, nhưng không thể vận hành một “hộp đen” hoàn toàn.

### HTTP contract và idempotency

GET dùng để đọc; POST thường tạo; PUT thường thay một tài nguyên theo ID; PATCH sửa một phần; DELETE xóa. Method chỉ là convention nếu server viết sai, nên đọc contract/test thực. Status 200/201/204 cho những kiểu thành công khác nhau; 400/422 cho input sai theo thiết kế; 401 khác 403; 404 có thể do route/ID; 500 nghĩa server lỗi, không tự xác định DB hay code. Khi client retry POST vì timeout, server có thể đã commit lần đầu. Với hành động tài chính/đơn hàng, dùng idempotency key hoặc thiết kế unique constraint + transaction; retry mù có thể tạo bản ghi đôi.

API nên log request ID, method, route, status, latency và lỗi đã được phân loại; tránh log secret, token hoặc toàn bộ dữ liệu người dùng. Metrics nên có số request, tỷ lệ lỗi và histogram latency; đừng dùng user ID làm label Prometheus vì cardinality nổ. Trace ID nối request qua proxy, API, queue và DB nếu stack hỗ trợ. Một endpoint `/health` có thể chỉ chứng minh process còn sống; readiness và smoke test phải phù hợp nghiệp vụ.

## SQL và transaction qua một ví dụ

Giả sử tạo note và một bản ghi audit cùng lúc. Nếu chèn note thành công nhưng chèn audit thất bại, bạn muốn cả hai cùng rollback hay chấp nhận audit bất đồng bộ? Transaction `BEGIN -> INSERT note -> INSERT audit -> COMMIT` cho tính nguyên tử trong một DB. Nếu app đóng connection trước commit hoặc exception xảy ra, thay đổi có thể rollback tùy cách quản lý transaction. Với Python `sqlite3` phiên bản hiện hành, tài liệu khuyến nghị điều khiển qua `Connection.autocommit`; code cũ dùng `isolation_level` có hành vi legacy. Khi đọc app mẫu, không suy đoán từ cú pháp SQL; xem connection mode, commit/rollback và test.

Parameterized query tách dữ liệu người dùng khỏi cú pháp SQL: `cur.execute("SELECT ... WHERE id = ?", (note_id,))`. Ghép chuỗi trực tiếp vào SQL mở đường injection và lỗi escaping. Unique constraint/index là lớp bảo vệ dữ liệu; validation ở API một mình không chống race condition giữa hai request. Index tăng tốc truy vấn phù hợp nhưng làm ghi tốn thêm và chiếm đĩa; xem query plan trước khi thêm hàng loạt index.

## Lab: theo một request đến file DB

**Điều kiện:** Python tương thích với app mẫu; dùng thư mục `lesson/labs/notes-api` và venv riêng, không dùng DB production. Đọc README/app.py trước để xác định lệnh chạy và biến môi trường. Chạy test có sẵn của dự án nếu bạn muốn kiểm chứng logic; ở đây bài học tập trung quan sát. Khởi động API trong terminal A với DB tạm và gọi request tạo note ở terminal B theo endpoint trong mã nguồn. **Kết quả dự kiến:** response có ID/trạng thái theo code; DB file xuất hiện ở đường cấu hình; query SELECT thấy bản ghi. Đừng ghi output mẫu như thể đã chạy trên máy bạn: port, ID và nội dung phụ thuộc môi trường.

Gây lỗi an toàn: đổi DB path sang thư mục không tồn tại hoặc không có quyền trong **bản cấu hình lab**, rồi gọi lại. Ghi HTTP status, exception log, file DB có được tạo không. Sau đó phục hồi path và xác nhận chức năng. Lỗi DB path khác lỗi validation request; người trực ca có thể phân biệt nhờ log, timing và phép thử đọc/ghi. Dọn file DB tạm sau khi xác nhận đúng đường dẫn. Nếu app dùng SQLite và nhiều process/replica, tìm hiểu giới hạn concurrency/locking trước khi kết luận mô hình scale được trên Kubernetes.

## Migration và release tương thích

Thêm cột `priority` có thể làm theo hướng expand/contract: thêm cột có default/nullable để app cũ vẫn chạy; deploy app mới bắt đầu ghi/đọc; backfill dữ liệu cũ theo batch có quan sát; khi mọi phiên bản cũ đã rời hệ thống mới bắt buộc cột/xóa đường tương thích ở release sau. Nếu app mới yêu cầu cột trước khi migration chạy, rollout có thể tạo 500 dù Pod Ready. Nếu rollback app sau khi dữ liệu đã viết theo schema mới, cần biết code cũ có đọc được không. Backup trước migration và restore drill quan trọng hơn một file SQL “DOWN” chưa từng chạy thử.

### Câu hỏi có lời giải

**API trả 500 sau deploy, CPU thấp.** Xem request ID/log/trace, DB connection/path/schema/quyền, dependency và release diff; CPU thấp không loại trừ I/O wait hoặc lock. **Cùng request gửi hai lần tạo hai note.** Đây là vấn đề idempotency; cần key/constraint/transaction thay vì chỉ giảm timeout. **Pod health xanh nhưng `POST /notes` lỗi.** Health check có thể chỉ kiểm tra process; thêm smoke test nghiệp vụ và metric theo route. **Một DB SQLite file đặt trong writable layer container.** Khi container/Pod bị thay, dữ liệu có thể mất; phải thiết kế storage/DB riêng và backup, không chỉ tăng replica.

Nguồn: [Python sqlite3 transaction control](https://docs.python.org/3/library/sqlite3.html#transaction-control), [SQLite documentation](https://www.sqlite.org/docs.html), [HTTP semantics RFC 9110](https://www.rfc-editor.org/rfc/rfc9110).
