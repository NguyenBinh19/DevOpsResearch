## State là sổ cái ánh xạ, không phải bản sao mã nguồn

Terraform có ba thứ: **configuration** mô tả mong muốn, **state** ánh xạ resource address tới ID/thông tin bên provider, và **hạ tầng thật** ở API cloud/on-prem. Khi bạn đổi HCL, Terraform dùng state và đọc API để tính plan. Nếu xóa file resource khỏi code, plan có thể đề nghị destroy object đang được state quản lý. Nếu một người sửa trực tiếp ở portal, plan có thể phát hiện drift; nhưng các thuộc tính do provider không đọc được hoặc bỏ qua có thể không xuất hiện theo cách bạn kỳ vọng. State chứa dữ liệu nhạy cảm tùy resource, vì vậy không commit vào Git và cần quyền truy cập, encryption/backup phù hợp.

**Resource address** như `module.network.azurerm_subnet.app` là danh tính logic trong state. Đổi tên block không có nghĩa muốn xóa subnet thật; nếu không chuyển state/moved block đúng cách, plan có thể đề nghị destroy/create. Import đưa object có sẵn vào quản lý nhưng không tự viết cấu hình đầy đủ hay bảo đảm thay đổi kế tiếp an toàn. Trước khi áp dụng cho resource production, review plan và ràng buộc dữ liệu/phụ thuộc.

### Đọc plan theo tác động, không theo số dòng

`+` là create, `~` update, `-` destroy, `-/+` replacement. Một plan “1 to add, 1 to destroy” có thể là thay VM tạm ít rủi ro hoặc thay database chứa dữ liệu; con số không cho biết mức độ. Với mỗi replacement hỏi: vì sao ForceNew, dữ liệu/địa chỉ IP có đổi không, downtime bao lâu, dependency nào theo sau, backup đã được restore thử chưa? `terraform plan -out=...` lưu kế hoạch cụ thể để apply lại, nhưng saved plan cũng có thể chứa thông tin nhạy cảm và chịu ảnh hưởng thay đổi ngoài luồng; bảo vệ như artifact nhạy cảm. Không tự động `apply -auto-approve` ở production khi chưa có review chính sách phù hợp.

## Lab review không tốn cloud

**Điều kiện:** Terraform CLI đã cài, dùng thư mục `lesson/labs/terraform-local` riêng; lab mẫu hiện có cấu hình local. Đọc `main.tf` và dự đoán resource/output. Chạy `terraform init`, `terraform fmt -check`, `terraform validate`, `terraform plan`. **Kết quả dự kiến:** init tải provider/module nếu mạng cho phép; validate kiểm tra cấu trúc; plan hiển thị thay đổi dự kiến, chưa tạo gì. Ghi version CLI/provider và thông báo thực. Sau khi hiểu plan, `terraform apply` **chỉ trong lab local** và xác nhận object/output. Chạy plan lần nữa: nếu cấu hình và thực tế ổn định, dự kiến không có thay đổi. Đó là một kiểm tra idempotency, không phải chứng minh mọi provider luôn không drift.

Thay một thuộc tính vô hại trong lab, chạy plan, đọc trước/sau, rồi apply. Sau đó chỉnh object bên ngoài Terraform nếu provider local cho phép để tạo drift, hoặc mô phỏng bằng cách thay file được quản lý; chạy plan và giải thích hướng Terraform muốn reconcile. Dọn bằng `terraform destroy` **chỉ khi cwd và state đúng thư mục lab**; đọc plan destroy trước khi chấp thuận. Đừng chạy trên backend/cloud chưa kiểm tra. Giữ bản ghi plan đã làm sạch secret và giải thích tại sao từng thao tác là create/update/delete.

## Cộng tác: backend, lock và pipeline

Local state phù hợp học một mình nhưng dễ mất và không hỗ trợ nhiều người cùng apply. Remote backend cần quyền tối thiểu, versioning/backup, encryption và locking nếu backend hỗ trợ. Lock ngăn hai writer đồng thời làm hỏng state. Khi thấy lock bị giữ, xác minh ai đang chạy và run nào còn sống; không dùng `-lock=false` hoặc force-unlock để “chạy cho xong”. Tài liệu HashiCorp chỉ cho force-unlock khi xử lý **lock của chính mình** sau khi unlock tự động thất bại; [xem hướng dẫn state locking](https://developer.hashicorp.com/terraform/language/state/locking).

Pipeline Terraform có bước plan trên PR, reviewer xem impact và policy, apply từ revision/plan được duyệt với identity phù hợp. Việc plan ở một thời điểm và apply nhiều ngày sau có thể gặp thay đổi thực tế; cần refresh/kiểm tra lại theo quy trình. Tách state theo phạm vi thay đổi/failure domain và quyền sở hữu, nhưng đừng chia cực nhỏ khiến dependency qua state khó quản lý. Output dùng để nối module/hệ thống, tránh đưa secret qua output công khai.

### Terraform, Bicep, Ansible và Helm

Terraform/Bicep/ARM thường tạo cloud resources; Ansible cấu hình host hoặc chạy nhiệm vụ; Helm đóng gói manifest Kubernetes. Ranh giới có thể chồng lấp nhưng một resource nên có owner rõ. Nếu Terraform tạo Helm release rồi Argo CD cũng quản lý cùng release, hai controller tranh desired state. Chọn một owner cho từng lớp. Với Azure enterprise, Bicep đi sát Azure Resource Manager; Terraform hữu ích khi đội dùng nhiều provider hoặc module chung. So theo yêu cầu review, state, quyền và kỹ năng đội chứ không có công cụ thắng tuyệt đối.

**Ca có lời giải:** plan đề nghị xóa database sau khi bạn đổi tên module. Đừng apply. So địa chỉ cũ/mới, state binding và `moved`/state move phù hợp; backup và kiểm tra dependency. **Ca khác:** plan báo no changes nhưng app lỗi; Terraform chỉ mô tả hạ tầng được quản lý, không chứng minh DNS, dữ liệu hoặc app đúng. Nguồn: [Terraform state](https://developer.hashicorp.com/terraform/language/state), [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan).
