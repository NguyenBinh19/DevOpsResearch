# Chuyên đề 10 - Database, cache và hệ thống message

JD 1 và 3 liệt kê rất nhiều hệ dữ liệu. Bài học đúng là hiểu kiểu dữ liệu, cam kết nhất quán, đường ghi/đọc, backup, replication và failure mode; sau đó vận hành sâu một database quan hệ. Một ứng viên mới không cần tự xưng thành thạo Oracle, MongoDB, Kafka, RabbitMQ và Ceph sau vài lab.

```text
Client -> API -> relational DB (source) -> replica
            |           |
            |        backup + restore test
            +-> outbox -> broker/stream -> worker -> DB/object storage
            +-> cache (Redis)
```

Mỗi mũi tên có thể chậm, lỗi hoặc lặp. Khi thiết kế, ghi dữ liệu gốc nằm đâu, cái gì có thể dựng lại, và giới hạn mất dữ liệu/thời gian phục hồi được chấp nhận.

## Bài 1. Một database quan hệ thực sự làm gì?

MySQL/MariaDB và PostgreSQL lưu dữ liệu theo bảng, có schema, index, transaction và giao thức client/server. Một query đi từ ứng dụng qua connection tới engine, engine chọn cách tìm dữ liệu, đọc trang dữ liệu/bộ nhớ/đĩa, có thể lấy lock, rồi trả hàng. Khi request API chậm, database có thể là nút thắt do query thiếu index, quá nhiều kết nối, lock contention hoặc đĩa chậm. Tăng CPU app không giải quyết mọi nguyên nhân.

Primary key xác định một hàng. Index giúp tìm nhanh theo một số điều kiện nhưng tốn dung lượng và chi phí ghi; thêm index cho mọi cột là sai. Transaction nhóm thao tác cần nhất quán. Isolation level ảnh hưởng chuyện transaction này nhìn thấy thay đổi của transaction khác; không cần thuộc mọi anomaly ngay, nhưng phải biết race condition có thể xảy ra nếu hai request cùng cập nhật số dư hoặc số lượng tồn.

### Lab SQL căn bản

Dùng SQLite của Notes API để học câu lệnh không tốn cài đặt. Tạo 10 ghi chú qua API. Mở database bằng công cụ SQLite phù hợp hoặc một script Python đọc-only; chạy `SELECT id, body FROM notes ORDER BY id`, rồi truy vấn theo `id`. Trước khi chạy `DELETE`, sao lưu file lab và xác nhận đúng đường dẫn. Viết một câu hỏi: "Có bao nhiêu ghi chú?" rồi dùng `SELECT COUNT(*) FROM notes`. Sau đó giải thích vì sao một app có thể trả 500 khi schema bảng chưa được tạo hoặc quyền ghi file bị chặn.

Khi chuyển sang MySQL/PostgreSQL, giữ cùng schema và câu hỏi nhưng học thêm user, quyền, connection, port, service, log, backup và restore. SQLite lab giúp hiểu SQL; nó không mô phỏng replication hay vận hành server nhiều người dùng.

## Bài 2. Replication, backup và failover

Replication chuyển thay đổi từ nguồn sang bản sao. Nó có thể giúp đọc, bảo trì hoặc tăng khả dụng, nhưng bản sao có thể trễ và có thể nhận cả lỗi xóa dữ liệu. Backup là khả năng quay về dữ liệu ở thời điểm đã lưu; restore là bằng chứng backup đó dùng được. Nếu RPO là 15 phút, quy trình backup mỗi ngày không đáp ứng dù có replica. Nếu RTO là một giờ, cần đo cả thời gian phục hồi dữ liệu, ứng dụng và kết nối người dùng.

