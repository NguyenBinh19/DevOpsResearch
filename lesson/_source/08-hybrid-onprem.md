# Chuyên đề 8 - Hybrid, VMware, storage và dịch vụ on-prem

Hai JD mô tả môi trường vừa có máy chủ tại doanh nghiệp vừa có cloud. Mục tiêu của chuyên đề là hiểu được các lớp vật lý, ảo hóa, mạng, lưu trữ và dịch vụ nền để không nhầm lỗi ứng dụng với lỗi hạ tầng. Lab máy cá nhân chỉ mô phỏng một phần; kinh nghiệm vận hành vSphere và SAN thật cần môi trường được cấp quyền.

```text
Client -> DNS/LB -> API VM/Pod -> Database VM -> block storage/SAN
                         |                 |
                      Harbor           backup/object storage
                         |
                    VMware host -> datastore -> network -> cloud link
```

Khi một request lỗi, đi theo sơ đồ để hỏi lớp nào còn hoạt động. Khi chuẩn bị nâng cấp, đi từ dưới lên để hỏi một thay đổi ở host/datastore/network tác động tới dịch vụ nào.

## Bài 1. Từ máy vật lý đến máy ảo

Một máy vật lý có CPU, RAM, đĩa và NIC. Hypervisor chia tài nguyên đó thành nhiều máy ảo (VM), mỗi VM có hệ điều hành và tiến trình riêng. Máy vật lý chạy hypervisor thường gọi là host; nhiều host hợp thành cluster. vSphere là hệ sinh thái VMware quản lý host, VM, network và storage. Ảo hóa giúp cấp máy nhanh và dùng tài nguyên linh hoạt hơn, nhưng không làm phần cứng biến mất: nếu mọi VM quan trọng cùng nằm trên một host, host hỏng vẫn gây gián đoạn lớn.

Khả năng sẵn sàng cao cần nói rõ đang chống lỗi nào. Một VM restart tự động trên host khác giúp khi host mất, nhưng thời gian khởi động và data consistency vẫn cần kiểm tra. Di chuyển VM đang chạy giữa host có thể giúp bảo trì nhưng phụ thuộc network/storage/cấu hình phù hợp. Một bản sao VM không mặc nhiên là backup; lỗi xóa dữ liệu trong guest có thể được mang theo. Khi thiết kế, vẽ các failure domain: host, rack, storage, network và site.

### Ví dụ thiết kế

Ứng dụng có hai VM chạy API, một VM database và một load balancer. Nếu API-1 hỏng, LB chuyển traffic sang API-2 nếu health check đúng. Nếu database VM hỏng, cả hai API có thể còn chạy nhưng không tạo ghi chú được. Nếu cả ba VM nằm trên cùng datastore và datastore mất, số VM không giúp. Do đó câu hỏi "có HA chưa?" phải được trả lời theo từng lớp, kèm cách thử failover và mục tiêu RTO/RPO.

### Bài tập trên giấy

Vẽ hai host H1/H2, một shared datastore, hai API VM và một DB VM. Đặt VM để giảm điểm lỗi đơn. Khoanh tròn các điểm vẫn là single point of failure. Đề xuất một phép kiểm tra để chứng minh API chuyển host hoặc traffic khi một VM mất. Ghi điều chưa thể kiểm chứng khi bạn không có vSphere lab; không biến giả định thành kinh nghiệm đã làm.

## Bài 2. Lưu trữ: block, file và object

Block storage trình bày các khối để hệ điều hành tạo filesystem hoặc database sử dụng; SAN là một kiến trúc kết nối storage ở mức block. File storage trình bày cây thư mục qua giao thức như NFS; nhiều client có thể mount theo quyền/cấu hình. Object storage lưu object trong bucket/namespace qua API, thường phù hợp artifact, media và backup. MinIO cung cấp object storage tương thích S3; Ceph có thể cung cấp block, file và object qua các thành phần khác nhau. Tên sản phẩm không thay thế việc chọn đúng mô hình truy cập.

Latency, throughput, IOPS, độ bền, khả năng chia sẻ, snapshot, replication và backup là các chiều đánh giá. Database nhạy với độ trễ I/O và tính nhất quán; file NFS gắn vào Pod cần hiểu access mode và failure mode; object storage không phải ổ đĩa POSIX mặc định. Một ứng dụng có thể dùng block cho database, object cho ảnh/backup và file cho chia sẻ cấu hình, nhưng cần xét chi phí và mức độ phức tạp.

### Tình huống điều tra

Nhiều VM cùng chậm lúc 09:00. CPU từng VM không cao. Nếu các VM dùng chung datastore, vấn đề I/O storage là một giả thuyết đáng kiểm tra. Thu thập latency/queue của storage, thay đổi/backup job gần thời điểm đó và hiệu năng network storage. Đừng tăng CPU tất cả VM khi bằng chứng không chỉ CPU. Ngược lại, nếu chỉ một app chậm và storage chung bình thường, xem truy vấn DB, lock hoặc cấu hình VM đó.

