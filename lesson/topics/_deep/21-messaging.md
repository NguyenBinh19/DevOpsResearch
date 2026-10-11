## Từ request đồng bộ sang công việc bất đồng bộ

API nhận yêu cầu tạo thumbnail, ghi trạng thái `pending`, rồi đưa message vào broker. Worker lấy message, xử lý file, cập nhật `done` hoặc `failed`. Điều này giảm thời gian chờ của request nhưng thêm trạng thái, retry, dead-letter và quan sát backlog. Producer cần quyết định điều gì xảy ra khi broker không nhận message; consumer cần quyết định khi xử lý xong nhưng ack thất bại. Message ID và idempotency key phải đi qua các lớp để đối soát.

Redis cache khác queue: cache giữ bản sao dữ liệu để đọc nhanh, có TTL/invalidation; queue giữ công việc cần xử lý. Redis có cấu trúc để làm queue nhưng yêu cầu durability/retry/ordering cần đánh giá theo cách dùng. Khi cache lỗi, hệ thống có thể fallback DB nhưng phải tránh stampede làm DB quá tải. Nếu Redis giữ session hoặc dữ liệu gốc, mất dữ liệu có tác động lớn hơn cache đơn thuần; persistence/replication/backup cần thiết kế tương ứng.

## RabbitMQ và Kafka: câu hỏi lựa chọn

Với RabbitMQ, xem exchange/queue/binding, ack, prefetch, retry và dead-letter; mỗi job có thể được phân phối tới một worker trong nhóm tùy topology. Với Kafka, event log chia partition, consumer group theo offset, nhiều nhóm độc lập có thể replay. Ordering trong một partition theo key; không hứa global order. Kafka Connect giúp chuyển dữ liệu nhưng connector/offset/schema/quyền vẫn cần vận hành. Chọn theo yêu cầu replay/retention/throughput/ordering, độ phức tạp và năng lực đội. Đừng thêm Kafka cho vài job nhỏ chỉ vì JD có chữ Kafka.

### Diễn tập duplicate delivery

Worker gọi API vận đơn thành công rồi chết trước ack. Broker giao lại message. Nếu worker tạo vận đơn mới, khách có hai vận đơn. Thiết kế key theo `order_id + action`, lưu kết quả đã xử lý và cho downstream nhận key nếu hỗ trợ. Trong test, tạo lỗi đúng ở cửa sổ sau side effect trước ack. Đo duplicate bị chặn, retry, dead-letter và tuổi message; sau sự cố đối soát kết quả nghiệp vụ, không chỉ xóa message khỏi queue.

## Backpressure và alert

Nếu producer gửi 1000 message/phút còn worker xử lý 700, backlog tăng 300/phút. Tăng worker chỉ hữu ích nếu downstream chịu được; nếu DB đã bão hòa, tăng concurrency làm tệ hơn. Alert nên xem tuổi message lâu nhất, backlog theo thời gian, throughput input/output và lỗi xử lý. Một queue depth 1000 có thể bình thường khi worker nhanh; 100 message cũ một giờ có thể nghiêm trọng. Với Kafka, consumer lag cần gắn với tốc độ vào/ra và event age để hiểu tác động.