Trong MySQL, replication có source/replica và log thay đổi. Failover cần xác định bản replica nào đã bắt kịp, ngăn split-brain/ghi vào hai nguồn, chuyển client và kiểm tra dữ liệu. Trong PostgreSQL, streaming replication/WAL cũng có vấn đề lag và cách chọn leader. Chi tiết lệnh phụ thuộc phiên bản và cấu hình; học qua tài liệu chính thức của phiên bản đang dùng. Một hệ thống có replica không tự động có HA: còn health detection, promotion, routing và thử nghiệm.

### Tình huống phỏng vấn

Primary hỏng, replica chậm 30 giây. Bạn cần hỏi dữ liệu mới nhất có giá trị thế nào, RPO đã cam kết, replica nào an toàn để promote, client sẽ trỏ về đâu và liệu có ghi từ primary cũ sau khi nó trở lại không. Câu "đổi DNS sang replica" bỏ qua dữ liệu, fencing và ứng dụng có kết nối cache. Hãy viết kế hoạch từng bước trên giấy trước khi làm lab failover.

### Lab restore có thể kiểm chứng

Với database lab, tạo dữ liệu đánh dấu thời điểm A; backup; thêm dữ liệu B; restore vào database **khác**; truy vấn để xác nhận dữ liệu A có, B không. Ghi độ trễ, kích thước file và thời gian restore. Sau đó viết RPO quan sát được giữa A và B. Không restore đè database đang dùng; không coi một lệnh backup exit 0 là đủ.

## Bài 3. Tuning hiệu năng MySQL/MariaDB/PostgreSQL

Tuning bắt đầu bằng đo. Lấy query chậm, tần suất, số hàng, plan thực thi và độ trễ theo thời gian. `EXPLAIN` hoặc công cụ tương đương cho thấy engine định đi qua index/scan thế nào. Một query chậm vì thiếu index khác với query bị lock bởi transaction dài. Connection pool cạn có thể làm app timeout dù DB CPU thấp. Đĩa đầy, I/O latency và memory pressure cũng là nguyên nhân. Thay một yếu tố rồi đo lại; không copy cấu hình "tối ưu" từ blog cho máy khác.

### Bài tập phân tích

Bảng notes có một triệu hàng. Query `SELECT * FROM notes WHERE id = ?` thường nhanh nhờ primary key; query tìm `body LIKE '%abc%'` có thể cần scan lớn hoặc giải pháp search khác. Hãy nêu bằng chứng cần xem trước khi thêm index hay đổi hệ. Nếu app gọi query này 500 lần cho một trang, vấn đề có thể là cách app dùng DB (N+1) hơn là cấu hình database.

## Bài 4. Redis: cache hay nguồn dữ liệu?

Redis thường được dùng làm cache, session store, queue nhẹ hoặc cấu trúc dữ liệu trong bộ nhớ. Khi là cache, dữ liệu gốc nằm nơi khác; mất Redis có thể làm hệ thống chậm nhưng không mất dữ liệu nghiệp vụ nếu thiết kế đúng. Khi dùng Redis như nguồn dữ liệu chính, persistence, replication và backup trở thành yêu cầu khác hẳn. Redis có các chế độ persistence như snapshot RDB và append-only file; lựa chọn liên quan độ bền và chi phí ghi.

Cache tạo hai câu hỏi khó: khi dữ liệu gốc thay đổi, cache được cập nhật/xóa thế nào; nếu cache lỗi hoặc trả dữ liệu cũ, người dùng thấy gì? TTL giúp giới hạn thời gian stale nhưng không giải quyết mọi trường hợp. Đừng thêm Redis trước khi đo vấn đề cần nó giải quyết.

## Bài 5. Queue và event stream

RabbitMQ/ActiveMQ thường dùng broker/queue để tách producer khỏi consumer. Producer gửi message; consumer xử lý; cần hiểu ack, retry, dead-letter queue và idempotency. Nếu consumer xử lý xong nhưng chết trước khi ack, message có thể được giao lại; logic xử lý phải chịu được việc lặp. Kafka là distributed event log: topic chia partitions, consumer group đọc theo offset, và nhiều nhóm có thể đọc cùng dữ liệu theo tiến độ riêng. Thứ tự được bảo đảm trong phạm vi partition theo cấu hình, không tự động trên toàn topic.

