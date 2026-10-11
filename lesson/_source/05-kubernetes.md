# Giai đoạn 5 - Kubernetes từ mô hình đến xử lý sự cố

Kubernetes điều phối container trên một cluster. Hãy học nó sau khi hiểu container, network và một quy trình triển khai đơn giản; như vậy bạn sẽ thấy nó giải quyết vấn đề gì và thêm độ phức tạp nào. Lab nên bắt đầu trên cluster local có dữ liệu giả.

## Bài 1. Mô hình cluster và vòng lặp điều khiển

Cluster gồm control plane và các node chạy workload. Bạn khai báo trạng thái mong muốn qua API; controller quan sát trạng thái thực tế và cố đưa hệ thống về trạng thái mong muốn. Ví dụ, Deployment yêu cầu ba bản sao của API. Nếu một Pod chết, controller tạo Pod mới. Điều này khác với một script chạy một lần rồi kết thúc: Kubernetes tiếp tục đối chiếu.

Pod là đơn vị nhỏ nhất được lập lịch, thường chứa một container ứng dụng và có thể có container phụ trợ. Pod có vòng đời; IP và nơi chạy có thể đổi khi được thay thế. Vì thế client không nên phụ thuộc vào IP cụ thể của Pod. Service cung cấp điểm truy cập ổn định theo tập Pod phù hợp nhãn. Deployment quản lý ReplicaSet và Pod cho ứng dụng stateless; StatefulSet và storage cần khi workload có trạng thái và danh tính ổn định hơn.

Scheduler quyết định Pod chạy ở node nào dựa trên requests tài nguyên và ràng buộc. `requests` giúp đặt chỗ và lập lịch; `limits` đặt trần một số tài nguyên. Nếu request quá lớn, Pod có thể Pending dù tổng CPU trên cluster nhìn có vẻ còn; nếu limit memory quá thấp, container có thể bị OOMKilled. Trước khi tăng con số, xem events và mức dùng thực tế.

### Sơ đồ tư duy

Người dùng -> Ingress/Gateway hoặc load balancer -> Service -> Pod -> container ứng dụng -> database. Control plane nhận mô tả và các controller tạo/sửa đối tượng; node thực thi container. Hãy vẽ hai luồng riêng: luồng request của người dùng và luồng điều khiển. Nhầm hai luồng này khiến việc chẩn đoán rất khó.

## Bài 2. Cấu hình, probe và rollout

ConfigMap lưu cấu hình không nhạy cảm; Secret lưu dữ liệu nhạy cảm theo cơ chế Kubernetes nhưng không tự biến thành kho bí mật an toàn tuyệt đối. Cần kiểm soát RBAC, encryption at rest theo môi trường và cách secret được đưa vào Pod. Đừng commit giá trị secret thật vào manifest. Namespace giúp nhóm đối tượng, nhưng một namespace đơn lẻ không phải biên cách ly bảo mật đầy đủ.

Liveness probe trả lời có nên restart container không; readiness probe trả lời có nên gửi traffic tới Pod không; startup probe cho ứng dụng cần thời gian khởi động dài. Dùng sai probe có thể tạo vòng restart hoặc đưa traffic quá sớm. Ví dụ API khởi động trong 20 giây nhưng liveness quá gắt có thể bị giết trước khi sẵn sàng. Probe nên kiểm tra điều có ý nghĩa nhưng không làm dependency quá tải.

Rollout thay Pod cũ bằng Pod mới theo chiến lược cấu hình. Trước deploy, biết image/digest, replica, request/limit, biến cấu hình và migration database. Sau deploy, kiểm tra rollout status, events, log và request thật. Nếu bản mới lỗi, rollback workload là một lựa chọn, nhưng phải xét tương thích dữ liệu. Kubernetes giúp thay Pod; nó không tự sửa lỗi business logic.

### Lab cluster local

Điều kiện: đã cài một môi trường Kubernetes local theo hướng dẫn chính thức và có image ứng dụng. Dùng namespace riêng cho lab. Tạo Deployment một replica với image xác định; tạo Service; kiểm tra Pod, Deployment, Service; dùng port-forward hoặc cách truy cập local được tài liệu môi trường hướng dẫn. Gọi health endpoint, ghi kết quả thực tế. Đổi image sang phiên bản B, xem rollout; nếu lỗi, thử rollback trong lab. Xóa namespace lab sau khi chắc chắn nó chỉ chứa dữ liệu giả.