### Lab tối giản

Trên máy lab, tạo hai thư mục: một thư mục lưu file ứng dụng, một thư mục lưu bản backup. Dùng ứng dụng Notes API để ghi dữ liệu, copy bằng quy trình backup an toàn sang nơi khác, rồi restore sang file mới và xác minh. Bài này dạy nguyên tắc tách nơi lưu và kiểm tra restore; nó **không** mô phỏng được tính chất của SAN/Ceph. Nếu có môi trường VM hợp pháp, bạn có thể thêm một NFS share thử và đo tác động khi share ngắt, nhưng chỉ trong mạng lab.

## Bài 3. Dịch vụ nền: Harbor và Vault

Harbor là registry quản lý image/artifact trong môi trường doanh nghiệp. Ngoài việc "push/pull image", người vận hành quan tâm project, quyền, retention, scanning, replication, backup registry và khả năng registry sẵn sàng khi cluster cần kéo image. Nếu registry lỗi, Pod đang chạy có thể vẫn phục vụ nhưng rollout/scale mới có thể thất bại vì không pull được image. Bài học là xem dependency ở thời điểm **thay đổi** chứ không chỉ thời điểm hiện tại.

Vault là hệ thống quản lý secrets và một số khả năng identity/cryptography. Câu hỏi vận hành gồm: ai xác thực, policy nào cho phép đọc secret, secret được cấp/rotate thế nào, audit log ở đâu, Vault không sẵn sàng thì ứng dụng khởi động ra sao. Không nên lấy một token quản trị rồi đặt vào mọi server. Một lab Vault local có thể dạy policy, nhưng chưa chứng minh kiến thức HA/unseal/backup production.

### Bài tập dependency graph

Vẽ GitLab/Jenkins -> build image -> Harbor -> Kubernetes -> ứng dụng -> Vault -> database. Với mỗi mũi tên, ghi credential và tín hiệu lỗi. Giả sử Harbor mất 30 phút: deployment mới bị ảnh hưởng thế nào? Giả sử Vault mất sau khi app đã khởi động: app có còn hoạt động tùy cách lấy/caching secret không? Đừng trả lời chung chung; nêu giả định rồi thử kiểm chứng trong lab.

## Bài 4. Ansible và tự động hóa cấu hình máy

Terraform thường quản lý vòng đời tài nguyên như network, VM hoặc dịch vụ cloud. Ansible thường dùng inventory và playbook để cấu hình hệ điều hành/phần mềm trên các máy. Một playbook mô tả trạng thái mong muốn bằng module; chạy lại nên đưa hệ thống về cùng kết quả nếu không có thay đổi đầu vào. Đây là tính idempotent cần kiểm tra, không phải chỉ chạy thành công một lần. Ansible cần kết nối và quyền trên managed node; kiểm soát inventory để tránh chạy vào sai môi trường.

### Lab Ansible an toàn

Khi có một VM Linux lab, tạo inventory chỉ chứa VM đó, viết playbook kiểm tra kết nối và tạo một file dấu trong thư mục lab theo tài liệu Ansible. Chạy lần một, ghi trạng thái changed; chạy lần hai, mong đợi không còn thay đổi nếu module dùng đúng. Sửa nội dung mong muốn, chạy lại và quan sát diff. Không dùng playbook cài package hoặc restart service trên máy chung trước khi đọc task và target inventory.

## Bài 5. Hybrid: đường mạng, identity và vận hành

Hybrid nghĩa là ứng dụng/dữ liệu chạy qua ít nhất hai môi trường có ranh giới quản trị. Một kết nối từ on-prem tới cloud có thể phụ thuộc VPN/dedicated link, route, DNS hai phía, firewall, certificate và identity. "Ping được" không chứng minh API kết nối DB qua TLS và quyền đúng; "portal báo VM running" không chứng minh người dùng truy cập được. Cần quan sát end-to-end và xác định ai chịu trách nhiệm mỗi lớp.

Khi đặt database on-prem và API trên cloud, latency đường truyền ảnh hưởng trực tiếp request. Nếu API gửi nhiều truy vấn nhỏ cho một thao tác, tổng độ trễ có thể lớn. Nếu đường liên kết mất, cần quyết định API trả lỗi, queue yêu cầu hay phục vụ đọc từ cache. Mỗi lựa chọn có tác động tới tính nhất quán và trải nghiệm; bài học này cần nối với kiến thức ứng dụng, không chỉ network.

## Bài 6. Capacity và khôi phục trong datacenter

