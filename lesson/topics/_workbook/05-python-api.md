## Đọc lỗi ứng dụng như một người vận hành

Giả sử `POST /notes` trả 500 trong 2% request. Đầu tiên tìm route, thời gian, revision và request ID; xem lỗi có tập trung ở một Pod/user/input hay mọi request. Nếu log nói `sqlite3.OperationalError: database is locked`, không kết luận ngay “SQLite hỏng”: kiểm tra transaction dài, số process/replica, timeout, path/mount và recent load. Nếu lỗi `no such table`, xem migration/schema version và DB path: app có thể vô tình tạo file DB mới trống do đường dẫn sai. Nếu lỗi `permission denied`, kiểm tra UID/GID/dir traverse và mount read-only. Cùng HTTP 500 nhưng ba nguyên nhân/đường khôi phục khác nhau.

### Contract test và test tầng nào?

Unit test logic validation không cần DB; integration test tạo DB tạm, chạy migration và endpoint, kiểm tra transaction; end-to-end test gọi đường ingress/Service như client; smoke test production chọn vài chức năng cốt lõi ít tác động. Không dùng một loại test để thay tất cả. Nếu smoke chỉ gọi `/health`, một migration lỗi có thể lọt; nếu smoke tạo note, cần tài khoản/dữ liệu lab riêng và cleanup để không làm bẩn production. Test cần đo reliability của hệ thống test: flaky test bị bỏ qua sẽ mất giá trị gate.

## Bài tập tính connection pool

API có 4 replica, mỗi replica pool tối đa 20 connection: tối đa 80 connection từ API, chưa tính admin/job/monitor. DB max connection 100, còn khoảng 20 cho nguồn khác trong trường hợp lý tưởng. Nếu HPA scale lên 8 replica, pool tối đa 160 có thể vượt DB trước khi CPU API cao. Thiết kế pool theo capacity DB và request concurrency, xem connection acquisition wait, idle time và timeout; thêm Pod không luôn tăng throughput. Khi phỏng vấn, nói rõ con số là giới hạn cấu hình, không phải luôn mở đủ.

**Câu hỏi:** `POST` timeout nhưng DB đã ghi, client retry tạo trùng; sửa ở đâu? Hợp đồng API/idempotency key, constraint và transaction, cộng timeout/retry budget; proxy chỉ là một lớp. **Câu hỏi:** health xanh nhưng DB schema sai? Health endpoint quá nông; thêm readiness/smoke theo chức năng và test migration. Nguồn: [Python sqlite3](https://docs.python.org/3/library/sqlite3.html), [SQLite transaction docs](https://www.sqlite.org/lang_transaction.html).
