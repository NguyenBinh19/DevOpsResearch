## Vận hành VMware khác nhìn VM “xanh”

Khi một ứng dụng chậm, đặt metric theo lớp: response p95 ở app, DB query time, guest CPU/iowait, hypervisor CPU ready/memory pressure, datastore latency/queue, network packet loss. CPU của VM 30% không chứng minh host còn CPU nếu vCPU đang chờ lịch chạy; datastore dùng chung có thể quá tải trong khi từng VM có ít I/O. Cần đối chiếu mốc thời gian với backup, snapshot, vMotion, host maintenance, failover và deploy. Một sự cố có thể do nhiều thay đổi trùng lúc; giữ giả thuyết và bằng chứng, không quy tội bước gần nhất mặc định.

### Snapshot có giới hạn

Snapshot VM tiện cho thay đổi ngắn hạn và rollback một số trạng thái VM, nhưng có chi phí storage/performance và có thể không cung cấp backup nhất quán/độc lập. Snapshot chain dài không nên là chiến lược DR. Với DB, cần phối hợp backup engine và ứng dụng để xác định điểm phục hồi. Nếu khôi phục snapshot VM cũ của DB trong khi app/queue vẫn ở trạng thái mới, dữ liệu có thể lệch; restore plan cần xét toàn giao dịch xuyên dịch vụ.

## Bảng quyết định khi bảo trì một host

Trước bảo trì, xác nhận cluster capacity N-1, placement VM control plane/worker/DB, datastore/network redundancy, backup gần nhất và alert. Di chuyển/evict workload theo cách hỗ trợ, theo dõi PodDisruptionBudget và số endpoint Ready. Nếu tất cả VM quan trọng đang ở host khác nhưng datastore/switch chung sắp bảo trì, rủi ro vẫn tồn tại. Trong bảo trì, theo dõi latency và error rate người dùng; sau đó xác nhận VM/Pod/DB/LB trở về topology mong muốn. Một checklist chỉ đánh dấu “vMotion done” chưa đủ.

## Bài tính placement

Có 4 host, mỗi host 32 vCPU và 128 GiB RAM hữu dụng. Workload VM tổng cộng 90 vCPU vảo và 330 GiB RAM reservation. Mất một host còn 96 vCPU và 384 GiB RAM về mặt cộng đơn giản, có vẻ đủ, nhưng CPU overcommit/NUMA, overhead, anti-affinity, storage IOPS và network uplink có thể làm lịch chạy không khả thi. Nếu DB VM cần 160 GiB RAM trên một host thì dù tổng cluster đủ, không host đơn nào đặt được DB. Capacity phải xét **kích thước lớn nhất của một VM**, ràng buộc placement và peak load, không chỉ tổng.

**Câu hỏi phỏng vấn:** mất một host, VM được restart sau 5 phút, ứng dụng cần 2 phút recovery, DNS/LB 1 phút, tổng RTO có thể hơn 8 phút chưa kể phát hiện; nói “HA” mà không đo là thiếu. **DR site cloud có backup nhưng không có VPN/DNS/identity sẵn:** restore dữ liệu xong app vẫn chưa phục vụ; kiểm thử toàn đường. Nguồn: [vSphere documentation](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere.html).
