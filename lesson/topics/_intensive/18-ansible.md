## Ansible là vòng lặp cấu hình qua inventory

Inventory định nghĩa host/group và biến; playbook mô tả task mong muốn; controller kết nối host qua SSH/WinRM tùy loại và module thực hiện thay đổi. Một task `package state=present` có thể kiểm tra gói đã cài rồi không đổi gì; một task `shell: apt install ...` tùy tiện có thể khó idempotent và khó hiểu changed status. Playbook tốt cho phép chạy lại để sửa drift mà không tạo tác động bất ngờ. Nhưng idempotency là thuộc tính của task/module/thực tế, không tự động có chỉ vì file viết bằng YAML.

Thứ tự biến trong Ansible có nhiều tầng và có thể phức tạp; khi một giá trị sai, ghi nguồn của biến (inventory, group_vars, host_vars, role defaults, extra vars...) thay vì sửa bừa ở nơi đầu tiên thấy. Template Jinja2 có thể tạo config khác nhau theo host; render output và so diff trước khi restart service. Handler chỉ chạy khi task notify thay đổi theo semantics của module; nếu task luôn `changed`, service có thể restart mỗi run. Với hệ thống production, `serial` giới hạn số host thay đồng thời; health check trước/sau từng batch và đường rollback quan trọng hơn chạy nhanh.

## Lab local an toàn: tạo file cấu hình có kiểm chứng

**Điều kiện:** Ansible trên Linux/WSL hoặc VM lab; dùng inventory chỉ trỏ `localhost ansible_connection=local`, không trỏ server công ty. Tạo playbook gồm task `file` tạo thư mục lab trong home, `copy` ghi file `app.conf` có `PORT=8765`, và `debug` in đường file (không in secret). Chạy `ansible-playbook -i inventory.ini playbook.yml --check --diff`, rồi chạy thật. **Kết quả dự kiến:** check mode báo dự kiến changed nếu module hỗ trợ, run thật tạo file. Chạy lần hai: các task idempotent nên `changed=0` trong điều kiện ổn định. Nếu không, điều tra task nào luôn đổi và vì sao.

Sửa port thành 8766, chạy `--check --diff` để thấy trước/sau, rồi apply và kiểm tra nội dung. Nếu file config là secret, **không dùng diff/log công khai**; dùng Vault/secret manager và `no_log` theo phạm vi cần thiết. Dọn đúng thư mục lab của bạn sau khi xác nhận. Không thử playbook với `hosts: all` khi inventory mặc định có máy khác; luôn in `--list-hosts` trước một run có tác động.

### Giới hạn check mode

Ansible docs nói check mode là mô phỏng; module không hỗ trợ có thể bỏ qua hoặc không báo đầy đủ. Task phụ thuộc output của task trước có thể cho kết quả khác run thật. Vì thế `--check --diff` là guardrail, không là bằng chứng duy nhất. Kiểm chứng sau apply bằng state/service/HTTP request thật. Một config file hợp lệ về text vẫn có thể làm Nginx không reload được; thêm validate command phù hợp trước khi thay file và handler reload chỉ khi cần.

## Ansible với Terraform và kubespray

Terraform phù hợp quản lý tài nguyên cloud/VM và state; Ansible phù hợp cấu hình OS/service trên host; kubespray dùng Ansible để triển khai cluster Kubernetes theo inventory/role và phiên bản dự án. Nếu Terraform và Ansible cùng quản lý một thuộc tính (ví dụ cloud-init user và Ansible user file), xác định owner để tránh ghi đè. Với kubespray, thay inventory/biến có thể tác động control plane/CNI/etcd; không chạy playbook upgrade trên production chỉ vì lab lên cluster thành công. Đọc version matrix, backup etcd và thử staging.

## Case có lời giải: run playbook xong web server mất traffic

Play recap có `changed=8, failed=0`, nhưng Nginx trả 502. Đừng kết luận playbook thành công về dịch vụ. So config đã render, `nginx -t`, trạng thái/restart time, upstream address/port, error log và request smoke. Nếu template đổi upstream từ 8000 thành 8001 mà app vẫn nghe 8000, Ansible đã thực thi đúng điều **bạn khai báo**, nhưng khai báo sai. Khôi phục config đã biết tốt theo runbook, xác nhận traffic, rồi sửa biến/test. Một task validate có thể bắt syntax, nhưng không bắt upstream không tồn tại nếu cấu hình vẫn hợp lệ.

**Câu hỏi:** tại sao `changed=0` ở run thứ hai quan trọng? Nó là một bằng chứng idempotency của điều kiện lab; không chứng minh mọi môi trường. **Câu hỏi:** `--check` có đủ an toàn tuyệt đối? Không; hành vi phụ thuộc module/playbook và kết quả có thể thiếu. **Câu hỏi:** vì sao dùng `serial`? Để giới hạn blast radius, giữ capacity và quan sát giữa các batch. Nguồn: [Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html), [check/diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html).