Các lệnh đọc thường dùng: `kubectl get pods`, `kubectl describe pod <ten>`, `kubectl logs <ten>`, `kubectl get events --sort-by=.lastTimestamp`, `kubectl rollout status deployment/<ten>`. Trước khi dùng `kubectl delete` hoặc apply, luôn nhìn `kubectl config current-context` và namespace; một lệnh đúng trên sai cluster vẫn gây hậu quả.

## Bài 3. Chẩn đoán lỗi theo triệu chứng

Pod `Pending`: xem events, resource requests, node capacity, scheduling constraints và volume binding. `ImagePullBackOff`: xem tên image, tag/digest, registry access và credentials; không sửa bằng cách tăng CPU. `CrashLoopBackOff`: xem log lần chạy trước, exit code, cấu hình, dependency và probe; Pod khởi động lại liên tục là triệu chứng chứ không phải nguyên nhân. `Running` nhưng không Ready: kiểm tra readiness probe và ứng dụng có thực sự nhận request không.

Service không route: kiểm tra selector/labels, endpoints, port/targetPort, network policy và ứng dụng có lắng nghe đúng interface/port không. DNS trong cluster có thể có lỗi tên, namespace hoặc CoreDNS; thử lookup từ Pod chẩn đoán ở đúng namespace. Nếu Ingress trả 502, xem đường từ controller tới Service rồi Pod; đừng thay cả ba cấu hình cùng lúc vì bạn sẽ mất khả năng biết sửa gì đã có tác dụng.

### Bài thực hành tạo lỗi

Trong cluster local, sửa label của Pod template để Service không chọn được Pod. Xem endpoints và thử gọi API; dự đoán kết quả, sau đó sửa label. Tiếp theo đặt image tag sai để quan sát ImagePullBackOff, rồi khôi phục. Cuối cùng đặt readiness path sai; xem Pod Running nhưng chưa Ready. Ghi chuỗi: triệu chứng -> bằng chứng -> giả thuyết -> thay đổi nhỏ -> kiểm tra lại.

## Bài 4. Bảo mật và câu hỏi thiết kế

RBAC quyết định identity được thao tác API nào. NetworkPolicy, khi plugin mạng hỗ trợ, giới hạn traffic giữa Pods/namespaces. Security context giúp kiểm soát user, privilege và filesystem. Pod Security Standards cung cấp mức chính sách chung. Dùng image được duy trì, quét dependency, hạn chế quyền, không mount secret không cần thiết và xem ai có thể đọc logs. Đây là nhiều lớp bảo vệ, không có một cờ bật "an toàn" cho mọi cluster.

Đặt câu hỏi "có cần Kubernetes không?" trước khi dùng. Nếu nhu cầu chỉ là một ứng dụng nhỏ và nhóm chưa sẵn sàng vận hành cluster, dịch vụ container managed hoặc VM có thể đơn giản hơn. Kubernetes hữu ích khi bạn cần chuẩn hóa triển khai nhiều workload và chấp nhận chi phí vận hành của hệ sinh thái đó.

## Bài 5. Đọc manifest dòng theo dòng

File `lesson/labs/kubernetes-local/web.yaml` gồm hai đối tượng. Deployment có `metadata.name` để định danh; `spec.replicas: 2` là số Pod mong muốn; `selector.matchLabels` và `template.metadata.labels` phải khớp. Nếu không khớp, Deployment không quản lý được Pod như dự định. Container dùng `nginx:stable` chỉ để học đường đi traffic; tag này có thể đổi nội dung theo thời gian, nên bản phát hành thực cần định danh image cụ thể hơn.

Container công bố `containerPort: 80`. `resources.requests` cho scheduler biết mức tối thiểu cần tính; `resources.limits` giới hạn mức dùng. Hai probe gọi `/` qua HTTP port 80. Service chọn Pod có label `app: notes-web` và chuyển từ cổng 80 của Service tới cổng 80 của Pod. Nếu đổi một bên thành label khác, Service không còn endpoint. Bài lab yêu cầu bạn tự dự đoán điều đó trước khi sửa file.

Hai số 80 trong Service không phải lúc nào cũng phải giống nhau. `port` là cổng Service; `targetPort` là cổng ở backend Pod. Ví dụ Service có thể nghe 8080 và chuyển tới container 80. Khi chẩn đoán, kiểm tra ứng dụng thực sự đang nghe cổng nào, không chỉ đọc `containerPort`, vì trường đó là metadata chứ không làm tiến trình mở cổng.

### Lab có lệnh rõ ràng

