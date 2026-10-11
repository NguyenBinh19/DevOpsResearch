## Plan review có lời giải: thay subnet kéo theo database

PR đổi CIDR subnet và `terraform plan` hiện một subnet `-/+`, hai NIC update và một database private endpoint replacement. Dù tác giả nói “chỉ đổi mạng”, tác động có thể cắt kết nối DB. Reviewer cần xác định force-replacement reason, IP/DNS, route, downtime, data plane, dependency và rollback; xem môi trường nào dùng subnet này và có tài nguyên ngoài state hay không. Nếu DB endpoint được recreate, DNS TTL/cache và firewall rule có thể làm downtime lâu hơn apply. Không approve theo số dòng HCL nhỏ.

**Phương án:** thiết kế subnet mới song song nếu provider/kiến trúc cho phép, chuyển workload theo batch, cập nhật DNS/route, smoke test, rồi xóa cũ sau thời gian quan sát. IaC giúp khai báo cả trạng thái trung gian; đôi khi cần nhiều PR/apply. Một `apply` lớn “atomic” trên giấy thực ra là nhiều API call, có thể fail giữa chừng; state và hạ tầng thực cần được kiểm tra sau lỗi.

### Sensitive output và state

`variable "password" { sensitive = true }` có thể che hiển thị trong CLI theo một số ngữ cảnh, nhưng state vẫn có thể chứa secret. Vì vậy bảo vệ backend, quyền đọc state, plan artifact, log CI và backup; không gửi `terraform.tfstate` cho người khác để “debug nhanh”. Nếu secret rotation làm state/plan đổi, cân nhắc tham chiếu secret manager phù hợp thay vì lưu value rõ trong resource khi provider cho phép.

**Câu hỏi:** vì sao `terraform apply` báo thành công mà app chết? IaC xác nhận API hạ tầng theo khai báo, không chứng minh request path/DB/schema. **Câu hỏi:** có nên force-unlock khi pipeline khác đang chạy? Không; hai writer có thể làm hỏng state. Nguồn: [Terraform state](https://developer.hashicorp.com/terraform/language/state).
