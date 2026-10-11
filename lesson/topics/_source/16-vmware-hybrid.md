# VMware và hạ tầng hybrid

Tài liệu độc lập theo một chủ đề. Đọc mô hình trước, làm lab trên môi trường riêng, ghi bằng chứng và tự giải thích failure mode. Các ví dụ dựa trên ứng dụng Notes API và bốn JD đã cung cấp.

## Từ máy vật lý đến máy ảo

Một máy vật lý có CPU, RAM, đĩa và NIC. Hypervisor chia tài nguyên đó thành nhiều máy ảo (VM), mỗi VM có hệ điều hành và tiến trình riêng. Máy vật lý chạy hypervisor thường gọi là host; nhiều host hợp thành cluster. vSphere là hệ sinh thái VMware quản lý host, VM, network và storage. Ảo hóa giúp cấp máy nhanh và dùng tài nguyên linh hoạt hơn, nhưng không làm phần cứng biến mất: nếu mọi VM quan trọng cùng nằm trên một host, host hỏng vẫn gây gián đoạn lớn.

Khả năng sẵn sàng cao cần nói rõ đang chống lỗi nào. Một VM restart tự động trên host khác giúp khi host mất, nhưng thời gian khởi động và data consistency vẫn cần kiểm tra. Di chuyển VM đang chạy giữa host có thể giúp bảo trì nhưng phụ thuộc network/storage/cấu hình phù hợp. Một bản sao VM không mặc nhiên là backup; lỗi xóa dữ liệu trong guest có thể được mang theo. Khi thiết kế, vẽ các failure domain: host, rack, storage, network và site.

### Ví dụ thiết kế

Ứng dụng có hai VM chạy API, một VM database và một load balancer. Nếu API-1 hỏng, LB chuyển traffic sang API-2 nếu health check đúng. Nếu database VM hỏng, cả hai API có thể còn chạy nhưng không tạo ghi chú được. Nếu cả ba VM nằm trên cùng datastore và datastore mất, số VM không giúp. Do đó câu hỏi "có HA chưa?" phải được trả lời theo từng lớp, kèm cách thử failover và mục tiêu RTO/RPO.

### Bài tập trên giấy

Vẽ hai host H1/H2, một shared datastore, hai API VM và một DB VM. Đặt VM để giảm điểm lỗi đơn. Khoanh tròn các điểm vẫn là single point of failure. Đề xuất một phép kiểm tra để chứng minh API chuyển host hoặc traffic khi một VM mất. Ghi điều chưa thể kiểm chứng khi bạn không có vSphere lab; không biến giả định thành kinh nghiệm đã làm.

## Hybrid: đường mạng, identity và vận hành

Hybrid nghĩa là ứng dụng/dữ liệu chạy qua ít nhất hai môi trường có ranh giới quản trị. Một kết nối từ on-prem tới cloud có thể phụ thuộc VPN/dedicated link, route, DNS hai phía, firewall, certificate và identity. "Ping được" không chứng minh API kết nối DB qua TLS và quyền đúng; "portal báo VM running" không chứng minh người dùng truy cập được. Cần quan sát end-to-end và xác định ai chịu trách nhiệm mỗi lớp.

Khi đặt database on-prem và API trên cloud, latency đường truyền ảnh hưởng trực tiếp request. Nếu API gửi nhiều truy vấn nhỏ cho một thao tác, tổng độ trễ có thể lớn. Nếu đường liên kết mất, cần quyết định API trả lỗi, queue yêu cầu hay phục vụ đọc từ cache. Mỗi lựa chọn có tác động tới tính nhất quán và trải nghiệm; bài học này cần nối với kiến thức ứng dụng, không chỉ network.

## Capacity và khôi phục trong datacenter

Một host báo còn 40% CPU không đồng nghĩa cluster còn 40% capacity an toàn. Cần để chỗ cho lúc một host hỏng hoặc bảo trì. Ví dụ hai host đều dùng 70% RAM; khi một host mất, toàn bộ workload không tự chạy trên host còn lại. Khi tính HA, ghi số VM, tài nguyên được cấp, mức dùng thực, overcommit, giới hạn datastore và băng thông mạng. Đặt ngưỡng cảnh báo theo capacity **sau một sự cố**, không chỉ ngày bình thường.

Trước khi nâng cấp host, xác nhận VM có thể di chuyển, shared storage và mạng còn truy cập, host còn lại đủ capacity, backup gần đây và cửa sổ bảo trì. Sau khi di chuyển, kiểm tra endpoint ứng dụng, độ trễ, log và dữ liệu; trạng thái VM `powered on` chưa đủ. Nếu lỗi, biết mốc dừng và cách khôi phục trước khi tiếp tục host kế.

### Diễn tập trên giấy: mất một site

Site A chứa API, database và Harbor; site B có VM dự phòng. Viết rõ dữ liệu DB đồng bộ cách nào, độ trễ sao chép, ai quyết định failover, DNS/LB chuyển ra sao, registry/image có sẵn ở B không và cách ngăn A cũ nhận ghi khi trở lại. Gắn RPO/RTO với từng bước đo được. Nếu backup hàng đêm nằm cùng site A, câu "có site B" chưa chứng minh khả năng phục hồi.

