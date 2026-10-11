## Mental model: configuration, state, real infrastructure

Terraform có ba hình ảnh cần so sánh: mã cấu hình mô tả mong muốn, state lưu mapping resource/thuộc tính mà Terraform biết, và hạ tầng thực tế qua provider API. `plan` tính chênh lệch giữa ba hình ảnh; `apply` thực hiện và cập nhật state. Nếu ai sửa resource bằng portal, lần plan sau có thể phát hiện drift. Nếu state mất hoặc bị sửa tay, Terraform có thể tưởng resource chưa tồn tại và định tạo lại. State có thể chứa dữ liệu nhạy cảm; bảo vệ bằng quyền, mã hóa, versioning và backend/locking phù hợp.

Đọc plan theo từng resource và loại hành động: create, update in-place, replace, destroy. Với `replace`, hỏi vì sao thuộc tính buộc thay mới, downtime và dữ liệu sẽ đi đâu. Một plan "2 to add, 0 to change" chưa đủ; resource mới có thể là public IP hoặc rule mở rộng. Đặc biệt tránh tự động apply một plan chưa review vào production. Plan dựa trên trạng thái tại thời điểm tạo; nếu hạ tầng đổi sau đó, cần lập plan lại hoặc dùng quy trình saved plan có kiểm soát.

## Lab providerless và bằng chứng idempotency

Trong `lesson/labs/terraform-local`, chạy `terraform init`, `terraform fmt -check`, `terraform validate`, `terraform plan`. Đọc `main.tf`: resource nào có địa chỉ nào, input/output là gì. Apply trên lab local sau khi xem plan; chạy plan lần hai, mong đợi không có thay đổi. Sửa một giá trị trong cấu hình, plan lại và dự đoán action. Sau đó `terraform destroy` chỉ sau khi xác nhận đang ở đúng thư mục/state lab. Ghi output plan trước/sau và điều gì khiến bạn tin lần hai idempotent. Lab providerless dạy workflow/state, không chứng minh bạn đã cấp cloud resource thật.

## Backend, locking và cộng tác

Local state đơn giản cho một người lab, nhưng đội cần backend chia sẻ có quyền/phiên bản và locking hoặc cơ chế tuần tự tương ứng để hai người không apply đồng thời lên cùng state. Tách state theo vòng đời/ranh giới sở hữu phù hợp; một state khổng lồ khiến plan chậm và blast radius lớn, quá nhiều state nhỏ làm dependency khó quản lý. Module giúp tái dùng cấu hình, nhưng module trừu tượng quá mức có thể giấu resource thật khỏi người review. Trong PR, hiển thị plan, ai review, ai apply, state nào bị tác động và cách revert.

Nếu deploy fail giữa chừng, đừng tự xóa state entry để "chạy lại". Đầu tiên xem resource thật đã tạo gì, state ghi gì, lỗi provider nào, rồi chọn import/move/taint/recreate phù hợp với tài liệu phiên bản. Một thao tác state sai có thể gây destroy ngoài ý muốn ở lần apply sau. Quyền cloud của pipeline Terraform nên giới hạn theo môi trường; không dùng tài khoản Owner toàn tổ chức cho một lab.

## Terraform với Ansible và Helm

Terraform tạo network/VM/managed cluster; Ansible cấu hình OS/package trên máy; Helm triển khai manifest ứng dụng trong Kubernetes. Đây là một ranh giới thường gặp, không phải luật cứng. Quan trọng là một tài nguyên/field có một owner rõ. Nếu Terraform và Helm cùng quản lý một namespace hoặc Helm release, hoặc người vận hành sửa tay thường xuyên, drift/chuỗi trách nhiệm khó hiểu. Lập bảng "ai tạo, ai sửa, ai xóa, ai backup" cho network, cluster, namespace, app, DB trước khi tự động hóa.

### Câu hỏi phỏng vấn có lời giải

"Terraform plan báo sẽ thay DB instance, bạn làm gì?" Trả lời: dừng apply; đọc thuộc tính buộc replace; đánh giá dữ liệu/downtime, backup và restore; xem có cách thay đổi in-place hoặc migration; kiểm tra đúng workspace/backend và drift; đưa plan cho owner review; chỉ thực hiện sau khi có cửa sổ và rollback/runbook. Không trả lời đơn giản "apply vì IaC luôn đúng".