Điều kiện: đang dùng **cluster local** và đã xem `kubectl config current-context`. Nếu context trỏ tới cluster dùng chung hoặc cloud, dừng và chọn đúng cluster trước khi tạo namespace. Chạy `kubectl create namespace devops-lab`. Từ thư mục có file manifest, chạy `kubectl apply -n devops-lab -f web.yaml`, sau đó `kubectl get deployment,pods,service -n devops-lab`. Mong đợi một Deployment với 2 Pod sau khi image được tải và probe qua. Lần đầu có thể mất thời gian tải image; quan sát bằng `kubectl get pods -n devops-lab -w` rồi Ctrl+C khi đủ thông tin.

Mở terminal thứ hai và chạy `kubectl port-forward -n devops-lab service/notes-web 8080:80`. Mở `http://127.0.0.1:8080`; mong đợi trang chào của nginx. Lệnh port-forward chỉ phục vụ phiên lab và dừng khi bạn Ctrl+C. Nếu port 8080 bận, chọn một cổng local khác ở bên trái dấu `:`. Nếu Pod chưa Ready, xem `kubectl describe pod` và events trước khi kết luận Service lỗi.

### Ba lỗi có kiểm soát

Lỗi 1: đổi selector của Service từ `app: notes-web` thành `app: wrong-label`, apply lại. Xem `kubectl get endpoints -n devops-lab notes-web` hoặc EndpointSlice tương ứng; backend sẽ trống. Khôi phục label và apply lại. Lỗi 2: sửa đường readiness từ `/` thành `/missing`; Pod có thể Running nhưng Ready bằng false, khiến Service không gửi traffic. Khôi phục. Lỗi 3: đặt image tag không tồn tại trên một nhánh manifest lab; quan sát image pull events rồi quay về `nginx:stable`. Sau mỗi lỗi, ghi triệu chứng, lệnh đọc bằng chứng, giả thuyết và thay đổi đã sửa.

Khi xong, kiểm tra lại context và namespace. Chỉ nếu namespace `devops-lab` do bạn tạo và chỉ chứa dữ liệu giả, chạy `kubectl delete namespace devops-lab`. Việc xóa namespace xóa tài nguyên bên trong; vì thế đừng copy lệnh này sang namespace của người khác hoặc production.

## Bài 6. Mô phỏng quyết định vận hành

Pod Pending không phải lý do để tăng số replica. Nếu node không đủ bộ nhớ cho một Pod, thêm replica chỉ làm nhiều Pod Pending hơn. Nếu Pod OOMKilled, tăng memory limit có thể là một hướng nhưng trước đó cần xem mức dùng, leak, cấu hình và giá trị request/limit. Nếu một service có 0 endpoint dù 2 Pod Running, xem readiness và selector/labels. Nếu người dùng báo lỗi 502 khi rollout, xem tỷ lệ Pod Ready, upstream và log của phiên bản mới, rồi cân nhắc rollback.

Viết một bảng bốn cột: triệu chứng, lệnh đọc đầu tiên, giả thuyết, hành động an toàn. Ví dụ `ImagePullBackOff` -> `kubectl describe pod` -> registry/tag/credential -> xác minh image và quyền pull, rồi sửa đúng chỗ. Bảng này là sơ đồ chẩn đoán, không phải danh sách lệnh chữa tự động.

### Câu hỏi sâu để tự giải thích

Vì sao Deployment tạo Pod mới thay vì hồi sinh đúng Pod cũ? Vì sao Service cần nhãn thay vì giữ danh sách IP Pod bằng tay? Khi readiness fail, điều gì xảy ra với traffic? Nếu một Pod có liveness fail liên tục, việc restart có thể làm tình hình tệ hơn thế nào? Khi dùng một Secret trong Pod, những ai có quyền đọc nó ở API hoặc qua truy cập container? Mỗi câu cần trả lời bằng mô hình hệ thống, không chỉ bằng câu lệnh.

## Bài 7. Storage và ứng dụng có trạng thái

Pod có thể bị thay bất kỳ lúc nào, vì vậy file ghi trong filesystem tạm của container không phải nơi bền cho dữ liệu cần giữ. Volume cung cấp nơi lưu bên ngoài vòng đời container; PersistentVolume/PersistentVolumeClaim là mô hình Kubernetes cho storage bền theo khả năng của cluster. Nhưng "có PVC" chưa đủ: cần biết dữ liệu gắn với zone nào, có thể attach vào nhiều node không, backup/restore ra sao và điều gì xảy ra khi xóa claim. StorageClass và reclaim policy có thể quyết định volume thật còn hay mất; kiểm tra trước khi xóa.