## Kubernetes on-prem khác cluster managed ở đâu?

Với cluster tự quản on-prem, đội của bạn phải lo control plane quorum/backup, etcd, chứng chỉ, network plugin, DNS, ingress/LB, storage class, upgrade và thay node. Kubespray giúp tạo cluster nhưng không làm mất trách nhiệm vận hành sau đó. Ba control-plane VM nằm trên cùng một host vật lý vẫn có điểm lỗi đơn. Hãy ánh xạ node VM -> host -> datastore -> rack/site trước khi gọi cấu hình "HA".

Deployment tăng replicas từ 2 lên 4, hai Pod mới `ImagePullBackOff` khi Harbor lỗi. Kiểm tra pod events, DNS tới registry, TLS/cert, credential pull, quota và trạng thái Harbor. Tạm dừng rollout và giữ Pod cũ phục vụ; không xóa chúng để "thử lại" khi chưa pull được image. Sau khôi phục, xác nhận bốn Pod đúng digest và Service có endpoint.

## Case study có lời giải: VM khỏe, ứng dụng không ghi được

**Bối cảnh:** API trên hai VM đều trả `/health` 200. Từ 14:05, `POST /notes` trả 500. Đồng thời dashboard storage báo datastore latency tăng mạnh, một job backup VM vừa bắt đầu. **Không kết luận ngay** backup là nguyên nhân: đó là tương quan thời gian. Thu một request ID, kiểm tra application log và DB error/slow query, đo latency I/O ở VM DB và datastore, rồi so với baseline trước 14:05. Nếu log cho thấy SQLite/MySQL timeout khi ghi và I/O wait cùng tăng, giả thuyết storage bottleneck mạnh hơn. Nếu app log báo `permission denied` sau deploy, backup có thể chỉ là trùng thời điểm.

**Giảm tác động:** nếu chính sách cho phép, tạm dừng job backup lab hoặc giảm tải nó; không tắt backup production tùy tiện. Xác nhận latency và error rate trở lại, ghi khung thời gian dữ liệu có thể bị ảnh hưởng. **Sửa lâu dài:** đặt lịch backup phù hợp, giới hạn I/O, capacity planning, và kiểm tra backup vẫn hoàn tất. Trong phỏng vấn, nêu bằng chứng nào sẽ khiến bạn đổi giả thuyết.

### Cổng năng lực

Bạn tự vẽ được VM/host/datastore/network và failure domain, phân biệt block/file/object, giải thích Harbor/Vault/Ansible trong chuỗi phát hành, lập kế hoạch chẩn đoán lỗi hybrid theo lớp. Nếu chưa có môi trường doanh nghiệp, ghi rõ "đã thiết kế và lab mô phỏng", không ghi "đã vận hành vSphere production" trong CV.

## Thiết kế HA theo failure domain

VMware vSphere quản lý VM trên host, network ảo và datastore. Một cụm có hai host nhưng cùng một switch và một datastore vẫn có điểm lỗi chung. Trước khi nói "HA", lập bảng cho từng thành phần: host mất thì ai khởi động VM, storage mất thì dữ liệu ở đâu, network mất thì client đổi đường thế nào, site mất thì ai quyết định DR. vSphere HA có thể restart VM trên host còn lại, nhưng ứng dụng vẫn mất thời gian khởi động và kiểm tra dữ liệu. Live migration phục vụ bảo trì theo điều kiện hạ tầng; nó không thay backup.

### Bài tập capacity N-1

Host A và B mỗi host có 64 GiB RAM; VM trên mỗi host hiện dùng 45 GiB thực. Nếu một host mất, host còn lại không chứa được tổng 90 GiB mà không giảm tải hoặc đổi placement. Dù dashboard bình thường còn 19 GiB mỗi host, cluster không đạt mục tiêu chịu mất một host ở tải hiện tại. Tính lại với RAM overhead và VM quan trọng trước; cân nhắc thêm host, giảm overcommit/tải hoặc ưu tiên workload. Làm phép tính tương tự cho storage IOPS và network bandwidth; không chỉ CPU.

## Hybrid path và quyền sở hữu

API cloud gọi database on-prem qua private link/VPN. Đường đi phụ thuộc DNS, route, firewall, certificate, identity và DB grants. Chia owner: đội cloud quản lý VNet/route một phía, đội network quản lý tunnel/firewall, đội DB quản lý listener/user, đội app quản lý timeout/retry. Khi lỗi, một bản đồ owner tiết kiệm thời gian hơn câu "mạng có vấn đề". Kiểm tra từ đúng runtime cloud, không chỉ từ laptop trong văn phòng. Một `ping` thành công chưa chứng minh TLS/DB auth.

### Case: mất link 10 phút

