## Chọn mô hình truy cập trước chọn sản phẩm

Block storage cho hệ điều hành/filesystem/DB quản lý block; file storage qua NFS cho nhiều client đọc/ghi theo semantics file; object storage qua API lưu object/bucket. SAN mô tả hạ tầng block; Ceph có thể cung cấp block, file, object theo service; MinIO là object storage tương thích S3. Không nên mount object như POSIX rồi giả định mọi thao tác rename/lock giống filesystem. Chọn theo pattern đọc/ghi, latency/IOPS, tính nhất quán, sharing, quyền, backup, vận hành và chi phí.

### Bài tập quyết định

Với Notes API: database cần ghi transaction nhỏ, có thể dùng block/PVC phù hợp; file đính kèm lớn dùng object; tập tin cấu hình chia sẻ nếu thực sự cần có thể dùng file. Nếu chỉ vì "có NFS" mà đặt database lên NFS, cần kiểm tra support/locking/durability/performance của DB và storage cụ thể. Nếu dùng Ceph, phải hiểu cluster storage có failure domain/quorum/capacity riêng; ba bản sao trên cùng một host không chống host hỏng.

## PersistentVolume và trách nhiệm dữ liệu

Trong Kubernetes, PVC yêu cầu storage theo access mode/capacity/storage class; PV là tài nguyên được cấp. StatefulSet giúp định danh Pod/volume ổn định nhưng không tự backup dữ liệu. Reclaim policy có thể giữ hoặc xóa volume khi PVC bị xóa; cần đọc trước khi dọn lab. Khi Pod chuyển node, storage phải hỗ trợ attach/mount ở node mới và dữ liệu còn nhất quán. `ReadWriteOnce` không nên diễn giải thành "chỉ một Pod" trong mọi trường hợp; đọc semantics chính thức theo driver/phiên bản. Một rollout app thành công không chứng minh volume phục hồi sau mất node.

## Backup khác snapshot, replication

Snapshot có thể giúp quay nhanh về điểm trước nhưng phụ thuộc hệ storage và tính nhất quán ứng dụng. Replica tăng khả dụng nhưng nhân bản lỗi logic. Backup nên tách failure domain, có retention, quyền, mã hóa và restore test. Với database, snapshot lúc transaction đang ghi có thể cần phối hợp DB hoặc log để đảm bảo phục hồi nhất quán. Diễn tập: backup A -> tạo dữ liệu B -> restore sang volume/file mới -> kiểm tra A/B theo kỳ vọng -> đo thời gian. Chỉ có file backup và chưa restore không đạt cổng năng lực.

## Case: nhiều VM cùng chậm, CPU bình thường

Thu datastore latency/queue, IOPS, thời điểm backup/snapshot, network storage, log ở DB và baseline. Nếu chỉ một VM chậm, xem VM/DB riêng; nếu nhiều VM cùng datastore chậm, giả thuyết shared storage mạnh hơn. Giảm tác động có thể điều tiết job I/O lab hoặc chuyển workload theo quy trình, rồi đo lại. Không xóa snapshot/volume production để "giải phóng" khi chưa hiểu dependency và retention.