Kafka Connect nối nguồn/đích dữ liệu với Kafka qua connector. Nó không biến mọi tích hợp thành "không cần code": connector có cấu hình, schema, offset, quyền và lỗi. RabbitMQ và Kafka không hoán đổi đơn giản chỉ vì đều truyền message. Hỏi nhu cầu: job queue, pub/sub, replay sự kiện, throughput, ordering, retention, vận hành và chi phí.

### Bài tập thiết kế xử lý ảnh

API nhận yêu cầu tạo thumbnail. Nếu làm đồng bộ, request chờ worker và dễ timeout. Với queue, API ghi trạng thái `pending`, gửi message, worker tạo ảnh rồi cập nhật `done`. Nếu worker lỗi, message retry; nếu lỗi vĩnh viễn, đưa vào dead-letter queue hoặc trạng thái lỗi để người vận hành thấy. Hãy xác định nơi lưu file gốc, message ID, cách tránh tạo thumbnail trùng và metric về số message chờ. Đây là bài tập áp dụng chung trước khi chọn RabbitMQ, Kafka hay Service Bus.

## Bài 6. Oracle, MongoDB và lựa chọn hệ phù hợp

Oracle là database quan hệ doanh nghiệp với hệ sinh thái quản trị và licensing riêng; kiến thức SQL, transaction, backup/restore chuyển một phần từ MySQL/PostgreSQL nhưng lệnh/công cụ không giống. MongoDB là document database; schema linh hoạt không có nghĩa là không cần thiết kế dữ liệu, index và backup. Khi JD liệt kê hai hệ này, nhà tuyển dụng có thể cần người hiểu tích hợp/vận hành ở mức khác nhau; hãy hỏi phạm vi thực tế trong phỏng vấn.

Một nguyên tắc lựa chọn: bắt đầu bằng yêu cầu truy vấn, tính nhất quán, thay đổi schema, lưu lượng, độ bền, vận hành và kỹ năng nhóm. Nếu dữ liệu giao dịch quan hệ và truy vấn SQL đủ tốt, không chuyển sang NoSQL chỉ vì tên hiện đại. Nếu cần stream sự kiện có thể replay và nhiều consumer group, một event log có thể phù hợp; nếu chỉ cần một hàng đợi công việc đơn giản, broker queue có thể dễ hơn.

## Bài 7. Tính nhất quán khi DB và message cùng tham gia

Request tạo đơn hàng có thể cần ghi DB rồi gửi message. Nếu ghi DB thành công nhưng gửi thất bại, worker không biết đơn hàng mới. Nếu gửi trước rồi DB rollback, worker xử lý order không tồn tại. Transactional outbox ghi bản ghi nghiệp vụ và một hàng outbox trong **cùng transaction DB**; publisher riêng gửi message. Publisher có thể gửi lặp nếu chết sau khi gửi nhưng trước khi đánh dấu, nên consumer cần idempotency và metric số outbox tồn đọng.

Vẽ bảng `orders(id,status)` và `outbox(id,event_type,payload,published_at)`. Mô tả transaction tạo order, publisher retry, consumer nhận cùng event hai lần và cơ chế tránh xử lý trùng. Theo dõi số hàng chưa publish, tuổi hàng lâu nhất, dead-letter và latency tới khi hoàn tất. Đừng hứa "exactly once" trên toàn chuỗi nếu chưa chỉ ra ranh giới và cơ chế chống lặp.

## Bài 8. Backup và recovery nhiều lớp

