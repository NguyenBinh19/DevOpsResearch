## Consistency: bản sao phải đại diện cho thời điểm nào?

Khi một DB đang ghi, copy trực tiếp file dữ liệu có thể lấy các trang ở những thời điểm khác nhau, tạo bản sao không nhất quán. Snapshot ở storage có thể là crash-consistent, tương đương máy mất điện tại một thời điểm; DB engine có thể recovery bằng log nếu snapshot gồm đúng tập volume/log và quy trình phù hợp. Application-consistent backup thường phối hợp DB flush/backup API/transaction checkpoint để khi restore dữ liệu có nghĩa. Trước khi chọn “snapshot nhanh”, hỏi workload có nhiều volume không, log/WAL ở đâu, có cần quiesce không, sau restore đã chạy kiểm tra tính nhất quán chưa. Đây là lý do backup policy phải do đội app/DB và storage cùng thiết kế.

Với object storage, versioning/immutability giúp chống xóa/ghi đè một số tình huống nhưng cũng tăng chi phí/retention; IAM sai vẫn có thể khiến dữ liệu lộ. Multipart upload đang dở có thể tốn chỗ; lifecycle cần kiểm tra. Với NFS, network latency/locking và server HA ảnh hưởng app; “có file share” không nghĩa mọi workload được scale nhiều writer. Với SAN, multipath và zoning có thể giúp đường I/O dự phòng, nhưng phải thử mất một path và đo failover. Không nên giới thiệu một giao thức là nhanh/bền tuyệt đối: hiệu năng phụ thuộc workload, cấu hình và phần cứng.

## Bài tập capacity và RTO

Giả sử DB 1,5 TB, tăng 100 GB/tháng, backup full hằng tuần giữ 4 tuần và incremental hằng ngày 6 ngày/tuần. Nếu full không nén, riêng 4 bản full là 6 TB, chưa tính incremental, metadata, snapshot, bản sao offsite và growth. Tính lại với tỷ lệ nén thực đo được, không lấy con số quảng cáo. Nếu restore throughput hữu dụng chỉ 150 MB/s, truyền 1,5 TB lý tưởng đã gần 2,8 giờ, chưa tính replay log và kiểm tra app. RTO 1 giờ đòi standby/replication hoặc phương án khác; một backup full mỗi tuần không thể tự đáp ứng.

**Bài tập lựa chọn:** log ứng dụng giữ 30 ngày, ảnh người dùng, data directory PostgreSQL và backup DB nên đặt vào block/file/object loại nào? Gợi ý: log có thể đưa collector tới object/index backend; ảnh hợp object API; PG data thường cần block/filesystem được engine hỗ trợ với latency/consistency phù hợp; backup phù hợp object/offsite theo công cụ. Không có đáp án duy nhất nếu thiếu RPO/RTO, throughput, quy mô và quyền; bạn phải nêu giả định và test.

## Ceph, MinIO, NFS: học trách nhiệm vận hành

Ceph phân phối dữ liệu qua cluster và có interface block/file/object, nhưng yêu cầu thiết kế failure domain, network, capacity headroom, recovery traffic, monitoring và upgrade. Một cluster có 3 node nhưng cùng rack/power chưa chịu lỗi rack. Khi một disk chết, recovery/replication có thể làm latency tăng; cần capacity và bandwidth để phục hồi mà không làm app quá tải. MinIO object storage tự quản cần xem erasure coding, drive/node failure, bảo vệ bucket, lifecycle, versioning, backup/DR theo phiên bản triển khai. NFS cần server/storage HA và kiểm tra mount semantics. Đừng nói “cài được” thành “vận hành được”.

## Runbook cho PVC Pending

1. Xác định PVC nào, namespace, StorageClass và event `ProvisioningFailed`/`WaitForFirstConsumer`/quota. 2. Đọc CSI controller/node plugin logs theo resource cụ thể, kiểm tra topology và quyền backend. 3. Nếu PVC Bound nhưng Pod Pending, xem node affinity/attach/mount và lỗi volume multi-attach. 4. Chỉ thay StorageClass/capacity sau khi hiểu dữ liệu đang ở đâu và thao tác có tạo volume mới hay không. 5. Sau sửa, kiểm tra Pod mount, app đọc/ghi, dữ liệu cũ còn, metric latency và backup. Không xóa PVC production để “tạo lại” nếu chưa có restore plan.

**Câu hỏi:** Vì sao `kubectl get pvc` Bound chưa đủ? Nó chỉ chứng minh binding; mount, quyền, consistency, hiệu năng và backup chưa được kiểm tra. **Vì sao replication không chống lỗi người dùng xóa bảng?** Lệnh xóa logic cũng được nhân bản. **RPO/RTO là lời hứa cho ứng dụng hay storage?** Cho dịch vụ/dữ liệu người dùng; storage chỉ cung cấp một số cơ chế để đạt mục tiêu. Nguồn: [Kubernetes persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), [Ceph architecture](https://docs.ceph.com/en/latest/architecture/).

**Bài tập phục hồi:** chọn một backup, ghi checksum và thời điểm, restore sang namespace/VM cách ly, chạy query kiểm tra ba bản ghi đã biết và một request app. Nếu chỉ mount được volume nhưng schema sai hoặc dữ liệu thiếu, restore chưa đạt. Đo thời gian từng bước để so với RTO, ghi thiếu sót và sửa runbook trước khi công bố mục tiêu phục hồi.
