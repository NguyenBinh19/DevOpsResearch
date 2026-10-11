## Reliability là lời hứa đo được

“Hệ thống HA” không đủ để điều hành. Hãy xác định dịch vụ nào, người dùng nào, SLI nào và cửa sổ nào. Một API có ba Pod nhưng DB một điểm hỏng có thể vẫn vi phạm SLO. SRE dùng SLO/error budget để thảo luận rủi ro release: khi còn nhiều budget, đội có thể chấp nhận thử nghiệm có guardrail; khi burn nhanh, ưu tiên ổn định và giảm tác động. Đây là chính sách ra quyết định, không phải con số để phạt đội.

RTO là thời gian phục hồi mục tiêu sau thảm họa; RPO là mức dữ liệu có thể mất tối đa tính theo thời gian. Snapshot mỗi ngày có thể tạo RPO tới gần 24 giờ nếu không có log/replication bổ sung. Có replica không đồng nghĩa có backup: lỗi xóa dữ liệu hoặc ransomware có thể lan sang replica. Có backup không đồng nghĩa phục hồi trong RTO: cần đo thời gian lấy bản sao, khôi phục, kiểm tra dữ liệu, chuyển DNS/traffic và mở lại dịch vụ. “Restore thành công” phải bao gồm kiểm tra ứng dụng đọc/ghi dữ liệu đúng.

## Một incident từ phút 0 đến postmortem

**Tình huống:** lúc 10:02 alert 5xx của Notes API tăng lên 8%; deploy mới lúc 09:58. Người trực ca xác nhận tác động bằng synthetic request và dashboard, lập incident, ghi timeline. Chỉ định incident commander điều phối, người điều tra kỹ thuật, người truyền thông khi quy mô đủ lớn. Người điều tra tìm bằng chứng: revision, route lỗi, DB status, log/trace; người điều phối quyết định giảm tác động. Không để cả đội cùng sửa production mà không ai ghi thay đổi.

**10:07:** giả thuyết migration mới làm query lỗi. Nếu có bằng chứng rõ và rollback app còn tương thích schema, rollback theo runbook; nếu không, tạm tắt feature/route hoặc roll-forward hotfix. **10:15:** theo dõi 5xx, p95, backlog và request thành công thực, không đóng incident ngay khi Pod xanh. **10:30:** cập nhật trạng thái cho stakeholder bằng dữ kiện: ảnh hưởng, hành động, thời gian cập nhật tiếp theo; tránh hứa ETA không có cơ sở. Sau phục hồi, viết postmortem không đổ lỗi cá nhân: timeline, nguyên nhân gần/gốc, yếu tố phát hiện muộn, điều gì đã làm tốt, action có owner/deadline/kiểm chứng.

### Runbook ngắn cho lỗi DB connection exhaustion

**Trigger:** API 5xx và timeout tăng; DB connection gần trần. **Xác nhận:** dashboard theo route, pool active/idle, DB connection count, query slow/lock, revision gần nhất. **Giảm tác động:** dừng rollout mới, giảm traffic tính năng gây bão hoặc rollback nếu tương thích; tránh tăng max connections vô hạn vì DB có giới hạn bộ nhớ. **Phục hồi:** kiểm tra request mới, p95, connection và queue sau hành động. **Leo thang:** gọi DB owner khi nghi replication/lock; lưu log/trace trước khi chúng hết retention. **Sau sự cố:** test load, pool timeout/retry budget, circuit breaker và alert sớm. Runbook phải được tập, không chỉ viết.

## Bài tập tính toán để không nhầm SLO

Trong 30 ngày có 2.000.000 request hợp lệ, SLO good request 99,95%. Budget là 0,05% x 2.000.000 = 1.000 request không tốt. Nếu một sự cố 12 phút gây 700 request lỗi, còn 300 request budget theo mô hình đơn giản; không thể nói “12 phút chỉ chiếm ít thời gian” để bỏ qua. Nếu traffic tăng gấp đôi, số request lỗi cho phép theo tỷ lệ cũng đổi. Nếu SLI đo availability bằng phút, phép tính khác; luôn nêu đơn vị và mẫu số.

Một burn rate 10x nghĩa tiêu budget nhanh gấp 10 so với tốc độ cho phép trung bình, không phải cứ 10% traffic lỗi. Thiết kế nhiều cửa sổ để nhận cả lỗi lớn nhanh và lỗi nhỏ kéo dài; không page vì một điểm dữ liệu đơn lẻ khi hệ thống nhiễu. Google SRE Workbook có [hướng dẫn alert trên SLO](https://sre.google/workbook/alerting-on-slos/) và [incident response](https://sre.google/workbook/incident-response/) để đào sâu.

## Failure domain và diễn tập

“Ba VM, ba replica” cần hỏi ba VM ở host/rack/zone nào; storage, DB, load balancer, identity và DNS có chung điểm hỏng không. Chọn một lỗi cụ thể để game day trên môi trường thử: mất một node, mất DB primary, DNS private trả IP sai hoặc registry tạm không truy cập được. Trước khi diễn tập, xác định phạm vi, cách dừng, tín hiệu dự kiến và người quan sát. Trong diễn tập, ghi thời gian phát hiện, quyết định, hành động, phục hồi và khoảng trống runbook. Không chủ động phá production chỉ để “thử HA” khi chưa có kế hoạch/ủy quyền.

**Câu hỏi có lời giải:** backup hằng ngày có RPO 1 giờ không? Không nếu không có cơ chế bổ sung và restore chứng minh được. **HPA có làm hệ thống HA?** Nó tăng Pod theo metric nhưng không sửa DB hay failure domain chung. **Postmortem có kết luận “người triển khai quên kiểm tra”?** Chưa đủ; cần chỉ ra vì sao gate, review, thiết kế và tín hiệu cho phép lỗi lọt qua, rồi đặt action kiểm chứng được.