Backup có thể là snapshot vật lý, logical dump hoặc continuous backup kèm log. Cần biết thời điểm nhất quán, retention, mã hóa/quyền, failure domain và khả năng restore sang phiên bản engine nào. Backup cùng đĩa với DB không chống mất đĩa; replica có thể nhân bản thao tác xóa sai. Nếu DB khôi phục về thời điểm cũ nhưng consumer offset ở thời điểm mới, dữ liệu có thể lệch; runbook phải chỉ cách đồng bộ hoặc replay có kiểm soát.

Diễn tập với Notes API: đặt RPO 15 phút, RTO 2 giờ; backup A, thêm ghi chú B, mô phỏng DB hỏng. Restore **vào file/instance mới**, xác nhận dữ liệu, đổi app lab sang DB mới, chạy smoke test. Ghi giờ bắt đầu-kết thúc, dữ liệu mất và điểm làm vượt RTO. Sau đó đề xuất cải tiến cụ thể về tần suất, tự động hóa hoặc vị trí bản sao.

## Bài 9. Chọn queue hay Kafka theo yêu cầu

Nếu cần phân phối công việc cho worker với ack/retry/dead-letter, queue như RabbitMQ/Service Bus thường tự nhiên. Nếu nhiều nhóm độc lập cần đọc cùng dòng sự kiện và phát lại lịch sử theo offset, Kafka có mô hình phù hợp. Các hệ có vùng chồng lắp; quyết định dựa vào ordering, retention, throughput, latency, kỹ năng đội và chi phí vận hành.

Với Kafka, partitions ảnh hưởng song song và thứ tự. Nếu cần thứ tự của **một order**, dùng key nhất quán để cùng order vào cùng partition; không hứa thứ tự giữa mọi order. Consumer lag tăng có thể do input tăng, consumer lỗi hoặc downstream chậm. Khi alert lag, xem cả tốc độ input, tốc độ xử lý và tuổi event; một con số lag đơn lẻ không luôn nói tác động người dùng.

## Case study có lời giải: đơn hàng trùng sau retry

**Bối cảnh:** worker tạo vận đơn từ message; hệ thống thấy hai vận đơn cho cùng order sau một lần consumer restart. Có thể worker đã gọi dịch vụ vận đơn thành công rồi chết trước khi ack, broker giao lại. Chỉ tăng timeout hoặc tắt retry sẽ che vấn đề và có thể làm mất việc. Kiểm tra message ID/order ID, thời điểm xử lý, ack log và trạng thái downstream. Thiết kế idempotency key cố định theo order + thao tác, lưu kết quả xử lý hoặc yêu cầu downstream hỗ trợ key; khi nhận lại, trả cùng kết quả thay vì tạo vận đơn mới. Cần kiểm chứng tình huống chết **ngay sau side effect nhưng trước ack**, vì đó là cửa sổ lỗi quan trọng.

**Theo dõi:** số retry, dead-letter, tuổi message, tỷ lệ duplicate bị chặn và đơn hàng chưa hoàn tất. Nếu muốn xóa vận đơn trùng, đó là quy trình nghiệp vụ/đối soát, không chỉ sửa queue. Bài này cho thấy tại sao hiểu transaction và application behavior quan trọng ngang việc cài broker.

## Cổng năng lực và nguồn

Bạn viết được query và đọc plan cơ bản, thực hành backup/restore, giải thích replication lag/failover, phân biệt cache với nguồn dữ liệu, queue với event log, và thiết kế xử lý retry/idempotency. Chỉ nhận "có kinh nghiệm vận hành" với hệ bạn đã thực sự triển khai và xử lý lỗi.

- MySQL backup/recovery: https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html
- PostgreSQL documentation: https://www.postgresql.org/docs/current/
- Redis persistence: https://redis.io/docs/latest/management/persistence/
- RabbitMQ tutorials: https://www.rabbitmq.com/tutorials
- Kafka documentation: https://kafka.apache.org/documentation/
- MongoDB documentation: https://www.mongodb.com/docs/