Ứng dụng Notes API dùng SQLite, vốn phù hợp lab một tiến trình và một file. Tăng Deployment lên ba replica cùng dùng chung file SQLite qua storage tùy ý có thể tạo vấn đề đồng thời hoặc truy cập storage; đừng làm vậy chỉ để có ba Pod màu xanh. Khi hệ thống cần nhiều replica và dữ liệu chung, một database service phù hợp là lựa chọn rõ hơn. Đây là bài học quan trọng: Kubernetes không tự biến một ứng dụng có trạng thái thành hệ thống phân tán an toàn.

### Bài tập thiết kế

Vẽ ba Pod API và một database. Ghi phần nào stateless, phần nào có state. Nếu một API Pod chết, request mới có thể đi sang Pod khác qua Service, nhưng data vẫn ở database. Nếu database chết, ba Pod API vẫn có thể Running nhưng chức năng tạo ghi chú lỗi. Health/readiness nên thể hiện khả năng phục vụ theo ý nghĩa của endpoint; quyết định có làm readiness phụ thuộc DB hay không cần cân nhắc vì dependency chập chờn có thể khiến toàn bộ Pod bị loại khỏi traffic.

## Bài 8. RBAC và NetworkPolicy theo nguyên tắc tối thiểu

Trong Kubernetes, service account là identity cho workload nói chuyện với Kubernetes API; RBAC cấp quyền theo Role/ClusterRole và binding. Phần lớn web API không cần liệt kê Pod hay sửa Deployment, nên không cần quyền rộng với API cluster. Quyền quản trị cluster là quyền rất mạnh, không nên gắn cho ứng dụng chỉ để tránh lỗi forbidden. Khi gặp lỗi RBAC, đọc hành động, resource và namespace bị từ chối rồi cấp đúng quyền nếu thực sự cần.

NetworkPolicy lọc traffic theo nhãn và namespace, nhưng chỉ có hiệu lực khi network plugin hỗ trợ. Một rule cho phép API tới database cần xét chiều ingress ở DB và egress ở API theo chính sách đang dùng; DNS cũng phải được phép khi bạn áp chính sách deny rộng. Một Pod không kết nối được sau khi thêm policy không nhất thiết là lỗi DNS: có thể gói DNS bị chặn. Trước lab, nắm rõ cách undo policy và đừng thử trên namespace dùng chung.

### Bài tập giấy

API chỉ cần nhận HTTP từ ingress và gửi TCP tới DB cùng DNS. Viết sơ đồ allowed edges: ingress -> API; API -> DB; API -> DNS. Gạch bỏ API -> Kubernetes API nếu app không cần. Sau đó giải thích vì sao namespace riêng chưa tự đảm bảo các edge bị chặn. Đây là tư duy chính sách, chưa cần nhớ toàn bộ cú pháp NetworkPolicy.

## Bài 9. Đọc events thay vì chữa triệu chứng

Một Pod Pending có event `Insufficient memory`: không phải lỗi image hay service. Một Pod `ImagePullBackOff` có event unauthorized: xem registry credential, không tăng replica. Một Pod CrashLoopBackOff có exit code khác 0: xem log lần chạy trước và thay đổi gần nhất. Một Pod Running/Ready nhưng browser 404: request đã tới backend; xem route/path hoặc proxy. Viết mối liên hệ giữa trạng thái, event và bước kiểm tra tiếp theo; mục tiêu là giảm số thay đổi thử mò.

Khi thao tác trong cluster, ghi `context`, namespace và tên resource vào nhật ký. Context là cấu hình client quyết định cluster nào nhận lệnh. Namespace là phạm vi resource nhưng có nhiều resource cấp cluster. `kubectl get pods -A` có thể cho cái nhìn toàn cluster; `kubectl delete` với tùy chọn rộng có thể ảnh hưởng ngoài lab. Một thói quen tốt là chạy lệnh đọc để xác nhận đích ngay trước lệnh thay đổi.

## Cổng năng lực và câu hỏi phỏng vấn

Bạn giải thích được control plane, node, Pod, Deployment và Service; triển khai ứng dụng local; tự xử lý ba lỗi có kiểm soát; xem đúng context/namespace trước thao tác; nêu giới hạn của Secret và NetworkPolicy. Tự trả lời: Vì sao Pod có thể Running nhưng Service không có endpoint? Requests khác limits thế nào? Vì sao một Pod thay thế có IP khác? Khi nào dùng StatefulSet thay Deployment?

## Tài liệu chính thức

- Kubernetes concepts - cluster architecture: https://kubernetes.io/docs/concepts/architecture/
- Kubernetes concepts - workloads: https://kubernetes.io/docs/concepts/workloads/
- Kubernetes concepts - services/networking: https://kubernetes.io/docs/concepts/services-networking/
- Kubernetes concepts - security: https://kubernetes.io/docs/concepts/security/
