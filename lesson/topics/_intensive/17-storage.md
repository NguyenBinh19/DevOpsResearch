## Chọn theo giao diện truy cập và tính chất dữ liệu

**Block storage** cho OS/DB thấy một thiết bị block để tạo filesystem; thường phù hợp DB cần I/O và semantics nhất định. **File storage** (NFS/SMB) cho nhiều client truy cập đường file theo giao thức và quyền; cần hiểu locking, cache và lỗi server/network. **Object storage** lưu object qua API/bucket/key, phù hợp backup/artifact/static asset; không là POSIX filesystem mặc định. MinIO cung cấp API tương thích S3 ở môi trường tự quản theo tính năng/phiên bản; Ceph có nhiều interface (object/block/file) với kiến trúc vận hành riêng. SAN mô tả mạng/hạ tầng block, không phải tự động tương đương backup hay HA.

Hỏi bốn câu trước khi chọn sản phẩm: app cần random write hay object PUT/GET? nhiều writer cùng file hay một writer? latency/throughput/IOPS mục tiêu? khi mất node/disk/site, dữ liệu được bảo toàn với RPO/RTO nào? SQLite trên NFS, nhiều Pod cùng ghi, có thể vấp semantics locking/performance; không “giải scale” bằng cách mount chung bừa. Một volume có thể `ReadWriteMany` về mặt storage nhưng DB vẫn chưa thiết kế multi-writer.

## Từ PVC đến byte trên đĩa

Trong Kubernetes, Pod yêu cầu PVC; PVC được bind tới PV/provisioner theo StorageClass, access mode, capacity và topology. PVC `Bound` chỉ chứng minh cấp volume, chưa chứng minh dữ liệu được backup hay Pod ghi đúng. Nếu Pod Pending vì PVC, đọc Events của PVC/Pod, StorageClass, provisioner, node topology và quota. Nếu Pod chạy nhưng ứng dụng báo permission denied, xem UID/GID, filesystem ownership và securityContext; đổi access mode không chữa quyền file. Nếu Pod chuyển zone trong khi volume chỉ gắn được một zone, scheduler/topology có thể ngăn placement hoặc khiến recovery kéo dài.

Reclaim policy quyết định tài nguyên storage sau khi PVC/PV bị xóa theo cấu hình; không dùng một giá trị mặc định làm giả định bảo vệ dữ liệu. Một thao tác `helm uninstall` có thể không xóa PVC hoặc có thể kéo theo dữ liệu tùy chart/policy; trước khi dọn lab, kiểm tra resource thực. Object storage lifecycle/retention cũng có thể xóa backup ngoài ý muốn nếu cấu hình sai.

## Backup, snapshot, replication và restore

Snapshot ghi lại trạng thái ở một thời điểm theo khả năng hệ thống; nếu cùng failure domain với dữ liệu gốc, nó không bảo vệ trước mất cả storage. Replication giúp có bản sao khi phần cứng hỏng nhưng lệnh xóa hoặc dữ liệu lỗi cũng có thể được nhân bản. Backup là bản sao độc lập theo retention/immutability/khả năng restore được thử. Với DB, cần transaction-consistent backup, log/WAL/binlog nếu muốn point-in-time recovery, kiểm tra checksum và một restore drill ở môi trường cách ly. RPO/RTO là kết quả đo, không phải thông số brochure.

Ví dụ backup mỗi 6 giờ, không có log liên tục: trong trường hợp xấu mất gần 6 giờ dữ liệu. Nếu copy 2 TB qua đường mạng thực 100 MB/s, riêng truyền lý tưởng mất khoảng 5,6 giờ (2.000.000 MB / 100 MB/s), chưa tính download, decompress, index rebuild, kiểm tra app. RTO 1 giờ không phù hợp nếu không có standby/replication hoặc đường phục hồi khác. Tính toán đơn giản giúp phát hiện lời hứa phi thực tế trước khi sự cố xảy ra.

## Lab mô hình trên máy riêng

Tạo một file SQLite lab và một bản sao độc lập bằng cơ chế backup phù hợp của SQLite/app, không chỉ `cp` file khi DB đang ghi. Ghi note A, backup, ghi note B, rồi restore bản backup vào **đường khác** để xác nhận bản restore có A và có/không có B theo thời điểm backup. Không ghi đè DB gốc trong bài. Ghi thời gian tạo backup, kích thước, checksum và thời gian restore. Nếu app mẫu đang dùng nhiều process, dừng ghi hoặc dùng SQLite backup API để có snapshot nhất quán; đọc tài liệu chính thức theo phiên bản. Dọn file restore riêng sau khi đã đối chiếu.

**Lỗi có chủ đích trên giấy:** PVC đầy, Pod vẫn `Running`, API trả 500 khi ghi. Kiểm tra dung lượng/inode ở filesystem container và storage backend, log DB, PVC capacity/expansion policy, metric storage. Giảm tác động bằng ngăn log/temp phình, mở rộng có kế hoạch hoặc khôi phục theo runbook; không xóa dữ liệu nghiệp vụ để có chỗ mà chưa biết retention. Nếu nhiều VM cùng chậm, tìm shared datastore/network thay vì tăng CPU từng VM.

**Câu hỏi:** ba replica Ceph có nghĩa không cần backup? Không; replication chống một số lỗi hạ tầng, không chống xóa logic/ransomware như backup độc lập. **Câu hỏi:** `ReadWriteMany` có cho ba MySQL instance cùng ghi một data directory? Không; access mode chỉ mô tả khả năng mount, không thay cơ chế DB cluster. Nguồn: [Kubernetes storage](https://kubernetes.io/docs/concepts/storage/), [Ceph documentation](https://docs.ceph.com/en/latest/), [SQLite backup API](https://www.sqlite.org/backup.html).