Nếu API ghi đồng bộ vào DB on-prem, request sẽ timeout; retry không giới hạn có thể làm link/DB quá tải khi hồi phục. Chọn chính sách rõ: trả lỗi sớm và cho người dùng thử lại, đưa yêu cầu vào queue durable, hoặc chỉ cho đọc dữ liệu cache có nhãn stale. Mỗi chính sách cần nêu tính nhất quán, trải nghiệm và cách đối soát sau khi link trở lại. Đặt timeout ở app/ngateway hợp lý, circuit breaker theo nhu cầu, metric số request lỗi và backlog. Trong phỏng vấn, không hứa "hybrid luôn sẵn sàng" nếu chưa có đường mạng và data replication dự phòng được kiểm chứng.

## Thay đổi host an toàn

Trước maintenance: inventory VM, dependency, placement, backup, capacity host còn lại và khả năng rollback. Trong maintenance: di chuyển theo batch, health check ứng dụng, theo dõi storage latency và network. Sau maintenance: xác nhận workload về trạng thái mong muốn, lỗi/độ trễ và backup job. Ghi lại VM nào có thể di chuyển, VM nào cần downtime và điều kiện dừng. Mô phỏng trên giấy hoặc lab VM cá nhân chỉ chứng minh quy trình tư duy; vận hành vSphere production cần môi trường được giao quyền.

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

## Vận hành VMware khác nhìn VM “xanh”

Khi một ứng dụng chậm, đặt metric theo lớp: response p95 ở app, DB query time, guest CPU/iowait, hypervisor CPU ready/memory pressure, datastore latency/queue, network packet loss. CPU của VM 30% không chứng minh host còn CPU nếu vCPU đang chờ lịch chạy; datastore dùng chung có thể quá tải trong khi từng VM có ít I/O. Cần đối chiếu mốc thời gian với backup, snapshot, vMotion, host maintenance, failover và deploy. Một sự cố có thể do nhiều thay đổi trùng lúc; giữ giả thuyết và bằng chứng, không quy tội bước gần nhất mặc định.

### Snapshot có giới hạn

Snapshot VM tiện cho thay đổi ngắn hạn và rollback một số trạng thái VM, nhưng có chi phí storage/performance và có thể không cung cấp backup nhất quán/độc lập. Snapshot chain dài không nên là chiến lược DR. Với DB, cần phối hợp backup engine và ứng dụng để xác định điểm phục hồi. Nếu khôi phục snapshot VM cũ của DB trong khi app/queue vẫn ở trạng thái mới, dữ liệu có thể lệch; restore plan cần xét toàn giao dịch xuyên dịch vụ.

## Bảng quyết định khi bảo trì một host

Trước bảo trì, xác nhận cluster capacity N-1, placement VM control plane/worker/DB, datastore/network redundancy, backup gần nhất và alert. Di chuyển/evict workload theo cách hỗ trợ, theo dõi PodDisruptionBudget và số endpoint Ready. Nếu tất cả VM quan trọng đang ở host khác nhưng datastore/switch chung sắp bảo trì, rủi ro vẫn tồn tại. Trong bảo trì, theo dõi latency và error rate người dùng; sau đó xác nhận VM/Pod/DB/LB trở về topology mong muốn. Một checklist chỉ đánh dấu “vMotion done” chưa đủ.

## Bài tính placement

Có 4 host, mỗi host 32 vCPU và 128 GiB RAM hữu dụng. Workload VM tổng cộng 90 vCPU vảo và 330 GiB RAM reservation. Mất một host còn 96 vCPU và 384 GiB RAM về mặt cộng đơn giản, có vẻ đủ, nhưng CPU overcommit/NUMA, overhead, anti-affinity, storage IOPS và network uplink có thể làm lịch chạy không khả thi. Nếu DB VM cần 160 GiB RAM trên một host thì dù tổng cluster đủ, không host đơn nào đặt được DB. Capacity phải xét **kích thước lớn nhất của một VM**, ràng buộc placement và peak load, không chỉ tổng.

**Câu hỏi phỏng vấn:** mất một host, VM được restart sau 5 phút, ứng dụng cần 2 phút recovery, DNS/LB 1 phút, tổng RTO có thể hơn 8 phút chưa kể phát hiện; nói “HA” mà không đo là thiếu. **DR site cloud có backup nhưng không có VPN/DNS/identity sẵn:** restore dữ liệu xong app vẫn chưa phục vụ; kiểm thử toàn đường. Nguồn: [vSphere documentation](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere.html).

## Tự đánh giá

1. Giải thích mô hình bằng lời của bạn, không dựa vào tên công cụ.
2. Làm lab và lưu kết quả mong đợi cùng kết quả thực tế.
3. Tạo một lỗi có kiểm soát, dùng bằng chứng để khoanh vùng và phục hồi.
4. Trả lời một câu hỏi thiết kế: tại sao chọn phương án này, tradeoff và giới hạn là gì?

## Nguồn chính thức và đọc thêm

- https://techdocs.broadcom.com/us/en/vmware-cis/vsphere.html
