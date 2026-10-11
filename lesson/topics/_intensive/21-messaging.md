## Vì sao cần queue thay vì gọi đồng bộ?

Một request tạo đơn hàng có thể cần gửi email, cập nhật search index và gọi đối tác. Nếu làm tuần tự trong HTTP request, latency và khả năng lỗi phụ thuộc mọi downstream. Queue tách thời điểm producer tạo công việc khỏi consumer xử lý. Producer ghi message và trả response theo contract; consumer nhận, xử lý, xác nhận hoặc retry. Điều này không làm mất lỗi: nó chuyển lỗi sang backlog/dead-letter và đòi observability, idempotency, retention và ownership rõ ràng.

RabbitMQ phù hợp nhiều kiểu routing/queue công việc; Kafka là log phân vùng cho stream/event có retention và consumer group. Chọn theo nhu cầu ordering, replay, throughput, số consumer và vận hành; không nói Kafka “mạnh hơn” nên luôn dùng. Redis có thể là cache, cấu trúc dữ liệu và một số kiểu message/stream, nhưng phải quyết định persistence/eviction/replication và dữ liệu nào là nguồn sự thật. Một cache miss phải có đường tới source; cache stale có thể gây kết quả sai nếu invalidation kém.

## Delivery semantics bằng timeline

Consumer nhận message `order-42`, ghi DB thành công, rồi chết **trước ack**. Broker có thể phát lại message. Nếu handler chèn đơn mới mỗi lần, tạo trùng. “At least once” nghĩa thiết kế idempotency, ví dụ message ID/unique constraint và transaction để chỉ áp hiệu ứng một lần. Nếu ack **trước** khi ghi DB rồi process chết, công việc có thể mất. “Exactly once” thường có phạm vi và giả định cụ thể; không dùng khẩu hiệu thay phân tích giao dịch qua DB và broker. RabbitMQ docs giải thích ack là chuyển trách nhiệm nhận/xử lý theo semantics của consumer; [xem reliability guide](https://www.rabbitmq.com/docs/reliability).

Ordering cũng có phạm vi. Kafka giữ thứ tự trong một partition; nếu key order ID được đưa tới cùng partition, event của một order có thứ tự tương đối ở đó, nhưng không có thứ tự toàn cục giữa mọi partition. Thêm consumer/partition để scale có thể đổi cách phân phối; retry/dead-letter có thể làm event tới muộn. Handler nên kiểm tra version/timestamp và chấp nhận duplicate/out-of-order theo bài toán. Với RabbitMQ, nhiều consumer/prefetch/requeue cũng ảnh hưởng thứ tự quan sát.

## DB và message: bài toán dual write

API ghi DB thành công rồi publish message thất bại: order tồn tại nhưng không ai gửi email. Publish trước rồi DB commit thất bại: email được gửi cho order không tồn tại. Transaction giữa hai hệ thống khác nhau không tự nhiên có atomicity. **Transactional outbox** ghi entity và outbox event trong cùng DB transaction; worker đọc outbox và publish, đánh dấu tiến độ. Nó giảm lỗ hổng dual write nhưng vẫn có thể publish lặp khi worker chết sau publish trước đánh dấu; consumer vẫn phải idempotent. Đây là mô hình quan trọng cho JD Kafka/RabbitMQ/Kafka Connect và microservices.

## Lab trên giấy và lab local tùy chọn

**Bài giấy:** vẽ producer -> broker -> consumer -> DB cho 1000 message/phút. Consumer xử lý 600/phút: backlog tăng 400/phút, sau 30 phút là 12.000 message nếu tốc độ không đổi. Thêm hai consumer mỗi cái 600/phút có thể giảm backlog, nhưng DB downstream có chịu nổi 1200 ghi/phút không? Tính age of oldest message, không chỉ count. Một queue dài nhưng message vừa đến có ý nghĩa khác backlog chờ hàng giờ.

**Lab local khi đã có Docker:** chạy broker riêng theo tài liệu chính thức trong môi trường lab, tạo một producer/consumer nhỏ có message ID và DB giả/SQLite. Gửi message, cố tình cho consumer chết sau ghi nhưng trước ack, quan sát redelivery và dùng unique constraint để tránh bản ghi trùng. Ghi kết quả thực, phiên bản broker và chính sách ack; không giả định behavior giống nhau giữa RabbitMQ/Kafka. Dọn container/volume lab sau khi xác nhận đúng tên; nếu muốn giữ dữ liệu làm bằng chứng, export trước khi xóa.

## Monitoring và runbook

Theo dõi publish/consume rate, backlog, age, retry, dead-letter, consumer lag, broker disk/memory/network và error downstream. Alert “queue length > 1000” thiếu ngữ cảnh: với 10.000 msg/s có thể bình thường, với 10 msg/s có thể nhiều giờ chậm. Đặt threshold theo SLO xử lý, capacity và tốc độ thay đổi. Khi backlog tăng, kiểm tra consumer còn sống, lỗi DB, poison message, partition skew, quota và recent deploy; không tăng số consumer vô hạn nếu DB đang nghẹt.

**Câu hỏi:** cache Redis có thể là nguồn dữ liệu duy nhất cho đơn hàng không? Chỉ khi kiến trúc/persistence/backup được thiết kế cho yêu cầu ấy; thông thường dữ liệu nghiệp vụ bền cần source khác. **Consumer ack sau ghi DB mà vẫn có duplicate?** Có, nếu chết giữa ghi và ack. **Kafka lag 0 nghĩa chức năng đúng?** Không; consumer có thể xử lý sai nhưng commit offset. Nguồn: [Kafka documentation](https://kafka.apache.org/documentation/), [RabbitMQ docs](https://www.rabbitmq.com/docs), [Redis docs](https://redis.io/docs/latest/).
