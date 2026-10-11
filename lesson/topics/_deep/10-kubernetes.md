## Mô hình control plane: vì sao hệ tự sửa được?

Kubernetes API server nhận khai báo và lưu trạng thái qua etcd. Controller manager liên tục so trạng thái mong muốn với quan sát; scheduler chọn node cho Pod chưa được gán; kubelet trên node kéo image và yêu cầu container runtime chạy container. Đây là các vòng lặp bất đồng bộ. Lệnh `kubectl apply` thành công chỉ cho biết API chấp nhận resource, không chứng minh Pod đã Ready hoặc người dùng truy cập được. Một Deployment mong 3 replica có thể vẫn chỉ có 1 replica khả dụng vì thiếu tài nguyên hoặc image pull lỗi.

Khi đọc trạng thái, phân biệt `desired`, `current`, `available`, `ready`. `Running` mô tả phase của Pod; readiness probe quyết định Pod có được đưa vào Service endpoints hay không. Liveness probe thất bại thường dẫn đến restart container; startup probe cho ứng dụng khởi động chậm có thời gian trước khi liveness kiểm tra. Nếu đặt liveness phụ thuộc DB, DB chập chờn có thể làm mọi Pod tự restart và tăng tải khởi động. Probe nên trả lời đúng câu hỏi: tiến trình kẹt cần restart, hay Pod tạm không nhận traffic?

### Sơ đồ đường request và điểm điều tra

```text
client -> load balancer -> ingress -> Service -> EndpointSlice -> Pod
                                                  |
                                         container -> DB/cache
```

Khi nhận 503, kiểm tra ingress/controller log và Service endpoints. Nếu Service không có endpoint, xem selector, pod labels, readiness và namespace. Nếu endpoint có nhưng lỗi, xem app log, port, NetworkPolicy và dependency. Đừng bắt đầu bằng tăng replicas khi cả replicas hiện tại đều sai cấu hình.

## Lập ngân sách tài nguyên trước khi autoscaling

`requests` cho scheduler biết lượng CPU/memory cần đặt chỗ; `limits` giới hạn tiêu thụ theo cơ chế runtime. CPU vượt limit thường bị throttling; memory vượt limit có thể OOM kill. HPA dựa trên metric và mục tiêu, không có phép màu tạo node: nếu cluster thiếu capacity, replicas tăng nhưng Pending. Cluster autoscaler (nếu có) và HPA giải hai bài khác nhau. Với database hoặc queue, tăng worker có thể đẩy nút thắt sang dependency. Trước HPA, đo throughput, latency, resource per request, max connection và thời gian warm-up.

Ví dụ CPU HPA target 60% khi Pod request 250m CPU. Mức dùng 150m là 60% request; nếu app có memory leak, CPU HPA có thể không phản ứng. Nếu mỗi Pod mở 20 DB connections, scale từ 3 lên 30 Pod có thể tạo 600 connections và làm DB quá tải. Vì vậy autoscaling cần giới hạn min/max, load test và quan sát downstream.

## Triển khai không gián đoạn và rollback thực sự

Rolling update tạo Pod mới rồi giảm Pod cũ theo `maxSurge`/`maxUnavailable`. Nó phụ thuộc readiness chính xác, capacity dư và app có tương thích với cả phiên bản cũ/mới trong giai đoạn chồng lắp. `kubectl rollout status deployment/notes-api` cho biết rollout controller hoàn tất; smoke test nghiệp vụ và metric sau phát hành mới kiểm tra tác động người dùng. Nếu DB migration đổi schema không tương thích, rollback image không đủ. Dùng expand/contract: thêm trường mới nhưng giữ đường cũ, chuyển app, xác nhận, rồi mới xóa trường cũ trong release sau.

Đặt PodDisruptionBudget giúp giới hạn số Pod mất đồng thời khi evict tự nguyện, nhưng không cứu được sự cố node đột ngột hoặc ứng dụng crash. Topology spread/anti-affinity giúp phân bố Pod qua node/zone; cần kiểm tra cluster thật có các failure domain khác nhau. Ba replica trên một node không chống mất node.

## Lab có trình tự: từ manifest đến chẩn đoán

Điều kiện: cluster local riêng như kind/minikube, `kubectl` trỏ đúng context. Bước 1: đọc `lesson/labs/kubernetes-local/web.yaml`, dự đoán Deployment và Service sẽ tạo gì. Bước 2: áp vào namespace lab và dùng `kubectl get deployment,pods,service -n <namespace> -o wide`; ghi image, replicas, labels và port. Bước 3: dùng `kubectl describe pod` và `kubectl get events --sort-by=.lastTimestamp` để thấy controller đã làm gì. Bước 4: sửa selector Service cho không khớp pod label; ghi endpoints rỗng và HTTP lỗi. Bước 5: phục hồi selector, xác nhận request lại thành công. Bước 6: sửa image thành tag không tồn tại; ghi `ImagePullBackOff` và event cụ thể, rồi quay image cũ. Bước 7: xóa namespace lab sau khi lưu log/bằng chứng.

**Kết quả mong đợi:** bạn giải thích được vì sao `kubectl apply` vẫn thành công ở bước 4/6, nhưng request không thành công; có ảnh hoặc log cho từng bằng chứng. **Không chạy lệnh xóa trên context/namespace chưa kiểm tra**; trong phỏng vấn hãy kể chính xác lỗi bạn đã tự tạo và giới hạn của lab local.

## Tình huống phỏng vấn: Pending, CrashLoop và 503

Pod `Pending`: đọc scheduler events. Có thể thiếu CPU/memory, node selector không khớp, PVC chưa bind hoặc taint/toleration sai. Pod `CrashLoopBackOff`: xem `kubectl logs --previous`, exit code, config/secret, liveness probe và OOMKilled. Ingress 503 trong khi Pod Running: xem readiness, Service selector/endpoints, target port, gateway route và network policy. Ba trạng thái có các nguyên nhân khác nhau; cùng một lệnh restart không phải lời giải.

Một câu trả lời tốt có thứ tự: xác nhận tác động; lấy trạng thái và events; so thay đổi gần nhất; tạo giả thuyết; kiểm tra một biến; giảm tác động; xác nhận hồi phục; ghi runbook. Với cluster on-prem, mở rộng kiểm tra xuống host vật lý, storage và registry.
