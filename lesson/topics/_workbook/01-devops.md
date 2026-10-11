## Một tuần làm việc giả định của DevOps Engineer

Thứ hai, đội sản phẩm muốn release tính năng lọc note. Bạn đọc yêu cầu, xác định app/DB/edge có gì đổi, yêu cầu test và rollback. Thứ ba, bạn giúp developer thêm integration test và image build có digest; không tự viết thay toàn bộ feature. Thứ tư, staging phát hiện query chậm khi dữ liệu lớn; bạn cùng developer xem query plan và thêm index có đo trước/sau. Thứ năm, production deploy theo gate, theo dõi SLI/error rate và giữ khả năng giảm tác động. Thứ sáu, alert báo queue backlog tăng; bạn điều tra consumer, DB, recent deploy, ghi runbook và cải tiến pipeline. Công việc là nối con người, mã nguồn và vận hành bằng bằng chứng, không chỉ “cài tool”.

### Toil và tự động hóa đáng làm

Nếu mỗi tuần bạn phải SSH vào 20 host để sửa cùng file Nginx, đó là ứng viên cho Ansible/IaC; nhưng trước khi tự động hóa, cần xác định file owner, cấu hình đúng, thứ tự rollout và smoke test. Nếu mỗi sáng bạn copy metric vào báo cáo, có thể tự động query/visualization. Nếu mỗi incident yêu cầu một quyết định rủi ro mới, không thể biến thành script một dòng; trước tiên viết tiêu chí/gate. Tự động hóa tốt giảm thao tác tay lặp lại và tăng khả năng kiểm tra, chứ không chỉ tăng tốc thay đổi sai.

## Bài tập đánh giá một hệ thống “DevOps”

Hệ thống A deploy 20 lần/ngày qua script, nhưng không có test, release ID, rollback hoặc alert. Hệ thống B deploy 2 lần/tuần, mỗi bản có test/approval, digest, smoke, SLO và restore drill. Bạn không thể kết luận A tốt hơn vì nhanh, cũng không thể kết luận B tối ưu vì chậm. Hỏi thêm lead time thực, change failure rate, time to restore, độ phức tạp thay đổi và tác động người dùng. Nếu B có manual gate mất 5 ngày mà không giảm rủi ro, cần cải tiến gate. Nếu A có 20 deploy nhỏ với blast radius thấp và phục hồi nhanh, có thể rất tốt sau khi bổ sung bằng chứng/quan sát. Dữ liệu dẫn quyết định, không phải nhãn “CI/CD hoàn chỉnh”.

**Câu hỏi phỏng vấn có lời giải:** “Bạn sẽ bắt đầu cải thiện delivery ở công ty mới thế nào?” Trước hết vẽ luồng hiện tại và đo điểm nghẽn/lỗi, chọn một dịch vụ nhỏ có owner, thêm versioned artifact, test có giá trị, deployment record và smoke/rollback, rồi mở rộng. Không khởi đầu bằng việc thay mọi tool hoặc chuyển ngay toàn công ty sang Kubernetes.
