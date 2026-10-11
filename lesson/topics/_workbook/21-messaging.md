## Poison message và retry storm

Một message có dữ liệu sai khiến consumer luôn exception. Nếu broker requeue ngay lập tức, cùng message chạy lặp hàng nghìn lần/giây, chiếm CPU/log và chặn message tốt. Thiết kế retry có số lần/độ trễ/backoff, phân biệt lỗi tạm thời (DB timeout) với lỗi vĩnh viễn (schema invalid), đưa poison message vào dead-letter sau giới hạn và alert có owner. DLQ không phải thùng rác quên đi: cần xem, sửa dữ liệu/code rồi replay có kiểm soát, tránh tạo duplicate side effect. Nếu consumer commit offset/ack sai thời điểm, message có thể mất hoặc xử lý lặp.

### Backpressure và downstream

Nếu producer 2000 msg/s, consumer 1000 msg/s, backlog tăng 1000 msg/s. Sau 15 phút có 900.000 message nếu tốc độ giữ nguyên. Tăng consumer từ 2 lên 4 có thể giúp khi bottleneck là CPU consumer; nếu DB chỉ ghi được 1000/s, tăng consumer làm DB timeout và retry, có thể còn tệ hơn. Đo processing rate, lag age, error/retry, DB capacity và partition/queue distribution. Rate limit producer hoặc ưu tiên loại message quan trọng có thể là biện pháp giảm tác động.

## Outbox có lời giải theo failure point

Worker đọc outbox row, publish Kafka thành công, chết trước khi đánh dấu row đã publish. Sau restart, nó publish lại: consumer phải dedupe theo event ID/transaction. Nếu đánh dấu row trước rồi publish thất bại, event có thể mất; vì thế thứ tự và retry phải được thiết kế. Outbox không loại bỏ mọi duplicate; nó giúp không bỏ sót event do dual write giữa DB và broker theo điều kiện triển khai. Giám sát outbox age và số row pending, không chỉ broker lag.

### Chọn key/partition cho Kafka

Nếu cần thứ tự event của từng order, dùng order ID làm key để các event của order vào cùng partition theo cơ chế partitioner của hệ thống. Nhưng một order rất “nóng” có thể tạo hot partition; tăng partition không tự chia event của cùng key. Nếu dùng key ngẫu nhiên để cân tải, mất thứ tự per order. Đây là tradeoff thiết kế. Consumer group có thể scale tới số partition hữu ích; nhiều consumer hơn partition không tăng parallelism cho topic đó theo mô hình thông thường.

**Câu hỏi:** queue rỗng nhưng người dùng không nhận email, có thể lỗi gì? Producer không publish, consumer ack trước gửi, downstream email lỗi nhưng handler nuốt lỗi, hoặc đang xem sai queue/tenant; cần trace/correlation. **Kafka lag tăng, CPU consumer thấp?** Có thể consumer chờ DB/network, partition skew, poll loop bị block hoặc rebalance; CPU thấp không đủ kết luận. Nguồn: [Kafka documentation](https://kafka.apache.org/documentation/), [RabbitMQ reliability](https://www.rabbitmq.com/docs/reliability).

## Bài tập chọn công cụ theo yêu cầu

**Tác vụ A:** gửi email xác nhận sau khi tạo note, retry có giới hạn, không cần replay lịch sử cho nhiều nhóm consumer. Queue kiểu RabbitMQ có thể phù hợp; cần ack, DLQ, idempotency và monitoring. **Tác vụ B:** nhiều đội cần đọc luồng event thay đổi đơn hàng trong 30 ngày, replay để xây lại projection. Kafka/log event có thể phù hợp nếu đội vận hành được partitions, retention, schema và consumer lag. **Tác vụ C:** cache dữ liệu note đọc nhiều, có thể tái tạo từ DB. Redis là ứng viên; cần TTL/invalidation và bảo vệ DB khỏi cache stampede. Những lựa chọn này chỉ là khởi điểm: traffic, compliance, ordering và kỹ năng đội có thể đổi quyết định.

Khi phỏng vấn, đừng trả lời bằng benchmark “Kafka nhanh hơn RabbitMQ”. Hỏi delivery semantics, replay, fan-out, latency, operations và failure recovery. Một hệ thống có thể dùng cả hai vì trách nhiệm khác nhau, nhưng mỗi broker mới là một dịch vụ stateful cần backup/upgrade/alert.
