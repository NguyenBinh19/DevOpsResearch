## Từ VM tới failure domain: nhìn xuyên qua lớp ảo hóa

Một VM có vCPU/vRAM, vNIC và virtual disk; chúng dùng tài nguyên vật lý của host, switch/network và datastore bên dưới. Khi vSphere hiển thị VM “Powered On”, ứng dụng vẫn có thể lỗi vì DNS, storage latency, guest OS, process hoặc DB. HA của hypervisor có thể khởi động lại VM khi host hỏng theo cấu hình/điều kiện, nhưng không chứng minh ứng dụng không gián đoạn và không thay backup. vMotion/migration live giúp bảo trì host trong điều kiện tương thích, nhưng shared storage/network có thể vẫn là điểm hỏng chung. Đọc sơ đồ vật lý cùng sơ đồ VM.

**Capacity N-1** nghĩa hạ tầng còn đủ khi mất một thành phần đã định, ví dụ một host trong cluster. Giả sử 3 host, mỗi host có 64 GiB RAM dùng cho VM, tổng VM đòi 150 GiB. Khi mất một host, hai host còn 128 GiB trước overhead/reservation; không đủ theo phép cộng đơn giản. CPU overcommit có thể chấp nhận tùy workload nhưng phải đo CPU ready/latency, không coi số vCPU đã cấp là CPU vật lý miễn phí. Storage IOPS/latency và network uplink cũng cần N-1, không chỉ RAM.

### Tách ba kiểu HA

**Host HA:** VM có thể được restart/chuyển sang host khác sau lỗi. **Application HA:** nhiều instance và load balancer giữ chức năng khi một instance mất. **Data HA:** replication/failover/consistency của DB hoặc storage. Ba lớp có RTO/RPO và điều kiện khác nhau. Nếu DB một VM trên datastore duy nhất, ba API Pod trên ba VM không đạt mục tiêu chịu mất datastore. Nếu ba VM ở cùng rack, mất điện rack vẫn làm cả ba chết. Vẽ failure domain host -> rack -> power -> datastore -> network -> site.

## Bài tập thiết kế hybrid dựa trên JD

**Bối cảnh:** công ty có VMware on-prem, một cluster Kubernetes dùng kubespray, cloud để DR. Notes API và MySQL phải tiếp tục phục vụ khi một host mất; mục tiêu RPO 15 phút, RTO 2 giờ khi cả site mất. **Bước 1:** vẽ physical hosts/racks/datastore/switch và VM control plane/worker/DB/LB. **Bước 2:** xác định placement rule để replica không cùng host; kiểm tra còn capacity N-1. **Bước 3:** mô tả backup/replication dữ liệu sang site/cloud, tần suất và quyền truy cập. **Bước 4:** ghi đường DNS/routing/VPN/identity khi failover. **Bước 5:** lập một restore drill có thời gian và kiểm tra dữ liệu nghiệp vụ, không chỉ VM boot được.

**Lời giải định hướng:** ba control-plane VM trên ba host nhưng cùng datastore/power chưa chống site failure. DB replication giảm RPO nhưng lỗi xóa dữ liệu có thể nhân sang replica; cần backup độc lập. RTO 2 giờ phải tính thời gian khôi phục network, DNS, DB, secret, image registry và smoke test. Cloud DR không có giá trị nếu CIDR chồng lấp hoặc credential/backup chỉ nằm on-prem. Chi phí warm standby và diễn tập là một phần quyết định.

## Hybrid network và identity

Đường người dùng có thể vào on-prem LB, tới ingress, Service và Pod; đường DB/backup/cloud đi qua firewall, VPN/leased connection và DNS split-horizon. Ghi từng CIDR, route, NAT, MTU, DNS zone và người sở hữu. Nếu Pod on-prem gọi Azure Key Vault được từ laptop nhưng timeout từ node, thử DNS/TCP/TLS từ đúng runtime. Nếu danh tính workload tới cloud dựa trên key dài hạn trong Secret, rủi ro rotation/lộ key cao; xem giải pháp federation/identity tương ứng với môi trường và chính sách tổ chức.

## Case có lời giải: mọi VM healthy, API ghi DB chậm

Từ request ID/trace thấy thời gian ở DB tăng, CPU DB thấp. Trên guest xem I/O wait và DB slow query/lock; trên hypervisor/storage xem datastore latency, queue depth và VM khác cùng datastore. Nếu cùng lúc backup job bắt đầu trên datastore, đây là giả thuyết hợp lý nhưng phải kiểm tra thời điểm/metric. Cũng kiểm tra network RTT/loss nếu DB ở VLAN khác. Tăng vCPU API không sửa I/O storage. Sau giảm tác động, xem lịch backup/QoS/placement và capacity. Một dashboard VM “green” không thay đo ứng dụng.

**Câu hỏi:** Snapshot VM có phải backup DB nhất quán? Không mặc nhiên; cần xem quiesce, DB flush/transaction, retention và thử restore. **Câu hỏi:** vSphere HA có đáp ứng RTO 0 không? Restart VM vẫn mất thời gian và app/DB cần phục hồi; đo thực tế. **Câu hỏi:** ba Pod trên ba VM cùng host chịu được host failure? Không. Nguồn: [vSphere documentation](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere.html), [Kubernetes HA considerations](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/ha-topology/).