Một host báo còn 40% CPU không đồng nghĩa cluster còn 40% capacity an toàn. Cần để chỗ cho lúc một host hỏng hoặc bảo trì. Ví dụ hai host đều dùng 70% RAM; khi một host mất, toàn bộ workload không tự chạy trên host còn lại. Khi tính HA, ghi số VM, tài nguyên được cấp, mức dùng thực, overcommit, giới hạn datastore và băng thông mạng. Đặt ngưỡng cảnh báo theo capacity **sau một sự cố**, không chỉ ngày bình thường.

Trước khi nâng cấp host, xác nhận VM có thể di chuyển, shared storage và mạng còn truy cập, host còn lại đủ capacity, backup gần đây và cửa sổ bảo trì. Sau khi di chuyển, kiểm tra endpoint ứng dụng, độ trễ, log và dữ liệu; trạng thái VM `powered on` chưa đủ. Nếu lỗi, biết mốc dừng và cách khôi phục trước khi tiếp tục host kế.

### Diễn tập trên giấy: mất một site

Site A chứa API, database và Harbor; site B có VM dự phòng. Viết rõ dữ liệu DB đồng bộ cách nào, độ trễ sao chép, ai quyết định failover, DNS/LB chuyển ra sao, registry/image có sẵn ở B không và cách ngăn A cũ nhận ghi khi trở lại. Gắn RPO/RTO với từng bước đo được. Nếu backup hàng đêm nằm cùng site A, câu "có site B" chưa chứng minh khả năng phục hồi.

## Bài 7. Kubernetes on-prem khác cluster managed ở đâu?

Với cluster tự quản on-prem, đội của bạn phải lo control plane quorum/backup, etcd, chứng chỉ, network plugin, DNS, ingress/LB, storage class, upgrade và thay node. Kubespray giúp tạo cluster nhưng không làm mất trách nhiệm vận hành sau đó. Ba control-plane VM nằm trên cùng một host vật lý vẫn có điểm lỗi đơn. Hãy ánh xạ node VM -> host -> datastore -> rack/site trước khi gọi cấu hình "HA".

Deployment tăng replicas từ 2 lên 4, hai Pod mới `ImagePullBackOff` khi Harbor lỗi. Kiểm tra pod events, DNS tới registry, TLS/cert, credential pull, quota và trạng thái Harbor. Tạm dừng rollout và giữ Pod cũ phục vụ; không xóa chúng để "thử lại" khi chưa pull được image. Sau khôi phục, xác nhận bốn Pod đúng digest và Service có endpoint.

## Case study có lời giải: VM khỏe, ứng dụng không ghi được

**Bối cảnh:** API trên hai VM đều trả `/health` 200. Từ 14:05, `POST /notes` trả 500. Đồng thời dashboard storage báo datastore latency tăng mạnh, một job backup VM vừa bắt đầu. **Không kết luận ngay** backup là nguyên nhân: đó là tương quan thời gian. Thu một request ID, kiểm tra application log và DB error/slow query, đo latency I/O ở VM DB và datastore, rồi so với baseline trước 14:05. Nếu log cho thấy SQLite/MySQL timeout khi ghi và I/O wait cùng tăng, giả thuyết storage bottleneck mạnh hơn. Nếu app log báo `permission denied` sau deploy, backup có thể chỉ là trùng thời điểm.

**Giảm tác động:** nếu chính sách cho phép, tạm dừng job backup lab hoặc giảm tải nó; không tắt backup production tùy tiện. Xác nhận latency và error rate trở lại, ghi khung thời gian dữ liệu có thể bị ảnh hưởng. **Sửa lâu dài:** đặt lịch backup phù hợp, giới hạn I/O, capacity planning, và kiểm tra backup vẫn hoàn tất. Trong phỏng vấn, nêu bằng chứng nào sẽ khiến bạn đổi giả thuyết.

### Cổng năng lực

Bạn tự vẽ được VM/host/datastore/network và failure domain, phân biệt block/file/object, giải thích Harbor/Vault/Ansible trong chuỗi phát hành, lập kế hoạch chẩn đoán lỗi hybrid theo lớp. Nếu chưa có môi trường doanh nghiệp, ghi rõ "đã thiết kế và lab mô phỏng", không ghi "đã vận hành vSphere production" trong CV.

## Nguồn chính thức

- VMware vSphere documentation: https://techdocs.broadcom.com/us/en/vmware-cis/vsphere.html
- Ceph documentation: https://docs.ceph.com/en/latest/
- MinIO concepts: https://min.io/docs/minio/linux/operations/concepts.html
- Harbor documentation: https://goharbor.io/docs/main/
- Vault documentation: https://developer.hashicorp.com/vault/docs
- Ansible getting started: https://docs.ansible.com/projects/ansible/latest/getting_started/index.html
